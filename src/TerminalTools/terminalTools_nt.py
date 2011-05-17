import os


class os2:
	def __init__(self):
		import copy
		self.ossystem = copy.copy(os.system)
	def system(self, command):
		if command == "clear":
			command = "cls"
		return self.ossystem(command)
os2 = os2()


os.system = os2.system
del os2
