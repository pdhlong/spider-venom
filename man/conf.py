# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options.
# For a full list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from glob import iglob
from os.path import dirname, join

FIGURE = """
.. figure:: {}

   .. include:: {}
"""

# Project information
project = 'spider-venom'

# Add any Sphinx extension module names here, as strings.
# They can be extensions coming with Sphinx (named 'sphinx.ext.*')
# or your custom ones.
extensions = ['sphinx.ext.githubpages']

# Options for HTML output
html_theme = 'alabaster'
html_logo = 'logo.png'
html_favicon = 'favicon.ico'
html_show_copyright = False

# Generate the result page
with open('results.rst', 'w') as results:
    results.write('Scraped images and captions\n'
                  '===========================\n')
    for image in iglob('venom/*/*/image.*'):
        results.write(FIGURE.format(image, join(dirname(image), 'caption')))
