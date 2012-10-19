from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		
		AboutText = _("Hardware: ") + about.getHardwareTypeString() + "\n"
# iq [
		import fcntl, socket, struct
		def getHwAddr(ifname):
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
			return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
		macaddress = getHwAddr("eth0") 
		self["MacAddress"] = StaticText(_("Mac Address:") + " " + macaddress)
		AboutText += _("Mac Address:") + " " + macaddress + "\n"

		from Tools.HardwareInfo import HardwareInfo
		if HardwareInfo().has_micom():
			AboutText += _("Micom Version: ") + about.getMicomVersionString() + "\n"
# ]
		AboutText += _("Image: ") + about.getImageTypeString() + "\n"
		AboutText += _("Kernel Version: ") + about.getKernelVersionString() + "\n"

		
		EnigmaVersion = "Enigma: " + about.getEnigmaVersionString()
		self["EnigmaVersion"] = StaticText(EnigmaVersion)
		AboutText += EnigmaVersion + "\n"
		
		ImageVersion = _("Last Upgrade: ") + about.getImageVersionString()
		self["ImageVersion"] = StaticText(ImageVersion)
		AboutText += ImageVersion + "\n"

		# [iq
		AboutText += _("Powered by 4D") + "\n"
		# iq]

		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"

		self["HDDHeader"] = StaticText(_("Detected HDD:"))
		AboutText += "\n" + _("Detected HDD:") + "\n"

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += "%s\n(%s, %d GB %s)" % (hdd.model(), hdd.capacity(), hdd.free()/1024, _("free"))
				else:
					hddinfo += "%s\n(%s, %d MB %s)" % (hdd.model(), hdd.capacity(), hdd.free(), _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		AboutText += hddinfo
		self["AboutScrollLabel"] = ScrollLabel(AboutText)

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"], 
			{
				"cancel": self.close,
				"ok": self.close,
				"green": self.showTranslationInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

# iq [
		self["hidden_action"] = ActionMap(["ColorActions"],
		{
			"red": self.red_action,
			"blue": self.blue_action,
		},-1)

		self.key_status = -1

	def red_action(self):
		if self.key_status == 1:
			self.key_status = 2
		else:
			self.key_status = -1

	def blue_action(self):
		if self.key_status == 2:
			from Screens.ChangeRCU import ChangeRCU
			self.session.open(ChangeRCU)
			self.close()
		else:
			self.key_status = 1
# ]

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = "(N/A)"

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"], 
			{
				"cancel": self.close,
				"ok": self.close,
			})
