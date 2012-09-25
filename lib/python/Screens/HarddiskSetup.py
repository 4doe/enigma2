from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Harddisk import harddiskmanager			#global harddiskmanager
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
import Components.Task

# [iq
from Components.config import config
from enigma import eTimer

class HarddiskWait(Screen):
	def doInit(self):
		self.timer.stop()
		for i in range(0,5):
			result = self.hdd.initialize()
			if result != -2:
				break;
		self.close(result)

	def doCheck(self):
		self.timer.stop()
		result = self.hdd.check()
		self.close(result)

	def doConvert(self):
		self.timer.stop()
		result = self.hdd.convertExt3ToExt4()
		self.close(result)

	def __init__(self, session, hdd, type):
		Screen.__init__(self, session)
		self.hdd = hdd
		self.timer = eTimer()
		if type == HarddiskSetup.HARDDISK_INITIALIZE:
			text = _("Formatting in progress, please wait.")
			self.timer.callback.append(self.doInit)
		elif type == HarddiskSetup.HARDDISK_CHECK:
			text = _("Checking Filesystem, please wait.")
			self.timer.callback.append(self.doCheck)
		else:
			text = _("Changing Filesystem ext3 to ext4, please wait.")
			self.timer.callback.append(self.doConvert)
		self["wait"] = Label(text)
		self.timer.start(100)
# iq]

class HarddiskSetup(Screen):
	HARDDISK_INITIALIZE = 1
	HARDDISK_CHECK = 2
	HARDDISK_CHANGE_FILESYSTEM = 3		# [iq]

#	def __init__(self, session, hdd, action, text, question):
	def __init__(self, session, hdd, action = None, text = None, question = None, type = None):		# [iq]
		Screen.__init__(self, session)
		self.hdd = hdd		# [iq]
		self.action = action
		self.question = question

# [iq
		if type not in (self.HARDDISK_INITIALIZE, self.HARDDISK_CHECK, self.HARDDISK_CHANGE_FILESYSTEM):
			self.type = self.HARDDISK_INITIALIZE
		else:
			self.type = type
# iq]

		self["model"] = Label(_("Model: ") + hdd.model())
		self["capacity"] = Label(_("Capacity: ") + hdd.capacity())
		self["bus"] = Label(_("Bus: ") + hdd.bus())
		self["initialize"] = Pixmap()

# [iq
		if self.type == self.HARDDISK_INITIALIZE:
			text = _("Format")
		elif self.type == self.HARDDISK_CHECK:
			text = _("Check")
		else: #HARDDISK_CHANGE_FILESYSTEM
			text = _("Convert ext3 to ext4")
# iq]
		self["initializetext"] = Label(text)
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.close,
			"cancel": self.close
		})
		self["shortcuts"] = ActionMap(["ShortcutActions"],
		{
			"red": self.hddQuestion
		})

# [iq
	def hddReady(self, result):
		print "Result: " + str(result)
		if (result != 0):
			if self.type == self.HARDDISK_INITIALIZE:
				message = _("Unable to format device.\nError: ")
			elif self.type == self.HARDDISK_CHECK:
				message = _("Unable to complete filesystem check.\nError: ")
			else:
				message = _("Unable to convert filesystem.\nError: ")
			self.session.open(MessageBox, message + str(self.hdd.errorList[0 - result]), MessageBox.TYPE_ERROR)
		else:
			self.close()
# iq]

	def hddQuestion(self):
#		message = self.question + "\n" + _("You can continue watching TV etc. while this is running.")
# [iq
		if self.type == self.HARDDISK_INITIALIZE:
			message = _("Do you really want to format the device?\nAll data on the disk will be lost!")
		elif self.type == self.HARDDISK_CHECK:
			message = _("Do you really want to check the filesystem?\nThis could take lots of time!")
		else:
			message = _("Do you really want to convert the filesystem?\nThis could take lots of time!")
# iq]
		self.session.openWithCallback(self.hddConfirmed, MessageBox, message)

	def hddConfirmed(self, confirmed):
		if not confirmed:
			return
#		try:
#			Components.Task.job_manager.AddJob(self.action())
#		except Exception, ex:
#			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)
#		self.close()
# [iq
		if config.usage.background_hddjob.value:
			try:
				Components.Task.job_manager.AddJob(self.action())
			except Exception, ex:
				self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)
			self.close()
		else:
			print "this will start either the initialize or the fsck now!"
			self.session.openWithCallback(self.hddReady, HarddiskWait, self.hdd, self.type)
# iq]

class HarddiskSelection(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		if harddiskmanager.HDDCount() == 0:
			tlist = []
			tlist.append((_("no storage devices found"), 0))
			self["hddlist"] = MenuList(tlist)
		else:			
			self["hddlist"] = MenuList(harddiskmanager.HDDList())
		
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.okbuttonClick ,
			"cancel": self.close
		})

	def doIt(self, selection):
		self.session.openWithCallback(self.close, HarddiskSetup, selection,
			 action=selection.createInitializeJob,
			 text=_("Initialize"),
#			 question=_("Do you really want to initialize the device?\nAll data on the disk will be lost!"))
# [iq
			 question=_("Do you really want to initialize the device?\nAll data on the disk will be lost!"),
			 type=HarddiskSetup.HARDDISK_INITIALIZE)
# iq]
	
	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
#			self.doIt(selection[1])
# [iq
			if config.usage.background_hddjob.value:
				self.doIt(selection[1])
			else:
				self.session.open(HarddiskSetup, selection[1], type=HarddiskSetup.HARDDISK_INITIALIZE)
# iq]

# This is actually just HarddiskSelection but with correct type
class HarddiskFsckSelection(HarddiskSelection):
	def __init__(self, session):
		HarddiskSelection.__init__(self, session)
		self.skinName = "HarddiskSelection"

# [iq
	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			if config.usage.background_hddjob.value:
				self.doIt(selection[1])
			else:
				self.session.open(HarddiskSetup, selection[1], type=HarddiskSetup.HARDDISK_CHECK)
# iq]

	def doIt(self, selection):
		self.session.openWithCallback(self.close, HarddiskSetup, selection,
			 action=selection.createCheckJob,
			 text=_("Check"),
#			 question=_("Do you really want to check the filesystem?\nThis could take lots of time!"))
# [iq
			 question=_("Do you really want to check the filesystem?\nThis could take lots of time!"),
			 type=HarddiskSetup.HARDDISK_CHECK)
# iq]

class HarddiskConvertExt4Selection(HarddiskSelection):
	def __init__(self, session):
		HarddiskSelection.__init__(self, session)
		self.skinName = "HarddiskSelection"

# [iq
	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			if config.usage.background_hddjob.value:
				self.doIt(selection[1])
			else:
				self.session.open(HarddiskSetup, selection[1], type=HarddiskSetup.HARDDISK_CHANGE_FILESYSTEM)
# iq]

	def doIt(self, selection):
		self.session.openWithCallback(self.close, HarddiskSetup, selection,
			 action=selection.createExt4ConversionJob,
			 text=_("Convert ext3 to ext4"),
#			 question=_("Do you really want to convert the filesystem?\nYou cannot go back!"))
# [iq
			 question=_("Do you really want to convert the filesystem?\nYou cannot go back!"),
			 type=HarddiskSetup.HARDDISK_CHANGE_FILESYSTEM)
# iq]

