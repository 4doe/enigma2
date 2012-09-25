from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from Components.Sources.StaticText import StaticText
import enigma
import urllib

class ChoiceBox(Screen):
#	def __init__(self, session, title = "", list = [], keys = None, selection = 0, skin_name = []):
	def __init__(self, session, title = "", list = [], keys = None, selection = 0, skin_name = [], extEntry = None):
		Screen.__init__(self, session)

		if isinstance(skin_name, str):
			skin_name = [skin_name]
		self.skinName = skin_name + ["ChoiceBox"] 
		if title:
			title = _(title)
# [iq
		try:
			if skin_name[0] == "ExtensionsList":
				from Components.Network import iNetwork
				from Components.config import ConfigIP, NoSave
				self.local_ip = NoSave(ConfigIP(default=iNetwork.getAdapterAttribute("eth0", "ip")))

				if self.local_ip.getText() is not None:
					self["text"] = Label("IP: getting...\n" + "Local IP: " + self.local_ip.getText())
				else:
					self["text"] = Label("IP: getting...\n" + "Local IP: getting...")
			else:
				if len(title) < 55:
					Screen.setTitle(self, title)
					self["text"] = Label("")
				else:
					self["text"] = Label(title)
		except:
# iq]
			if len(title) < 55:
				Screen.setTitle(self, title)
				self["text"] = Label("")
			else:
				self["text"] = Label(title)
		self.list = []
		self.extEntry = extEntry		# [iq]
		self.summarylist = []
		if keys is None:
			self.__keys = [ "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "red", "green", "yellow", "blue" ] + (len(list) - 10) * [""]
		else:
			self.__keys = keys + (len(list) - len(keys)) * [""]
			
		self.keymap = {}
		pos = 0
		for x in list:
			strpos = str(self.__keys[pos])
			self.list.append(ChoiceEntryComponent(key = strpos, text = x))
			if self.__keys[pos] != "":
				self.keymap[self.__keys[pos]] = list[pos]
			self.summarylist.append((self.__keys[pos],x[0]))
			pos += 1
		self["list"] = ChoiceList(list = self.list, selection = selection)
		self["summary_list"] = StaticText()
		self["summary_selection"] = StaticText()
		self.updateSummary(selection)
				
#		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions", "InfobarChannelSelection"], 
		{
			"ok": self.go,
			"back": self.cancel,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal,
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"up": self.up,
			"down": self.down,
# [iq
			"openSatellites": self.extEntryReady,
			"menu": self.extEntryGo,
# iq]
		}, -1)

# [iq
		self.extEntryExecuted = -1

		try:
			if skin_name[0] == "ExtensionsList":
				self.StaticIPTimer = enigma.eTimer()
				self.StaticIPTimer.callback.append(self.iptimeout)
				self.iptimeout()
		except:
			pass

	def extEntryReady(self):
		if self.extEntry is not None:
			if self.extEntryExecuted == 1 :
				self.extEntryExecuted = 2
			else:
				self.extEntryExecuted = -1
	def extEntryGo(self):
		if self.extEntry is not None:
			if self.extEntryExecuted == 2:
				self.close(("extEntry", self.extEntry[0][0]))
			self.extEntryExecuted = 1
# iq]
	def autoResize(self):
		orgwidth = self.instance.size().width()
		orgpos = self.instance.position()
#		textsize = self["text"].getSize()
		textsize = (textsize[0] + 50, textsize[1])		# [iq]
		count = len(self.list)
		if count > 10:
			count = 10
		offset = 25 * count
		wsizex = textsize[0] + 60
		wsizey = textsize[1] + offset
		if (520 > wsizex):
			wsizex = 520
		wsize = (wsizex, wsizey)
		# resize
		self.instance.resize(enigma.eSize(*wsize))
		# resize label
		self["text"].instance.resize(enigma.eSize(*textsize))
		# move list
		listsize = (wsizex, 25 * count)
		self["list"].instance.move(enigma.ePoint(0, textsize[1]))
		self["list"].instance.resize(enigma.eSize(*listsize))
		# center window
		newwidth = wsize[0]
		self.instance.move(enigma.ePoint((720-wsizex)/2, (576-wsizey)/(count > 7 and 2 or 3)))

	def keyLeft(self):
		pass
	
	def keyRight(self):
		pass
	
	def up(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	# runs a number shortcut
	def keyNumberGlobal(self, number):
		self.goKey(str(number))

	# runs the current selected entry
	def go(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.goEntry(cursel[0])
		else:
			self.cancel()

	# runs a specific entry
	def goEntry(self, entry):
		if len(entry) > 2 and isinstance(entry[1], str) and entry[1] == "CALLFUNC":
			# CALLFUNC wants to have the current selection as argument
			arg = self["list"].l.getCurrentSelection()[0]
			entry[2](arg)
		else:
			self.close(entry)

	# lookups a key in the keymap, then runs it
	def goKey(self, key):
		if self.keymap.has_key(key):
			entry = self.keymap[key]
			self.goEntry(entry)

	# runs a color shortcut
	def keyRed(self):
		self.goKey("red")

	def keyGreen(self):
		self.goKey("green")

	def keyYellow(self):
		self.goKey("yellow")

	def keyBlue(self):
		self.goKey("blue")

	def updateSummary(self, curpos=0):
		pos = 0
		summarytext = ""
		for entry in self.summarylist:
			if pos > curpos-2 and pos < curpos+5:
				if pos == curpos:
					summarytext += ">"
					self["summary_selection"].setText(entry[1])
				else:
					summarytext += entry[0]
				summarytext += ' ' + entry[1] + '\n'
			pos += 1
		self["summary_list"].setText(summarytext)

	def cancel(self):
		self.close(None)
# [iq
	def iptimeout(self):
		import os
		static_ip =urllib.urlopen('http://en2.ath.cx/iprequest.php').read()
#		if os.path.isfile("/tmp/extip"):
#			fp = file('/tmp/extip', 'r')
#			static_ip = fp.read()
#			fp.close()
		if static_ip=="":
#			conn.reqest("GET","/iprequest.php")
#			r1 = conn.getresponse()
#			static_ip = r1.read()
				#os.system("wget -O /tmp/extip -T 4 -t 1 http://en2.ath.cx/iprequest.php")
			print "NOK : ", static_ip
		else:
			print "OK : ", static_ip
			self.StaticIPTimer.stop()

			self["text"].setText("IP: " + static_ip + "\nLocal IP: " + self.local_ip.getText())
				
			self["text"].show()
			return
#		else:
#			conn.reqest("GET","/iprequest.php")
#			r1 = conn.getresponse()
#            data1 = r1.read()
#			static_ip = r1.read()
			#os.system("wget -O /tmp/extip -T 2 -t 1 http://en2.ath.cx/iprequest.php")

		self.StaticIPTimer.stop()
		self.StaticIPTimer.start(2000, True)	
# iq]

