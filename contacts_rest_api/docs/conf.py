import sys
import os

sys.path.append(os.path.abspath('..'))
# List of modules to mock
# autodoc_mock_imports = ['main', 'src.routes.contacts', 'src.routes.users', 'src.routes.auth', 'src.services.auth', 'src.services.email']

project = 'Contacts REST API'
copyright = '2023, lana-sviatash'
author = 'lana-sviatash'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
