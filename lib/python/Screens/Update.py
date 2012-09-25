# [iq]
from Screen import Screen
from Components.Label import Label,MultiColorLabel
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap,MultiPixmap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelectionNumber, NoSave
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Screens.MessageBox import MessageBox

from ftplib import FTP 
from enigma import MiniFTP_Thread, eTimer
import os

from Components.Harddisk import harddiskmanager, getProcMounts

def readFile(filename):
	file = open(filename)
	data = file.read().strip()
	file.close()
	return data

class UpdateModeChoice(Screen, ConfigListScreen):
	SETTINGS = 1
	CONFIGURATIONS = 2
	CHANNEL_LISTS = 4

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = [ "Setup" ]
		self.setup_title = _("Update Options")

		self.list = [ ]
#		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
		ConfigListScreen.__init__(self, self.list, session = session)

		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions"], 
			{
				"cancel": self.keyCancel,
				"save": self.apply,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Update"))

		config.update = ConfigSubsection()
		config.update.settings = ConfigYesNo(default = False)
		config.update.configurations = ConfigYesNo(default = False)
		config.update.channellists = ConfigYesNo(default = False)

		self.ret = 90

		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)

	def createSetup(self):
		self.list = [ ]

		self.list.append(getConfigListEntry(_("Keep enigma2 settings file"), config.update.settings))
		self.list.append(getConfigListEntry(_("Keep configuration files"), config.update.configurations))
		self.list.append(getConfigListEntry(_("Keep channel lists"), config.update.channellists))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def keyCancel(self):
		self.close(False)

	def apply(self):
		if config.update.settings.value:
			self.ret = self.ret + self.SETTINGS
		if config.update.configurations.value:
			self.ret = self.ret + self.CONFIGURATIONS
		if config.update.channellists.value:
			self.ret = self.ret + self.CHANNEL_LISTS

		self.close(self.ret)

class Update(Screen):
	skin = """
        <screen name="Update" position="center,center" size="560,380" title="Software Update">
			<ePixmap pixmap="skin_default/buttons/key_blue.png" position="10,0" size="40,40" alphatest="on" />
			<widget name="key_blue" position="50,0" zPosition="1" size="540,40" font="Regular;20" halign="left" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="text" position="0,40" zPosition="1" size="560,260" font="Regular;20" halign="center" valign="center" />
			<widget name="top" position="10,40" zPosition="2" size="540,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<eLabel backgroundColor="#4E5664" position="13,82" size="534,2" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="13,275" size="534,2" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="13,82" size="2,194" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="547,82" size="2,194" zPosition="1"/>
			<widget name="menulist" position="15,85" scrollbarMode="showOnDemand" size="530,190" zPosition="10"/>
			<widget name="percent" position="15,282" zPosition="2" size="30,40" valign="center" halign="center" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="run" position="45,282" zPosition="2" size="50,40" valign="center" halign="left" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<widget name="prog" position="95,280" zPosition="2" size="455,40" valign="center" halign="left" font="Regular;18" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
    		<eLabel backgroundColor="#4E5664" position="5,350" size="550,2" zPosition="1"/>
			<widget name="bottom" position="10,355" zPosition="2" size="540,20" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""

	SERVER_DNS = "en2.ath.cx"

	INTERNET_UPDATE = 0
	INTERNET_UPDATE_BETA = 1
	INTERNET_SR_UPDATE = 2
	INTERNET_SR_UPDATE_BETA = 3

	def __init__(self, session, type = 0, iface='eth0'):
		Screen.__init__(self, session)
		self.session = session
		self.type = type # update type
		self.iface = iface

		self.drawProgressBarTimer = eTimer()
		self.drawProgressBarTimer.callback.append(self.drawProgressBar)

		self.checkEnvTimer = eTimer()
		self.checkEnvTimer.callback.append(self.checkEnv)

		self.progressSpin = [ "%  /", "%  |", "%  -" ]
		if self.iface == 'wlan0' or self.iface == 'ath0' or self.iface == 'ra0':
			lan = "Wireless"
		else:
			lan = "Integrated Ethernet"
		modelDir = open("/proc/stb/info/modelname").read().strip('\n')
		self.imageInfo = { self.INTERNET_UPDATE : { "title" : "SW Update - "+lan, "imagedir" : "NEW/"+modelDir+"_REL" },
			self.INTERNET_SR_UPDATE : { "title" : "SR SW Update - "+lan, "imagedir" : "NEW/"+modelDir+"SR_REL" },
			self.INTERNET_UPDATE_BETA : { "title" : "SW Update (BETA) - "+lan, "imagedir" : "NEW/"+modelDir },
			self.INTERNET_SR_UPDATE_BETA : { "title" : "SR SW Update (BETA) - "+lan, "imagedir" : "NEW/"+modelDir+"SR" }
		}
		self.setTitle(self.imageInfo[self.type]["title"])

		self.swList = []
		self.hddList = []
		self["menulist"] = MenuList(self.swList)
		self["menulist"].hide()
		self["percent"] = Label(_(" "))
		self["run"] = Label(_(" "))
		self["prog"] = Label(_(" "))
		self["top"] = Label(_(" "))
		self["bottom"] = Label(_(" "))
		self["text"] = Label(_("Downloading list information. Please wait..."))
#		self["key_blue"] = Button(_("Backup location : " + config.swupdate.downloadlocation.value))
		self["key_blue"] = Button(_("Backup location : "))

		self["actions"] = ActionMap(["MinuteInputActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"up": self.up,
				"down": self.down,
				"blue": self.toggleHddSW,
			},-1)

		self.requiredSize = -1
		self.serverAlive = False
		self.showingHddList = False
		self.downloadingSW = False
		self.depSWList = [ "cfe", "kernel" ]
		self.existDepSWList = []
		self.downloadedSW = {}

		def progressBar(configElement):
			num = int(configElement.value)
			if num > 0: 
				self["run"].setText(_(self.progressSpin[num%3]))
				self["prog"].setText("[" + "="*(40*num/100) + "]")
				self["percent"].setText(_("%d" % num))
			else:
				self["run"].setText(_(" "))
				self["prog"].setText(_(" "))
				self["percent"].setText(_(" "))

		def progressAction(configElement):
			num = int(configElement.value)
			if num == -1:
				self.drawProgressBarTimer.stop()
				MiniFTP_Thread.getInstance().Stop_Thread();
				self.downloadingSW = False
				self.hiddenSWNum = 0
				self.downloadedSW = {}
				self.removeDownloadDir()
			elif num < 100:
				self.drawProgressBarTimer.start(1000, True)	
			elif num == 100:
				self.drawProgressBarTimer.stop()
				MiniFTP_Thread.getInstance().Stop_Thread();
				self.downloadingSW = False

				if len(self.existDepSWList):
					self.download(extStr=self.existDepSWList.pop())
				else:
					if self.downloadedSWSizeOk():
						self.session.openWithCallback(self.downloadBurn, UpdateModeChoice)
					else:
						self.session.open(MessageBox, _("Failed while checking downloaded SW!\nTry again please."), MessageBox.TYPE_ERROR)
						self.downloadCancel(True)

		config.progress = NoSave(ConfigSelectionNumber(-1, 100, 1, default = -1))
		config.progress.addNotifier(progressBar, False)
		config.progress.addNotifier(progressAction, False)

		def downloadLocation(configElement):
			if "key_blue" in self:
				self["key_blue"].setText(_("Backup location : " + configElement.value))

		config.swupdate.downloadlocation.addNotifier(downloadLocation)

		self.checkEnvTimer.start(1000, True)

	def downloadedSWSizeOk(self):
		for sw in self.downloadedSW.keys():
			if self.downloadedSW[sw][1] != os.path.getsize(self.downloadedSW[sw][0]):
				return False
		return True

	def checkDepSW(self):
		self.existDepSWList = []
		if self.serverAlive:
			for sw in self.depSWList:
				ftp = FTP(self.SERVER_DNS)
				ftp.login()
				ls = []
				try:
					listCmd = "LIST " + self.imageInfo[self.type]["imagedir"] + "/." + self["menulist"].getCurrent() + "." + sw
					ftp.retrlines(listCmd, ls.append)
				except:
					print "failed to get image list"
					pass

				ftp.quit()

				if ls:
					self.existDepSWList.append(sw)

	def checkEnv(self):
		# server check
		if 0 == MiniFTP_Thread.getInstance().Alive_Check(0, self.SERVER_DNS):
			self.serverAlive = True
			self.loadSWList()
		else:
			self.serverAlive = False
			self.swList = []

		# hdd check
		hddList = self.getHddList() 
		for hdd in hddList:
			if self.isFileSystemSupported(hdd=hdd[1]):
				self.hddList.append(hdd)
		config.swupdate.downloadlocation.setChoices(self.hddList)

		# draw menu
		self.drawMenu()

	def getHddList(self):
		newHddList = []

		hddList = harddiskmanager.HDDList()
		for h in hddList:
			devpath = "/sys/block/" + h[1].device[:3]
			removable = bool(int(readFile(devpath + "/removable")))
			if removable:
				newHddList.append((h[1].findMount(), h[1]))

		return newHddList

	def loadSWList(self):
		if self.serverAlive:
			ftp = FTP(self.SERVER_DNS)
			ftp.login()
			try:
				ftp.cwd(self.imageInfo[self.type]["imagedir"])
				self.swList = ftp.nlst()
			except:
				print "failed to get image list"
				pass

			self.requiredSize = 0 
			for sw in self.swList:
				if self.requiredSize < ftp.size(sw):
					self.requiredSize = ftp.size(sw) + 10*1024

			ftp.quit()

	def getSWSize(self, sw):
		size = 0
		if self.serverAlive:
			ftp = FTP(self.SERVER_DNS)
			ftp.login()
			size = ftp.size(sw)
			ftp.quit()
		return size

	def freeSizeOk(self, path):
		if self.requiredSize != -1:
			s = os.statvfs(path)
			free = s.f_bsize * s.f_bavail
			if free > self.requiredSize:
				return True
		return False

	def drawMenu(self):
		self.showingHddList = False
		if not self.serverAlive:
			self["menulist"].hide()
			self["text"].setText(_("No Internet\nPress \"EXIT\" for exit"))
			self["text"].show()
		elif not self.hddList:
			self["menulist"].hide()
#			self["text"].setText(_("Found no usb storage devices for downloading S/W.\nSupporting file system : vfat, fat"))
			self["text"].setText(_("Please insert USB storage device."))
			self["text"].show()
		elif not self.swList:
			self["menulist"].hide()
			self["text"].setText(_("Empty (update file is not ready)\nPress \"EXIT\" for exit"))
			self["text"].show()
		elif not self.freeSizeOk(config.swupdate.downloadlocation.value):
			self.showingHddList = True
			self["text"].hide();
#			self["top"].setText(_("Not enough space for downloading S/W."))
			self["top"].setText(_("Not enough USB storage free space."))
			self["bottom"].setText(_("Please check USB storage device."))
			self["menulist"].l.setList(self.hddList)
			self["menulist"].moveToIndex(config.swupdate.downloadlocation.getIndex())
			self.showHddInfo()
			self["menulist"].show();
		else:
			self["text"].hide();
			self["top"].setText(_("Please select the software version to upgrade to"))
			self["bottom"].setText(_("Please select version to upgrade or exit to abort"))
			self["menulist"].l.setList(self.swList)
			self["menulist"].show();

	def drawProgressBar(self):
		config.progress.value = str(MiniFTP_Thread.getInstance().GetState())

	def downloadBurn(self, val):
		from enigma import quitMainloop
		if not val:
			config.progress.value = str(-1)
			self.drawMenu()
#			self.close()
		else:
			'''
			files = [ "oe_kernel.bin" ]
			for f in files:
				ifile = self.getDownloadDir()+"/"+f
				ofile = self.getDownloadDir()+"/cfe/"+f
				if os.path.exists(ifile):
					os.system("dd if=%s of=%s ibs=4160 skip=1; rm -f %s" % (ifile, ofile, ifile))
			'''
			os.system("echo %s > /tmp/.update_file" % (config.swupdate.downloadlocation.value + "/update/" + config.misc.boxtype.value + "/oe_rootfs.bin"))
			self.hide()
			from Screens.Standby import QuitMainloopScreen
			self.quitScreen = self.session.instantiateDialog(QuitMainloopScreen,retvalue=val)
			self.quitScreen.show()
			quitMainloop(val)

	def toggleHddSW(self):
		if not self.downloadingSW and self.hddList:
			if not self.showingHddList:
				self.showingHddList = True
				self["text"].hide();
				self["top"].setText(_("Select device for downloading S/W."))
				self["bottom"].setText(_("Please select device or exit to abort."))
				self["menulist"].l.setList(self.hddList)
				self["menulist"].moveToIndex(config.swupdate.downloadlocation.getIndex())
				self.showHddInfo()
				self["menulist"].show();
			else:
				self.drawMenu()

	def cancel(self):
		if self.downloadingSW:
			self.session.openWithCallback(self.downloadCancel, MessageBox, _("Do you really want to exit downloading\nthe file \"%s\"?") % self["menulist"].getCurrent())
		else:
			self.close()

	def downloadCancel(self, val):
		if val:
			self.downloadingSW = False

			self["text"].hide()
			self["menulist"].show()

			config.progress.value = str(-1)

	def download(self, val=True, extStr=""):
		if val:
			# first download file must be rootfs
			if not extStr:
				self.removeDownloadDir()
				self.checkDepSW()

			self["menulist"].hide()
			if not extStr:
				self["text"].setText(_("Downloading \"%s\"\nIf you want to exit, press \"EXIT\" key in rcu") % self["menulist"].getCurrent())
				self.swPath = self.imageInfo[self.type]["imagedir"] + "/" + self["menulist"].getCurrent()
			else:
				self["text"].setText(_("Downloading \"%s\"\nIf you want to exit, press \"EXIT\" key in rcu") % extStr)
				self.swPath = self.imageInfo[self.type]["imagedir"] + "/." + self["menulist"].getCurrent() + "." + extStr
			self["text"].show()

			dlfile = self.getDownloadDir()
			if extStr == "cfe":
				dlfile += "/cfe/cfe.bin"
			elif extStr == "kernel":
				dlfile += "/cfe/oe_kernel.bin"
			else:
				dlfile += "/oe_rootfs.bin"
			self.downloadedSW[self.swPath] = (dlfile, self.getSWSize(self.swPath))
			MiniFTP_Thread.getInstance().DownloadFile(0, self.iface, self.SERVER_DNS, self.swPath, "anonymous", " ", dlfile)
			self.downloadingSW = True

			self.drawProgressBarTimer.start(1000, True)	

	def getDownloadDir(self):
		dldir = config.swupdate.downloadlocation.value + "/update/" + config.misc.boxtype.value
		if not os.path.exists(dldir):
			os.system("mkdir -p " + dldir + "/cfe")

		return dldir

	def removeDownloadDir(self):
		dldir = config.swupdate.downloadlocation.value + "/update/" + config.misc.boxtype.value
		if os.path.exists(dldir):
			os.system("rm -rf " + dldir)

	def isFileSystemSupported(self, filesystem=None, hdd=None):
		supportedFileSystem = ["fat", "vfat"]
		if filesystem and filesystem in supportedFileSystem:
			return True
		elif hdd:
			try:
				mounts = open("/proc/mounts")
			except IOError:
				return False

			lines = mounts.readlines()
			mounts.close()

			for line in lines:
				if hdd.device in line:
					for fs in supportedFileSystem:
						if fs in line:
							return True
		return False

	def ok(self):
		# return if menu list is empty
		if self["menulist"].getCurrent() == None:
			return

		if self.downloadingSW:
			return

		if not self.showingHddList:
			if os.path.exists(config.swupdate.downloadlocation.value + "/update/" + config.misc.boxtype.value):
				self.session.openWithCallback(self.download, MessageBox, _("Overwrite S/W files during S/W upgrade?"))
			else:
				self.download()
		elif self.showingHddList:
			if not self.isFileSystemSupported(hdd=self["menulist"].getCurrent()[1]):
				self.session.open(MessageBox, _("Only file system \'fat\' and \'vfat\' are supported."), MessageBox.TYPE_ERROR, timeout=7)
			elif not self.freeSizeOk(self["menulist"].getCurrent()[1].findMount()):
				self.session.open(MessageBox, _("Not enough USB storage free space.\nPlease check USB storage device."), MessageBox.TYPE_ERROR, timeout=7)
				'''
				from Screens.HarddiskSetup import HarddiskSetup
				self.session.openWithCallback(self.timeout, HarddiskSetup, self["menulist"].getCurrent()[1],
					 action=self["menulist"].getCurrent()[1].createInitializeJob,
					 text=_("Initialize"),
					 question=_("Do you really want to initialize the device?\nAll data on the disk will be lost!"),
					 type=HarddiskSetup.HARDDISK_INITIALIZE)
				'''
			else:
				config.swupdate.downloadlocation.value = self["menulist"].getCurrent()[1].findMount()
				self.drawMenu()

	def up(self):
		self["menulist"].up()

		self.showHddInfo()

	def down(self):
		self["menulist"].down()

		self.showHddInfo()

	def showHddInfo(self):
		if not self.showingHddList:
			self["prog"].setText(_(" "))
		else:
			desc = self["menulist"].getCurrent()[1].findMount()
			desc += " - "
			desc += self["menulist"].getCurrent()[1].bus()

			cap = self["menulist"].getCurrent()[1].capacity()
			if cap != "":
				desc += " (" + cap + ")"

			free = "free"
			stat = os.statvfs(self["menulist"].getCurrent()[1].findMount())
			mbFree = (stat.f_bfree/1024) * (stat.f_bsize/1024)
			if mbFree < 1000:
				free += " %d MB" % mbFree
			else:
				free += " %d.%3d GB" % (mbFree/1024, mbFree%1024)
			desc += " - " + free

			self["prog"].setText(_(desc))


