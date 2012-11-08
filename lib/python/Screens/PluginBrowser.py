from Screen import Screen
from Components.Language import language
from enigma import eConsoleAppContainer, eDVBDB

from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.Label import Label
from Components.Harddisk import harddiskmanager
from Components.Sources.StaticText import StaticText
from Components import Ipkg
from Components.config import config # [iq]
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.Console import Console as SwapConsole		# [iq]
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Tools.LoadPixmap import LoadPixmap

from time import time
import os

def languageChanged():
	plugins.clearPluginList()
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

class PluginBrowserSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["entry"] = StaticText("")
		self["desc"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, name, desc):
		self["entry"].text = name
		self["desc"].text = desc


class PluginBrowser(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		self.firsttime = True

# [iq
		self.mtdSwap = 0

		self.pathForSwap = None
		if not self.mtdSwap:

#			hddList = harddiskmanager.HDDList()
#			for h in hddList:
#				if "/media/hdd" in h[1].findMount():
#					self.hddForSwap = h[1].findMount()
#					break
#
#				devpath = "/sys/block/" + h[1].device[:3]
#				removable = bool(int(readFile(devpath + "/removable")))
#				if not removable:
#					if not self.hddForSwap:
#					self.hddForSwap = h[1].findMount()

			from Components.Harddisk import isFileSystemSupported
			for partition in harddiskmanager.getMountedPartitions():
				if "/media/hdd" in partition.mountpoint:
					self.pathForSwap = partition.mountpoint
					break

				if partition.device and isFileSystemSupported(partition.filesystem()):
					if not self.pathForSwap:
						self.pathForSwap = partition.mountpoint

		self.Console = SwapConsole()
		self.swapOn()
# iq]

		self["red"] = Label(_("Remove Plugins"))
		self["green"] = Label(_("Download Plugins"))
		
		self.list = []
		self["list"] = PluginList(self.list)
		if config.usage.sort_pluginlist.value:
			self["list"].list.sort() # sort

# NOTE : plugins sort
		
		self["actions"] = ActionMap(["WizardActions"],
		{
			"ok": self.save,
			"back": self.close,
		})
		self["PluginDownloadActions"] = ActionMap(["ColorActions"],
		{
			"red": self.delete,
			"green": self.download
		})

		self.onFirstExecBegin.append(self.checkWarnings)
		self.onShown.append(self.updateList)
		self.onChangedEntry = []
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.saveListsize)
# [iq
#		self.onLayoutFinish.append(self.swapOn)
		self.onClose.append(self.swapOff)
	
	def swapOn(self):
		if self.mtdSwap:
			mtd = 3
			self.Console.ePopen("mkswap /dev/mtdblock%d; swapon /dev/mtdblock%d" % (mtd, mtd), self.swapFinished) 
		else:
			if self.pathForSwap:
				command = "if [ ! -e %s/.swapfile ]; then dd if=/dev/zero of=%s/.swapfile bs=1024 count=102400; fi" % (self.pathForSwap, self.pathForSwap)
#				command = "dd if=/dev/zero of=%s/.swapfile bs=1024 count=102400; fi" % self.pathForSwap
				command += "; mkswap %s/.swapfile" % self.pathForSwap
				command += "; swapon %s/.swapfile" % self.pathForSwap
				self.Console.ePopen(command, self.swapFinished) 

	def swapOff(self):
		if self.mtdSwap:
			mtd = 3
			self.Console.ePopen("swapoff /dev/mtdblock%d; flash_eraseall -jq /dev/mtd%d" % (mtd, mtd), self.swapFinished) 
		else:
			if self.pathForSwap:
				command = "swapoff %s/.swapfile" % self.pathForSwap
#				command += "; rm -f %s/.swapfile" % self.pathForSwap
				self.Console.ePopen(command) 

	def swapFinished(self, result, retval, extra_args):
		pass
# iq]

	def saveListsize(self):
		listsize = self["list"].instance.size()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()

	def createSummary(self):
		return PluginBrowserSummary
		
	def selectionChanged(self):
		item = self["list"].getCurrent()
		if item:
			p = item[0]
			name = p.name
			desc = p.description
		else:
			name = "-"
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)
	
	def checkWarnings(self):
		if len(plugins.warnings):
			text = _("Some plugins are not available:\n")
			for (pluginname, error) in plugins.warnings:
				text += _("%s (%s)\n") % (pluginname, error)
			plugins.resetWarnings()
			self.session.open(MessageBox, text = text, type = MessageBox.TYPE_WARNING)

	def save(self):
		self.run()
	
	def run(self):
		plugin = self["list"].l.getCurrentSelection()[0]
		plugin(session=self.session)
		
	def updateList(self):
		self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
		self.list = [PluginEntryComponent(plugin) for plugin in self.pluginlist]
		self["list"].l.setList(self.list)

#  [iq 
	def delete(self):
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.REMOVE)
#		self.session.openWithCallback(self.PluginDownloadBrowserClosed, OldPluginDownloadBrowser, OldPluginDownloadBrowser.REMOVE)		# [iq]
	
	# NOTE : Download Menu Added
	# download1 : PLi Server
	# download2 : iQ Server

	def download(self):
		self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginDownloadBrowser, PluginDownloadBrowser.DOWNLOAD, self.firsttime)
		self.firsttime = False


	def PluginDownloadBrowserClosed(self):
		self.updateList()
		self.checkWarnings()

	def openExtensionmanager(self):
		if fileExists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/SoftwareManager/plugin.py")):
			try:
				from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
			except ImportError:
				self.session.open(MessageBox, _("The Softwaremanagement extension is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			else:
				self.session.openWithCallback(self.PluginDownloadBrowserClosed, PluginManager)

	# NOTE : iQ and PLi Server chooser function define.
	
	def doPliServer(self):
		res = 0
		cmd = 'rm -rf /etc/opkg/*.conf;tar xf /etc/.pli.conf.tar.gz -C /etc/opkg/;opkg update'
		res = os.system(cmd)
		if res != 0:
			print "# doPliServer update Error"
		else:
			print "# doPliServer update Success"

	def doiQServer(self):
		res = 0
		cmd = 'rm -rf /etc/opkg/*.conf;tar xf /etc/.iq.conf.tar.bz -C /etc/opkg/;opkg update'
		res = os.system(cmd)
		if res != 0:
			print "# doiQServer update Error"
		else:
			print "# doiQServer update Success"

class PluginDownloadBrowser(Screen):
	DOWNLOAD = 0
	REMOVE = 1
	PLUGIN_PREFIX = 'enigma2-plugin-'
	lastDownloadDate = None

	def __init__(self, session, type = 0, needupdate = True):
		Screen.__init__(self, session)
		
		self.type = type
		self.needupdate = needupdate
		
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
		
		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.install_settings_name = ''
		self.remove_settings_name = ''
		
		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		elif self.type == self.REMOVE:
			self["text"] = Label(_("Getting plugin information. Please wait..."))
		
		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions"], 
		{
			"ok": self.go,
			"back": self.requestClose,
		})
		if os.path.isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove' 
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install -force-defaults'
			self.ipkg_remove =  self.ipkg + ' remove' 

	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		sel = sel[0]
		if isinstance(sel, str): # category
			if sel in self.expanded:
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
		else:
			if self.type == self.DOWNLOAD:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to download\nthe plugin \"%s\"?") % sel.name)
			elif self.type == self.REMOVE:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to REMOVE\nthe plugin \"%s\"?") % sel.name)

	def requestClose(self):
		if self.plugins_changed:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		if self.reload_settings:
			self["text"].setText(_("Reloading bouquets and services..."))
			eDVBDB.getInstance().reloadBouquets()
			eDVBDB.getInstance().reloadServicelist()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.container.appClosed.remove(self.runFinished)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def resetPostInstall(self):
		try:
			del self.postInstallCall
		except:
			pass

	def installDestinationCallback(self, result):
		if result is not None:
			dest = result[1]
			if dest.startswith('/'):
				# Custom install path, add it to the list too
				dest = os.path.normpath(dest)
				extra = '--add-dest %s:%s -d %s' % (dest,dest,dest)
				Ipkg.opkgAddDestination(dest)
			else:
				extra = '-d ' + dest
			self.doInstall(self.installFinished, self["list"].l.getCurrentSelection()[0].name + ' ' + extra)
		else:
			self.resetPostInstall()

	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
				if self["list"].l.getCurrentSelection()[0].name.startswith("picons-"):
					supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts() 
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint)) 
					if candidates:
						from Components.Renderer import Picon
						self.postInstallCall = Picon.initPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install picons on"), list=candidates)
					return
				self.install_settings_name = self["list"].l.getCurrentSelection()[0].name
# iq [
#				if self["list"].l.getCurrentSelection()[0].name.startswith('settings-'):
				if self["list"].l.getCurrentSelection()[0].name.startswith('settings-') or self["list"].l.getCurrentSelection()[0].name.startswith('channel.'):
# ]
					self.check_settings = True
# iq [
#					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
					self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list_installed " + self.PLUGIN_PREFIX + "settings-* ; " + self.ipkg + Ipkg.opkgExtraDestinations() + " list_installed " + self.PLUGIN_PREFIX + "channel.*")
# ]
				else:
					self.runSettingsInstall()
			elif self.type == self.REMOVE:
				self.doRemove(self.installFinished, self["list"].l.getCurrentSelection()[0].name)

	def doRemove(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_remove + Ipkg.opkgExtraDestinations() + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def doInstall(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def runSettingsRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_settings_name)

	def runSettingsInstall(self):
		self.doInstall(self.installFinished, self.install_settings_name)

	def setWindowTitle(self):
		if self.type == self.DOWNLOAD:
			self.setTitle(_("Downloadable new plugins"))
		elif self.type == self.REMOVE:
			self.setTitle(_("Remove plugins"))

	def startIpkgListInstalled(self, pkgname = PLUGIN_PREFIX + '*'):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list_installed '%s'" % pkgname)

	def startIpkgListAvailable(self):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list '" + self.PLUGIN_PREFIX + "*'")

	def startRun(self):
		listsize = self["list"].instance.size()
		self["list"].instance.hide()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()
		if self.type == self.DOWNLOAD:
			if self.needupdate and not PluginDownloadBrowser.lastDownloadDate or (time() - PluginDownloadBrowser.lastDownloadDate) > 3600:
				# Only update from internet once per hour
				self.container.execute(self.ipkg + " update")
				PluginDownloadBrowser.lastDownloadDate = time()
			else:
				self.run = 1
				self.startIpkgListInstalled()
		elif self.type == self.REMOVE:
			self.run = 1
			self.startIpkgListInstalled()

	def installFinished(self):
		if hasattr(self, 'postInstallCall'):
			try:
				self.postInstallCall()
			except Exception, ex:
				print "[PluginBrowser] postInstallCall failed:", ex
			self.resetPostInstall()
		try:
			os.unlink('/tmp/opkg.conf')
		except:
			pass
		for plugin in self.pluginlist:
			if plugin[3] == self["list"].l.getCurrentSelection()[0].name:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if self["list"].l.getCurrentSelection()[0].name.startswith("settings-"):
			self.reload_settings = True
		else:
		 	if self["list"].l.getCurrentSelection()[0].name.startswith("channel."):
		 		self.reload_settings =True
			else:
				print "reload settings pass"
		self.expanded = []
		self.updateList()
		self["list"].moveToIndex(0)

	def runFinished(self, retval):
		if self.check_settings:
			self.check_settings = False
			self.runSettingsInstall()
			return
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			if self.type == self.DOWNLOAD:
				self.startIpkgListInstalled()
		elif self.run == 1 and self.type == self.DOWNLOAD:
			self.run = 2
			self.startIpkgListAvailable()
		else:
			if len(self.pluginlist) > 0:
				self.updateList()
				self["list"].instance.show()
			else:
				self["text"].setText("No new plugins found")

	def dataAvail(self, str):
		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		lines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			#remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""

		if self.check_settings:
			self.check_settings = False
			self.remove_settings_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runSettingsRemove, MessageBox, _('You already have a channel list installed,\nwould you like to remove\n"%s"?') % self.remove_settings_name)
			return

		for x in lines:
			plugin = x.split(" - ", 2)
			# 'opkg list_installed' only returns name + version, no description field
			if len(plugin) >= 2:
				if not plugin[0].endswith('-dev') and not plugin[0].endswith('-dbg'):
					if self.run == 1 and self.type == self.DOWNLOAD:
						if plugin[0] not in self.installedplugins:
							self.installedplugins.append(plugin[0])
					else:
						if plugin[0] not in self.installedplugins:
							if len(plugin) == 2:
								# 'opkg list_installed' does not return descriptions, append empty description
								plugin.append('')
							plugin.append(plugin[0][15:])

							self.pluginlist.append(plugin)
	
	def updateList(self):
		list = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/verticalline-plugins.png"))
		
		self.plugins = {}
		for x in self.pluginlist:
			split = x[3].split('-', 1)
			if len(split) < 2:
				continue
			if not self.plugins.has_key(split[0]):
				self.plugins[split[0]] = []

			self.plugins[split[0]].append((PluginDescriptor(name = x[3], description = x[2], icon = verticallineIcon), split[1], x[1]))

# NOTE : plugin list sort
		temp = self.plugins.keys() 
		if config.usage.sort_pluginlist.value:
			temp.sort()

#		for x in self.plugins.keys():
		for x in temp:
			if x in self.expanded:
				list.append(PluginCategoryComponent(x, expandedIcon, self.listWidth))
				list.extend([PluginDownloadComponent(plugin[0], plugin[1], plugin[2], self.listWidth) for plugin in self.plugins[x]])
			else:
				list.append(PluginCategoryComponent(x, expandableIcon, self.listWidth))
		self.list = list
		self["list"].l.setList(list)

language.addCallback(languageChanged)
# [iq]
from Components.ProgressBar import ProgressBar
class OldPluginDownloadBrowser(Screen):
	skin = """
	<screen name="OldPluginDownloadBrowser"	position="center,center" size="600,460" title="Downloadable plugins">
		<widget name="list" position="30,10" size="540,415" scrollbarMode="showOnDemand" backgroundColor="#263c59"/>
		<widget name="text" position="30,10" size="540,415" halign="center" valign="center" font="Regular;30" foregroundColor="yellow" backgroundColor="black" transparent="1"/>

		<widget name="percent" position="10,430" size="50,30" halign="center" valign="center" font="Regular;23" foregroundColor="white" />
		<widget name="free_progress" position="60,437" size="300,15" borderWidth="2" borderColor="white" pixmap="skin_default/progress_big.png" />
		<widget name="free_size" position="380,430" size="250,30" halign="left" valign="center" font="Regular;23" foregroundColor="white" />
	</screen>"""

	DOWNLOAD = 0
	REMOVE = 1
	PLUGIN_PREFIX = 'enigma2-plugin-'
	lastDownloadDate = None

	def __init__(self, session, type = 0, needupdate = True):
		Screen.__init__(self, session)

		self.type = type
		self.needupdate = needupdate
		
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun)
		self.onShown.append(self.setWindowTitle)
		
		self.list = []
		self["list"] = PluginList(self.list)
		self.pluginlist = []
		self.expanded = []
		self.installedplugins = []
		self.plugins_changed = False
		self.reload_settings = False
		self.check_settings = False
		self.check_bootlogo = False
		self.install_settings_name = ''
		self.remove_settings_name = ''
		
		if self.type == self.DOWNLOAD:
			self["text"] = Label(_("Downloading plugin information. Please wait..."))
		elif self.type == self.REMOVE:
			self["text"] = Label(_("Getting plugin information. Please wait..."))
		
		self.run = 0
		self.remainingdata = ""
		self["actions"] = ActionMap(["WizardActions"], 
		{
			"ok": self.go,
			"back": self.requestClose,
		})
		if os.path.isfile('/usr/bin/opkg'):
			self.ipkg = '/usr/bin/opkg'
			self.ipkg_install = self.ipkg + ' install'
			self.ipkg_remove =  self.ipkg + ' remove --autoremove' 
		else:
			self.ipkg = 'ipkg'
			self.ipkg_install = 'ipkg install -force-defaults'
			self.ipkg_remove =  self.ipkg + ' remove' 

	def go(self):
		sel = self["list"].l.getCurrentSelection()

		if sel is None:
			return

		sel = sel[0]
		if isinstance(sel, str): # category
			if sel in self.expanded:
				self.expanded.remove(sel)
			else:
				self.expanded.append(sel)
			self.updateList()
		else:
			if self.type == self.DOWNLOAD:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to download\nthe plugin \"%s\"?") % sel.name)
			elif self.type == self.REMOVE:
				self.session.openWithCallback(self.runInstall, MessageBox, _("Do you really want to REMOVE\nthe plugin \"%s\"?") % sel.name)

	def requestClose(self):
		if self.plugins_changed:
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		if self.reload_settings:
			self["text"].setText(_("Reloading bouquets and services..."))
			eDVBDB.getInstance().reloadBouquets()
			eDVBDB.getInstance().reloadServicelist()
			self.removeChInfoFromSettings()		# [iq]
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
		self.container.appClosed.remove(self.runFinished)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()

	def resetPostInstall(self):
		try:
			del self.postInstallCall
		except:
			pass

	def installDestinationCallback(self, result):
		if result is not None:
			dest = result[1]
			if dest.startswith('/'):
				# Custom install path, add it to the list too
				dest = os.path.normpath(dest)
				extra = '--add-dest %s:%s -d %s' % (dest,dest,dest)
				Ipkg.opkgAddDestination(dest)
			else:
				extra = '-d ' + dest
			self.doInstall(self.installFinished, self["list"].l.getCurrentSelection()[0].name + ' ' + extra)
		else:
			self.resetPostInstall()
				
	def runInstall(self, val):
		if val:
			if self.type == self.DOWNLOAD:
# [iq
				print "download"
				if not self.isFreeSizeOk(self["list"].l.getCurrentSelection()[0].name):
					noSpace="No more capacity in the Flash memory.. \nPlease remove some files in Plugins menu if you want to download new files."
					self.session.open(MessageBox, noSpace, type = MessageBox.TYPE_WARNING)
					return
# iq]
				if self["list"].l.getCurrentSelection()[0].name.startswith("picons-"):
					print "picons"
					supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts() 
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint)) 
					if candidates:
						from Components.Renderer import Picon
						self.postInstallCall = Picon.initPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install picons on"), list=candidates)
					return
				elif self["list"].l.getCurrentSelection()[0].name.startswith("lcdpicons-"):
					print "lcdpicons"
					supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'reiser', 'reiser4', 'jffs2', 'ubifs', 'rootfs'))
					candidates = []
					import Components.Harddisk
					mounts = Components.Harddisk.getProcMounts() 
					for partition in harddiskmanager.getMountedPartitions(False, mounts):
						if partition.filesystem(mounts) in supported_filesystems:
							candidates.append((partition.description, partition.mountpoint)) 
					if candidates:
						from Components.Renderer import LcdPicon
						self.postInstallCall = LcdPicon.initLcdPiconPaths
						self.session.openWithCallback(self.installDestinationCallback, ChoiceBox, title=_("Install lcd picons on"), list=candidates)
					return
				self.install_settings_name = self["list"].l.getCurrentSelection()[0].name
				self.install_bootlogo_name = self["list"].l.getCurrentSelection()[0].name
				if self["list"].l.getCurrentSelection()[0].name.startswith('settings-'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'settings-*')
# [iq
				elif self["list"].l.getCurrentSelection()[0].name.startswith('channel.'):
					self.check_settings = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'channel.*')
# iq]
				elif self["list"].l.getCurrentSelection()[0].name.startswith('bootlogo-'):
					print "bootlogo"
					self.check_bootlogo = True
					self.startIpkgListInstalled(self.PLUGIN_PREFIX + 'bootlogo-*')
				else:
					print "etc"
					self.runSettingsInstall()
			elif self.type == self.REMOVE:
				print "remove"
				self.doRemove(self.installFinished, self["list"].l.getCurrentSelection()[0].name + " --force-remove --force-depends")

	def doRemove(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_remove + Ipkg.opkgExtraDestinations() + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def doInstall(self, callback, pkgname):
		self.session.openWithCallback(callback, Console, cmdlist = [self.ipkg_install + " " + self.PLUGIN_PREFIX + pkgname, "sync"], closeOnSuccess = True)

	def runSettingsRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_settings_name)

	def runBootlogoRemove(self, val):
		if val:
			self.doRemove(self.runSettingsInstall, self.remove_bootlogo_name + " --force-remove --force-depends")

	def runSettingsInstall(self):
		self.doInstall(self.installFinished, self.install_settings_name)

	def setWindowTitle(self):
		if self.type == self.DOWNLOAD:
			self.setTitle(_("Install plugins"))
		elif self.type == self.REMOVE:
			self.setTitle(_("Remove plugins"))

	def startIpkgListInstalled(self, pkgname = PLUGIN_PREFIX + '*'):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list_installed '%s'" % pkgname)

	def startIpkgListAvailable(self):
		self.container.execute(self.ipkg + Ipkg.opkgExtraDestinations() + " list '" + self.PLUGIN_PREFIX + "*'")

	def startRun(self):
		listsize = self["list"].instance.size()
		self["list"].instance.hide()
		self.listWidth = listsize.width()
		self.listHeight = listsize.height()
		if self.type == self.DOWNLOAD:
			if self.needupdate and not PluginDownloadBrowser.lastDownloadDate or (time() - PluginDownloadBrowser.lastDownloadDate) > 3600:
				# Only update from internet once per hour
				self.container.execute(self.ipkg + " update")
				PluginDownloadBrowser.lastDownloadDate = time()
			else:
				self.run = 1
				self.startIpkgListInstalled()
		elif self.type == self.REMOVE:
			self.run = 1
			self.startIpkgListInstalled()

	def installFinished(self):
		if hasattr(self, 'postInstallCall'):
			try:
				self.postInstallCall()
			except Exception, ex:
				print "[PluginBrowser] postInstallCall failed:", ex
			self.resetPostInstall()
		try:
			os.unlink('/tmp/opkg.conf')
		except:
			pass
		for plugin in self.pluginlist:
			if plugin[3] == self["list"].l.getCurrentSelection()[0].name:
				self.pluginlist.remove(plugin)
				break
		self.plugins_changed = True
		if self["list"].l.getCurrentSelection()[0].name.startswith("settings-"):
			self.reload_settings = True
# [iq
#		if self["list"].l.getCurrentSelection()[0].name.startswith("channel."):
#			self.reload_settings = True
		if self["list"].l.getCurrentSelection()[0].name.startswith("channel."):
			self.reload_settings = True
		self.session.open(MessageBox, _("Reloading bouquets and services..."), type = MessageBox.TYPE_INFO, timeout = 15, default = False)
		eDVBDB.getInstance().reloadBouquets()
		eDVBDB.getInstance().reloadServicelist()
# iq]
		self.expanded = []
		self.updateList()
		self["list"].moveToIndex(0)

	def runFinished(self, retval):
		if self.check_settings:
			self.check_settings = False
			self.runSettingsInstall()
			return
		if self.check_bootlogo:
			self.check_bootlogo = False
			self.runSettingsInstall()
			return
		self.remainingdata = ""
		if self.run == 0:
			self.run = 1
			if self.type == self.DOWNLOAD:
				self.startIpkgListInstalled()
		elif self.run == 1 and self.type == self.DOWNLOAD:
			self.run = 2
			self.startIpkgListAvailable()
		else:
			if len(self.pluginlist) > 0:
				self.updateList()
				self["list"].instance.show()
			else:
				self["text"].setText("No new plugins found")

	def dataAvail(self, str):
		print "dataAvail"
		#prepend any remaining data from the previous call
		str = self.remainingdata + str
		#split in lines
		lines = str.split('\n')
		#'str' should end with '\n', so when splitting, the last line should be empty. If this is not the case, we received an incomplete line
		if len(lines[-1]):
			#remember this data for next time
			self.remainingdata = lines[-1]
			lines = lines[0:-1]
		else:
			self.remainingdata = ""

		# DEBUG ::: channel list 
		if self.check_settings:
			self.check_settings = False
			self.remove_settings_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runSettingsRemove, MessageBox, _('You already have a channel list installed,\nwould you like to remove\n"%s"?') % self.remove_settings_name)
			return

		if self.check_bootlogo:
			self.check_bootlogo = False
			self.remove_bootlogo_name = str.split(' - ')[0].replace(self.PLUGIN_PREFIX, '')
			self.session.openWithCallback(self.runBootlogoRemove, MessageBox, _('You already have a bootlogo installed,\nwould you like to remove\n"%s"?') % self.remove_bootlogo_name)
			return

		for x in lines:
			plugin = x.split(" - ", 2)
			# 'opkg list_installed' only returns name + version, no description field
			if len(plugin) >= 2:
				if not plugin[0].endswith('-dev') and not plugin[0].endswith('-dbg'):
					if self.run == 1 and self.type == self.DOWNLOAD:
						if plugin[0] not in self.installedplugins:
							self.installedplugins.append(plugin[0])
					else:
						if plugin[0] not in self.installedplugins:
							if len(plugin) == 2:
								# 'opkg list_installed' does not return descriptions, append empty description
								plugin.append('')
							plugin.append(plugin[0][15:])

							self.pluginlist.append(plugin)
	
	def updateList(self):
		list = []
		expandableIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expandable-plugins.png"))
		expandedIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/expanded-plugins.png"))
		verticallineIcon = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/verticalline-plugins.png"))
		
		self.plugins = {}
		for x in self.pluginlist:
			split = x[3].split('-', 1)
			if len(split) < 2:
				continue
			if not self.plugins.has_key(split[0]):
				self.plugins[split[0]] = []

			self.plugins[split[0]].append((PluginDescriptor(name = x[3], description = x[2], icon = verticallineIcon), split[1], x[1]))

		temp = self.plugins.keys()
		temp.sort()
		for x in temp:
			if x in self.expanded:
				list.append(PluginCategoryComponent(x, expandedIcon, self.listWidth))
				list.extend([PluginDownloadComponent(plugin[0], plugin[1], plugin[2], self.listWidth) for plugin in self.plugins[x]])
			else:
				list.append(PluginCategoryComponent(x, expandableIcon, self.listWidth))
		self.list = list
		self["list"].l.setList(list)

		self["text"].setText(_(" "))
		self.updateNandStatus()

# [iq]
	def updateNandStatus(self):
		partitions = harddiskmanager.getMountedPartitions()
		partitiondict = {}
		for partition in partitions:
			if partition.mountpoint == "/":
				self.freeSize = partition.free()

		if self.freeSize >= 1024*1024:
			self["free_size"].setText(_("free size : %d MB" % ( self.freeSize/1024/1024 ) ))
		else:
			self["free_size"].setText(_("free size : %.2f MB" % ( self.freeSize/1024/1024.0 ) ))
		from os import statvfs
		s=statvfs("/")
		percent  = str(100 - ((100 * s.f_bavail)/ s.f_blocks))
					
		self["percent"].setText(percent+'%')
		self["free_progress"].setValue(int(percent))
		self["free_progress"].show()

#		from os import system
#		system("df | grep /dev/root > /tmp/nand_info")
#		readFp=open("/tmp/nand_info", "r")
#		lines = readFp.readlines()
#		readFp.close()
#		lines = lines[0] # change list to string
#		lines = lines.split('%') #  "rootfs 54528 48960 5568 90% /" ==> "rootfs 54528 48960 5568 90" , " /"
#		lines = lines[0].split(' ')
#		percent = lines.pop()
					
		self["percent"].setText(percent+'%')
		self["free_progress"].setValue(int(percent))
		self["free_progress"].show()

	def isFreeSizeOk(self, package):
		cmd = "ipkg info enigma2-plugin-" + package + " | grep Size > /tmp/package_size"	
		from os import system
		system(cmd)
		#  # ipkg info enigma2-plugin-softcams-camd3 | grep Size
		#  Size: 167142

		readFp=open("/tmp/package_size", "r")
		lines = readFp.readlines()
		readFp.close()
		lines = lines[0] # change list to string
		lines = lines.split(' ')
		packageSize = int(lines[1])
		if (self.freeSize - packageSize)  < (1024 * 1024):
			return False

		return True

	def removeChInfoFromSettings(self):
		from Components.config import config, configfile
		import re
		config.saveToFile("/tmp/settings_tmp")
		readFp=open("/tmp/settings_tmp", "r")
		writeFp=open("/etc/enigma2/settings", "w")
		lines = readFp.readlines()
		for line in lines:
			if re.search("config.servicelist.startuproot", line) == None \
				and re.search("config.servicelist.startupservice", line) == None \
				and re.search("config.tv.lastroot", line) == None \
				and re.search("config.tv.lastservice", line) == None:
				writeFp.write(line)	
			else:
				print "remove line : ",line
		readFp.close()
		writeFp.close()
		config.loadFromFile("/etc/enigma2/settings")

