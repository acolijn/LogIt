import os
import sys
sys.path.insert(0, os.path.abspath('../../app/routes'))      # Point this to your code directory if needed
sys.path.insert(0, os.path.abspath('../'))       # Points to the docs directory
sys.path.insert(0, os.path.abspath('.'))  # Points to the source directory where your .rst files are


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'LogIt'
copyright = '2024, Auke Colijn'
author = 'Auke Colijn'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',   # Auto-generates documentation from docstrings
    'sphinx.ext.napoleon',  # Supports Google-style and NumPy-style docstrings
    'sphinx.ext.viewcode'  # Links to the source code in the documentation
]

templates_path = ['_templates']
exclude_patterns = []

autodoc_inherit_docstrings = True
# Default autodoc options
autodoc_default_options = {
    'members': True,  # Document all functions
    'undoc-members': True,  # Document even if some members don’t have docstrings
    'show-inheritance': True,  # Show class inheritance
    'private-members': False,  # Document only public members
    'special-members': False,
    'exclude-members': '__weakref__'
}

viewcode_import = True

#autodoc_mock_imports = ['pandas', 'shutil', 'json', 'mendeleev', 'nlohmann', 'app', 'flask', 'flask_login', 'pymongo', 'werkzeug', 'werkzeug.security', 'getpass', 'plotly', 'dash', 'dash_core_components', 'dash_html_components', 'dash.dependencies']
autodoc_mock_imports = ['pandas', 'pymongo', 'shutil', 'plotly', 'app']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
