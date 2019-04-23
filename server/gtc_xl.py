"""
Interface between GTC and XL.

The actual COM server will be handled elsewhere.
This module provides the underlying implementation

B D Hall, March 2015
 
"""
from __future__ import division

from GTC import *

# `global_context` is a snapshot of the module's globals
# but we can extend it by statements like:
#
#   exec "import math" in global_context
#
global_context = globals().copy()

from win32com.server.exception import COMException
import winerror

import os
import sys
import re
import itertools
import numbers
import types
import logging
import traceback 

# Control logging 
_LOG_ = False    

if _LOG_ :
    # The log file will be written to 
    #   `C:\Users\b.hall\AppData\Local\Temp`
    
    tmp = os.environ['TEMP']   
    logging.basicConfig(
        filename=r'C:\tmp\gtxl_log.txt',
        # filename=os.path.join(tmp,r'gtxl_log.txt'),
        level=logging.INFO
        # level=logging.DEBUG
    )

__all__ = ('GTXL',)

#--------------------------------------------------------------------------
# !!!NB!!!
# These re's may be too detailed, and therefore slow. It may be better to
# define just a minimum signature to be used to triage the input and let
# Python throw an error if the string is malformed.

# An assignment has the form: "valid_identifier (or tuple of identifiers) = anything", where
#   identifier ::=  (letter|"_") (letter | digit | "_" | "[" | "]")*
IDENTIFIER = r"[_a-zA-Z][\w]*(\[.*\])?"
ID_SEQUENCE = r"{IDENTIFIER}(\s*,\s*{IDENTIFIER})*".format(IDENTIFIER=IDENTIFIER)
re_assignment = re.compile(r'^{IDENTIFIER}\s*=.+'.format(IDENTIFIER=ID_SEQUENCE))

# A command starts as any valid identifier or a mathematical expression. So check
# after the assignment match has failed.
COMMAND = r'^[_a-zA-Z\(\+-][_\w\[\]]*'

# A list, or tuple, starts with `[`, or `(`, and could contain 
# pretty much anything after that!
SEQUENCE = r'^[\[\(].*'

re_command = re.compile(
    r"{0}|{1}".format(COMMAND,SEQUENCE)
)

# A number is also valid 
NUMBER = r"\d+[.\d]?\d*([eE][+-]\d{1,3})?"
SIGNED_NUMBER = "[+-]?{0}".format(NUMBER)
re_number = re.compile(
    r'^{0}'.format(SIGNED_NUMBER)
)
#re_number = re.compile(r'^\d*')

# Any `@` characters indicate substitutions are required
re_inline = re.compile(r'@')

IMAGINARY = r"{}[ji]".format(NUMBER)
REAL_IMAGINARY = r"{0}[+-]{1}".format(SIGNED_NUMBER,IMAGINARY)
BRACKETED_REAL_IMAGINARY = r"[(]{0}[)]".format(REAL_IMAGINARY)

COMPLEX_NUMBER = r"{0}|{1}|{2}".format(
    IMAGINARY,REAL_IMAGINARY,BRACKETED_REAL_IMAGINARY
)
re_complex_number = re.compile(COMPLEX_NUMBER)

ANY_NUMBER = r"{0}|{1}".format(
    SIGNED_NUMBER,COMPLEX_NUMBER
)
re_any_number = re.compile(ANY_NUMBER)

# The contents of an Excel cell are passed as '(???,cell-reference);'
# NB group(value) of any match is the '???' part, which may be an identifier
# or a real or complex number.
# group(ref) is the cell-reference part. 
# The Excel reference format is 
#   "'[wb_name]sheet'!R1C1"
# `wb_name` is any valid Windows file name including extension
# `sheet` is any valid sheet name 
# Note the ''! mark-up around the book-sheet combo.
VALID_CHAR = r"[^\/:*?<>|]"
VALID_WS_CHAR = r"[^\[\]*/\?:]"

# Note the use of non-greedy `*?`
CELL_REF = r"'?\[{VALID_CHAR}*?\]{VALID_WS_CHAR}*?'?!R\d+C\d+".format(
    VALID_CHAR=VALID_CHAR,
    VALID_WS_CHAR=VALID_WS_CHAR
)

ITEM = r"[(](?P<value>{ANY_NUMBER}|[_a-zA-Z][_\w\[\]]*),(?P<ref>{CELL_REF})[)]".format(
    ANY_NUMBER=ANY_NUMBER,
    CELL_REF=CELL_REF
)
re_item = re.compile(ITEM)

# Indirect inputs can only have a valid identifier as a value
IDENTIFIER_ITEM = r"[(](?P<value>{IDENTIFIER}),(?P<ref>{CELL_REF})[)]".format(
    IDENTIFIER=IDENTIFIER,
    CELL_REF=CELL_REF
)
re_item_id = re.compile(IDENTIFIER_ITEM)

# A single item may also be a sequence of items
#   i.e.: "[(value,cell_ref)(value,cell_ref)...];" 
re_seq_item = re.compile( r"\[(?P<item>{0})+\]".format(ITEM) )

#--------------------------------------------------------------------------
def _is_sequence(x):
    """
    True when `x` is a suitable sequence type (not a string!)
    
    """
    # NB namedtuple is also an instance of tuple
    return isinstance(x,(list,tuple))
            
#--------------------------------------------------------------------------
def _extract_value(s):
    """
    If `s` is a sequence, construct a Python list of values
    If `s` is just one item, return the value
    
    """
    # print "got {}".format(s)
    
    # Only the value part of the item is needed
    if re_seq_item.match(s) is not None:
        # if _LOG_ : 
            # logging.info(
                # "_extract_value sequence: got {}".format(
                    # s
                # )
            # )
        rtn = "[" + ",".join(
            item_i.group('value')
                for item_i in re_item.finditer(s)        
        ) + "]"
    else:
        # if _LOG_ : 
            # logging.info(
                # "_extract_value single: got {}".format(
                    # s
                # )
            # )
        rtn = re_item.match(s).group('value')
       
    # print "got {}, return {}".format(s,rtn)
    if _LOG_ : 
        logging.info(
            "_extract_value: return {}".format(
                rtn
            )
        )

    return rtn 
    
#--------------------------------------------------------------------------
def _xl_type_cast(x):
    """
    If `x` is a string or number type then return it unchanged
    otherwise return the repr() 
    
    `None` is also returned (not sure if this is good)
    
    """
    if isinstance(x,(numbers.Complex,types.StringTypes,types.NoneType)):
        return x
    else:
        raise RuntimeError(
            "invalid Excel type '{}'".format( repr(x) )
        )
        
#--------------------------------------------------------------------------
class GTXL(object):

    def __init__(self):
        self.register = dict()
        self.errors = dict()
                
    #------------------------------------------------------------------------
    def _asxl(self,cells,rtn):
        """
        Convert `rtn` to a suitable type for output to Excel
        
        A single complex number can be returned as an Excel 
        complex type or as a pair of real numbers
        
        """
        
        # Clear the calling range. If it is
        # bigger than the output, too bad:
        # just clear all the caller cell
        # error messages.
        for c in cells:
            if c in self.errors:
                del self.errors[c]
        
        n_cells = len(cells)
        
        if _is_sequence(rtn):
            
            if _is_sequence(rtn[0]):
                # Assume a 2-D iterable structure, where 
                # each element of `rtn` is iterable (not checked). 
                # The result is a 1-D list 
                rtn = list( itertools.chain.from_iterable(rtn) )
            else:
                rtn = [ x_i for x_i in rtn ]
                
            # print "array: ",repr(rtn)

            if len(rtn) > n_cells:
                # Error check the target range with the array size
                raise RuntimeError(
                    "Cannot return {} elements to {} cells".format(
                        len(rtn), n_cells
                    )
                )
            else:

                # `rtn` is a 1-D sequence of objects, but 
                # they may not be Excel-compatible! 
                rtn = [ _xl_type_cast(x_i) for x_i in rtn ]
                                        
                extra = n_cells - len(rtn)
                if extra > 0:
                    rtn += [""] * extra
                    assert len(rtn) == n_cells
                    # print "extra cells: ", rtn
                    
                    
        elif isinstance(rtn,complex):

            if n_cells == 1:
                # Excel uses a string format for complex numbers 
                if rtn.imag != 0.0:
                    rtn = "{0.real:.15G}{0.imag:+.15G}j".format(rtn)
                else:
                    rtn = "{0.real:.15G}".format(rtn)
                    
                    
            elif n_cells == 2:
                rtn = [rtn.real,rtn.imag]
                
            else:
                raise RuntimeError(
                    "Cannot return a complex to {} cells".format(
                        n_cells
                    )
                )
                    
        else:
            # Anything else

            rtn = _xl_type_cast(rtn)

            # Quite possibly more than one cell was
            # selected but a single object is returned!
            if n_cells != 1:
                raise RuntimeError(
                    "Cannot return '{}' to {} cells".format(
                        rtn, n_cells
                    )
                )            

        return rtn                 
        
    #--------------------------------------------------------------------------
    def _extract_args(self,s):
        """
        The method provides value-cell_ref pairs, where the value is a user 
        named object and the cell_ref is a reference to that object in the 
        GTXL register. 
        
        If `s` is a sequence string, construct a Python list of items
        If `s` is just one item, return the item
    
        """
        # print "got {}".format(s)
        
        # group('value') is the cell contents: the name 
        # group('ref') is the cell reference: the register key
        # group('value','ref') is a pair 
          
        try:
            if re_seq_item.match(s) is not None:
                # rtn = []
                # for i,item_i in enumerate( re_item_id.finditer(s) ):
                    # if _LOG_ and item_i is None:
                        # logging.info(
                            # "item: {} failed for {}".format(
                                # i,s
                            # )
                        # )
                    # ii = item_i.group('value','ref')
                    # rtn.append(ii)
                    
                rtn = [
                    item_i.group('value','ref')
                        for item_i in re_item_id.finditer(s)
                ]
            else:
                item = re_item_id.match(s)
                rtn = item.group('value','ref')
                
        except AttributeError as aerr:
            raise RuntimeError(
                "Internal error (invalid arguments): '{}'".format(s)
            )

        # print "got {}, return {}".format(s,rtn)
        return rtn 
   
    # #--------------------------------------------------------------------------
    # def _extract_args_seq(self,seq):
        # """
        # `seq` is of the form
            # [ (name,cell_ref), (name, cell_ref), ... ]
            
        # Take the first name and then form a sequence of objects 
        # by looking up the cell references. 
        
        # Return the name-sequence as a pair
        
        # """
        # name = seq[0][0]
        # seq = [
            # self.register[ x_i[1] ]
                # for x_i in seq 
        # ]
        
        # return name, seq 
   
    #------------------------------------------------------------------------
    def _arguments(self,s,n_subs):
        """
        `s` - a string of name-cell_ref pairs
        `n_subs` - the number of direct substitutions
    
        `s` is of the form
            "(name,cell ref); (name,cell ref); ..."
        or
            "(etc); [(name,cell ref)(name,cell ref)(name,cell ref)]; (etc); 
        where   
            `cell ref` is of the form "sheet_name!R1C1"
            and the second form defines a sequence of inputs
            to be treated as a single input
            
        If `s` is not empty then it finishes with a ';'
            
        """
        i_split, iN = 0, len(s)
                
        # `n_subs` might be > 0 yet `s` == "", or `n_subs` might 
        # be greater than the number of arguments supplied, 
        # these would be caused by user entry error. 
        if n_subs != 0:
            
            # `n_subs` is the number of direct substitutions 
            # being passed in the string `s`. Count off the same  
            # number of `;` separators and cut the string there. 
            # NB, we must have the trailing ';' for this to work 
            # if there are no indirect arguments. 
            for x in xrange(n_subs):
                 
                # Will raise ValueError if not found
                i_split = s.index(";",i_split+1,iN)
                
            # print s,i_split,s[:i_split]
            arg_strings = s[:i_split].split(';')  
            
            assert s[i_split] == ';'
            i_split += 1    # Step past it for later
            
            # These entries are of the form 
            #   "(value,cell ref); ...
            assert arg_strings != []
            # if _LOG_:
                # logging.info(
                    # "_arguments, arg_strings: {}".format(
                        # arg_strings
                    # )
                # )
                
            # subs = []
            # for s_i in arg_strings:
                # s_ii = _extract_value(s_i)
                # subs.append(s_ii)
                
            subs = [
                _extract_value(s_i) 
                    for s_i in arg_strings
            ]
        else:
            subs = []
               
        # We need to look up the remaining arguments in the register,
        # if there are any
        s_args = s[i_split:]
        if len(s_args) != 0:
        
            # There will always be a trailing ';' 
            assert s_args[-1] == ';'
            s_args = s_args[:-1]  
            
            # The leading ';' should be removed when `subs` is formed
            assert s_args[0] != ';'
            
            arg_strings = s_args.split(';')
            # print "arg strings", repr(s_args), repr(arg_strings)
            
            # At least one element 
            assert len(arg_strings) > 0
           
            arguments = [
                self._extract_args(s_i)  # either a pair or a sequence of pairs
                    for s_i in arg_strings 
            ] 
            
        else:
            arguments = []
         
        return subs, arguments
        
    #------------------------------------------------------------------------
    def _caller_lst(self,caller):
        """
        Return a list of cell references
        
        The caller may be a single cell or a range of cells
        
        """
        assert len(caller), caller
        
        if caller[-1] == ',':         
            caller = caller[:-1]    # Remove trailing separator
            
        cells = caller.split(',')
        
        return cells

    #------------------------------------------------------------------------
    def _raise_error(self,msg,cells,error):
        """
        Register `msg` with the calling cells and raise a `COMException` 
        
        `msg` - the gtc error message
        `cells` - a sequence of cell references for the caller
        `error` - the exception message
        
        """
        if _LOG_ : 
            logging.info(
                "_raise_error: got {!s}; {!s}; {!s}".format(
                    msg,cells,error
                )
            )
        # print "reg error: ",msg,cells
        N = len(cells)
        
        # print repr(error)
        # print dir(error)
        if isinstance(error,SyntaxError):
            description="{}: {}".format(error.msg,msg)
            
        elif isinstance(error,Exception):
            description="{}: {}".format(error.message,msg)
            
        else:
            # `error` is not an exception    
            description="{}: {}".format(error,msg)
                
        if N == 1:
            self.errors[cells[0]] = description
            if _LOG_ : 
                logging.info(
                    "_raise_error: logged: {!s} to {!s}".format(
                        cells[0],description
                    )
                )
                            
        elif N > 1:
            # for i in xrange(N):
                # self.errors[cells[i]] = description
            for c in cells:
                self.errors[c] = description
                if _LOG_ : 
                    logging.info(
                        "_raise_error: logged: {!s} to {!s}".format(
                            c,description
                        )
                    )
                
        else:
            # There must be at least one cell
            assert False
            
        raise COMException(
            description=description,
            hresult=winerror.DISP_E_EXCEPTION
        )
 
    #------------------------------------------------------------------------
    def _register(self,result,cells,identifier):
        """
        Register `result` with the `cells` and return `identifier`

        `result` - object
        `cells` - a sequence of cell references
        `identifier` - the identifier Excel will receive       
        
        If `identifier` is a comma separated sequence use 
        it to name each of the objects referred to. 
        
        """
        N = len(cells)
        
        if N == 1:
            self.register[cells[0]] = result
            if cells[0] in self.errors: 
                del self.errors[cells[0]]
            # print "registered {} = result".format(cells[0])
            return identifier
            
        elif N == 2 and isinstance(result,complex):
            ids = []
            
            self.register[cells[0]] = result.real
            if cells[0] in self.errors: 
                del self.errors[cells[0]]
                
            ids.append(
                "{!s}.re".format(identifier)
            )
            
            self.register[cells[1]] = result.imag
            if cells[1] in self.errors: 
                del self.errors[cells[1]]
                
            ids.append(
                "{!s}.im".format(identifier)
            )
            
            return ids
                
        elif N > 1:
            id_names = [x.strip() for x in identifier.split(',')] 
            n_names = len(id_names) 
            assert n_names > 0
            
            # If `result` does not support `len()` raises TypeError
            if len(result) != N:
                raise RuntimeError(
                    "'{!r}' does not fit in the calling range".format(result)
                )
            # When a multi-cell range is associated with a
            # name, append `[x,y]` to the name to identify
            # each cell individually.
            elif n_names > 1:
                if n_names != N:
                    raise RuntimeError(
                        "'{!s}' does fit the calling range".format(id_names)
                    )
                else:
                    for i in xrange(N):
                    
                        self.register[ cells[i] ] = result[i]
                        if cells[i] in self.errors: 
                            del self.errors[cells[i]]
                            
                    return id_names
                             
            else:
                ids = []
                for i in xrange(N):
                
                    self.register[ cells[i] ] = result[i]
                    if cells[i] in self.errors: 
                        del self.errors[cells[i]]
                        
                    ids.append(
                        "{0:s}_{1:d}".format(
                            identifier,i
                        )
                    )
                return ids
        else:
            assert False
        
    #------------------------------------------------------------------------
    def gtc(self,caller,expression,arguments):
        """
        Execute GTC expressions with `arguments` in the local context 
        
        The expression may be an assignment or simply 
        a command. Assignments will be registered, and
        the associated name is returned, commands will 
        simply be returned.
        
        """
        if _LOG_ : 
            logging.info(
                '''gtc:
                    caller: {}
                    expression: {}
                    arguments: {}
                '''.format(
                   caller,expression,arguments 
                )
            )
        
        # Process the caller string into a sequence of cell references
        cells = self._caller_lst(caller)
        # print "cells: ",cells
        
        try:
            # Any `@` characters are replaced with `{}` and  
            # the number of instances is reported. 
            expr, n_substitutions = re_inline.subn('{}',expression)
            # print "expression: ",expression
            # print "expr: ",expr
     
            # Process the `arguments` string. 
            # Obtain a sequence of direct string values for substitution in `subs` 
            # and a mapping of names to values in `args`
            subs, args_ = self._arguments(arguments, n_substitutions)
            
        except Exception as error:
            if _LOG_:
                logging.info(
                    "failed to separate subs and args (line 620) gtc_xl"
                )
            self._raise_error(
                "invalid arguments for: '{}'".format(expression),
                cells,
                error
            )
        # print "arguments substituted ",arguments, subs, args_
        
        assert n_substitutions == len(subs),(n_substitutions, len(subs))
        
        # Retrieve registered objects for the remaining arguments
        # An unregistered cell raises KeyError
        args = global_context.copy()    
        # args = dict()
        try:
            for a_i in args_:
                if isinstance(a_i,list):
                    # # Extract the registered values from the list in a sequence
                    # # and associate that sequence with the first named argument 
                    # k, seq = self._extract_args_seq(a_i) 
                    # # print "Adding '{}'".format(k)
                    # args[ k ] = seq
                    
                    # Extract the registered values from a sequence of 
                    # name-cell_ref pairs and add them to the mapping 
                    # of arguments. 
                    arg_seq = {
                        x_i[0] : self.register[ x_i[1] ]
                            for x_i in a_i
                    }
                    args.update( arg_seq )
                else:
                    # print "Adding '{}'".format(a_i[0])
                    args[ a_i[0] ] = self.register[ a_i[1] ]
        
        except Exception as error:
            # print "unregistered arguments: {}; {}".format(args,error)
            self._raise_error(
                "GTXL System Error: unregistered argument",
                cells,
                error
            )
        # print "args", args
                    
        if len(expr):
            # Make the direct substitutions now 
            expr_s = expr.format(*subs)
            # print repr(expr_s)
            
            if re_assignment.match(expr_s) is not None:
                # A valid assignment syntax 
                
                identifier,ix,operation = expr_s.partition('=')
                # print "expression: ",expr_s,args
                # print identifier,ix,operation

                try:
                    # result = eval(operation,args) 
                    opn = compile(operation.strip(),'<GTX>','eval')
                    result = eval(opn,args) 
                except Exception as error:
                    # print "assignment error: ",error
                    # print "identifier: ",repr(identifier)
                    # print "operation: ",repr(operation)
                    # print "args ", args
                    
                    # print 
                    # for k,v in global_context.iteritems():
                        # print " {}: {}".format(k,repr(v)) 
                        
                    # print
                    # for k,v in args.iteritems():
                        # print " {}: {}".format(k,repr(v)) 

                    self._raise_error(
                        "'{}'".format(expr_s),
                        cells,
                        error
                    )
                
                # The result must be registered using the cell 
                # references as keys
                try:
                    return self._register(result,cells,identifier.strip())
                except Exception as error:
                    # print "registration error: ", str(error)
                    self._raise_error(
                        "GTXL System Error: could not register '{}'".format(result),
                        cells,
                        error
                    )
                           
            elif re_command.match(expr_s) is not None:
                # A valid command syntax 
                # NB this must come after the assignment test!
                # print "command: ",expr_s,args
                try:
                    # rtn = eval(expr_s,args) 
                    opn = compile(expr_s.strip(),'<GTX>','eval')
                    rtn = eval(opn,args)                    
                except Exception as error:
                    # print "command error: ", error
                    self._raise_error(
                        "'{}'".format(expr_s),
                        cells,
                        error
                    )
                
                # Process the return values to be in a form 
                # that VBA can interpret.
                try:
                    return self._asxl(cells,rtn)
                except Exception as error:
                    # print "output error: ", str(error)
                    self._raise_error(
                        "Output error",
                        cells,
                        error
                    )
                                    
            elif re_number.match(expr_s) is not None:
                # A valid number syntax 
                # NB this must come after the assignment test!
                
                try:
                    # rtn = eval(expr_s,args)
                    opn = compile(expr_s.strip(),'<GTX>','eval')                    
                    rtn = eval(opn,args)                    
                    return self._asxl(cells,rtn)
                except Exception as error:
                    # print "number error: ", expr_s
                    self._raise_error(
                        "'{}'".format(expr_s),
                        cells,
                        error
                    )
                

            else:
                # print "Invalid format: '{}'".format(expr_s)
                self._raise_error(
                    "'{}'".format(expr_s),
                    cells,
                    "Invalid input"
                )

    #------------------------------------------------------------------------
    def error(self,caller,cellref):
        """
        `caller` - a single cell reference
        `cellref` - a single cell reference to the cell with an error
        
        Return an error message, if registered
        
        """
        if _LOG_ : logging.info(
            '`error:` from {!s} for error in {!s}'.format(caller,cellref)
        )
        cells = self._caller_lst(caller)
        
        if len(cells) != 1:
            raise COMException(
                description=str(
                    "This function requires a single cell reference"
                ),
                hresult=winerror.DISP_E_EXCEPTION
            )
        else:
            try:
                if _LOG_ : logging.info(
                    '`error: ` registered msg: {!s}'.format(self.errors[cellref])
                )
                return self.errors[cellref]
            except KeyError:
                # No error recorded
                if _LOG_ : logging.info(
                    '`error: ` no registered msg\nOther keys: {!s}'.format(self.errors.keys())
                )
                return "OK"
                
        
    #------------------------------------------------------------------------
    def empty(self,caller):
        """
        Any cell references in `caller` will be removed from the register
        
        This function is called when VBA detects that a cell has changed and 
        does not refer to anything defined by GTC. 
        
        """
        if _LOG_ : logging.info('called `empty`')
        cells = self._caller_lst(caller)
        
        reg = self.register
        err = self.errors
        for cell_i in cells:
            if cell_i in reg: 
                # print "removed: ",cell_i
                del reg[cell_i]
            if cell_i in err: 
                # print "error removed: ",cell_i
                del err[cell_i]

    #------------------------------------------------------------------------
    def startup(self):
        """
        Add directories to `sys.path` and run startup scripts 
        
        The scripts directories may contain Python package folders.
        
        The startup directory may contain individual modules 
        
        All the `.py` modules in the startup directory will be 
        executed, to configure GTXL with user-defined functions.
        
        """
        if 'GTXL_LIB' in os.environ:
            scripts = os.environ['GTXL_LIB'].split(';')

            if _LOG_ : 
                logging.info(
                    "GTXL_LIB: {}".format(scripts)
                )

            for p_i in scripts:
                if _LOG_  and not os.path.isdir(p_i):
                    logging.info(
                        "startup: not a folder {}".format(p_i)
                    ) 
                # This adds the directory to the search path 
                # It does not modify `global_context`
                sys.path.insert(0,p_i) 

        if 'GTXL_STARTUP' in os.environ:
            startup = os.environ['GTXL_STARTUP']
            
            if len(startup):
                if _LOG_ and not os.path.isdir(startup):
                    logging.info(
                        "startup: not a folder {}".format(p_i)
                    )   
                
                files = [
                    f_i for f_i in os.listdir(startup)    
                        if os.path.splitext(f_i)[1] == '.py'
                ]
                
                for f_i in files: 
                    e = self.script( os.path.join(startup,f_i) )   
                    if e != '': return e
        
        return ''
        
            
    #------------------------------------------------------------------------
    def script(self,file):
        """
        `file` - a GTC filename and path for context initialisation
        
        """
        if _LOG_ : logging.info("called `script` with : {}".format(file))
        global global_context
        
        if not os.path.isfile(file):
            error_msg = "file not found: '{}'".format(file)
            if _LOG_ : logging.info("Error : {}".format(error_msg))
            # print error_msg
            return error_msg
            
        else:
            try:
                with open(file,'r') as f:
                    exec(f.read(),global_context)
                    
                return ""
                
            except Exception as x:
                if _LOG_ : logging.info("script: error: {}".format(x))
                return _excepthook(file) 
                
        if _LOG_ : logging.info("`script` OK")
   
#-----------------------------------------------------------------
def _excepthook(file):
    """
    This function re-defines error reporting
    
    `file` - the full path to the file being executed

    """
    # `tp` is the exception type
    # `va` is the exception parameter
    # `tb` is the traceback object, which encapsulates
    #   the call stack at the point
    #   where the exception originally occurred  
    tp,va,tb = sys.exc_info() 
    
    # The API module names need to be augmented
    # with all other modules in GTC, as an error
    # may arise anywhere. 
    submodules = (
        'function','reporting','linear_algebra',
        'type_b','type_a','core','number_strings',
        'sim','archive'
    )
    
    modules = submodules + (
        'context','library_real','library_complex','LU',
        'symmetric_matrix','named_tuples','special_fns',
        'node','vector','quantiles'
    )
    # These `outer_modules` provide the top level calling
    # context, which we need to remove.
    outer_modules = ('gtc_xl',)
    
    # Need to step through the traceback chain
    # until something in the GTC libraries is
    # found. The source for these is unavailable
    # to users, so we do not report beyond that.
    
    # `depth` will be set to avoid inaccessible GTC modules
    outer = 0
    depth = 0
    t = tb
    while True: 
        name = os.path.splitext(
            os.path.basename(t.tb_frame.f_code.co_filename)
        )[0]
        
        if name in outer_modules: outer += 1
        if name in modules: break
        
        depth += 1
            
        if t.tb_next is not None:   
            t = t.tb_next
        else:
            break

    _text = ''
    # _text ="{}:\r\n".format(file)

    tb_text = traceback.format_exception(tp,va,tb,depth)
    
    # The first line is just the intro: `Traceback (most recent call last):`
    _text += "{}\r\n".format( tb_text[0] )
    
    # Now skip any reference to the outer modules as well as
    # any reference to internal GTC modules
    for l in tb_text[1+outer:]:
        l = l.replace('<string>',file,1)
        _text += "{}\r\n".format(l)  

    return _text