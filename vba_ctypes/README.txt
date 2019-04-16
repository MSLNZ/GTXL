6 March 2015
============

Began project to build a comtypes version of the GTXL COM server.

Have created the IDL file and built a shell server class that appears to be working in late binding (call from Python) and early binding (can register the DLL, but have not tested from VBA).

9 March 2015
============

Have modified the addin that worked with Pythoncom, but I cannot get it to load the server

16 March 2015
=============

The server.dll can be complied and an NSIS installer can register it on Windows. It's all good :-), except the problem associated with loading the Python uuid module.