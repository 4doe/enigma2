from Tools.Profile import profile

# workaround for required config entry dependencies.
import Screens.MovieSelection

from Screen import Screen

profile("LOAD:enigma")
from enigma import iPlayableService

profile("LOAD:InfoBarGenerics")
from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarRdsDecoder, \
	InfoBarEPG, InfoBarSeek, InfoBarInstantRecord, InfoBarRedButton, \
	InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey, \
	InfoBarSubserviceSelection, InfoBarShowMovies, InfoBarTimeshift,  \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, \
	InfoBarSubtitleSupport, InfoBarPiP, InfoBarPlugins, InfoBarServiceErrorPopupSupport, InfoBarJobman, \
	setResumePoint, delResumePoint

profile("LOAD:InitBar_Components")
from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

profile("LOAD:HelpableScreen")
from Screens.HelpMenu import HelpableScreen

class InfoBar(InfoBarBase, InfoBarShowHide,
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder,
	InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton,
	HelpableScreen, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey,
	InfoBarSubserviceSelection, InfoBarTimeshift, InfoBarSeek,
	InfoBarSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions,
	InfoBarPiP, InfoBarPlugins, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarJobman,
	Screen):
	
	ALLOW_SUSPEND = True
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		self["actions"] = HelpableActionMap(self, "InfobarActions",
			{
				"showMovies": (self.showMovies, _("Play recorded movies...")),
				"showRadio": (self.showRadio, _("Show the radio player...")),
				"showTv": (self.showTv, _("Show the tv player...")),
# [iq
				"openBouquetList": self.openBouquetList,
				"showMediaPlayer": (self.showMediaPlayer, _("Show the media player...")),
				"openTimerList": (self.openTimerList, _("Show the tv player...")),
				"ZoomInOut":(self.ZoomInOut, _("Zoom In/Out TV...")), 
				"ZoomOff":(self.ZoomOff, _("Zoom Off...")),
				"HarddiskSetup": (self.HarddiskSetup, _("Select HDD")),
# iq]
			}, prio=2)
		
		self.allowPiP = True
		
		for x in HelpableScreen, \
				InfoBarBase, InfoBarShowHide, \
				InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder, \
				InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarUnhandledKey, \
				InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarSubserviceSelection, \
				InfoBarTimeshift, InfoBarSeek, InfoBarSummarySupport, InfoBarTimeshiftState, \
				InfoBarTeletextPlugin, InfoBarExtensions, InfoBarPiP, InfoBarSubtitleSupport, InfoBarJobman, \
				InfoBarPlugins, InfoBarServiceErrorPopupSupport:
			x.__init__(self)

		self.helpList.append((self["actions"], "InfobarActions", [("showMovies", _("view recordings..."))]))
		self.helpList.append((self["actions"], "InfobarActions", [("showRadio", _("hear radio..."))]))

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evUpdatedEventInfo: self.__eventInfoChanged
			})

		self.current_begin_time=0
# [iq
		self.zoomrate=0
		self.zoomin=1
# iq]
		assert InfoBar.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		InfoBar.instance = self

# iq - save & config list update
	def serviceSave(self):  
		from Components.config import configfile
		slist = self.servicelist
		config.servicelist.startupservice.value = slist.getCurrentSelection().toString()
		path = ''
		for i in slist.servicePath:
			path += i.toString()
			path += ';'
		config.servicelist.startuproot.value = path
		config.servicelist.save()
		configfile.save()
# iq]


	def __onClose(self):
		InfoBar.instance = None

	def __eventInfoChanged(self):
		if self.execing:
			service = self.session.nav.getCurrentService()
			old_begin_time = self.current_begin_time
			info = service and service.info()
			ptr = info and info.getEvent(0)
			self.current_begin_time = ptr and ptr.getBeginTime() or 0
			if config.usage.show_infobar_on_event_change.value:
				if old_begin_time and old_begin_time != self.current_begin_time:
					self.doShow()

	def __checkServiceStarted(self):
		self.__serviceStarted(True)
		self.onExecBegin.remove(self.__checkServiceStarted)
		self.serviceSave()		# [iq]
	
# iq]
	def openBouquetList(self):
		if config.usage.tvradiobutton_mode.value == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
	
	def showMediaPlayer(self):
		try:
			from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
			self.session.open(MediaPlayer)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def openTimerList(self):
		from Screens.TimerEdit import TimerEditList
		self.session.open(TimerEditList)



# iq]
	def serviceStarted(self):  #override from InfoBarShowHide
		new = self.servicelist.newServicePlayed()
		if self.execing:
			InfoBarShowHide.serviceStarted(self)
			self.current_begin_time=0
		elif not self.__checkServiceStarted in self.onShown and new:
			self.onShown.append(self.__checkServiceStarted)

	def __checkServiceStarted(self):
		self.serviceStarted()
		self.onShown.remove(self.__checkServiceStarted)

	def showTv(self):
		self.showTvChannelList(True)

	def showRadio(self):
		if config.usage.e1like_radio_mode.value:
			self.showRadioChannelList(True)
		else:
			self.rds_display.hide() # in InfoBarRdsDecoder
			from Screens.ChannelSelection import ChannelSelectionRadio
			self.session.openWithCallback(self.ChannelSelectionRadioClosed, ChannelSelectionRadio, self)

	def ChannelSelectionRadioClosed(self, *arg):
		self.rds_display.show()  # in InfoBarRdsDecoder

	def showMovies(self, defaultRef=None):
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, defaultRef)

	def movieSelected(self, service):
		ref = self.lastservice
		del self.lastservice
		if service is None:
			if ref and not self.session.nav.getCurrentlyPlayingServiceReference():
				self.session.nav.playService(ref)
		else:
			self.session.open(MoviePlayer, service, slist = self.servicelist, lastservice = ref)
# [iq
	def ZoomInOut(self):
		zoomval=0
		if self.zoomrate > 3:
			self.zoomin = 0
		elif self.zoomrate < -9:
			self.zoomin = 1

		if self.zoomin == 1:
			self.zoomrate += 1
		else:
			self.zoomrate -= 1

		if self.zoomrate < 0:
		    zoomval=abs(self.zoomrate)+10
		else:
		    zoomval=self.zoomrate
		print "zoomRate:", self.zoomrate
		print "zoomval:", zoomval
		file = open("/proc/stb/vmpeg/0/zoomrate", "w")
		file.write('%d' % int(zoomval))
		file.close()

	def ZoomOff(self):
		self.zoomrate = 0
		self.zoomin = 1
		open("/proc/stb/vmpeg/0/zoomrate", "w").write(str(0))

	def HarddiskSetup(self):
		from Screens.HarddiskSetup import HarddiskSelection
		self.session.open(HarddiskSelection)
# iq]


class MoviePlayer(InfoBarBase, InfoBarShowHide, \
		InfoBarMenu, \
		InfoBarSeek, InfoBarShowMovies, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications,
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView,
		InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, Screen, InfoBarTeletextPlugin,
		InfoBarServiceErrorPopupSupport, InfoBarExtensions, InfoBarPlugins, InfoBarPiP):

	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
		
	def __init__(self, session, service, slist = None, lastservice = None):
		Screen.__init__(self, session)
		
		self["actions"] = HelpableActionMap(self, "MoviePlayerActions",
			{
				"leavePlayer": (self.leavePlayer, _("leave movie player..."))
			})

		self["DirectionActions"] = HelpableActionMap(self, "DirectionActions",
			{
				"left": self.left,
				"right": self.right
			}, prio = -2)

		self.allowPiP = True
		
		for x in HelpableScreen, InfoBarShowHide, InfoBarMenu, \
				InfoBarBase, InfoBarSeek, InfoBarShowMovies, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, \
				InfoBarTeletextPlugin, InfoBarServiceErrorPopupSupport, InfoBarExtensions, \
				InfoBarPlugins, InfoBarPiP:
			x.__init__(self)

		self.servicelist = slist
		self.lastservice = lastservice or session.nav.getCurrentlyPlayingServiceReference()
		session.nav.playService(service)
		self.returning = False
		self.onClose.append(self.__onClose)

	def __onClose(self):
		self.session.nav.playService(self.lastservice)

	def handleLeave(self, how):
		self.is_closing = True
		if how == "ask":
			if config.usage.setup_level.index < 2: # -expert
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue")
				)
			else:
				list = (
					(_("Yes"), "quit"),
					(_("Yes, returning to movie list"), "movielist"),
					(_("Yes, and delete this movie"), "quitanddelete"),
					(_("No"), "continue"),
					(_("No, but restart from begin"), "restart")
				)

			from Screens.ChoiceBox import ChoiceBox
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		setResumePoint(self.session)
		self.handleLeave(config.usage.on_movie_stop.value)

	def deleteConfirmed(self, answer):
		if answer:
			self.leavePlayerConfirmed((True, "quitanddeleteconfirmed"))

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]

		if answer in ("quitanddelete", "quitanddeleteconfirmed"):
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			from enigma import eServiceCenter
			serviceHandler = eServiceCenter.getInstance()
			if answer == "quitanddelete":
				msg = ''
				if config.usage.movielist_trashcan.value:
					import Tools.Trashcan
					try:
						trash = Tools.Trashcan.createTrashFolder(ref.getPath())
						Screens.MovieSelection.moveServiceFiles(ref, trash)
						# Moved to trash, okay
						self.close()
						return
					except Exception, e:
						print "[InfoBar] Failed to move to .Trash folder:", e
						msg = _("Cannot move to trash can") + "\n" + str(e) + "\n"
				info = serviceHandler.info(ref)
				name = info and info.getName(ref) or _("this recording")
				msg += _("Do you really want to delete %s?") % name
				from Screens.MessageBox import MessageBox
				self.session.openWithCallback(self.deleteConfirmed, MessageBox, msg)
				return

			elif answer == "quitanddeleteconfirmed":
				offline = serviceHandler.offlineOperations(ref)
				if offline.deleteFromDisk(0):
					from Screens.MessageBox import MessageBox
					self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
					return

		if answer in ("quit", "quitanddeleteconfirmed"):
			self.close()
		elif answer == "movielist":
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			self.returning = True
			self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)
			self.session.nav.stopService()
		elif answer == "restart":
			self.doSeek(0)
			self.setSeekState(self.SEEK_STATE_PLAY)

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if ref:
			delResumePoint(ref)
		self.handleLeave(config.usage.on_movie_eof.value)

	def up(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			slist.moveUp()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def down(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			slist.moveDown()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def right(self):
		# XXX: gross hack, we do not really seek if changing channel in pip :-)
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapDown here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value and slist.atEnd():
							slist.nextBouquet()
						else:
							slist.moveDown()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveDown()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekFwd(self)

	def left(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapUp here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.value:
							if slist.atBegin():
								slist.prevBouquet()
						slist.moveUp()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveUp()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekBack(self)

	def showPiP(self):
		slist = self.servicelist
		if self.session.pipshown:
			if slist and slist.dopipzap:
				slist.togglePipzap()
			del self.session.pip
			self.session.pipshown = False
		else:
			from Screens.PictureInPicture import PictureInPicture
			self.session.pip = self.session.instantiateDialog(PictureInPicture)
			self.session.pip.show()
			self.session.pipshown = True
			self.session.pip.playService(slist.getCurrentSelection())

	def swapPiP(self):
		pass

	def showMovies(self):
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		self.playingservice = ref # movie list may change the currently playing
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)

	def movieSelected(self, service):
		if service is not None:
			self.is_closing = False
			self.session.nav.playService(service)
			self.returning = False
		elif self.returning:
			self.close()
		else:
			self.is_closing = False
			ref = self.playingservice
			del self.playingservice
			# no selection? Continue where we left off
			if ref and not self.session.nav.getCurrentlyPlayingServiceReference():
				self.session.nav.playService(ref)
