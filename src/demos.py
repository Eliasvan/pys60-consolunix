# -*- coding: utf-8 -*-

def checkTerminalTools(version = 1.0):
	global terminalTools
	ok = False
	try:
		if float(terminalTools.version) >= version:
			ok = True
	except:
		print "I did not found a native terminalTools. I'll try to load a local one (terminalTools.py)."
		try:
			from TerminalTools import terminalTools
			if float(terminalTools.version) >= version:
				ok = True
		except:
			print "I did not found a local terminalTools. Giving up."
	if ok:
		print "Successfully loaded terminalTools!"
	else:
		print "Failed to load terminalTools. If you experience problems, you know what's the reason."
	print "=" * 20 + "\n"
	return ok

def checkTerminalToolsQuick():
	global terminalTools
	try:
		terminalTools.version
	except:
		try:
			from TerminalTools import terminalTools
		except:
			print "No module 'terminalTools' found."
			return False
	return True



def sayHello():
	print "This is a simple script."
	print "It will demonstrate some funcionality of 'terminalTools' of the Terminal for PyS60."
	print

def inputDemo():
	isSupported = terminalTools.checkFeature("styledPrinting", True)
	
	inp = "EMPTY"
	while inp:
		inp = raw_input("Do you want to test special? (Press ENTER to stop) ")
		
		if inp == "yes":
			answer = terminalTools.raw_input_special("This is special! Type somthing: ", highlight_color = 0x00FF00)
			terminalTools.print_special("Hello! ", bold = True, doNL = False)
			terminalTools.print_special("You typed: ")
			terminalTools.print_special( ("'%s'" % answer), color = 0x4488BB )
		elif inp == "no":
			answer = raw_input("This is boring: type somthing: ")
			print "You typed: '%s'" % answer

def drawDemo():
	import os, time

	print "Here we go!"
	time.sleep(1.)
	os.system("clear")

	seconds = 7
	fps = 20
	
	timePerFrame = 1.0/fps
	t = time.time()
	for i in range(seconds * fps):
		out = ""
		for ii in range(10, 20):
			out += " " * (i % ii) + "|" + "\n"
		print out
		
		t = time.time() - t
		if t < timePerFrame:
			time.sleep(timePerFrame - t)
		t = time.time()
		
		os.system("clear")

def keyGrabDemo():
	if terminalTools.checkFeature("keyGrabber", True):
		isSupported = terminalTools.checkFeature("keyGrabber.contineousPress", True)
	else:
		isSupported = False
	
	if raw_input("Do you want to enable contineous-press? ") == "yes":
		terminalTools.keyGrabber.setContineousPress(True)
	else:
		terminalTools.keyGrabber.setContineousPress(False)
	print "ContineousPress is %s." % ("disabled", "enabled")[terminalTools.keyGrabber.contineousPress]

	print "Press some keys and see their names appearing. Press ENTER to stop."
	
	terminalTools.keyGrabber.start()
	
	keys = []
	while not ("ENTER", 0) in keys:
		keys = terminalTools.keyGrabber.get()
		if keys:
			print keys
	
	terminalTools.keyGrabber.stop()

def historyDemo():
	isSupported = terminalTools.checkFeature("history", True)

	if raw_input("Do you want to reset history? ") == "yes":
		terminalTools.history.reset()
		print "History has been reset."
	else:
		print "Ok, history will go on."
	
	terminalTools.history.active = True
	
	t = "EMPTY"
	while t:
		t = raw_input("Type something (ENTER to quit): ")
		print "You typed %s." % t
	
	terminalTools.history.active = False

def autoCompleteDemo():
	isSupported = terminalTools.checkFeature("autoComplete", True)
	
	print "First, you may type a couple of names."
	names = []
	i = 1
	name = "EMPTY"
	while name:
		name = raw_input("Type name %s: " % i)
		if name and not name.lower() in names:
			names.append(name.lower())
			i += 1
	
	print "Ok, now we will start!"
	
	def autoCompleteCallback(inp):
		orig = inp
		n = inp.lower()
		if n in names:
			print "\nYou did effort to type the whole name. Bravo!"
		elif n:
			for name in names:
				if n == name[:len(n)]:
					return name[0].upper() + name[1:]
		return orig
	
	name = "EMPTY"
	while name:
		name = terminalTools.raw_input_special("Type a name: ", autoComplete = autoCompleteCallback)
		if name.lower() in names:
			print "Hey, I know that name!"
		elif name:
			print "Who? I don't know %s." % name

def defaultInputTextDemo():
	isSuported = terminalTools.checkFeature("defaultInputText", True)

	if isSuported:
		inp = terminalTools.raw_input_special("Type a comment: ", defaultText = "# a comment")
		print 'You typed "%s".' % inp



if checkTerminalTools():
	import os

	sayHello()
	
	demos = ["sayHello", "inputDemo", "drawDemo", "keyGrabDemo", "historyDemo", "autoCompleteDemo", "defaultInputTextDemo"]
	text = ""
	for i, demo in enumerate(demos):
		text += " %s. %s() \n" % (i+1, demo)

	while True:
		inp = input(text + " 0. quit \n \nChoose an option: ")
		
		if 0 < inp <= len(demos):
			exec "%s()" % demos[inp-1]
		elif inp == 0:
			break
		else:
			print "No such demo."
		
		os.system("clear")

	print "Bye!"
