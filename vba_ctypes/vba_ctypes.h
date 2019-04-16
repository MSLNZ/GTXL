

/* this ALWAYS GENERATED file contains the definitions for the interfaces */


 /* File created by MIDL compiler version 7.00.0555 */
/* at Wed Apr 29 16:38:47 2015
 */
/* Compiler settings for vba_ctypes.idl:
    Oicf, W1, Zp8, env=Win32 (32b run), target_arch=X86 7.00.0555 
    protocol : dce , ms_ext, c_ext, robust
    error checks: allocation ref bounds_check enum stub_data 
    VC __declspec() decoration level: 
         __declspec(uuid()), __declspec(selectany), __declspec(novtable)
         DECLSPEC_UUID(), MIDL_INTERFACE()
*/
/* @@MIDL_FILE_HEADING(  ) */

#pragma warning( disable: 4049 )  /* more than 64k source lines */


/* verify that the <rpcndr.h> version is high enough to compile this file*/
#ifndef __REQUIRED_RPCNDR_H_VERSION__
#define __REQUIRED_RPCNDR_H_VERSION__ 475
#endif

#include "rpc.h"
#include "rpcndr.h"

#ifndef __RPCNDR_H_VERSION__
#error this stub requires an updated version of <rpcndr.h>
#endif // __RPCNDR_H_VERSION__

#ifndef COM_NO_WINDOWS_H
#include "windows.h"
#include "ole2.h"
#endif /*COM_NO_WINDOWS_H*/

#ifndef __vba_ctypes_h__
#define __vba_ctypes_h__

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

/* Forward Declarations */ 

#ifndef __IGtx_FWD_DEFINED__
#define __IGtx_FWD_DEFINED__
typedef interface IGtx IGtx;
#endif 	/* __IGtx_FWD_DEFINED__ */


#ifndef __GtxObject_FWD_DEFINED__
#define __GtxObject_FWD_DEFINED__

#ifdef __cplusplus
typedef class GtxObject GtxObject;
#else
typedef struct GtxObject GtxObject;
#endif /* __cplusplus */

#endif 	/* __GtxObject_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"
#include "ocidl.h"

#ifdef __cplusplus
extern "C"{
#endif 


#ifndef __IGtx_INTERFACE_DEFINED__
#define __IGtx_INTERFACE_DEFINED__

/* interface IGtx */
/* [object][oleautomation][dual][uuid] */ 


EXTERN_C const IID IID_IGtx;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    MIDL_INTERFACE("6744394C-F5AA-4337-9C10-40CF4AFE4D93")
    IGtx : public IDispatch
    {
    public:
        virtual HRESULT STDMETHODCALLTYPE startup( 
            /* [retval][out] */ BSTR *presult) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE gtc( 
            /* [in] */ BSTR caller,
            /* [in] */ BSTR expression,
            /* [in] */ BSTR arguments,
            /* [retval][out] */ VARIANT *presult) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE error( 
            /* [in] */ BSTR caller,
            /* [in] */ BSTR cellref,
            /* [retval][out] */ BSTR *presult) = 0;
        
        virtual HRESULT STDMETHODCALLTYPE empty( 
            /* [in] */ BSTR caller) = 0;
        
    };
    
#else 	/* C style interface */

    typedef struct IGtxVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE *QueryInterface )( 
            IGtx * This,
            /* [in] */ REFIID riid,
            /* [annotation][iid_is][out] */ 
            __RPC__deref_out  void **ppvObject);
        
        ULONG ( STDMETHODCALLTYPE *AddRef )( 
            IGtx * This);
        
        ULONG ( STDMETHODCALLTYPE *Release )( 
            IGtx * This);
        
        HRESULT ( STDMETHODCALLTYPE *GetTypeInfoCount )( 
            IGtx * This,
            /* [out] */ UINT *pctinfo);
        
        HRESULT ( STDMETHODCALLTYPE *GetTypeInfo )( 
            IGtx * This,
            /* [in] */ UINT iTInfo,
            /* [in] */ LCID lcid,
            /* [out] */ ITypeInfo **ppTInfo);
        
        HRESULT ( STDMETHODCALLTYPE *GetIDsOfNames )( 
            IGtx * This,
            /* [in] */ REFIID riid,
            /* [size_is][in] */ LPOLESTR *rgszNames,
            /* [range][in] */ UINT cNames,
            /* [in] */ LCID lcid,
            /* [size_is][out] */ DISPID *rgDispId);
        
        /* [local] */ HRESULT ( STDMETHODCALLTYPE *Invoke )( 
            IGtx * This,
            /* [in] */ DISPID dispIdMember,
            /* [in] */ REFIID riid,
            /* [in] */ LCID lcid,
            /* [in] */ WORD wFlags,
            /* [out][in] */ DISPPARAMS *pDispParams,
            /* [out] */ VARIANT *pVarResult,
            /* [out] */ EXCEPINFO *pExcepInfo,
            /* [out] */ UINT *puArgErr);
        
        HRESULT ( STDMETHODCALLTYPE *startup )( 
            IGtx * This,
            /* [retval][out] */ BSTR *presult);
        
        HRESULT ( STDMETHODCALLTYPE *gtc )( 
            IGtx * This,
            /* [in] */ BSTR caller,
            /* [in] */ BSTR expression,
            /* [in] */ BSTR arguments,
            /* [retval][out] */ VARIANT *presult);
        
        HRESULT ( STDMETHODCALLTYPE *error )( 
            IGtx * This,
            /* [in] */ BSTR caller,
            /* [in] */ BSTR cellref,
            /* [retval][out] */ BSTR *presult);
        
        HRESULT ( STDMETHODCALLTYPE *empty )( 
            IGtx * This,
            /* [in] */ BSTR caller);
        
        END_INTERFACE
    } IGtxVtbl;

    interface IGtx
    {
        CONST_VTBL struct IGtxVtbl *lpVtbl;
    };

    

#ifdef COBJMACROS


#define IGtx_QueryInterface(This,riid,ppvObject)	\
    ( (This)->lpVtbl -> QueryInterface(This,riid,ppvObject) ) 

#define IGtx_AddRef(This)	\
    ( (This)->lpVtbl -> AddRef(This) ) 

#define IGtx_Release(This)	\
    ( (This)->lpVtbl -> Release(This) ) 


#define IGtx_GetTypeInfoCount(This,pctinfo)	\
    ( (This)->lpVtbl -> GetTypeInfoCount(This,pctinfo) ) 

#define IGtx_GetTypeInfo(This,iTInfo,lcid,ppTInfo)	\
    ( (This)->lpVtbl -> GetTypeInfo(This,iTInfo,lcid,ppTInfo) ) 

#define IGtx_GetIDsOfNames(This,riid,rgszNames,cNames,lcid,rgDispId)	\
    ( (This)->lpVtbl -> GetIDsOfNames(This,riid,rgszNames,cNames,lcid,rgDispId) ) 

#define IGtx_Invoke(This,dispIdMember,riid,lcid,wFlags,pDispParams,pVarResult,pExcepInfo,puArgErr)	\
    ( (This)->lpVtbl -> Invoke(This,dispIdMember,riid,lcid,wFlags,pDispParams,pVarResult,pExcepInfo,puArgErr) ) 


#define IGtx_startup(This,presult)	\
    ( (This)->lpVtbl -> startup(This,presult) ) 

#define IGtx_gtc(This,caller,expression,arguments,presult)	\
    ( (This)->lpVtbl -> gtc(This,caller,expression,arguments,presult) ) 

#define IGtx_error(This,caller,cellref,presult)	\
    ( (This)->lpVtbl -> error(This,caller,cellref,presult) ) 

#define IGtx_empty(This,caller)	\
    ( (This)->lpVtbl -> empty(This,caller) ) 

#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __IGtx_INTERFACE_DEFINED__ */



#ifndef __GtxTypeLib_LIBRARY_DEFINED__
#define __GtxTypeLib_LIBRARY_DEFINED__

/* library GtxTypeLib */
/* [uuid] */ 


EXTERN_C const IID LIBID_GtxTypeLib;

EXTERN_C const CLSID CLSID_GtxObject;

#ifdef __cplusplus

class DECLSPEC_UUID("72D37073-ED56-46E0-9E7C-BBAB0FFFC5C1")
GtxObject;
#endif
#endif /* __GtxTypeLib_LIBRARY_DEFINED__ */

/* Additional Prototypes for ALL interfaces */

unsigned long             __RPC_USER  BSTR_UserSize(     unsigned long *, unsigned long            , BSTR * ); 
unsigned char * __RPC_USER  BSTR_UserMarshal(  unsigned long *, unsigned char *, BSTR * ); 
unsigned char * __RPC_USER  BSTR_UserUnmarshal(unsigned long *, unsigned char *, BSTR * ); 
void                      __RPC_USER  BSTR_UserFree(     unsigned long *, BSTR * ); 

unsigned long             __RPC_USER  VARIANT_UserSize(     unsigned long *, unsigned long            , VARIANT * ); 
unsigned char * __RPC_USER  VARIANT_UserMarshal(  unsigned long *, unsigned char *, VARIANT * ); 
unsigned char * __RPC_USER  VARIANT_UserUnmarshal(unsigned long *, unsigned char *, VARIANT * ); 
void                      __RPC_USER  VARIANT_UserFree(     unsigned long *, VARIANT * ); 

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif


