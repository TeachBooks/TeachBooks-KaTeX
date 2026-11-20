from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file
from sphinx.config import Config
from sphinx.application import Sphinx

def port_and_set_config(app: Sphinx, config: Config):
    # Add our custom CSS using the sphinxcontrib.katex interface
    config.katex_custom_css = "teachbooks-katex-math.css"
    # (TODO) Port MathJax settings
    return
 
def copy_custom_assets(app: Sphinx, exc: Exception | None) -> None:
    # Only copy when building HTML and if the build succeeded
    if app.builder.format == "html" and not exc:
        src = Path(__file__).parent / "_static" / "teachbooks-katex-math.css"
        dest = Path(app.builder.outdir) / "_static"
        copy_asset_file(str(src), str(dest))

def modify_css_attributes(app: Sphinx, pagename: str, templatename: str, 
                          context: dict, doctree) -> None:
    """Add crossorigin attribute to KaTeX CSS in page context."""
    if 'css_files' not in context:
        return
    
    for css_file in context['css_files']:
        # Sphinx uses _CascadingStyleSheet objects with filename and attributes
        if hasattr(css_file, 'filename') and hasattr(css_file, 'attributes'):
            # Match KaTeX CSS by filename
            if str(css_file.filename) == str(app.config.katex_css_path):
                # The attributes dict is mutable, even though the object is immutable
                css_file.attributes['crossorigin'] = 'anonymous'

def setup(app: Sphinx):
    # Port MathJax and add KaTeX settings
    # Has to be before the config-inited from sphinxcontrib.katex
    # Therefore first connect with high priority (low number == higher priority)
    app.connect('config-inited', port_and_set_config,priority=1)
    # Enable sphinxcontrib.katex
    app.setup_extension("sphinxcontrib.katex")
    # Copy our own custom KaTeX CSS for TeachBooks
    app.connect("build-finished", copy_custom_assets)
    # Add crossorigin='anonymous' to the KaTeX remote CSS
    app.connect("html-page-context",modify_css_attributes)
    
    return {}