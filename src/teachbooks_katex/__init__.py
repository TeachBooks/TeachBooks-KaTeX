from copy import deepcopy
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file
from sphinx.config import Config
from sphinx.errors import ExtensionError

import json5

from sphinx.util import logging

logger = logging.getLogger(__name__)

DEFAULT_OPTIONS = {
    "trust": True,  # to enable commands starting with `html`
    "strict": False,  # to disable stopping on errors/warnings
}

DEFAULT_MACROS = {
    "\\class": "\\htmlClass{#1}{#2}"  # port of MathJax `\class` to KaTeX `\htmlClass`
}

DEFAULT_SETTINGS = {"show_warnings": True}


def port_and_set_config(app: Sphinx, config: Config):
    # Load settings for this extension
    settings = config.teachbooks_katex
    if not isinstance(settings, dict):
        raise ExtensionError(
            "[TeachBooks-KaTeX] `config.teachbooks_katex` must be a dictionary, "
            f"not a {type(settings).__name__}."
        )
    settings = DEFAULT_SETTINGS | settings
    # Raise an exception if unrecognised settings are found
    unknown_keys = set(settings) - set(DEFAULT_SETTINGS)
    if unknown_keys:
        raise ExtensionError(
            "[TeachBooks-KaTeX] The following keys in `config.teachbooks_katex` "
            f"are not supported: {', '.join(sorted(str(k) for k in unknown_keys))}"
        )
    if not isinstance(settings["show_warnings"], bool):
        raise ExtensionError(
            "[TeachBooks-KaTeX] The value of `config.teachbooks_katex.show_warnings` "
            f"must be a true boolean, not {settings['show_warnings']!r} "
            f"({type(settings['show_warnings']).__name__})"
        )
    # Add our custom CSS using the sphinxcontrib.katex interface,
    # without overriding a user value
    config.katex_custom_css = "teachbooks-katex-math.css" | config.katex_custom_css
    # Load user KaTeX settings
    katex_options = config.katex_options
    if isinstance(katex_options, str):
        if not katex_options.startswith("{"):
            katex_options = "{\n" + katex_options
        if not katex_options.endswith("}"):
            katex_options = katex_options + "\n}"
        katex_options = json5.loads(katex_options)
    # Add non-set options from default options without overriding user options
    katex_options = DEFAULT_OPTIONS | katex_options
    # add default macros without overriding user macros
    if "macros" in katex_options:
        katex_options["macros"] = DEFAULT_MACROS | katex_options["macros"]
    else:
        katex_options["macros"] = DEFAULT_MACROS
    # Port MathJax settings
    mathjax3_config = config.mathjax3_config
    mathjax3_original = deepcopy(mathjax3_config)
    if mathjax3_config:
        if "loader" in mathjax3_config:
            if "load" in mathjax3_config["loader"]:
                if "ui/lazy" in mathjax3_config["loader"]["load"]:
                    if settings["show_warnings"]:
                        logger.warning(
                            "[TeachBooks-KaTeX] KaTeX does not (yet) support "
                            "lazy-loading. "
                            "If you would like to have this option, "
                            "please raise an issue or open a pull request. "
                            "Alternatively, consider setting "
                            "`config.katex_prerender = true` "
                            "and install `node.js`."
                        )
                    mathjax3_original["loader"]["load"].remove("ui/lazy")
                # clean up "loader.load"
                if not mathjax3_original["loader"]["load"]:
                    mathjax3_original["loader"].pop("load", None)
            # clean up "loader"
            if not mathjax3_original["loader"]:
                mathjax3_original.pop("loader", None)
        if "chtml" in mathjax3_config:
            if "mtextInheritFont" in mathjax3_config["chtml"]:
                config.katex_inherit_font = True
                # register handling of "chtml.mtextInheritFont"
                mathjax3_original["chtml"].pop("mtextInheritFont", None)
            # clean up "chtml"
            if not mathjax3_original["chtml"]:
                mathjax3_original.pop("chtml", None)
        if "tex" in mathjax3_config:
            if "macros" in mathjax3_config["tex"]:
                for name, command in mathjax3_config["tex"]["macros"].items():
                    if not isinstance(name, str):
                        name = str(name)
                    name = "\\" + name
                    if isinstance(command, list):
                        if len(command) > 2:
                            if not isinstance(command[2], list):
                                full_command = name + "[#1]"
                                for i in range(command[1] - 1):
                                    full_command += f"{{#{i + 2}}}"
                                new_command = full_command.replace("[#1]", "{#1}")
                                if settings["show_warnings"]:
                                    logger.warning(
                                        "[TeachBooks-KaTeX] Found macro with an "
                                        "optional argument. "
                                        "Currently such macros are not possible "
                                        "with KaTeX. "
                                        f"Replace the use of `{full_command}` "
                                        f"with `{new_command}`."
                                    )
                            else:
                                new_command = name
                                for i in range(command[1]):
                                    new_command += f"{{#{i + 1}}}"
                                full_command = name + command[2][0]
                                for i in range(command[1]):
                                    full_command += f"#{i + 1}"
                                    full_command += command[2][i + 1]
                                if settings["show_warnings"]:
                                    logger.warning(
                                        "[TeachBooks-KaTeX] Found macro with "
                                        "template strings. "
                                        "Currently such macros are not possible "
                                        "with KaTeX. "
                                        f"Replace the use of `{full_command}` "
                                        f"with `{new_command}`."
                                    )
                        command = command[0]
                    # katex defined macros take precedence
                    if name not in katex_options["macros"]:
                        katex_options["macros"][str(name)] = command
                # register handling of "tex.macros"
                mathjax3_original["tex"].pop("macros", None)
            # clean up "tex"
            if not mathjax3_original["tex"]:
                mathjax3_original.pop("tex", None)
    config.katex_options = katex_options
    if settings["show_warnings"] and mathjax3_original:
        logger.warning(
            "[TeachBooks-KaTeX] The following options in `mathjax3_config` "
            "have not been processed:\n"
            f"{json5.dumps(mathjax3_original, indent=4)}"
            "\nIf you would like to have (some of) these options processed, "
            "please raise an issue or open a pull request."
        )
    return


def copy_custom_assets(app: Sphinx, exc: Exception | None) -> None:
    # Only copy when building HTML and if the build succeeded
    if app.builder.format == "html" and not exc:
        src = Path(__file__).parent / "_static" / "teachbooks-katex-math.css"
        dest = Path(app.builder.outdir) / "_static"
        copy_asset_file(str(src), str(dest))


def modify_css_attributes(
    app: Sphinx, pagename: str, templatename: str, context: dict, doctree
) -> None:
    """Add crossorigin attribute to KaTeX CSS in page context."""
    if "css_files" not in context:
        return

    for css_file in context["css_files"]:
        # Sphinx uses _CascadingStyleSheet objects with filename and attributes
        if hasattr(css_file, "filename") and hasattr(css_file, "attributes"):
            # Match KaTeX CSS by filename
            if str(css_file.filename) == str(app.config.katex_css_path):
                # The attributes dict is mutable, even though the object is immutable
                css_file.attributes["crossorigin"] = "anonymous"


def setup(app: Sphinx):
    # Port MathJax and add KaTeX settings
    # Has to be before the builder-inited from sphinxcontrib.katex
    # Therefore connect with config-inited
    # Want to convert as many MathJax settings from other extensions
    # So very low priority
    app.connect("config-inited", port_and_set_config, priority=10000000000000000000)
    # Enable sphinxcontrib.katex
    app.setup_extension("sphinxcontrib.katex")
    # Copy our own custom KaTeX CSS for TeachBooks
    app.connect("build-finished", copy_custom_assets)
    # Add crossorigin='anonymous' to the KaTeX remote CSS
    app.connect("html-page-context", modify_css_attributes)
    # Add config values
    app.add_config_value("teachbooks_katex", {}, "env")

    return {}
