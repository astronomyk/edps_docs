"""Sphinx configuration for the unofficial EDPS documentation."""

# -- Project information -----------------------------------------------------

project = "ESO Data Processing System (EDPS)"
copyright = "European Southern Observatory (ESO). Documentation compiled by the EDPS docs contributors"
author = "L. Coccato, W. Freudling, S. Zampieri (original ESO manuals)"

# Version of the upstream material this site is derived from.
version = "1.3"
release = "EDPS tutorial 0.9.7 / workflow design guide 0.8"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.extlinks",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Treat single backticks as literal text rather than "title reference".
default_role = "literal"

# Substitutions available in every page.
rst_prolog = """
.. |edps| replace:: :abbr:`EDPS (ESO Data Processing System)`
"""

extlinks = {
    "eso": ("https://www.eso.org/%s", "eso.org/%s"),
}

todo_include_todos = False

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = "EDPS Documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "source_repository": "https://github.com/astronomyk/edps_docs/",
    "source_branch": "master",
    "source_directory": "docs/",
    "navigation_with_keys": True,
    "light_css_variables": {
        "color-brand-primary": "#0a5ca8",
        "color-brand-content": "#0a5ca8",
    },
    "dark_css_variables": {
        "color-brand-primary": "#6cb2f2",
        "color-brand-content": "#6cb2f2",
    },
}

# -- Options for copybutton --------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

# -- Options for LaTeX / PDF output ------------------------------------------

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "10pt",
}
