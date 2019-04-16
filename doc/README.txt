19 Dec 2014
===========

Created the sphinx configuration and managed to generate the HTML and HTMLHelp builds.

.. note::

    Need to remember to edit HTMLHELP in config.py: it changes the style used in the build.
    

Context IDs
-----------

I could not get the anchors to work, but it is possible to build a CHM file with Context IDs that link to the VBA function help. 

.. note::

    HAVE TO REMEMBER TO ADD THE MAP.H AND ALIAS.H FILES TO THE HHP PROJECT EACH TIME!

TODO
====

    * Have a problem with the root in the breadcrumbs navigation for HTML (don't know how to make that a parameter)