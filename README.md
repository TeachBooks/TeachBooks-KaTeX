# TeachBooks KaTeX

A wrapper for [sphinxcontrib.katex](https://sphinxcontrib-katex.readthedocs.io/).

TeachBooks KaTeX operates as a Sphinx extension target to TeachBooks. When you enable it, it:

1. **Loads automatically** when you enable it in your `_config.yml`;
2. **Converts MathJax settings** from `mathjax3_config` to `katex_options` for compatibility;
3. **Applies TeachBooks defaults** to KaTeX options and adds custom CSS;
4. **Reports on conversion** via warnings if `show_warnings` is enabled.

## Requirements

- **Python**: >=3.11
- **Sphinx**: (automatically installed as dependency)
- **sphinxcontrib.katex**: (automatically installed as dependency)

## Installation

To install the TeachBooks KaTeX extension, follow these steps:

**Step 1: Install the Package**

Install the `TeachBooks KaTeX` package using `pip`:
```
pip install teachbooks-katex
```

**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
teachbooks-katex
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions:
```
sphinx: 
  extra_extensions:
      - teachbooks_katex
```

## Configuration

The following Sphinx configuration options are exposed currently, with the following default values:

```
sphinx:
  config:
    teachbooks_katex:
      show_warnings: true
```

If `teachbooks_katex.show_warnings` is `true`, warnings on

- lazy loading;

- MathJax3 macros that result in unsupported KaTeX syntax;

- unprocessed MathJax3 settings;

are shown if applicable.

**Advice**: Initially use the default value `true`. When everything works as you prefer, set to `false`.

## Project Structure

The package contains:

- **`src/teachbooks_katex/__init__.py`** — Main extension code that handles Sphinx extension setup, configuration validation, and automatic MathJax-to-KaTeX setting conversion
- **`src/teachbooks_katex/_static/teachbooks-katex-math.css`** — Custom CSS for TeachBooks-specific math styling, including:
  - Responsive equations (scrollable on small screens)
  - Increased margins around equations
  - Equation number formatting and permalinks
  - Text styling within math expressions

## Usage

### Automatic MathJax Setting Conversion

Some existing MathJax settings will be automatically ported to KaTeX settings from [sphinxcontrib.katex](https://sphinxcontrib-katex.readthedocs.io/). The next table indicates which are currently supported:

| MathJax setting | Status | KaTeX result |
| --- | --- | --- |
| `chtml.mtextInheritFont` | Supported | Sets `katex_inherit_font = True`. |
| `tex.macros` | Supported (with warnings for some macros) | Added to `katex_options.macros`; macros already defined by KaTeX are not overridden. Macros with an optional argument or template strings are ported as-is and produce a warning, since KaTeX does not support them. |
| `loader.load` with `ui/lazy` | Not supported | Ignored, with a warning. |
| Any other setting | Not supported | Left unprocessed, with a warning listing it. |

### Warning Examples

When `show_warnings` is `true`, you may see warnings like:

**Lazy-loading not supported:**
```
[TeachBooks-KaTeX] KaTeX does not (yet) support lazy-loading.
If you would like to have this option, please raise an issue or open a pull request.
Alternatively, consider setting `config.katex_prerender = true` and install `node.js`.
```

**Macro with optional argument:**
```
[TeachBooks-KaTeX] Found macro with an optional argument.
Currently such macros are not possible with KaTeX.
Replace the use of `\myMacro[#1]{#2}{#3}` with `\myMacro{#1}{#2}{#3}`.
```

**Unprocessed settings:**
```
[TeachBooks-KaTeX] The following options in `mathjax3_config` have not been processed:
{
    "myCustomOption": true
}
If you would like to have (some of) these options processed, please raise an issue or open a pull request.
```

### TeachBooks KaTeX Defaults

Furthermore, the following changes are made compared to the defaults from [sphinxcontrib.katex](https://sphinxcontrib-katex.readthedocs.io/):

| Setting | Default value | TeachBooks KaTeX value | Reason |
| --- | --- | --- | --- |
| `katex_options.trust` | `False` | `True` | Enables KaTeX commands starting with `html`, such as `\htmlClass` for custom styling. |
| `katex_options.strict` | `True` | `False` | Disables stopping on rendering errors or warnings, allowing builds to continue even if some math fails to render. |
| `katex_options.macros.\class` | Not defined | `\htmlClass{#1}{#2}` | Provides a MathJax-compatible `\class` macro for adding CSS classes to math expressions. |
| `katex_custom_css` | CSS provided by [sphinxcontrib.katex](https://sphinxcontrib-katex.readthedocs.io/) | `teachbooks-katex-math.css` (if not overridden by user in Sphinx configuration.) | Loads TeachBooks-specific styling for mathematics rendering. User values are not overridden. |

These defaults can be overridden by adding options from [sphinxcontrib.katex](https://sphinxcontrib-katex.readthedocs.io/) in your Sphinx configuration.

## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/TeachBooks-KaTeX). If you'd like to contribute, you can open an issue or create a pull request on the [GitHub repository](https://github.com/TeachBooks/TeachBooks-KaTeX).