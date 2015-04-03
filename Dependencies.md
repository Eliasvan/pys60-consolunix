# Introduction #

The _TerminalTools_ modules can be used without dependencies, but to get the extra features included in the Terminal console for S60 (_Terminal.py_), you'll have to install some additional stuff.


# Details #

The previous dependencies (_colorama_ and _pyHook_) will become deprecated, instead the '**curses**' (for _posix_) and '**Console**' (for _Windows_) modules will be used.

In other words: everything will work out of the box on _posix_ systems, but on a _Windows_ system, you'll need to install the 'Console' module which can be found here: http://effbot.org/media/downloads/console-1.1a1-20011229.zip.

Currently that part is still under development. For the moment, I've got no time to proceed with this project.