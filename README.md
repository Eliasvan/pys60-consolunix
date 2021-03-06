README
------

_Warning:
Automatically exported from "code.google.com/p/pys60-consolunix",
so some things might be wrongly converted._

A simple but powerful Unix-like console for S60 devices based on Python.
It features a built-in python command and also some common commands of a standard Unix terminal.
You will directly feel the flexibility of the built-in python command facing the standard pys60 suite.
The goal is that the user/developer would experience it as if he was using the combination of a console with python on his home computer.

This project differs from 'pyunix' by being more complex and it differs from 'minix' and 'ayix' by not really emulating a unix device,
but by merging S60 functionality (e.g. executing *.exe) with that of unix.

The project consists out of two parts: the S60 part ("Terminal.py") and the non-S60 part (for on a computer "terminalTools.py").
The console has some advanced functions like auto-completion, history, styled printing, ...
Therefore, the goal of the provided 'terminalTools' module,
is to implement similar functions on the home computer.

You can start the console via PyS60 -> "Run script" -> "Terminal.py".
No installation via *.sis files is needed.
A Unixbased Terminal/Console for S60 devices able to run PyS60 (Python). 
