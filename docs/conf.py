# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup ---------------------------------------------------------------
# Add the project root so autodoc can import app.py
sys.path.insert(0, os.path.abspath('..'))

# Set environment variables required by app.py to avoid errors at import time
os.environ.setdefault('SECRET_KEY', 'sphinx-doc-key')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')

# -- Project information ------------------------------------------------------
project = 'Dev Journal'
copyright = '2024, Dev Journal Contributors'
author = 'Dev Journal Contributors'
release = '1.0.0'

# -- General configuration ----------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',      # Support Google/NumPy style docstrings
    'sphinx.ext.viewcode',      # Add source code links
    'sphinx.ext.intersphinx',   # Link to other Sphinx projects
    'sphinx.ext.todo',          # Support .. todo:: directives
]

# Napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_attr_annotations = True

# autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,
    'show-inheritance': True,
    'member-order': 'bysource',
}
autodoc_typehints = 'description'
autodoc_mock_imports = ['flask_sqlalchemy', 'flasgger']

# intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/3.0.x/', None),
}

todo_include_todos = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


def _strip_flasgger_yaml(app, what, name, obj, options, lines):
    """Remove Flasgger OpenAPI YAML sections (after '---') from docstrings.

    Flasgger uses a '---' separator followed by YAML in docstrings to define
    OpenAPI specs. These sections cause RST parse errors in Sphinx. This hook
    strips everything from '---' onward before Sphinx renders the docstring.
    """
    try:
        separator = lines.index('---')
        del lines[separator:]
    except ValueError:
        pass  # No Flasgger section found, nothing to strip


def setup(app):
    """Register Sphinx event hooks."""
    app.connect('autodoc-process-docstring', _strip_flasgger_yaml)


# -- Options for HTML output --------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2c3e50',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

html_static_path = []
html_title = 'Dev Journal Documentation'
html_short_title = 'Dev Journal'
