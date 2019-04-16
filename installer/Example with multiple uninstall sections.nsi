RequestExecutionLevel user 
;---------------------
;Include Modern UI

!include "MUI.nsh"

;--------------------------------
;General

;Name and file
Name "Modern UI Test 0.1"
OutFile "InstallOptions.exe"

;Default installation folder
InstallDir "$PROFILE\Modern UI Test"

;Get installation folder from registry if available
InstallDirRegKey HKCU "Software\Modern UI Test" ""

;--------------------------------
;Pages

;!insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_INSTFILES


;--------------------------------
;Interface Settings

!define MUI_ABORTWARNING

;--------------------------------
;Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Dummy Section" SecDummy
DetailPrint "this really does not install anything except the uninstaller"
SetOutPath "$INSTDIR"
;Create uninstaller
WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd


;--------------------------------
;Uninstaller Sections

Section un.Section1 Section1
DetailPrint "This actually does nothing for section 1"
SectionEnd

Section un.Section2 Section2
    IfFileExists "$INSTDIR\Uninstall.exe" 0 +2 
        DetailPrint "found $INSTDIR\Uninstall.exe"
        
    DetailPrint "Removes folder and uninstaller for section 2"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
 
    IfFileExists "$INSTDIR\Uninstall.exe" 0 +2 
        DetailPrint "found $INSTDIR\Uninstall.exe again"
 
SectionEnd

;Language strings
LangString DESC_Section1 ${LANG_ENGLISH} "First uninstall section."
LangString DESC_Section2 ${LANG_ENGLISH} "Second uninstall section."

;Assign language strings to sections
!insertmacro MUI_UNFUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Section1} $(DESC_Section1)
!insertmacro MUI_DESCRIPTION_TEXT ${Section2} $(DESC_Section2)
!insertmacro MUI_UNFUNCTION_DESCRIPTION_END
