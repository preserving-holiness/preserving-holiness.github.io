#Persistent

; This script keeps running in the background to listen for events.

/*
================================================================================
AutoHotkey script to automatically press Enter on the autopost.bat console window.
================================================================================

This script operates in two modes:

1. TIMED MODE (Default Behavior):
   - When you run this script normally (e.g., by double-clicking it), it will run
     silently in the background.
   - It will only take action between 8:00 AM and 8:15 AM.
   - During this window, it will look for a console window with "autopost.bat"
     in its title.
   - When it finds the window, it will automatically activate it, send an Enter key
     press (to get past the "pause" command), and then it will not run again
     until the next day.

2. INVOKE MODE (Manual Trigger):
   - You can trigger the script manually from a command line, another script,
     or the Task Scheduler.
   - To use this mode, execute the script with the "invoke" parameter like this:
     "C:\Program Files\AutoHotkey\AutoHotkeyU64.exe" "F:\Websites\pelican_tryout\pelican_autohotkey.ahk" invoke
   - When run this way, it will immediately look for the "autopost.bat" window
     for up to 10 seconds. If found, it will press Enter and then exit immediately.
     This is useful for testing or running your batch file outside the scheduled time.
================================================================================
*/


; --- Configuration ---
global hasRunToday := false
; The script will look for a window title that CONTAINS this text.
; When you run "autopost.bat", its path usually appears in the console title.
global targetWindowTitle := "autopost.bat"


; --- Main Logic: Check for 'invoke' command-line parameter ---
if (A_Args.Length() > 0 and A_Args[1] = "invoke") {
    InvokeMode()
    ExitApp ; Terminate the script after manual invocation is complete
} else {
    TimedMode()
}
return ; End of the auto-execute section of the script


; --- Mode Functions ---

TimedMode() {
    ; In timed mode, we set up timers to perform checks periodically.
    SetTimer, CheckForWindow, 5000   ; Check for the window every 5 seconds.
    SetTimer, ResetDailyFlag, 60000  ; Check every minute to reset the daily flag.
    return
}

InvokeMode() {
    SetTitleMatchMode, 2 ; Set match mode to find a substring in the title.
    ; Wait up to 10 seconds for the target window to appear.
    WinWait, %targetWindowTitle%, , 10
    if !ErrorLevel { ; ErrorLevel is 0 if the window was found.
        WinActivate   ; Bring the window to the front.
        Send, {Enter} ; Send the Enter keystroke.
    }
    return
}


; --- Timed Subroutines ---

CheckForWindow:
    global hasRunToday
    global targetWindowTitle

    ; If the script has already successfully run today, do nothing.
    if (hasRunToday) {
        return
    }

    ; Only proceed if the current time is between 8:00 AM and 8:15 AM.
    if (A_Hour = 8 and A_Min <= 15)
    {
        SetTitleMatchMode, 2 ; Set match mode to find a substring in the title.
        IfWinExist, %targetWindowTitle%
        {
            WinActivate ; Bring the console window to the front.
            Send, {Enter} ; Send the Enter keystroke.
            hasRunToday := true ; Set the flag to true so this only happens once per day.
        }
    }
    return

ResetDailyFlag:
    global hasRunToday
    ; This subroutine resets the flag for the next day.
    ; If we are outside the 8:00-8:15 window, the flag should be false.
    if (A_Hour != 8 or A_Min > 15) {
        hasRunToday := false
    }
    return 