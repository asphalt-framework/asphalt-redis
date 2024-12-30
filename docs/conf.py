#!/usr/bin/env python3
import importlib.metadata

from packaging.version import parse

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "asphalt-redis"
author = "Alex Grönholm"
copyright = "2016, " + author

v = parse(importlib.metadata.version(project))
version = v.base_version
release = v.public

language = "en"

exclude_patterns = ["_build"]
pygments_style = "sphinx"
autodoc_default_options = {"members": True, "show-inheritance": True}
autodoc_inherit_docstrings = False
highlight_language = "python3"
todo_include_todos = False

html_theme = "sphinx_rtd_theme"
htmlhelp_basename = project.replace("-", "") + "doc"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "asphalt": ("https://asphalt.readthedocs.org/en/latest/", None),
    "redis": ("https://redis.readthedocs.org/en/latest/", None),
}
