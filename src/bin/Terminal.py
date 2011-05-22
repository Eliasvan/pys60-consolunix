# -*- coding: utf-8 -*-


import appuifw, e32
import keycapture, key_codes

import os, sys
from time import sleep, time


MAX_HISTORY = 30
MAX_TERMINAL_LENGTH = 3200
MAX_FILELENGTH = 32000
MAX_FILELISTINGLENGTH = 30
MAX_COPY_STEP = 1024000
MAX_INITDELAY_CONTINEOUS_PRESS = 0.500
MAX_DELAY_CONTINEOUS_PRESS = 0.200
MIN_TAP_TO_AUTOCOMPLETE = 2
DO_CURSOR_REFRESH_FOR_SIMPLE_PRINT = False
DO_INPUT_REFRESH_FOR_SIMPLE_PRINT = True
NAVIGATION_LINESPEED = 4
DEFAULT_STYLE = {'color' : 0x000000, 'highlight_color' : 0xFFFFFF, 'bold' : False, 'style' : 0}

exitAllPython = False






class KeyGrabber:
	def __init__(self):
		self.keyWrapper = {\
			key_codes.EKeySelect : "ENTER", 13 : "ENTER", 32 : "SPACE", \
			key_codes.EKeyUpArrow : "UP", key_codes.EKeyDownArrow : "DOWN", \
			key_codes.EKeyLeftArrow : "LEFT", key_codes.EKeyRightArrow : "RIGHT", \
			key_codes.EKey0 : "0", key_codes.EKey1 : "1", key_codes.EKey2 : "2", key_codes.EKey3 : "3", \
			key_codes.EKey4 : "4", key_codes.EKey5 : "5", key_codes.EKey6 : "6", \
			key_codes.EKey7 : "7", key_codes.EKey8 : "8", key_codes.EKey9 : "9", \
			key_codes.EKeyEdit : "EDIT", key_codes.EKeyYes : "YES", key_codes.EKeyMenu : "MENU" \
		}
		
		self.setContineousPress(False)
		self.stop()
	def setContineousPress(self, b):
		self.contineousPress = b
		self.clear()
	def clear(self):
		self.timeDowns = {}
		self.keys = []
	def append(self, key):
		if self.contineousPress:
			t = time()
			if key in self.timeDowns:
				del self.keys[self.keys.index(key)]
				self.timeDowns[key][1] = t
			else:
				self.timeDowns[key] = [t, t]
			self.keys.append(key)
		else:
			self.keys += (key, True), (key, False)
	def request(self):
		if self.contineousPress:
			l = []
			t = time()
			for i, key in enumerate(list(self.keys)):
				b = t - self.timeDowns[key][1] <= MAX_DELAY_CONTINEOUS_PRESS + MAX_INITDELAY_CONTINEOUS_PRESS * (self.timeDowns[key][0] == self.timeDowns[key][1])
				l.append((key, b))
				if not b:
					del self.keys[i]
					del self.timeDowns[key]
		else:
			l = list(self.keys)
			self.clear()
		return l
	def add(self, key):
		if key in self.keyWrapper:
			self.append(self.keyWrapper[key])
		elif 32 <= key <= 126:
			self.append(chr(key).upper())
		else:
			self.append("UNKNOWN")
	def start(self):
		if inputHandler.waitForInput:
			print "\nTerminal: Grabbing keys whilest doing an input-request is forbidden."
			print "Terminal: Probably you attempted to grab keys in an autocomplete callback."
		else:
			self.active = True
	def stop(self):
		self.active = False
		self.clear()
	def pause(self):
		self.active = False
	def resume(self):
		self.start()
	def get(self):
		e32.ao_yield()
		checkForExit()
		return self.request()


class InputHandler:
  def __init__(self):
    self.inputBuffer = ""
    self.waitForInput = False
  def set(self, inp):
    self.inputBuffer = inp
    self.waitForInput = False
    prompt.toEnd()
  def update(self):
    if self.waitForInput:
      terminalTools.print_special(self.updateData[0], doNL = False, **self.updateData[1])
      prompt.setPosToEnd(True)
  def get(self, s, autoComplete, **kwargs):
    if self.waitForInput:
      print "\nTerminal: Getting input in an existing input-request is forbidden."
      print "Terminal: Probably you attempted to do an input-request in an autocomplete callback."
      return ""
    elif terminalTools.keyGrabber.active:
      print "\nTerminal: Getting input whilest grabbing keys is forbidden."
      print "Terminal: Call 'terminalTools.keyGrabber.pause()' before doing any input-request."
      print "Terminal: Afterwards, call 'terminalTools.keyGrabber.resume()' to continue grabbing keys."
      return ""
    e32.ao_yield()
    self.updateData = s, kwargs
    prompt.enterKey = self.set
    prompt.setAutoComplete(autoComplete)
    terminalTools.print_special(s, doNL = False, **kwargs)
    prompt.setPosToEnd(True)
    self.waitForInput = True
    while True:
      if wantExit or not self.waitForInput:
        prompt.enterKey = None
        prompt.setAutoComplete(False)
        print
        self.waitForInput = False
        checkForExit()
        return self.inputBuffer
      else:
        e32.ao_yield()


class Prompt:
  def __init__(self):
    self.autoCompleteCount = 0
    self.navigation = False
    
    self.history = None
    self.enterKey = None
    self.setAutoComplete(False)
    
    self.update()
    
    self.initKeycapturer()
  def getInput(self):
    inp = text.get(self.pos, text.len() - self.pos)
    try:
      return str(inp)
    except UnicodeEncodeError:
      if type(inp) == unicode:
        exec "inp = %s" % repr(inp)[1:]
        return inp
    return ""
  def toPos(self):
    text.set_pos(self.pos)
  def toEnd(self):
    text.set_pos(text.len())
  def setPos(self, pos = None):
    if pos != None:
      self.pos = pos
    self.clear()
  def setPosToEnd(self, syncHistory = False):
    self.setPos(text.len())
    if syncHistory and self.history:
      self.history.setLast()
  def clear(self):
    if text.len() > self.pos:
      text.delete(self.pos, text.len() - self.pos)
    text.set_pos(self.pos)
  def add(self, s):
    if not s:
      return
    if text.len() + len(s) > MAX_TERMINAL_LENGTH:
      if len(s) > MAX_TERMINAL_LENGTH:
        s = s[len(s) - MAX_TERMINAL_LENGTH:]
      toRemove = text.len() + len(s) - MAX_TERMINAL_LENGTH
      if toRemove:
        text.delete(0, toRemove)
        self.pos -= toRemove
    try:
      text.add(unicode(s))
    except UnicodeDecodeError:
      exec "out = u%s" % repr(s)
#      out = u""
#      for char in s:
#        try:
#          out += unicode(char)
#        except UnicodeDecodeError:
#          out += u"?"
      text.add(out)
  def update(self, syncHistory = True):
    p = os.path.abspath(".")
    if not p in e32.drive_list():
      p = os.path.basename(p)
    txt = "[%s %s]$ " % ("user@pys60", p)
    self.toEnd()
    self.add(txt)
    
    self.setPosToEnd(syncHistory)    
  def setAutoComplete(self, autoComplete):
    if autoComplete == False:
      self.autoComplete = self.builtInAutoComplete
    else:
      self.autoComplete = autoComplete
  def builtInAutoComplete(self, cms):
    commands = extractCommands(cms)
    
    lastArg = commands[-1][-1]
    if lastArg[1] == "/":
      if len(commands[-1]) == 1:
        return cms
      del commands[-1][-1]
      lastArg = commands[-1][-1]
    
    args, unique = completeArg(lastArg[0], len(commands) == 1 and len(commands[-1]) == 1)
    if len(args) == 0:
      return cms
    elif len(args) == 1:
      return cms[:lastArg[2]] + formatArg(args[0], lastArg[1], unique)
    
    if len(args) <= MAX_FILELISTINGLENGTH:
      print
      for arg in args:
        print arg
    else:
      print "\nToo many files to show here; use 'ls -a'."
    self.update(False)
    
    return cms
  def doKey(self, key):
    if not (not tasksRunning or self.enterKey):
      return 0
    
    forwarding = 0
    pos = text.get_pos()
    autoCompleteCount = self.autoCompleteCount
    
    if key in (key_codes.EKeySelect, 13):
      if self.history:
        self.history.add(self.getInput())
      if self.enterKey:
        self.enterKey(self.getInput())
      else:
        e32.ao_sleep(0, execute)
    elif key in (key_codes.EKeyUpArrow, key_codes.EKeyDownArrow, key_codes.EKeyLeftArrow, key_codes.EKeyRightArrow):
      if self.navigation:
        if key in (key_codes.EKeyUpArrow, key_codes.EKeyDownArrow):
          delta = (key == key_codes.EKeyDownArrow)
          end = delta * (text.len() - 1)
          lines = 0
          for i in range(pos - 1 * (1 - delta), end - 1 + 2*delta, 2*delta - 1):
            if text.get(i, 1) in ("\n", u"\u2029"):
              lines += 1
            if lines == NAVIGATION_LINESPEED or i == end:
              text.set_pos(i)
              break
        else:
          forwarding = 1
      else:
        if key in (key_codes.EKeyUpArrow, key_codes.EKeyDownArrow):
          if self.history:
            self.history.browse(1 - 2 * (key == key_codes.EKeyUpArrow))
        elif pos > self.pos and key == key_codes.EKeyLeftArrow:
          forwarding = 1
        elif key == key_codes.EKeyRightArrow:
          if pos == text.len():
            self.autoCompleteCount += 1
            if self.autoCompleteCount >= MIN_TAP_TO_AUTOCOMPLETE and self.autoComplete:
              sys.stdout.hasWritten = False
              toReplaceWith = self.autoComplete(self.getInput())
              if sys.stdout.hasWritten:
                inputHandler.update()
              self.setPos()
              self.add(toReplaceWith)
          else:
            forwarding = 1
    else:
      if pos < self.pos:
        prompt.toEnd()
      if not (pos <= self.pos and key == key_codes.EKeyBackspace):
        forwarding = 1
    
    if self.autoCompleteCount == autoCompleteCount and key in (key_codes.EKeyBackspace, key_codes.EKeyLeftArrow, key_codes.EKeySelect, 13):
      self.autoCompleteCount = 0
    elif self.autoCompleteCount > MIN_TAP_TO_AUTOCOMPLETE:
      self.autoCompleteCount = MIN_TAP_TO_AUTOCOMPLETE
    return forwarding
  def initKeycapturer(self):
    self.keycapturer = keycapture.KeyCapturer(self.keyCallback)
    # Append point and comma
    keycapture.all_keys.append(44)
    keycapture.all_keys.append(46)
    self.keycapturer.keys = keycapture.all_keys
    self.keycapturer.forwarding = 0
    self.keycapturer.start()
  def keyCallback(self, key):
    global w
    
    while w:
      pass
    w = True

    self.keycapturer.forwarding = 0
    if terminalTools.keyGrabber.active:
      terminalTools.keyGrabber.add(key)
    else:
      self.keycapturer.forwarding = self.doKey(key)
    w = False


class History:
  def __init__(self):
    self.active = True
    self.reset()
  def reset(self):
    self.history = [""]
    self.historyIdx = 0
    self.currentHistory = self.history[self.historyIdx]
  def add(self, command):
    if not self.active:
      return
    if self.history[-1] != command:
      self.history.append(command)
      if len(self.history) > MAX_HISTORY:
        del self.history[0]
    self.historyIdx = len(self.history)-1
  def browse(self, i):
    if not self.active:
      return
    modHistory = prompt.getInput()
    if self.historyIdx < len(self.history):
      if modHistory != self.history[self.historyIdx]:
        self.currentHistory = modHistory
    else:
      self.currentHistory = modHistory
    
    self.historyIdx += i
    if self.historyIdx >= len(self.history):
      h = self.currentHistory
      self.historyIdx = len(self.history)
    elif self.historyIdx < 0:
      self.historyIdx = 0
      h = self.history[0]
    else:
      h = self.history[self.historyIdx]
    
    prompt.setPos()
    prompt.add(h)
  def setLast(self):
    if not self.active:
      return
    self.historyIdx = len(self.history)
    self.currentHistory = ""


class PseudoStdOut(object):
  def write(self, s, **kwargs):
    if kwargs:
      for item in DEFAULT_STYLE:
        if not item in kwargs:
          kwargs[item] = DEFAULT_STYLE[item]
      prompt.toEnd()
      text.color = kwargs['color']
      text.highlight_color = kwargs['highlight_color']
      text.style = ((kwargs['highlight_color'] != 0xFFFFFF) * appuifw.HIGHLIGHT_STANDARD | kwargs['bold'] * appuifw.STYLE_BOLD)
      prompt.add(s)
      text.color = DEFAULT_STYLE['color']
      text.highlight_color = DEFAULT_STYLE['highlight_color']
      text.style = DEFAULT_STYLE['style']
    else:
      if DO_CURSOR_REFRESH_FOR_SIMPLE_PRINT:
        prompt.toEnd()
      prompt.add(s)
    if inputHandler.waitForInput:
      sys.stdout.hasWritten = True
    elif kwargs or (not kwargs and DO_INPUT_REFRESH_FOR_SIMPLE_PRINT):
      e32.ao_yield()


class TerminalTools:
  def __init__(self):
    self.features = ["keyGrabber", "keyGrabber.contineousPress", "history", "autoComplete", "styledPrinting"]
    self.keyGrabber = KeyGrabber()
    self.version = "1.0"
    self.versionStatus = "beta stable"
    self.history = History()
  def checkFeature(self, feature, verbose = False):
    b = feature in self.features
    if not b and verbose:
      print "Warning: '%s' is not supported (yet) and will not work properly." % feature
    return b
  def print_special(self, s, doNL = True, styles = None, **kwargs):
    if styles:
      for styleText in s:
        sys.stdout.write(styleText[0], color = styles[styleText[1]][0], highlight_color = styles[styleText[1]][1], bold = styles[styleText[1]][2])
      if doNL:
        print
    else:
      sys.stdout.write(s+"\n"*doNL, **kwargs)
  def raw_input(self, s = ""):
    return self.raw_input_special(s)
  def raw_input_special(self, s = "", autoComplete = None, **kwargs):
    return inputHandler.get(s, autoComplete, **kwargs)
  def input(self, s = ""):
    return self.input_special(s)
  def input_special(self, s = "", autoComplete = None, **kwargs):
    exec 'toReturn = %s' % self.raw_input_special(s, autoComplete, **kwargs)
    return toReturn


def checkForExit():
  if wantExit:
    raise KeyboardInterrupt


def copyFile(src, dest):
	try:
		fi = open(src, 'rb')
	except:
		print "No read access to %s." % src
		return -1
	try:
		fo = open(dest, 'wb')
	except:
		print "No write access to %s." % dest
		return -1
	
	try:
		step = "EMPTY"
		while step:
			step = fi.read(MAX_COPY_STEP)
			fo.write(step)
		fo.flush()
		fo.close()
	except:
		try:
			os.remove(dest)
		except:
			pass
		print "An error occured while copying. Maybe not enough space left on device?"
		return -1
	
	return 0


def genNamespace():
  return {\
    "sys.argv" : list(sys.argv), "sys.path" : list(sys.path), \
    "sys.stdout" : sys.stdout, "os.system" : os.system, \
    "raw_input" : raw_input, "input" : input, \
    "terminalTools" : terminalTools \
  }


def extractArgInfo(command, i = 0):
  return [arg[i] for arg in command]

def hasOption(command, option):
  hasIt = False
  try:
    types = extractArgInfo(command, 1)
    args = extractArgInfo(command)
    idx = 0
    while idx != -1:
      idx = args.index(option, idx)
      if not types[idx]:
        del command[idx]
        if not command:
          command.append(("", "", 0))
        hasIt = True
        break
      idx += 1
  except ValueError:
    pass
  return hasIt

def pseudo_osSystem(commands):
	commands = extractCommands(commands)
	toReturn = 0
	for cmd in commands:
		if pseudo_osSystemCommand(cmd[0][0], cmd[1:]):
			toReturn = 1
	return toReturn


executables = ["exit", "help", "clear", "sleep", "echo", "cat", "cp", "mv", "rm", "rmdir", "mkdir", "cd", "ls", "pwd", "python"]
executables.sort()
def getExecHelp():
  styledText = [("Common functions are ", 0),]
  for i, exe in enumerate(executables):
    s = 2
    if exe == "python":
      s = 3
    styledText += [("'", 0), (exe, s), ("'", 0)]
    if i < len(executables)-2:
      styledText.append((", ", 0))
    elif i == len(executables)-2:
      styledText.append((" and ", 0))
  styledText.append((".\n", 0),)
  return styledText


def addNewPythonScript():
  pythonScripts.append(prompt.history)

def endLastPythonScript():
  if len(pythonScripts) == 1:
    prompt.history = history
  else:
    prompt.history = pythonScripts[-2]
  del pythonScripts[-1]


def pseudo_osSystemCommand(cmd, args):
  global wantExit
  if pythonScripts:
    checkForExit()
  if cmd == "exit":
    if not pythonScripts:
      print "Bye!"
      exit(True)
  elif cmd == "help":
    styles = ((0x000000, 0xFFFFFF, True), (0xFFFFFF, 0x000000, True), (0xAA0000, 0xFFFFFF, True), (0x4444FF, 0xFFFFFF, True))
    terminalTools.print_special((("Welcome to the ", 0), ("Terminal", 1), (". [to view this text, use '", 0), ("help", 2), ("']", 0)), styles = styles)
    terminalTools.print_special("________________________", bold = True)
    terminalTools.print_special("This tend's to simulate an extremely basic Unix terminal and it is based on Python.", bold = True)
    terminalTools.print_special("Use UP/DOWN to look in history and use RIGHT on the end of the line for auto-complete.")
    terminalTools.print_special(getExecHelp(), styles = styles)
    terminalTools.print_special("Available drives on device: ", bold = True)
    for txt in e32.drive_list():
      terminalTools.print_special(((txt, 3),), styles = styles)
    print "\n"
  elif cmd == "testInput":
    print "You typed %s." % terminalTools.raw_input_special("lalaaalaa: ", color=0xFFFFFF, highlight_color=0x000000)
  elif cmd == "testKeys":
    terminalTools.keyGrabber.start()
    l = []
    while not "DOWN" in l:
      l = terminalTools.keyGrabber.get()
      for i in l:
        print i
    terminalTools.keyGrabber.stop()
  elif cmd == "clear":
    text.clear()
  elif cmd == "sleep":
    try:
      t = float(args[0][0])
    except ValueError:
      t = 1
    sleep(t)
  elif cmd == "echo":
    print " ".join(extractArgInfo(args))
  elif cmd == "cat":
    if os.path.exists(args[0][0]) and os.path.isfile(args[0][0]):
      if os.path.getsize(args[0][0]) < MAX_FILELENGTH:
        try:
          print open(args[0][0], 'rb').read()
        except IOError:
          print "File cannot be read."
      else:
        print "File is too big to show here."
        return 2
    else:
      print "%s: no such file." % args[0][0]
      return -1
  elif cmd == "cp":
    if not args[1][0]:
      print "No destination file specified, aborting."
      return -1
    destination = args[1][0]
    if os.path.isfile(args[0][0]) and os.path.isdir(destination):
      destination = os.path.join(destination, os.path.basename(os.path.abspath(args[0][0])))
    if copyFile(args[0][0], destination) == -1:
      print "Copy operation failed."
      return -1
  elif cmd == "mv":
    if not args[1][0]:
      print "No destination file specified, aborting."
      return -1
    destination = args[1][0]
    try:
      if os.path.isfile(args[0][0]) and os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(os.path.abspath(args[0][0])))
      os.rename(args[0][0], destination)
    except:
      print "Move operation failed."
      return -1
  elif cmd == "rm":
    toReturn = 0
    for arg in extractArgInfo(args):
      if os.path.exists(arg) and os.path.isfile(arg):
        try:
          os.remove(arg)
        except:
          print "Permission denied."
      else:
        print "%s: no such file." % arg
        toReturn = -1
    return toReturn
  elif cmd == "rmdir":
    toReturn = 0
    for arg in extractArgInfo(args):
      if os.path.exists(arg) and os.path.isdir(arg):
        try:
          os.rmdir(arg)
        except:
          print "Permission denied."
      else:
        print "%s: no such directory." % arg
        toReturn = -1
    return toReturn
  elif cmd == "mkdir":
    toReturn = 0
    for arg in extractArgInfo(args):
      p = os.path.abspath(arg)
      if os.path.exists(os.path.dirname(p)):
        try:
          os.mkdir(p)
        except:
          print "Permission denied."
      else:
        print "%s: no such parent directory." % os.path.dirname(p)
        toReturn = -1
    return toReturn
  elif cmd == "cd":
    try:
        if args[0][0]:
            os.chdir(args[0][0])
        else:
            os.chdir(startPath)
    except:
        print "%s: no such directory." % args[0][0]
        return -1
  elif cmd == "ls":
    listAll = hasOption(args, "-a")
    if args[0][0]:
      if os.path.exists(args[0][0]):
        p = args[0][0]
      else:
        p = ""
    else:
      p = "."
    if p:
      if os.path.isfile(p):
        print "%s    %s bytes" % (os.path.basename(os.path.abspath(p)), os.path.getsize(p))
      else:
        l = sorted(map(str, os.listdir(p)), key = str.lower)
        if len(l) > MAX_FILELISTINGLENGTH and not listAll:
          print "Too much files to display, use option '-a'."
          return -1
        k = 0
        for ii in range(len(l)):
          if os.path.isdir(os.path.join(p, l[ii])):
            l.insert(k, l[ii])
            del l[ii+1]
            k += 1
        for j in range(len(l)):
          if j < k:
            terminalTools.print_special(l[j], color = 0x0000FF, bold = True)
          elif os.path.islink(os.path.join(p, l[j])):
            terminalTools.print_special(l[j], color = 0xFF00FF)
          else:
            print l[j]
    else:
      print "%s: no such file or directory." % args[0][0]
      return -1
  elif cmd == "pwd":
    print os.path.abspath('.')
  elif cmd == "python":
    if args[0][0]:
      if not os.path.exists(args[0][0]):
        print "%s: no such file." % args[0][0]
        return -1
      terminalTools.history.active = False
      prompt.history = terminalTools.history
      addNewPythonScript()
      toReturn = 0
      sys.path[0] = os.path.abspath('.')
      sys.argv = map(str, extractArgInfo(args))
      namespace = genNamespace()
      try:
        execfile(args[0][0], namespace)
      except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type != SystemExit:
          import traceback
          print "Exception in script '%s' code:" % args[0][0]
          print '-'*36
          traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
          print '-'*36
        if exc_type in (KeyboardInterrupt, SystemExit) and wantExit and not exitAllPython:
          wantExit = False
        if exceptionCallback and exc_type != SystemExit:
          exceptionCallback(exc_type, exc_value, traceback.extract_tb(exc_traceback))
        toReturn = -1
      endLastPythonScript()
      return toReturn
    else:
      sys.path[0] = os.path.abspath('.')
      prompt.history = History()
      addNewPythonScript()
      namespace = genNamespace()
      inp = ""
      indent = False
      buffer = ""
      styles = ((0x000000, 0xFFFFFF, True), (0xFFFFFF, 0x000000, True), (0xAA0000, 0xFFFFFF, True))
      terminalTools.print_special((("Welcome to the ", 0), ("Interactive Python Shell", 1), ("!", 0)), styles = styles)
      while True:
        try:
          inp = raw_input((">>> ", "... ")[indent])
        except KeyboardInterrupt:
          print "KeyboardInterrupt"
          endLastPythonScript()
          if wantExit and not exitAllPython:
            wantExit = False
          print "Bye!"
          return -1
        if inp in ("quit()", "exit()"):
          break
        if inp:
          if inp[0] in (" ", "\t"):
            indent = True
          elif inp[-1] == ":":
            indent = True
          elif indent:
            print "Please end with a ENTER after an indentation-block."
            buffer = ""
            indent = False
        else:
          inp = buffer
          buffer = ""
          indent = False
        if indent:
          buffer += inp + "\n"
        elif inp:
          terminalTools.history.active = False
          prompt.history = terminalTools.history
          addNewPythonScript()
          exc_type = exc_value = exc_traceback = None
          extended_inp = "terminalTools.tmpValue = (%s)" % inp
          try:
            exec extended_inp in namespace
            if terminalTools.tmpValue != None:
              namespace['_'] = terminalTools.tmpValue
              print repr(namespace['_'])
          except SyntaxError:
            try:
              exec inp in namespace
            except:
              exc_type, exc_value, exc_traceback = sys.exc_info()
          except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
          if not exc_type == exc_value == exc_traceback == None:
            if exc_type != SystemExit:
              import traceback
              print "Exception in user code:"
              print '-'*36
              traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
              print '-'*36
            if exc_type in (KeyboardInterrupt, SystemExit) and wantExit and not exitAllPython:
              wantExit = False
          endLastPythonScript()
      endLastPythonScript()
      print "Bye!"
  elif cmd:
    try:
      toReturn = e32.start_exe(unicode(cmd), " ".join(extractArgInfo(args)), True)
      if toReturn == 2:
        print "Application terminated abnormally."
      return toReturn
    except:
      print "%s: command not found." % cmd
      return -1
    #return os.__system__(cmd)
  
  return 0  


def completeArg(orig, executablesFirst):
  hits = []
  unique = False
  arg = orig
  prefix = ".\\"
  
  if executablesFirst:
    l = [exe for exe in executables if exe[:len(arg)] == arg]
    hits += l
    if l:
      prefix = ""
  
  if prefix:
    if arg[:2] == prefix:
      arg = arg[2:]
      if executablesFirst:
        executablesFirst += 1
    
    if executablesFirst != True:
      if os.path.isdir(os.path.dirname(arg)):
        prefix = os.path.dirname(arg)
        if prefix[-1] != "\\":
          prefix += "\\"
        arg = arg[len(prefix):]
      files = sorted(map(str, os.listdir(prefix)), key = str.lower)
      l = [file for file in files if file[:len(arg)] == arg]
      for i, file in enumerate(l):
        if os.path.isdir(os.path.join(prefix, file)):
          l[i] += "\\"
        if executablesFirst and prefix == ".\\":
          l[i] = prefix + l[i]
      hits += l
    
    if executablesFirst == 2 and prefix == ".\\":
      arg = prefix + arg
  
  
  if arg in hits and len(hits) > 1:
    del hits[hits.index(arg)]
  
  unique = True
  if len(hits) == 0:
    hits = [orig]
    unique = False
  elif len(hits) == 1:
    hits[0] = prefix + hits[0]
  else:
    minLen = min(map(len, hits))
    for i in range(len(arg), minLen):
      char = hits[0][i]
      for hit in hits[1:]:
        if hit[i] != char:
          unique = False
          break
      if not unique:
        break
    if unique:
      hits = [prefix + hits[0][:i+1]]
      unique = False
    elif i > len(arg):
      hits = [prefix + hits[0][:i]]
  if unique:
    if os.path.isdir(hits[0]):
      unique = False
  
  return hits, unique

def formatArg(arg, quote, unique):
  out = quote
  for char in arg:
    if (char in ("\\", '"') and quote == '"') or (char in ("\\", "&", "'", '"') and not quote) or (char == "'" and quote == "'"):
      out += "\\"
    out += char
  if unique:
    out += quote
    out += " " * unique
  return out


def extractCommands(cms):
	#if not cms:
	#	return []
	
	quoteChars = ["'", '"']
	
	quote = ""
	quoteBuffer = quote
	start = 0
	amp = False
	escape = False
	argumentBuffer = ""
	
	commands = [[]]
	
	for i, char in enumerate(cms):
		tmpArg = argumentBuffer
		if not escape and not quote:
			if char == " " or char == "&":
				if (char == " " or (char == "&" and amp)):
					if argumentBuffer:
						commands[-1].append((str(argumentBuffer), quoteBuffer, start))
						quoteBuffer = ""
					if char == "&" and amp:
						commands.append([])
					amp = False
					argumentBuffer = ""
				elif char == "&" and not amp:
					amp = True
				else:
					amp = False
			else:
				if char == "\\":
					escape = True
				elif char in quoteChars:
					quote = char
					quoteBuffer = quote
				else:
					argumentBuffer += char
				amp = False
		elif escape and quote:
			if char != quote and char != "\\":
				argumentBuffer += "\\"
			argumentBuffer += char
			escape = False
		elif not escape and quote:
			if char == "\\" and quote == '"':
				escape = True
			elif char == quote:
				quote = ""
			else:
				argumentBuffer += char
		elif escape and not quote:
			argumentBuffer += char
			escape = False
		if argumentBuffer and not tmpArg:
			start = i
			if quoteBuffer:
				start -= 1
	
	if argumentBuffer:
		commands[-1].append((str(argumentBuffer), quoteBuffer, start))
		quoteBuffer = ""
	
	commands = [i for i in commands if i]
	for command in commands:
		if len(command) == 1:
			command.append(("", "/" * (argumentBuffer != ""), len(cms)-(argumentBuffer != "")))
	if not commands:
		commands.append([("", "", 0)])
	
	return commands

def execute():
  global tasksRunning, wantExit
  
  command = prompt.getInput()
  prompt.toEnd()
  prompt.add("\n")
  
  tasksRunning = True
  if command == 'toggleFullscreen':
    toggleFullscreen()
  else:
    os.system(command)
  tasksRunning = False
  
  prompt.update()
  
  wantExit = False


def initTerminal():
  global startPath, tasksRunning
  global prompt, inputHandler, history
  global pythonScripts
  
  pythonScripts = []
  tasksRunning = 0
  
  history = History()
  prompt = Prompt()
  prompt.history = history
  inputHandler = InputHandler()
  
  os.system("clear")
  os.system("help")
  
  startPath = os.path.abspath(".")
  sys.argv = [""]
  sys.path.insert(0, startPath)
  prompt.update()


def changeSize():
  global fontSize
  if tasksRunning:
    appuifw.note(u"Please close running applications first.")
    return
  size = appuifw.query(u"Give FontSize: ", 'number', fontSize)
  if size < 2:
    appuifw.note(u"That's too small!")
  elif size > 30:
    appuifw.note(u"That's too big!")
  else:
    fontSize = size
    text.font = (font, fontSize)
    os.system("clear")
    prompt.update()

def toggleFullscreen():
	if appuifw.app.screen == "normal":
		appuifw.app.screen = "full"
		appuifw.note(u"To go back to windowed, type 'toggleFullscreen' in the commandline.")
	else:
		appuifw.app.screen = "normal"


def toggleNavigation():
  global navigation
  prompt.navigation = not prompt.navigation
  appuifw.app.menu = [(u'%s navigation' % ["Enable", "Disable"][prompt.navigation], toggleNavigation), (u'Send KeyInterrupt', sendInterrupt), (u'Change FontSize', changeSize), (u'Toggle Fullscreen', toggleFullscreen)]
  
def sendInterrupt():
  global wantExit
  if pythonScripts:
    wantExit = True


def backupFunctions():
	# Copy important wrapper functions
	global __raw_input__, __input__
	from copy import copy

	os.__system__ = copy(os.system)
	# sys.__stdout__ = copy(sys.stdout) # No need, already done
	__raw_input__ = copy(raw_input)
	__input__ = copy(input)

def replaceFunctions():
	global raw_input, input
	os.system = pseudo_osSystem
	sys.stdout = PseudoStdOut()
	raw_input = terminalTools.raw_input
	input = terminalTools.input

def restoreFunctions():
	global raw_input, input
	os.system = os.__system__
	sys.stdout = sys.__stdout__
	raw_input = __raw_input__
	input = __input__


def main(excCallback = None):
  global lock, text, w, exceptionCallback, wantExit, font, fontSize, terminalTools
  
  wantExit = False
  
  terminalTools = TerminalTools()
  
  backupFunctions()
  replaceFunctions()
  
  w = False
  exceptionCallback = excCallback

  font = "normal"
  fontSize = 15
  for f in appuifw.available_fonts():
    if "mono" in f.lower():
      font = f
      break

  text = appuifw.Text()
  text.font = (font, fontSize)
  text.color = 0x000000
  text.highlight_color = 0xFFFFFF
  text.style = appuifw.HIGHLIGHT_STANDARD
  appuifw.app.body = text
  appuifw.app.title = u"Terminal"
  appuifw.app.menu = [(u'Enable navigation', toggleNavigation), (u'Send KeyInterrupt', sendInterrupt), (u'Change FontSize', changeSize), (u'Toggle Fullscreen', toggleFullscreen)]
  
  initTerminal()

  lock = e32.Ao_lock()
  appuifw.app.exit_key_handler=exit
  lock.wait()

def exit(force = False):
  doIt = True
  if tasksRunning and not force:
    doIt = appuifw.query(u"There are still tasks(%s) running. Stop them first with 'Send Interrupt' to avoid crashes. \nDo you want to exit anyway?" % len(pythonScripts), 'query')
  if not doIt:
    return
  prompt.keycapturer.stop()
  restoreFunctions()
  lock.signal()


if __name__ == "__main__":
  main()

