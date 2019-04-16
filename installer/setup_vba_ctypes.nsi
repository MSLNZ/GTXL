RequestExecutionLevel admin 

!include LogicLib.nsh

;!include EnvVarUpdate.nsh
!include WinVer.nsh
!include Library.nsh

; Define your application name
!define APPNAME "GTXL"
!define VERSION "0.1"

!define APPNAMEANDVERSION "${APPNAME} ${VERSION}"

; Main Install settings
Name "${APPNAME}"
InstallDir "$PROGRAMFILES32\GTXL"
InstallDirRegKey HKLM "Software\${APPNAME}" ""

OutFile "gtxl_setup.exe"

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

!insertmacro MUI_PAGE_LICENSE "..\license\GTXL_license.txt"
;!insertmacro MUI_PAGE_COMPONENTS

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!define MUI_FINISHPAGE_TEXT "${APPNAMEANDVERSION} has been un-installed. \
\r\n\r\nSome files cannot be removed automatically. \r\n\r\nThose files can be deleted manually, if required."
!insertmacro MUI_UNPAGE_FINISH


;--------------------------------
; Set languages (first is default language)

!insertmacro MUI_LANGUAGE "English"
;!insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
; For installation size info
!define ARP "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
!include "FileFunc.nsh"

;--------------------------------
Section "GTXL" Section1

    ; Sets the context of $SMPROGRAMS and other shell folders.
    SetShellVarContext all
    
	; Set Section properties
	SetOverwrite on

	; Set Section Files and Shortcuts
	SetOutPath "$INSTDIR\"
	File "..\vba_ctypes\dist\*.*"

	SetOutPath "$INSTDIR\license\"
	File "..\license\GTXL_license.txt"
	File "..\license\python LICENSE.txt"

    SetOutPath "$INSTDIR\icon"
	File "..\icon\gt.ico"

    SetOutPath "$INSTDIR\addin"
	File "..\vba_ctypes\*.xlam"
	File "..\vba_ctypes\GTXL.chm"

	SetOutPath "$INSTDIR\Microsoft.VC90.CRT\"
	File "..\vba_ctypes\dist\Microsoft.VC90.CRT\*.*"

	SetOutPath "$INSTDIR\doc\html"
	File /r "..\doc\html\*."
 
    SetOutPath "$INSTDIR\examples"
    File /r "..\vba_ctypes\examples\*.*"
    
    ; Register the COM server
    ; !insertmacro InstallLib libtype shared install localfile destfile tempbasedir
    !insertmacro InstallLib REGDLLTLB NOTSHARED NOREBOOT_PROTECTED "..\vba_ctypes\dist\server.dll" "$INSTDIR\server.dll" "$INSTDIR"
  
        ;-------------------------------------------------------------------------------------

SectionEnd

Section -FinishSection
    ;-------------------------------------------------------------------------------------	
    WriteUninstaller "$INSTDIR\uninstall.exe"
    ;-------------------------------------------------------------------------------------
	WriteRegStr HKLM "Software\${APPNAME}" "" "$INSTDIR"
    
    ; These lines put information in for the Add/Remove feature of Windows 
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \ 
		"DisplayName" "${APPNAME}" 
        
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"\ 
		"UninstallString" "$\"$INSTDIR\uninstall.exe$\""
        
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
        "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
                 
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
        "DisplayIcon" "$\"$INSTDIR\icon\gt.ico$\""
                 
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
                 "NoModify" 1
                 
	WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
                 "NoRepair" 1
                 
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
                 "DisplayVersion" "${VERSION}"
                 
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
                 "Publisher" "Measurement Standards Laboratory of New Zealand"


        ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
     IntFmt $0 "0x%08X" $0
     WriteRegDWORD HKLM "${ARP}" "EstimatedSize" "$0"
 
    ;-------------------------------------------------------------------------------------
	CreateDirectory "$SMPROGRAMS\GTXL"

	CreateShortCut "$SMPROGRAMS\GTXL\Uninstall.lnk" "$INSTDIR\uninstall.exe"\ 
										"" "$INSTDIR\uninstall.exe"
    
	CreateShortCut "$SMPROGRAMS\GTXL\GTXL Help (CHM).lnk" "$INSTDIR\addin\GTXL.chm"\
										"" "" "" SW_SHOWMAXIMIZED "" "Windows Help for GTXL"

	CreateShortCut "$SMPROGRAMS\GTXL\GTXL Help (HTML).lnk" "$INSTDIR\doc\html\index.html"\
										"" "" "" SW_SHOWMAXIMIZED "" "HTML Help for GTXL"

	CreateShortCut "$SMPROGRAMS\GTXL\GTXL examples.lnk" "$INSTDIR\examples"\
										"" "" "" SW_SHOWNORMAL "" "GTXL examples"
                                        
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
  
  ; Use the 'quiet' form of uninstall to remove a previous version 
  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\GTXL" \
  "QuietUninstallString"
  StrCmp $R0 "" done
 
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "GTXL is already installed. $\n$\nClick `OK` to remove the \
  previous version or `Cancel` to cancel this upgrade." \
  IDOK uninst
  Abort

uninst:
  ClearErrors
  Exec $R0
done:
  
FunctionEnd


;==================================================================
;Uninstall section
Section Uninstall

    ; Sets the context of $SMPROGRAMS and other shell folders.
    SetShellVarContext all

    ; Unregister COM server
    ; !insertmacro UnInstallLib libtype shared uninstall file
    !insertmacro UnInstallLib REGDLLTLB NOTSHARED REBOOT_NOTPROTECTED "$INSTDIR\server.dll"
    
	;Remove from registry...
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
	DeleteRegKey HKLM "SOFTWARE\${APPNAME}"

    ; RMDir: Without /r, the directory will only be removed if it is completely empty. 
    ; If /r is specified, the directory will be removed recursively, 
    ; so all directories and files in the specified directory will be removed.
    ; With /REBOOTOK the removal may be flagged to take place the next time
    ; Windows boots up, if the removal is blocked initially.
    
	; Delete Shortcuts
	RMDir /r "$SMPROGRAMS\GTXL"

	RMDir /r "$INSTDIR\examples"

    RMDir /r "$INSTDIR\addin"

    ; Leave the Python license there (because the DLLs are not always removed)
    Delete "$INSTDIR\license\GTXL_license.txt"
	; RMDir /r "$INSTDIR\license\"

    RMDir /r "$INSTDIR\icon"
	
	RMDir /r "$INSTDIR\doc"
    
	RMDir /r "$INSTDIR\Microsoft.VC90.CRT"
    
;	RMDir /r "$INSTDIR\scripts"	 

	; Delete self some files at the top level but 
    ; don't do a RMDir /r /REBOOTOK "$INSTDIR" !!!
	Delete "$INSTDIR\uninstall.exe"
	Delete "$INSTDIR\server.dll"
  
    ; Tell the user if they need to reboot!
;    IfRebootFlag 0 noreboot
;      MessageBox MB_YESNO "A reboot is required to finish the uninstall process. Do you wish to reboot now?" IDNO noreboot
;        Reboot
;    noreboot: 
    
SectionEnd

; --------------------------------------------------------------
; Catch a failure to reboot
;Function un.onRebootFailed
;    MessageBox MB_OK|MB_ICONSTOP "Reboot failed. Please reboot manually." /SD IDOK
;FunctionEnd

BrandingText "GUM Tree Excel Uncertainty Addin"

; eof