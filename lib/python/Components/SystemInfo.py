from enigma import eDVBResourceManager
from Tools.Directories import fileExists
from Tools.HardwareInfo import HardwareInfo

SystemInfo = { }

#FIXMEE...
def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d"%(idx), 'f'):
		idx += 1
	return idx

SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds

SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
# iq [
#SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["FrontpanelDisplay"] = HardwareInfo().has_micom()
# ]
SystemInfo["FrontpanelDisplayGrayscale"] = fileExists("/dev/dbox/oled0")
# iq [
#SystemInfo["DeepstandbySupport"] = HardwareInfo().get_device_name() != "dm800"
def isSupportDeepStandby():
	if HardwareInfo().has_micom():
		FP_IOCTL_SUPPORT_DEEP_STANDBY = 0x429
		fp = open('/dev/dbox/fp0', 'w')
		import fcntl
		return fcntl.ioctl(fp.fileno(), FP_IOCTL_SUPPORT_DEEP_STANDBY)
SystemInfo["DeepstandbySupport"] = isSupportDeepStandby()
from enigma import eDVBCIInterfaces
SystemInfo["NumCiSlots"] = eDVBCIInterfaces.getInstance().getNumOfSlots()
# ]
