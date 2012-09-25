# [iq]
from Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import ConfigSubsection,ConfigInteger,getConfigListEntry, ConfigSelection, ConfigTextLeft, ConfigPassword, config
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from os import system

class PasswordBox(ConfigListScreen, Screen):
	skin = """
		<screen name="PasswordBox" position="center,center" size="520,250" title="Check Password">
			<widget name="state" position="10,30" zPosition="1" size="500,30" font="Regular;20" halign="left" valign="center" />
			<widget name="config" position="10,90" size="500,80" scrollbarMode="showOnDemand" />
			<widget name="text" position="10,170" zPosition="1" size="500,40" font="Regular;20" halign="center" valign="center" />
			<ePixmap alphatest="on" pixmap="%s/buttons/red.png" position="10,210" size="140,40"/>
			<ePixmap alphatest="on" pixmap="%s/buttons/blue.png" position="370,210" size="140,40"/>
			<widget font="Regular;20" halign="center" position="10,210" render="Label" size="140,40" source="key_red" transparent="1" valign="center" zPosition="1"/>
			<widget font="Regular;20" halign="center" position="380,210" render="Label" size="140,40" source="key_blue" transparent="1" valign="center" zPosition="1"/>
        </screen>""" % (("ViX_HD_Common" if "ViX" in config.skin.primary_skin.value.split("/")[0] else "skin_default"), 
		("ViX_HD_Common" if "ViX" in config.skin.primary_skin.value.split("/")[0] else "skin_default"))
				#( config.skin.primary_skin.value.split("/")[0], config.skin.primary_skin.value.split("/")[0] )
	def __init__(self, session):
		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("Close"))
		self["key_blue"] = StaticText(_("OK"))
		self["text"] = Label(_(""))
		self["state"] = Label(_(""))

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyCancel,
		}, -2)
		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"red": (self.close, _("exit")),
			"blue": (self.checkGo, _("check password")),
		})

		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.pw = ConfigSubsection()
		self.createConfig()
		self.createSetup()
		self.timeout=8

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def checkGo(self):
		print "#checking password :",self.pw.enteredPassword.value
		self.pw.enteredPassword.value=self.pw.enteredPassword.value.rstrip()

		if self.checkPassword("root", self.pw.enteredPassword.value):
			self.close(True)
		else:
			msg=_("Wrong password ('%s')" % (self.pw.enteredPassword.value))
			self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, self.timeout)
			self.createConfig()
			self.createSetup()

	def keyCancel(self):
		self.close(False)

	def createConfig(self):
		self.pw.enteredPassword = ConfigTextLeft("", 20)
		self.pw.enteredPassword.setUseableChars(u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

	def createSetup(self):
		self.list = []
		self["text"].setText(_("Press blue button(OK) after entering current password"))
		self.list.append(getConfigListEntry(_('Enter password :'), self.pw.enteredPassword))
		self["state"].setText(_("Enter password with characters (0-9, a-z, A-Z)"))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def checkPassword(self, user, password):
		import crypt, pwd
		try:
			pw1 = pwd.getpwnam(user)[1]
			pw2 = crypt.crypt(password, pw1)
			return pw1 == pw2
		except KeyError:
			return 0 # no such user


