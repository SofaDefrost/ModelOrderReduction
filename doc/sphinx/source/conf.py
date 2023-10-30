# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
# see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import os
import sys

sys.path.append(os.getcwd()+"/../../../python")

project = u'ModelOrderReduction'
copyright = u'2018, Defrost Team'
author = u'Defrost Team'

# The short X.Y version
version = u'1.0'
# The full version, including alpha/beta/rc tags
release = u'1.0'


# -- General configuration ---------------------------------------------------

extensions = [
    # extension autodoc
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints', # Automatically document param types (less noise in class signature)
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    # 'sphinx.ext.doctest',
    # 'sphinx.ext.autosectionlabel',

    # Link to source code
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',

    'sphinxcontrib.bibtex',

    # Generate pdf
    # 'rst2pdf.pdfbuilder'
]

bibtex_bibfiles = ['references.bib']

#################################
### THEME
#################################
extensions.extend([
    # Doc Theme
    'sphinx_rtd_theme',])
html_theme = "sphinx_rtd_theme"
# see here for options
# https://sphinx-rtd-theme.readthedocs.io/en/stable/configuring.html
# html_theme_options = {'navigation_depth': 4,}#"collapse_navigation":True,}
#show_nav_level": 2,}
#################################
###     MYST_PARSER
#################################
extensions.extend([
    # new parser
    'myst_parser',
    # 'autodoc2',
    ])

suppress_warnings = ["design.fa-build"]
myst_enable_extensions = ["colon_fence", "deflist", "substitution", "html_image"]

## autodoc2 options
# autodoc2_packages = [
#     {
#         "path": "../../../python",
#         "auto_mode": False,
#     },
# ]
# autodoc2_module_all_regexes = [
#     r"python\..*",
# ]
#################################
###     sphinx.ext.autodoc
#################################
autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = False  # If no docstring, inherit from base class
#autodoc_typehints = "description" # Sphinx-native method. Not as good as sphinx_autodoc_typehints
set_type_checking_flag = False  # Enable 'expensive' imports for sphinx_autodoc_typehints
add_module_names = False # Remove namespaces from class/method signatures

## Include Python objects as they appear in source files
## Default: alphabetically ('alphabetical')
autodoc_member_order = 'bysource'
## Default flags used by autodoc directives
autodoc_default_flags = []
## Generate autodoc stubs with summaries from code
autosummary_generate = True
autoclass_content = 'both' # When auto doc a class it will automatically add the special method __init__ doc
add_function_parentheses = False
#################################
### FOR GOOD UI
#################################
extensions.extend([
    'sphinx_design',
    'sphinx_copybutton',
    'sphinxemoji.sphinxemoji',])
#################################
###     C++ doc
#################################
# extensions.extend([
    # C++ doc with Breathe
    # 'sphinx.ext.ifconfig',
    # 'sphinx.ext.todo',
    # 'breathe',
    # 'exhale'])
#################################

pdf_documents = [('index', u'morDoc', u'Model Order Reduction Documentation', u'Olivier Goury & Félix Vanneste')]

# myst_heading_anchors = 1
# Make sure the target is unique
autosectionlabel_prefix_document = True



# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = [u'_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Custom html visual -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
# html_css_files = []
# html_js_files = []

# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``
html_sidebars = {
    '**': [
            'about.html',
            'navigation.html',
            'searchbox.html',
    ]
}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ModelOrderReductiondoc'


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'ModelOrderReduction.tex', u'ModelOrderReduction Documentation',
     u'Defrost Team', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'modelorderreduction', u'ModelOrderReduction Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'ModelOrderReduction', u'ModelOrderReduction Documentation',
     author, 'ModelOrderReduction', 'One line description of project.',
     'Miscellaneous'),
]


# -- Extension configuration -------------------------------------------------

autodoc_mock_imports = ['Sofa',
                        'stlib3','splib3',
                        'SofaPython','Quaternion','SofaPython.Quaternion',  # Needed for numerics
                        'PythonScriptController', 'Sofa.PythonScriptController',
                        'launcher',
                        # 'yaml',
                        'numpy','scipy',
                        'PyQt5',"PyQt5.QtCore","PyQt5.QtGui","PyQt5.QtWidgets"]

# MOCK_CLASSES = [
#     # classes you are inheriting from
#     "QAbstractItemModel",
#     "QDialog",
#     "QCompleter",
#     "QWidget",
#     "QLineEdit",
#     "QMainWindow"
# ]
#
# MockingClass = type('MockingClass', (), {})
#
# from unittest import *
# from mock import MagicMock
# class Mock(MagicMock):
#     @classmethod
#     def __getattr__(cls, name):
#         if name in MOCK_CLASSES:
#             return object #MockingClass
#         return MagicMock()


# -- Intersphinx configuration -------------------------------------------------

intersphinx_mapping = {
    'stlib': ('https://stlib.readthedocs.io/en/latest/', None),
    'python': ('https://docs.python.org/3', None),
    'softrobotscomponents': ('https://softrobotscomponents.readthedocs.io/en/latest/', None),
    'sofaPy3':('https://sofapython3.readthedocs.io/en/latest/',None)
}
intersphinx_disabled_reftypes = ["*"]

###########################################################
# -- To Build EXHALE --------------------------------------

# # Setup the breathe extension
# breathe_projects = {
#     "ExhaleTest": "./doxyoutput/xml"
# }
#
# breathe_default_project = "ExhaleTest"
# import textwrap
# # Setup the exhale extension
# exhale_args = {
#     # These arguments are required
#     "containmentFolder":     "./api",
#     "rootFileName":          "library_root.rst",
#     "rootFileTitle":         "Library API",
#     "doxygenStripFromPath":  "../../../src/ModelOrderReduction/component",
#     # Suggested optional arguments
#     "createTreeView":        True,
#     # TIP: if using the sphinx-bootstrap-theme, you need
#     # "treeViewIsBootstrap": True,
#     # "verboseBuild":True
#     "exhaleExecutesDoxygen": True,
#     "exhaleDoxygenStdin":    textwrap.dedent('''
#         INPUT = ../../../src/ModelOrderReduction/component
#         FILE_PATTERNS = *.h
#         ''')
# }

# # Tell sphinx what the primary language being documented is.
# primary_domain = 'cpp'

# # Tell sphinx what the pygments highlight language should be.
# highlight_language = 'cpp'

###############################################################################
# -- To Build Breath doc with ReadTheDocs--------------------------------------


# # Breathe 
# import glob


# listProject = [("loader",os.getcwd()+"/../../../src/component/loader"),
#                ("forcefield",os.getcwd()+"/../../../src/component/forcefield"),
#                ("mapping",os.getcwd()+"/../../../src/component/mapping")]

# breathe_projects_source = {}

# def addDoxiProject(projectName,pathToProject,filesType = "/*.h"):
#     filesPath = glob.glob(pathToProject+filesType)
#     filesNames = [os.path.basename(x) for x in filesPath]
#     print(filesNames)
#     breathe_projects_source[projectName] = (pathToProject,filesNames) 

# for projectName,pathToProject in listProject:
#     addDoxiProject(projectName,pathToProject)

# print (breathe_projects_source)

# breathe_default_members = ('members', 'undoc-members')

# breathe_doxygen_config_options = {
#     'ENABLE_PREPROCESSING' : 'YES',
#     'PREDEFINED' : 'DOXYGEN_SHOULD_SKIP_THIS',
#     'EXTRACT_LOCAL_METHODS' : 'YES',
#     'HIDE_UNDOC_MEMBERS' : 'YES',
#     'HIDE_UNDOC_CLASSES' : 'YES',
#     'HIDE_SCOPE_NAMES' : 'YES'}

# import subprocess

# # read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

# # if read_the_docs_build:

# #     subprocess.call('cd .. ; doxygen', shell=True)
# #     html_extra_path = ['../build/html']

# def run_doxygen(folder):
#     """Run the doxygen make command in the designated folder"""

#     try:
#         retcode = subprocess.call("cd %s; make" % folder, shell=True)
#         if retcode < 0:
#             sys.stderr.write("doxygen terminated by signal %s" % (-retcode))
#     except OSError as e:
#         sys.stderr.write("doxygen execution failed: %s" % e)


# def generate_doxygen_xml(app):
#     """Run the doxygen make commands if we're on the ReadTheDocs server"""

#     read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

#     if read_the_docs_build:

#         run_doxygen("../../../src/component/loader")
#         run_doxygen("../../../src/component/forcefield")
#         run_doxygen("../../../src/component/mapping")

# def setup(app):

#     # Add hook for building doxygen xml when needed
#     app.connect("builder-inited", generate_doxygen_xml)