from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file
from sphinx.config import Config
from sphinx.application import Sphinx

def port_and_set_config(app: Sphinx, config: Config):
    # (TODO) port MathJax settings
    # (TODO) add our custom CSS
    return
 
def copy_custom_assets(app: Sphinx, exc: Exception | None) -> None:
    # Only copy when building HTML and if the build succeeded
    if app.builder.format == "html" and not exc:
        src = Path(__file__).parent / "_static" / "teachbooks-katex-math.css"
        dest = Path(app.builder.outdir) / "_static"
        copy_asset_file(str(src), str(dest))
 
def setup(app: Sphinx):
    # Enable sphinxcontrib.katex
    app.setup_extension("sphinxcontrib.katex")
    # Port MathJax and add KaTeX settings
    app.connect('config-inited', port_and_set_config)
    # Copy our own custom KaTeX CSS for TeachBooks
    app.connect("build-finished", copy_custom_assets)
    
    
    return {}