from Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
import os, fcntl

class ChangeRCU(Screen, ConfigListScreen):
	skin = """
		<screen name="ChangeRCU" position="center,center" size="500,300" title="Change RCU" >
			<widget name="security" position="10,10" size="540,22" valign="center" font="Regular;22" />
			<widget source="rcu_sel" render="Listbox" position="10,80" size="480,220" >
				<convert type="StringList" />
			</widget>
		</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, [])

		self["setupActions"] = ActionMap(["OkCancelActions"],
		{
			"cancel": self.keyCancel,
			"ok": self.ok,
		}, -1)
		
		self.rculist = []

		# keep order
		self.rculist.append("RCU for TM-2T [ver1.0]")		# 1
		self.rculist.append("RCU for TM-TWIN-OE[ver1.0]")	# 2
		self.rculist.append("RCU for IOS-100HD[ver1.0]")	# 3
		self.rculist.append("RCU for TM-SINGLE[ver1.0]")	# 4

		self.rcuMenuList = []
		for rcu in self.rculist:
			self.rcuMenuList.append("    " + rcu)

		self["rcu_sel"] = List(self.rcuMenuList)

	def keyCancel(self):
		self.close()
	
	def ok(self):
		index = self["rcu_sel"].getIndex()
		self.rcuMenuList = []
		for rcu in self.rculist:
			if index == self.rculist.index(rcu):
				self.rcuMenuList.append(">>  " + rcu)
			else:
				self.rcuMenuList.append("    " + rcu)
		self["rcu_sel"].setList(self.rcuMenuList)

		device = os.open("/dev/RCProtocol", os.O_RDWR)
		fcntl.ioctl(device, 7, index + 1)
		os.close(device)

		savefile = open("/etc/.rcu", "w+");
		savefile.write("%d" % (index + 1))
		savefile.close()
		## TODO : select rcu Key Load


from Tools.HardwareInfo import HardwareInfo
from Screens.MessageBox import MessageBox
from enigma import eTimer
class ChangeRCUWithoutRCU():
	def __init__(self):
		# support only tm models
		self.devices = { "tm2toe":1, "tmtwinoe":2, "tmsingle":4 }
		self.models = { 1:"TM-2T", 2:"TM-Twin", 4:"TM-Single" }
		self.rcu = self.devices.get(HardwareInfo().get_device_name())
		self.rcuSaveFile = "/etc/.rcu"
		if os.path.exists(self.rcuSaveFile):
			fd = open(self.rcuSaveFile, "r")
			try:
				if int(fd.readline().strip()) in self.devices.values():
					self.rcu = int(fd.readline().strip()) 
			except:
				pass

		self.menuKeyCount = 0

		self.resetMenuKeyCountTimer = eTimer()
		self.resetMenuKeyCountTimer.callback.append(self.resetMenuKeyCount)

	def resetMenuKeyCount(self):
		# if not pressed menu key in 1000ms, reset count
		self.menuKeyCount = 0

	def countMenuKey(self):	
		if self.rcu and HardwareInfo().get_device_name() in self.devices.keys():
			self.resetMenuKeyCountTimer.stop()
			self.menuKeyCount += 1
			if self.menuKeyCount == 5:
				self.switchRCU()
			else:
				# if not pressed menu key in 1000ms, reset count
				self.resetMenuKeyCountTimer.start(1000)

	def switchRCU(self):
		self.menuKeyCount = 0

		# skip non tm rcu
		self.rcu += 1
		if self.rcu == 3:
			self.rcu += 1
		elif self.rcu > 4:
			self.rcu = 1

		rcDevice = os.open("/dev/RCProtocol", os.O_RDWR)
		fcntl.ioctl(rcDevice, 7, self.rcu)
		os.close(rcDevice)

		fd = open(self.rcuSaveFile, "w+");
		fd.write("%d" % self.rcu)
		fd.close()

#		self.session.openWithCallback(self.showVfdMessage, MessageBox, (_("Warning :\n Remote Controller has been set to %s" % self.models.get(self.rcu))), MessageBox.TYPE_WARNING, timeout=7)
		from Tools import Notifications
		Notifications.AddNotificationWithCallback(self.showVfdMessage, MessageBox, (_("Warning :\n Remote Controller has been set to %s" % self.models.get(self.rcu))), MessageBox.TYPE_WARNING, timeout=7)

	def showVfdMessage(self, ret):
		os.system("echo \"RCU: %s\" > /proc/stb/lcd/show_txt" % self.models.get(self.rcu))


def SetPrivateRCU():
	savefile = "/etc/.rcu"
	if os.path.exists(savefile):
		fd = open(savefile, "r")
		rcuType = -1
		try:
			rcuType = int(fd.readline().strip())
		except:
			pass
		fd.close()

		if rcuType in (1, 2, 3, 4):
			device = os.open("/dev/RCProtocol", os.O_RDWR)
			fcntl.ioctl(device, 7, rcuType)
			os.close(device)

