class HardwareInfo:
	device_name = None
	device_version = None

	def __init__(self):
		if HardwareInfo.device_name is not None:
#			print "using cached result"
			return

		HardwareInfo.device_name = "unknown"
		try:
# iq [
#			file = open("/proc/stb/info/model", "r")
			file = open("/proc/stb/info/hwmodel", "r")
# ]
			HardwareInfo.device_name = file.readline().strip()
			file.close()
			try:
				file = open("/proc/stb/info/version", "r")
				HardwareInfo.device_version = file.readline().strip()
				file.close()
			except:
				pass
		except:
			print "----------------"
			print "you should upgrade to new drivers for the hardware detection to work properly"
			print "----------------"
			print "fallback to detect hardware via /proc/cpuinfo!!"
			try:
				rd = open("/proc/cpuinfo", "r").read()
				if rd.find("Brcm4380 V4.2") != -1:
					HardwareInfo.device_name = "dm8000"
					print "dm8000 detected!"
				elif rd.find("Brcm7401 V0.0") != -1:
					HardwareInfo.device_name = "dm800"
					print "dm800 detected!"
				elif rd.find("MIPS 4KEc V4.8") != -1:
					HardwareInfo.device_name = "dm7025"
					print "dm7025 detected!"
			except:
				pass

	def get_device_name(self):
		return HardwareInfo.device_name

	def get_device_version(self):
		return HardwareInfo.device_version

	def has_hdmi(self):
# iq [
#		return (HardwareInfo.device_name == 'dm7020hd' or HardwareInfo.device_name == 'dm800se' or HardwareInfo.device_name == 'dm500hd' or HardwareInfo.device_name == 'tmtwin' or (HardwareInfo.device_name == 'dm8000' and HardwareInfo.device_version != None))

		DEVICES_WITHOUT_HDMI = []
		if HardwareInfo.device_name in DEVICES_WITHOUT_HDMI:
			return False
		else:
			return True

	def has_rfmod(self):
		DEVICES_WITHOUT_RFMOD = [ 'tmsingle', 'ios300hd' ]
		if HardwareInfo.device_name in DEVICES_WITHOUT_RFMOD:
			return False
		else:
			return True

	def has_micom(self):
# var SystemInfo["FrontpanelDisplay"], SystemInfo["OledDisplay"] functioning similar with this function looks like not work properly on our device
#		DEVICES_WITHOUT_MICOM = [ 'single', 'ios300hd' ]
# ios300 will have micom 
		DEVICES_WITHOUT_MICOM = []
		if HardwareInfo.device_name in DEVICES_WITHOUT_MICOM:
			return False
		else:
			return True

	def has_vcr(self):
		DEVICES_WITHOUT_VCR = [ 'tmsingle', 'tm2toe', 'ios300hd', 'ios200hd' ]
		if HardwareInfo.device_name in DEVICES_WITHOUT_VCR:
			return False
		else:
			return True

	def has_yuv(self):
		DEVICES_WITHOUT_YUV = [ 'tmsingle', 'tm2toe', 'ios300hd', 'ios200hd' ]
		if HardwareInfo.device_name in DEVICES_WITHOUT_YUV:
			return False
		else:
			return True

# temp test mode tmsinglemini
# tmsinglemini model has not scart ic.

	def has_scart(self):
		DEVICES_WITHOUT_SCART = [ 'tmsinglemini' ]
		if HardwareInfo.device_name in DEVICES_WITHOUT_SCART:
			return False
		else:
			return True

	def support_1080p(self):
		DEVICES_WITHOUT_1080P = []
		if HardwareInfo.device_name in DEVICES_WITHOUT_1080P:
			return False
		else:
			return True
# ]
