6 March 2015
============

I need to separate the Python code that handles the Excel-GTC interface from the implementation of a COM server (because there are alternatives).

The contents of `gtc_xl.py` where copied from `vba/server.py` today, and the pythoncom-specific stuff (which implements a server) has been removed.

So now the `gtc_xl.py` module should be the common basis for different server implementations. 