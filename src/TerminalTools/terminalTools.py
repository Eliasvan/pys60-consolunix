# -*- coding: utf-8 -*-

description = \
"""
This is an alternative for the terminalTools module builtin in the 'Terminal for PyS60'.
Some functionality is lacking, e.g. the 'keyGrabber' is not functional, 
things like history or autocomplete aren't either and 
also the special printing output (with colours and styled text) is not available.
However most of these options could be implemented, 
like for example with the module 'curses' for Linux terminals, 
but it will lose the platform-independance. (See the section at the bottom for more info.)
"""

print description


features = []
def checkFeature(feature, verbose = False):
  b = feature in features
  if not b and verbose:
    print "Warning: '%s' is not supported (yet) and will not work properly." % feature
  return b


class KeyGrabber:
	def __init__(self):
		self.setContineousPress(False)
		self.stop()
	def setContineousPress(self, b):
		self.contineousPress = b
		self.keys = []
	def start(self):
		self.active = True
	def stop(self):
		self.active = False
		self.keys = []
	def pause(self):
		self.active = False
	def resume(self):
		self.start()
	def get(self):
		return self.keys

class History:
  def __init__(self):
    self.active = True
  def reset(self):
    pass


keyGrabber = KeyGrabber()
version = "1.0"
versionStatus = "beta stable"
history = History()
history.active = False


def print_special(s, doNL = True, styles = None, **kwargs):
  if styles:
    for styleText in s:
      sys.stdout.write(styleText[0])
    if doNL:
      print
  else:
    print s

def raw_input_special(s = "", autoComplete = None, **kwargs):
  return raw_input(s)

def input_special(s = "", autoComplete = None, **kwargs):
  return input(s)




try: # Override platform dependant functions
	import os
	osname = os.name
	del os # Let the platform dependant functions be able to override 'os'

	exec "from terminalTools_%s import *" % osname
except ImportError:
	pass
