# -*- coding: utf-8 -*-

description = \
"""
This is an alternative for the terminalTools module builtin in the 'Terminal for PyS60'.
Some functionality is lacking, e.g. the 'keyGrabber' is not yet functional, 
things like history or autocomplete aren't either and 
also the bold feature of styled text printing are not available (yet).
Not all colours of styled text printing are supported: only the ones available in xterm.
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


class ColoramaWrapper:
  
  def __init__(self):
    try:
      import colorama
      self.colorama = colorama
      self.colorama.init()
      features.append("styledPrinting")
      self.fake = False
    except ImportError:
      print "Warning: The python depencency 'colorama' is not installed. Styled printing will not work."
      self.colorama = None
      self.fake = True
    
    self.setup()
  
  def setup(self, fake = False):
    if self.fake:
      self.resetChars = ""
      return
    else:
      self.resetChars = self.colorama.Fore.RESET + self.colorama.Back.RESET + self.colorama.Style.RESET_ALL
    
    self.foreColors = []
    self.backColors = []
    for color in ('BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE'):
      exec 'self.foreColors.append(self.colorama.Fore.%s)' % color
      exec 'self.backColors.append(self.colorama.Back.%s)' % color
    self.RgbColors = []

    # Normal
    self.RgbColors.append((0, 0, 0))
    self.RgbColors.append((205, 0, 0))
    self.RgbColors.append((0, 205, 0))
    self.RgbColors.append((205, 205, 0))
    self.RgbColors.append((0, 0, 238))
    self.RgbColors.append((205, 0, 205))
    self.RgbColors.append((0, 205, 205))
    self.RgbColors.append((229, 229, 229))

    # Bright
    self.RgbColors.append((127, 127, 127))
    self.RgbColors.append((255, 0, 0))
    self.RgbColors.append((0, 255, 0))
    self.RgbColors.append((255, 255, 0))
    self.RgbColors.append((92, 92, 255))
    self.RgbColors.append((255, 0, 255))
    self.RgbColors.append((0, 255, 255))
    self.RgbColors.append((255, 255, 255))
  
  def getPreceedingChars(self, h, mode):
    if self.fake:
      return ""
    
    def colorHypot(c1, c2):
      return sum([(c1[i] - c2[i])**2 for i in range(3)])
    
    color = [(h / 256**i) % 256 for i in reversed(range(3))]
    l = [colorHypot(color, c) for c in self.RgbColors]
    idx = l.index(min(l))
    if idx / 8 and mode == "fore":
      out = self.colorama.Style.BRIGHT
    else:
      out = self.colorama.Style.NORMAL
    if mode == "fore":
      out += self.foreColors[idx % 8]
    else:
      out += self.backColors[idx % 8]
    
    return out


keyGrabber = KeyGrabber()
version = "1.0"
versionStatus = "beta stable"
history = History()
history.active = False
coloramaWrapper = ColoramaWrapper()
del ColoramaWrapper


def print_special(s, doNL = True, styles = None, reset = True, **kwargs):
  def write(s, **kwargs):
    import sys
    out = ""
    if 'highlight_color' in kwargs:
      out += coloramaWrapper.getPreceedingChars(kwargs['highlight_color'], "back")
    if 'color' in kwargs:
      out += coloramaWrapper.getPreceedingChars(kwargs['color'], "fore")
    out += s
    if reset:
      out += coloramaWrapper.resetChars
    sys.stdout.write(out)
  
  if styles:
    for styleText in s:
      write(styleText[0], color = styles[styleText[1]][0], highlight_color = styles[styleText[1]][1])
    if doNL:
      print
  else:
    write(s + "\n"*doNL, **kwargs)

def raw_input_special(s = "", autoComplete = None, **kwargs):
  print_special(s, doNL = False, reset = False, **kwargs)
  out = raw_input()
  import sys
  sys.stdout.write(coloramaWrapper.resetChars)
  return out

def input_special(s = "", autoComplete = None, **kwargs):
  print_special(s, doNL = False, reset = False, **kwargs)
  out = input()
  import sys
  sys.stdout.write(coloramaWrapper.resetChars)
  return out




try: # Override platform dependant functions
	import os
	osname = os.name
	del os # Let the platform dependant functions be able to override 'os'

	exec "from terminalTools_%s import *" % osname

except ImportError:
	pass
