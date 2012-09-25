from config import config, ConfigSelection, ConfigSubsection, ConfigOnOff, ConfigSlider
from enigma import eRFmod
from Components.SystemInfo import SystemInfo

# CHECK ME.
RFMOD_CHANNEL_MIN = 21
RFMOD_CHANNEL_MAX = 69 + 1

class RFmod:
	def __init__(self):
		pass

	def setFunction(self, value):
		eRFmod.getInstance().setFunction(not value)
	def setTestmode(self, value):
		eRFmod.getInstance().setTestmode(value)
	def setSoundFunction(self, value):
		eRFmod.getInstance().setSoundFunction(not value)
	def setSoundCarrier(self, value):
		eRFmod.getInstance().setSoundCarrier(value)
	def setChannel(self, value):
		eRFmod.getInstance().setChannel(value)
	def setFinetune(self, value):
		eRFmod.getInstance().setFinetune(value)

def InitRFmod():
	detected = eRFmod.getInstance().detected()
	SystemInfo["RfModulator"] = detected
	if detected:
		config.rfmod = ConfigSubsection()
		# [ iq
		#config.rfmod.enable = ConfigOnOff(default=False)
		# iq]
		config.rfmod.enable = ConfigOnOff(default=True)
		config.rfmod.test = ConfigOnOff(default=False)
		config.rfmod.sound = ConfigOnOff(default=True)
		config.rfmod.soundcarrier = ConfigSelection(choices=[("4500","4.5 MHz"), ("5500", "5.5 MHz"), ("6000", "6.0 MHz"), ("6500", "6.5 MHz")], default="5500")
		# [iq
		#config.rfmod.channel = ConfigSelection(default = "36", choices = ["%d" % x for x in range(RFMOD_CHANNEL_MIN, RFMOD_CHANNEL_MAX)])
		config.rfmod.channel = ConfigSelection(default = "40", choices = ["%d" % x for x in range(RFMOD_CHANNEL_MIN, RFMOD_CHANNEL_MAX)])
		# iq]
		config.rfmod.finetune = ConfigSlider(default=5, limits=(1, 10))

		iRFmod = RFmod()

		def setFunction(configElement):
			iRFmod.setFunction(configElement.value);
		def setTestmode(configElement):
			iRFmod.setTestmode(configElement.value);
		def setSoundFunction(configElement):
			iRFmod.setSoundFunction(configElement.value);
		def setSoundCarrier(configElement):
			iRFmod.setSoundCarrier(configElement.index);
		def setChannel(configElement):
			iRFmod.setChannel(int(configElement.value));
		def setFinetune(configElement):
			iRFmod.setFinetune(configElement.value - 5);

		# this will call the "setup-val" initial
		config.rfmod.enable.addNotifier(setFunction);
		config.rfmod.test.addNotifier(setTestmode);
		config.rfmod.sound.addNotifier(setSoundFunction);
		config.rfmod.soundcarrier.addNotifier(setSoundCarrier);
		config.rfmod.channel.addNotifier(setChannel);
		config.rfmod.finetune.addNotifier(setFinetune);

# [iq - for rf menu
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigClock,getConfigListEntry,ConfigBoolean
class RFSetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# for the skin: first try RFmod, then Setup, this allows individual skinning
		self.skinName = ["RFSetup", "Setup" ]
		self.setup_title = _("RF output")
		self.onChangedEntry = [ ]

		self.list = [ ]
		ConfigListScreen.__init__(self, self.list, session = session, on_change = self.changedEntry)
		from Components.ActionMap import ActionMap
		self["actions"] = ActionMap(["SetupActions"], 
			{
				"cancel": self.keyCancel,
				"save": self.apply,
			}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)
	
        def changedEntry(self):
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	
        def apply(self):
	        self.keySave()
	
        def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())


	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def createSetup(self):
		self.list.append(getConfigListEntry(_("Modulator"), config.rfmod.enable))
		self.list.append(getConfigListEntry(_("Test mode"), config.rfmod.test))
		self.list.append(getConfigListEntry(_("Sound"), config.rfmod.sound))
		self.list.append(getConfigListEntry(_("Soundcarrier"), config.rfmod.soundcarrier))
		self.list.append(getConfigListEntry(_("Channel"), config.rfmod.channel))
		self.list.append(getConfigListEntry(_("Finetune"), config.rfmod.finetune))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def confirm(self, confirmed):
		self.keySave()
		configfile.save()
# iq]
