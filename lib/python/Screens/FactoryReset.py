from Screens.MessageBox import MessageBox

'''
class FactoryReset(MessageBox):
	def __init__(self, session):
		MessageBox.__init__(self, session, _("When you do a factory reset, you will lose ALL your configuration data\n"
			"(including bouquets, services, satellite data ...)\n"
			"After completion of factory reset, your receiver will restart automatically!\n\n"
			"Really do a factory reset?"), MessageBox.TYPE_YESNO)
		self.skinName = "MessageBox"
'''
# [iq
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import PinInput
from Screen import Screen
from Components.config import config
from Tools.BoundFunction import boundFunction
import os 

from os import system, _exit

class FirstInstall(Screen):
	skin = """
		<screen name="FirstInstall" position="center,center" size="560,150" title="Default Install">
			<widget name="text1" position="10,20" zPosition="1" size="550,30" font="Regular;19" halign="left" valign="center" />
			<ePixmap alphatest="on" pixmap="skin_default/buttons/r_buttons/r_red.png" position="10,110" size="140,40"/>
			<ePixmap alphatest="on" pixmap="skin_default/buttons/r_buttons/r_blue.png" position="410,110" size="140,40"/>
			<widget backgroundColor="buttonRed" font="Regular;20" halign="center" position="10,110" render="Label" size="140,40" source="key_red" transparent="1" valign="center" zPosition="1"/>
			<widget backgroundColor="buttonBlue" font="Regular;20" halign="center" position="410,110" render="Label" size="140,40" source="key_blue" transparent="1" valign="center" zPosition="1"/>
        </screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("No"))
		self["key_blue"] = StaticText(_("Yes"))
		self["text1"] = Label(_("Are you sure you want to install default channel?"))

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyCancel,
		}, -2)

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"red": (self.keyCancel, _("no install")),
			"blue": (self.installchannel, _("install")),
		})

	def installchannel(self):
		self.hide()
		system("/etc/def_inst/install; mv /etc/def_inst /etc/.def_inst")
		self.session.open(MessageBox, _("Reloading bouquets and services..."), type = MessageBox.TYPE_INFO, timeout = 15, default = False)
		from enigma import eDVBDB
		eDVBDB.getInstance().reloadBouquets()
		eDVBDB.getInstance().reloadServicelist()
		self.close()

	def keyCancel(self):
		system("/etc/def_inst/not_install; mv /etc/def_inst /etc/.def_inst");
		self.close()


class ProtectedScreen2:
	def __init__(self):
		if self.isProtected():
			self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList = [self.protectedWithMasterPin(), self.protectedWithPin()], triesEntry = self.getTriesEntry(), title = self.getPinText(), windowTitle = _("Enter pin code")))

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def getPinText(self):
		return _("Please enter the correct pin code")

	def isProtected(self):
		True

	def protectedWithMasterPin(self):
		return config.ParentalControl.mastersetuppin.value

	def protectedWithPin(self):
		return config.ParentalControl.setuppin.value

	def pinEntered(self, result):
		if result is None:
			self.close(False)
		elif not result:
			self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)

class FactoryReset(ChoiceBox, Screen, ProtectedScreen2):
	def __init__(self, session):
		Screen.__init__(self, session)

		self.list = [(_("cancel factory reset"), "CALLFUNC", self.quitMainloopScreen),
		(_("do factory reset"), "CALLFUNC", self.quitMainloopScreen),
		(_("do full factory reset"), "CALLFUNC", self.quitMainloopScreen) ]

		ChoiceBox.__init__(self, session, _("When you do a factory reset,"
			"you will lose your configuration data\n"
			"(including bouquets, services...)\n"
			"Really do a factory reset?"), self.list)

		ProtectedScreen2.__init__(self)

	def quitMainloopScreen(self, ret):
		retval = {"cancel factory reset":None, "do factory reset":65, "do full factory reset":64}
		if retval[ret[0]]:
			from Screens.Standby import QuitMainloopScreen
			from enigma import quitMainloop
			self.quitScreen = self.session.instantiateDialog(QuitMainloopScreen,retvalue=retval[ret[0]])
			self.quitScreen.show()
			quitMainloop(retval[ret[0]])

		self.close()

	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and config.ParentalControl.configured.value

from Components.config import ConfigSubsection,ConfigInteger,getConfigListEntry, ConfigSelection, ConfigTextLeft, ConfigPassword
from Components.ConfigList import ConfigListScreen 
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText

class ChangePW(ConfigListScreen, Screen):
	skin = """
		<screen name="ChangePW" position="center,center" size="620,250" title="Box Password Change">
			<widget name="step" position="10,0" zPosition="1" size="600,30" font="Regular;20" halign="left" valign="center" />
			<widget name="state" position="10,30" zPosition="1" size="600,30" font="Regular;20" halign="left" valign="center" />
			<widget name="config" position="10,90" size="600,80" scrollbarMode="showOnDemand" />
			<widget name="text" position="10,160" zPosition="1" size="600,40" font="Regular;20" halign="center" valign="center" />
			<ePixmap alphatest="on" pixmap="skin_default/buttons/key_red.png" position="10,210" size="140,40"/>
			<ePixmap alphatest="on" pixmap="skin_default/buttons/key_yellow.png" position="324,210" size="140,40"/>
			<ePixmap alphatest="on" pixmap="skin_default/buttons/key_blue.png" position="470,210" size="140,40"/>
			<widget font="Regular;20" halign="center" position="10,210" render="Label" size="140,40" source="key_red" transparent="1" valign="center" zPosition="1"/>
			<widget font="Regular;20" halign="center" position="324,210" render="Label" size="140,40" source="key_yellow" transparent="1" valign="center" zPosition="1"/>
			<widget font="Regular;20" halign="center" position="470,210" render="Label" size="140,40" source="key_blue" transparent="1" valign="center" zPosition="1"/>
        </screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)

		self["key_red"] = StaticText(_("Close"))
		self["key_yellow"] = StaticText(_("Delete"))
		self["key_blue"] = StaticText(_("OK"))
		self["text"] = Label(_(""))
		self["state"] = Label(_(""))
		self["step"] = Label(_(""))

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.keyCancel,
		}, -2)
		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
		{
			"red": (self.close, _("exit")),
			"yellow": (self.DeleteGo, _("password set to blank")),
			"blue": (self.ChangeGo, _("making new password for telnet and ftp")),
		})

		self.hideDeleteButton = False
		if self.checkPassword("root", ""):
			self.hideDeleteButton = True

		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.pw = ConfigSubsection()
		self.login = 0
		self.createConfig()
		self.createSetup()
		self.timeout=8
		self.reset = False

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def checkPassword(self, user, password):
		import crypt, pwd
		try:
			pw1 = pwd.getpwnam(user)[1]
			pw2 = crypt.crypt(password, pw1)
			return pw1 == pw2
		except KeyError:
			return 0 # no such user

	def DeleteGo(self):
		if self.hideDeleteButton:
			pass
		else:
			import os
			self.pw.oldenter.value=self.pw.oldenter.value.rstrip()

			print "# checking current password :", self.pw.oldenter.value
			if self.checkPassword("root", self.pw.oldenter.value):
				print "password is current"
				self.reset = True
			else:
				msg=_("Wrong password ('%s')" % (self.pw.oldenter.value))
				self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, self.timeout)

			if self.reset:
				print " new passwd"
				os.system("(echo '%s';sleep 1;echo '%s';) | passwd" % ("", "") )
				msg  = _("Password updated successfully\nSet new PW (blank)")
				self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, self.timeout)
				self.close()
			else:
				self.createConfig()
				self.createSetup()

	def ChangeGo(self):
		import os
		if self.login == 0:
			self.pw.oldenter.value=self.pw.oldenter.value.rstrip()

			print "# checking current password :", self.pw.oldenter.value, type(self.pw.oldenter.value)
			if self.checkPassword("root", self.pw.oldenter.value):
				print "password is current"
				self.login = 1
			else:
				msg=_("Wrong password ('%s')" % (self.pw.oldenter.value))
				self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, self.timeout)

			self.createConfig()
			self.createSetup()
		else:
			print "new password",self.pw.enter.value
			self.pw.enter.value=self.pw.enter.value.rstrip()

			if self.pw.enter.value == "" :
				msg  = _("Password updated successfully\nSet new PW (blank)")
			else:
				msg  = _("Password updated successfully\nSet new PW ('%s')" % (self.pw.enter.value))
			self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, self.timeout)

			print " new passwd"
			os.system("(echo '%s';sleep 1;echo '%s';) | passwd" % (self.pw.enter.value, self.pw.enter.value) )
			self.close()

	def keyCancel(self):
		self.close()

	def createConfig(self):
		#self.pw.enter = ConfigInteger(default = 0000, limits = (1, 9999999999))
		if self.login == 0:
			self.pw.oldenter = ConfigTextLeft("", 20)
			self.pw.oldenter.setUseableChars(u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
		else:
			self.pw.enter = ConfigTextLeft("", 20)
			self.pw.enter.setUseableChars(u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

	def createSetup(self):
		self.list = []

		if self.login == 0:
			self["step"].setText(_("#Step 1"))
			if self.hideDeleteButton:
				self["key_yellow"] = StaticText(_(" "))
				self["text"].setText(_("Press blue button after entering current PW to change PW"))
			else:
				self["key_yellow"] = StaticText(_("Delete"))
				self["text"].setText(_("Press yellow button after entering current PW to delete PW\nPress blue button after entering current PW to change PW"))

			self.list.append(getConfigListEntry(_('Enter current password :'), self.pw.oldenter))
			self["state"].setText(_("Insert current PW with characters (0-9, a-z, A-Z)"))
		else:
			self["step"].setText(_("#Step 2"))
			if self.hideDeleteButton:
				self["key_yellow"] = StaticText(_(" "))
				self["text"].setText(_("Press blue button after entering new PW to change PW"))
			else:
				self["key_yellow"] = StaticText(_("Delete"))
				self["text"].setText(_("Press yellow button to delete PW\nPress blue button after entering new PW to change PW"))

			self.list.append(getConfigListEntry(_('Enter new password :'), self.pw.enter))
			self["state"].setText(_("Insert new PW with characters (0-9, a-z, A-Z)"))

		self["config"].list = self.list
		self["config"].l.setList(self.list)
# iq]

