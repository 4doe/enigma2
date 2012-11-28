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
			<widget name="text" position="0,30" zPosition="1" size="560,260" font="Regular;20" halign="center" valign="center" />
			<widget name="top" position="10,30" zPosition="2" size="540,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
			<eLabel backgroundColor="#4E5664" position="13,72" size="534,2" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="13,275" size="534,2" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="13,72" size="2,204" zPosition="1"/>
			<eLabel backgroundColor="#4E5664" position="547,72" size="2,204" zPosition="1"/>
			<widget name="menulist" position="15,75" scrollbarMode="showOnDemand" size="530,200" zPosition="10"/>
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
		self.imageInfo = { self.INTERNET_UPDATE : { "title" : "SW Update - "+lan, "imagedir" : "K3/"+modelDir+"_REL" },
			self.INTERNET_SR_UPDATE : { "title" : "SR SW Update - "+lan, "imagedir" : "K3/"+modelDir+"SR_REL" },
			self.INTERNET_UPDATE_BETA : { "title" : "SW Update (BETA) - "+lan, "imagedir" : "K3/"+modelDir },
			self.INTERNET_SR_UPDATE_BETA : { "title" : "SR SW Update (BETA) - "+lan, "imagedir" : "K3/"+modelDir+"SR" }
		}
		self.setTitle(self.imageInfo[self.type]["title"])

		self.swList = []
		self["menulist"] = MenuList(self.swList)
		self["menulist"].hide()
		self["percent"] = Label(_(" "))
		self["run"] = Label(_(" "))
		self["prog"] = Label(_(" "))
		self["top"] = Label(_(" "))
		self["bottom"] = Label(_(" "))
		self["text"] = Label(_("Downloading list information. Please wait..."))

		self["actions"] = ActionMap(["MinuteInputActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"up": self.up,
				"down": self.down,
			},-1)

		self.requiredSize = -1
		self.serverAlive = False
		self.downloadingSW = False
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
				self.downloadedSW = {}
			elif num < 100:
				self.drawProgressBarTimer.start(1000, True)	
			elif num == 100:
				self.drawProgressBarTimer.stop()
				MiniFTP_Thread.getInstance().Stop_Thread();
				self.downloadingSW = False

				if self.downloadedSWSizeOk():
#					self.downloadBurn()
					self.session.openWithCallback(self.downloadBurn, MessageBox, _("Downloading Finished!!\nDo you really want to update \nthe file \"%s\"?") % self["menulist"].getCurrent())
				else:
					self.session.open(MessageBox, _("Failed while checking downloaded SW!\nTry again please."), MessageBox.TYPE_ERROR)
					self.downloadCancel(True)

		config.progress = NoSave(ConfigSelectionNumber(-1, 100, 1, default = -1))
		config.progress.addNotifier(progressBar, False)
		config.progress.addNotifier(progressAction, False)

		self.checkEnvTimer.start(1000, True)

	def downloadedSWSizeOk(self):
		for sw in self.downloadedSW.keys():
			if self.downloadedSW[sw][1] != os.path.getsize(self.downloadedSW[sw][0]):
				return False
		return True

	def checkEnv(self):
		# server check
		if 0 == MiniFTP_Thread.getInstance().Alive_Check(0, self.SERVER_DNS):
			self.serverAlive = True
			self.loadSWList()
		else:
			self.serverAlive = False
			self.swList = []

		# draw menu
		self.drawMenu()

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

	def drawMenu(self):
		if not self.serverAlive:
			self["menulist"].hide()
			self["text"].setText(_("No Internet\nPress \"EXIT\" for exit"))
			self["text"].show()
		elif not self.swList:
			self["menulist"].hide()
			self["text"].setText(_("Empty (update file is not ready)\nPress \"EXIT\" for exit"))
			self["text"].show()
		else:
			self["top"].setText(_("Please select the software version to upgrade to"))
			self["bottom"].setText(_("Please select version to upgrade or exit to abort"))
			self["text"].hide();
			self["menulist"].l.setList(self.swList)
			self["menulist"].show();

	def drawProgressBar(self):
		config.progress.value = str(MiniFTP_Thread.getInstance().GetState())

	def downloadBurn(self, val):
		if not val:
			config.progress.value = str(-1)
			self.drawMenu()
#			self.close()
		else:
			if os.path.exists("/tmp/update_files.tar"):
				from Components.About import about
				from Screens.Console import Console

				cmds = []
				cmds.append("tar xf /tmp/update_files.tar -C /tmp/")
				cmds.append("if [ -e /tmp/oe_kernel.bin ]; then flash_eraseall -j /dev/mtd6; nandwrite -p /dev/mtd6 /tmp/oe_kernel.bin; fi")
				cmds.append("if [ -e /tmp/bcmlinuxdvb.ko ]; then mv /tmp/bcmlinuxdvb.ko %s; fi" % 
						("/lib/modules/" + about.getKernelVersionString() + "/extra/bcmlinuxdvb.ko"))
				cmds.append("if [ \"`find /tmp/ -name enigma2*ipk`\" != \"\" ]; then opkg install `ls /tmp/enigma2*ipk`; fi")
				cmds.append("sync")
				self.session.openWithCallback(self.reboot, Console, title = _("Update is running..."), cmdlist = cmds, closeOnSuccess = True)

	def reboot(self, val = 2):	# 2 - reboot
		self.hide()
		from enigma import quitMainloop
		from Screens.Standby import QuitMainloopScreen
		self.quitScreen = self.session.instantiateDialog(QuitMainloopScreen, retvalue=val)
		self.quitScreen.show()
		quitMainloop(val)

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

	def download(self, val=True):
		if val:
			self["menulist"].hide()
			self["text"].setText(_("Downloading \"%s\"\nIf you want to exit, press \"EXIT\" key in rcu") % self["menulist"].getCurrent())
			self.swPath = self.imageInfo[self.type]["imagedir"] + "/" + self["menulist"].getCurrent()
			self["text"].show()

			dlfile = "/tmp/update_files.tar"
			self.downloadedSW[self.swPath] = (dlfile, self.getSWSize(self.swPath))
			MiniFTP_Thread.getInstance().DownloadFile(0, self.iface, self.SERVER_DNS, self.swPath, "anonymous", " ", dlfile)
			self.downloadingSW = True

			self.drawProgressBarTimer.start(1000, True)	

	def ok(self):
		# return if menu list is empty
		if self["menulist"].getCurrent() == None:
			return

		if self.downloadingSW:
			return

		self.download()

	def up(self):
		self["menulist"].up()

	def down(self):
		self["menulist"].down()

