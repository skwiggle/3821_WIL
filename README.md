# Terminal Genie
A custom debugging program built for Android version 25.0 and higher to debug Unity projects.
Comes with a remote terminal to run on windows/mac/linux.

![Image](../3821_WIL/app/ui/screenshots/readme.png)

---
#####App
The main application is run on android while the terminal is run from a computer. 
The app will be used in conjunction with the terminal to check for Unity updates but also 
comes with a list of commands to do operations manually. List of commands include:

| Commands                   | Description                                            |
|----------------------------|--------------------------------------------------------|
| __?__                      | *get list of commands*                                   |
| __get log__                | *request current log from unity*                         |
| __get log --today__        | *get all logs from today*                                |
| __get log --00-01-2000__   | *get all logs from specific day on *day-month-year**     |
| __clear logs__             | *delete all temporary log files*                         |
| __clear log --today__      | *delete all logs from today*                             |
| __clear log --00-01-2000__ | *delete log from specific day*                           |

---
#####Terminal
The terminal can be run from windows/mac/linux and only prints out any commands sent via the main
application. Commands that come with the terminal will be sent to the **terminal_log.txt** 
file.

The following command can be used with either batch or windows to pipe data
from the terminal:
```shell script
terminal_genie.exe > some_other_file
```

---
### Requirements
* Android Version - 7.1 and above
* API/NDK Version - API Level 25 and above
* Unity Version 2019.3.10 and above

