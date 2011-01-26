Nanozope
========

Experimental minimalistic publisher for WSGI-based Zope3/BlueBream sites.

Main goals:

- be minimalistic as possible
- reduced memory footprint
- be enought to support functionality needed by z3c.contents / z3c.forms


Various notes
--------------
paster setup-app  zope.ini#nanozope bootstrap zodb and fire bootstrap events.

Set bootstrap_database = False in paster .ini to inhibit database events on
startup.


Examples
--------

docs/examples/* contains some useless examples copied from test installation
