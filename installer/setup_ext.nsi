RequestExecutionLevel user 

!include LogicLib.nsh

!include EnvVarUpdate.nsh
!include WinVer.nsh

; Define your application name
!define APPNAME "GTXL"
!define VERSION "Extensions"

!define APPNAMEANDVERSION "${APPNAME} ${VERSION}"

; Main Install settings
Name "${APPNAMEANDVERSION}"
InstallDir "$PROFILE\${APPNAME}"

OutFile "gtxl_ext_setup.exe"

;ShowInstDetails show
;ShowUninstDetails show

; Modern interface settings
!include "MUI.nsh"

;--------------------------------
;Interface Settings

!define MUI_ICON "..\icon\gt.ico"
!define MUI_UNICON "..\icon\gt_uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\icon\GTCwin.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "..\icon\GTCwin.bmp"

!define MUI_ABORTWARNING

!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_UNFINISHPAGE_NOAUTOCLOSE
;--------------------------------
;Pages

!insertmacro MUI_PAGE_WELCOME
;!insertmacro MUI_PAGE_LICENSE "..\license\GTC_license.txt"

!insertmacro MUI_PAGE_COMPONENTS

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Set languages (first is default language)

!insertmacro MUI_LANGUAGE "English"
;!insertmacro MUI_RESERVEFILE_LANGDLL


;--------------------------------
; For installation size info
!define ARP "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}"
!include "FileFunc.nsh"

;--------------------------------
Section -Section1

	; Create folders, if not already created

	SetOutPath "$INSTDIR\Extensions\packages"
	SetOutPath "$INSTDIR\Extensions\startup"
	SetOutPath "$INSTDIR\Extensions\examples"
 
SectionEnd

Section "GTXL Example extension" Section2

    ; Don't clobber user-modified files
    SetOverwrite ifnewer

	SetOutPath "$INSTDIR\Extensions\packages"
	File /r "..\packages\test"

	SetOutPath "$INSTDIR\Extensions\startup"
	File "..\startup\test.py"

SectionEnd

; Invisible sections begin with `-`
Section -FinishSection

    ;-------------------------------------------------------------------------------------
	WriteUninstaller "$INSTDIR\Extensions\uninstall.exe"

    ;-------------------------------------------------------------------------------------
	; These lines put information in for the Add/Remove feature of Windows 
	WriteRegStr HKCU "Software\${APPNAMEANDVERSION}" "" "$INSTDIR"
    
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}"\ 
		"DisplayName" "${APPNAMEANDVERSION}"
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}"\ 
		"UninstallString" "$\"$INSTDIR\Extensions\uninstall.exe$\""
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
                 "QuietUninstallString" "$\"$INSTDIR\Extensions\uninstall.exe$\" /S"
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
                 "DisplayIcon" "$\"$INSTDIR\gt.ico$\""
;	WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
;                 "NoModify" 0
;	WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
;                 "NoRepair" 0
;	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
;                 "DisplayVersion" "0.1"
	WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}" \
                 "Publisher" "Measurement Standards Laboratory of New Zealand"

    ;-------------------------------------------------------------------------------------
    ${GetSize} "$INSTDIR\Extensions" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "${ARP}" "EstimatedSize" "$0"
   
    ;-------------------------------------------------------------------------------------
    ; CreateShorCut link.lnk target.file [parameters [icon.file [icon_index_number [start_options [keyboard_shortcut [description]]]]]]
	CreateDirectory "$SMPROGRAMS\${APPNAME}\Extensions"

	CreateShortCut "$SMPROGRAMS\${APPNAME}\Extensions\packages.lnk" "$INSTDIR\Extensions\packages\" \
										"" "" "" SW_SHOWNORMAL "" "packages"

	CreateShortCut "$SMPROGRAMS\${APPNAME}\Extensions\startup.lnk" "$INSTDIR\Extensions\startup" \
										"" "" "" SW_SHOWNORMAL "" "startup"

	CreateShortCut "$SMPROGRAMS\${APPNAME}\Extensions\examples.lnk" "$INSTDIR\Extensions\examples" \
										"" "" "" SW_SHOWNORMAL "" "examples"
                                        
	CreateShortCut "$SMPROGRAMS\${APPNAME}\Extensions\Uninstall.lnk" "$INSTDIR\Extensions\uninstall.exe" \ 
										"" "$INSTDIR\Extensions\uninstall.exe"
	
    ;-------------------------------------------------------------------------------------
	${EnvVarUpdate} $0 "GTXL_LIB" "P" "HKCU" "$INSTDIR\Extensions\packages" 
	${EnvVarUpdate} $0 "GTXL_STARTUP" "P" "HKCU" "$INSTDIR\Extensions\startup" 
   
SectionEnd

; --------------------------------------------------------------
; Function needs to follow sections because flags are controlled
; for the XP choices
Function .onInit  
  ${IfNot} ${AtLeastWinXP}
	MessageBox MB_OK|MB_ICONSTOP "This software requires Windows XP, or above."
    SetErrorLevel 2 ; Aborted by script
	Quit
  ${EndIf}
  
FunctionEnd

;--------------------------------
;Descriptions

;LangString DESC_Section1 ${LANG_ENGLISH} "Basic GTXL extensions"
LangString DESC_Section2 ${LANG_ENGLISH} "Example extension"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
;  !insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
  !insertmacro MUI_DESCRIPTION_TEXT ${Section2} $(DESC_Section2)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
;	!insertmacro MUI_DESCRIPTION_TEXT ${Section1} "Install basic GTXL extensions" ;$(DESC_Section1)    
;!insertmacro MUI_FUNCTION_DESCRIPTION_END

;==================================================================
;Uninstall section
Section un.Section2 unSection2

    ; Note that in uninstaller code, $INSTDIR contains the directory where the 
    ; uninstaller is located, which was "$INSTDIR\Extensions" during installation

    Delete "$INSTDIR\startup\test.py"

    RMDir /r "$INSTDIR\packages\test" 
    
SectionEnd

Section -un.Uninstall

    RMDir "$INSTDIR\packages"
    RMDir "$INSTDIR\startup"
    RMDir "$INSTDIR\examples"

    ; improvised AND
    ; Only executes if all extension folders have been removed
    IfFileExists "$INSTDIR\packages\*.*" ExtensionsNotEmpty 0
        IfFileExists "$INSTDIR\startup\*.*" ExtensionsNotEmpty 0
            IfFileExists "$INSTDIR\examples\*.*" ExtensionsNotEmpty 0
        
            ; Delete Extensions folder
            RMDir /r "$INSTDIR"		    

            ;Remove from registry...
            DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAMEANDVERSION}"
            DeleteRegKey HKCU "SOFTWARE\${APPNAMEANDVERSION}"

            ; Delete Extensions Shortcuts (other GTXL may remain)
            RMDir /r "$SMPROGRAMS\${APPNAME}\Extensions"		    
         
            ; The folder `$SMPROGRAMS\${APPNAME}` may be empty now
            RMDir "$SMPROGRAMS\${APPNAME}"
            
            ; Clean up the environment variables    
            ${un.EnvVarUpdate} $0 "GTXL_LIB" "R" "HKCU" "$INSTDIR\packages" 
            ${un.EnvVarUpdate} $0 "GTXL_STARTUP" "R" "HKCU" "$INSTDIR\startup" 

    ExtensionsNotEmpty:

SectionEnd


;Language strings
;LangString DESC_unSection1 ${LANG_ENGLISH} "First uninstall section."
LangString DESC_unSection2 ${LANG_ENGLISH} "Remove the example extension."

;Assign language strings to sections
!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
;!insertmacro MUI_DESCRIPTION_TEXT ${unSection1} $(unDESC_Section1)
!insertmacro MUI_DESCRIPTION_TEXT ${unSection2} $(DESC_unSection2)
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END


BrandingText "GTXL Extensions"

; eof