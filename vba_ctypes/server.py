from gtxl.server.gtc_xl import GTXL

import comtypes
import comtypes.server.inprocserver
import logging
import os

# # generate wrapper code for the type library, this needs
# # to be done only once (but also each time the IDL file changes)
# # !!! NB  It needs to be done before py2exe is run !!!
# from comtypes.client import GetModule
# GetModule("vba_ctypes.tlb")

# Something has been created here
from comtypes.gen.GtxTypeLib import GtxObject

class GtxObjectImpl(GtxObject):

    # registry entries
    _reg_threading_ = "Both"
    _reg_progid_ = "GtxTypeLib.GtxObject"
#    _reg_novers_progid_ = "GtxTypeLib.GtxObject"
    _reg_desc_ = "A COM server for uncertainty calculation"
    _reg_clsctx_ = comtypes.CLSCTX_INPROC_SERVER

    def __init__(self):
        GtxObject.__init__(self)
        self.gtxl = GTXL()
        
    def gtc(self, caller, expression, arguments):
        """Stub for `gtc`"""
        return self.gtxl.gtc(caller, expression, arguments)

    def error(self, caller, cellref):
        """Stub for `error`"""
        return self.gtxl.error(caller, cellref)

    def empty(self, caller):
        """Stub for `empty`"""
        self.gtxl.empty(caller)

    def startup(self):
        """Stub for `start-up`"""
        return self.gtxl.startup()
        
if __name__ == "__main__":
    from comtypes.server.register import UseCommandLine
    UseCommandLine(GtxObjectImpl)
   
    # Does it work?
    # Must register the server using the two lines above first, 
    # then uncomment these and comment out those above.
    # from comtypes.client import CreateObject
    # x = CreateObject("GtxTypeLib.GtxObject")
    # print x.error("1cc","2")
