installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = SoftwareManager PositionerSetup Satfinder \
	SkinSelector SatelliteEquipmentControl Videomode VideoTune Hotplug \
	CommonInterfaceAssignment \
	CableScan FastScan VideoClippingSetup HdmiCEC \
	VideoEnhancement WirelessLan NetworkWizard OSDPositionSetup OSD3DSetup 

#if HAVE_TEMPFANCONTROL
SUBDIRS += TempFanControl
#endif

if DREAMBOX
SUBDIRS += FrontprocessorUpgrade NFIFlash
endif

install_PYTHON =	\
	__init__.py
