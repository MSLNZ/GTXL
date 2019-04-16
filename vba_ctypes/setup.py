from distutils.core import setup
import py2exe
from glob import glob

data_files = [
		("Microsoft.VC90.CRT", glob(r'C:\usr\lib\msvcr\*.*'))
	]
    
class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the version info resources (Properties -- Version)
        self.version = "0.0.1"
        self.company_name = "Callaghan Innovation"
        self.copyright = "c 2015, Callaghan Innovation"
        self.name = "GTXL"

my_com_server_target = Target(
    description = "A COM server for uncertainty calculations",
    # use module name for win32com exe/dll server
    modules = ["server"],
    # the following line embeds the typelib within the dll
    other_resources = [("TYPELIB", 1, open(r"vba_ctypes.tlb", "rb").read())],
    # specify which type of com server you want (exe and/or dll)
    create_exe = False,
    create_dll = True
)

includes = ["win32com" ,"win32service", "win32serviceutil", "win32event"]
excludes = ['tcl', 'Tkconstants', 'Tkinter', 'distutils','numpy','unittest']
packages = []
dll_excludes = [
    'tcl84.dll', 'tk84.dll', 
    'SHFOLDER.dll', 
    'Secur32.dll', 
    'MPR.dll', 
    'CRYPT32.dll', 
    'KERNELBASE.dll',
    'MSASN1.dll', 'API-MS-Win-Core-LocalRegistry-L1-1-0','API-MS-Win-Core-ErrorHandling-L1-1-0.dll',
    'API-MS-Win-Core-LibraryLoader-L1-1-0.dll', 'API-MS-Win-Core-Misc-L1-1-0.dll',
    'API-MS-Win-Core-ProcessThreads-L1-1-0.dll', 'API-MS-Win-Core-Profile-L1-1-0.dll',
    'API-MS-Win-Core-String-L1-1-0.dll', 'API-MS-Win-Core-SysInfo-L1-1-0.dll',
    'API-MS-Win-Security-Base-L1-1-0.dll'
]
setup(
    data_files=data_files, 
    options={ "py2exe":
        dict(
            includes=includes,
            excludes=excludes,
            packages=packages,
            dll_excludes=dll_excludes,
            ascii=False,
            bundle_files=3,
            # skip_archive=True
        )      
    },
    ctypes_com_server = [my_com_server_target],
    zipfile=None,
)