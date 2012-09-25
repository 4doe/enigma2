# ---- coding: utf-8 --
###########################################################################
##################### By:subixonfire  www.satforum.me #####################
###########################################################################
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import MoviePlayer as MP_parent
from Screens.InfoBar import InfoBar
from Screens.MessageBox import MessageBox
from ServiceReference import ServiceReference
from enigma import eServiceReference, eConsoleAppContainer, ePicLoad, getDesktop, eServiceCenter
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from Components.Input import Input
from Screens.InputBox import InputBox
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from cookielib import CookieJar
import urllib, urllib2, re, time, os
from urllib2 import Request, urlopen, URLError, HTTPError



###########################################################################
class ShowHelp(Screen):
    wsize = getDesktop(0).size().width() - 200
    hsize = getDesktop(0).size().height() - 300
    
    skin = """
        <screen position="100,150" size=\"""" + str(wsize) + "," + str(hsize) + """\" title="1channel" >
        <widget name="myLabel" position="10,10" size=\"""" + str(wsize - 20) + "," + str(hsize - 20) + """\" font="Console;18" />
        </screen>"""
        
    def __init__(self, session, args = None):
        self.session = session

        Screen.__init__(self, session)
        
        #Help text
        text = """
HELP:
To add links to this plugin check urllist.txt file in plugin folder.
Za dodati linkove u ovaj plugin pogledajte datoteku urllist.txt u folderu plugina.

TODO: Write some nice help text here.
        
ABOUT:

        
Thanx to/ Zahvale:
        
Satforum.me ( For being a nice litle buletinboard where we all feel like a family.)
grle @ satforum.me (Testing and finding bugs in all my plugins incl. this one.)

Posebna zahvala bosnianrasta @ satforum.me koj mi je nije dao da dišem dok nisam slozio plugin za letmewatch/1channel!

LICENCE:
This is a test and bugfix release, you are not allowed to redistribute in any way, this includes posting this plugin to other forum's or packing it in any E2 Img!
Ovo je test i bugfix verzija, nije dozvoljena redistribucija iste na bilo koj način, to uključuje postavljanje  na druge forume, i/ili pakiranje iste u bilo koj E2 Img.
        """
         
        self["myLabel"] = ScrollLabel(text)
        self["myActionMap"] = ActionMap(["WizardActions", "SetupActions", "ColorActions"],
        {
        "cancel": self.close,
        "ok": self.close,
        "up": self["myLabel"].pageUp,
		"down": self["myLabel"].pageDown,
        }, -1)
###########################################################################
class MyMenux(Screen):
    wsize = getDesktop(0).size().width() - 200
    hsize = getDesktop(0).size().height() - 300
    
    skin = """
        <screen position="100,150" size=\"""" + str(wsize) + "," + str(hsize) + """\" title="1channel" >
        <widget name="myMenu" position="10,10" size=\"""" + str(wsize - 20) + "," + str(hsize - 20) + """\" scrollbarMode="showOnDemand" />
        </screen>"""
            

        
    def __init__(self, session, action, value):
        
        self.session = session

        self.action = action
        
        self.value = value
        
        
        osdList = []
        
        if self.action is "start":
            osdList.append((_("Movie"), "movie"))
            osdList.append((_("Tv Show"), "tvshow"))
            osdList.append((_("Userlist"), "userlist"))
        
        elif self.action is "userlist":    
            urlList = open(os.path.dirname( __file__ ) + "/urllist.txt", 'r')
            urlData = urlList.readlines()
            for urlLine in urlData:
                if not urlLine.startswith("#"): 
                    urlLine = urlLine.split("; ")
                    osdList.append((_(urlLine[0]), urlLine[1]))
        
        elif self.action is "movie" or "tvshow":
            osdList = [(' --- 123 --- ', '123'), (' ---- A ---- ', 'a'), (' ---- B ---- ', 'b'), (' ---- C ---- ', 'c'), (' ---- D ---- ', 'd'), (' ---- E ---- ', 'e'), (' ---- F ---- ', 'f'), (' ---- G ---- ', 'g'), (' ---- H ---- ', 'h'), (' ----  I  ---- ', 'i'), (' ---- J ---- ', 'j'), (' ---- K ---- ', 'K'), (' ---- L ---- ', 'l'), (' ---- M ---- ', 'm'), (' ---- N ---- ', 'n'), (' ---- O ---- ', 'o'), (' ---- P ---- ', 'p'), (' ---- Q ---- ', 'q'), (' ---- R ---- ', 'r'), (' ---- S ---- ', 's'), (' ---- T ---- ', 't'), (' ---- U ---- ', 'u'), (' ---- V ---- ', 'v'), (' ---- W ---- ', 'w'),  (' ---- X ---- ', 'x'), (' ---- Y ---- ', 'y'), (' ---- Z ---- ', 'z'),('Search', 'search')]
            
        elif self.action is "page":
            print "########PMOVIE#################" + self.value
            page = self.value
            url = "http://www.1channel.ch/index.php?letter=" + page + "&sort=alphabet&page=1"
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            htmlDoc = str(response.read())
            response.close()
            pages = (re.compile ('<a href="/index.php\?letter=.+?&sort=alphabet&page=([0-9]*)"> >> </a>').findall(htmlDoc))
     
            for page in range(int(pages[0]) / 5):
                page = int(page + 1) * 5
                osdList.append((_("Page " + str(page - 4) + " - " + str(page) ), "page"))
            
               
        osdList.append((_("Help & About"), "help"))
        osdList.append((_("Exit"), "exit"))
        
        Screen.__init__(self, session)
        self["myMenu"] = MenuList(osdList)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
        "ok": self.go,
        "cancel": self.cancel
        }, -1)    
        
        #urlList = open(os.path.dirname( __file__ ) + "/urllist.txt", 'r')
    
    def go(self):
        returnValue = self["myMenu"].l.getCurrentSelection()[1]
        
        
        if returnValue is "help":
                self.session.open(ShowHelp)
        elif returnValue is "exit":
                self.close(None)
            
        
        elif self.action is "start":
            if returnValue is "movie":
                self.session.open(MyMenux, "movie", "0")
            if returnValue is "tvshow":
                self.session.open(MyMenux, "tvshow", "0")
            elif returnValue is "userlist":
                self.session.open(MyMenux, "userlist", "0")
        
        elif self.action is "userlist":
            fileUrl = returnValue
            if (fileUrl.find("putlocker") > -1 ):
                self.Putlocker(fileUrl)
                
        elif self.action is "movie":
            if returnValue is "search":
                print "search"
                self.mySearch()
            else:     
                value = returnValue
                self.session.open(MyMenu2, "page", value)
            
        elif self.action is "tvshow":
            value = returnValue
            action = ""
            self.session.open(MyMenux, "tvshowp", value)
    
    def mySearch(self):
        self.session.openWithCallback(self.askForWord, InputBox, title=_("Search: (unstabile as hell)"), text=" " * 55, maxSize=55, type=Input.TEXT)
       
    def askForWord(self, returnValue):
        if returnValue is None:
            pass
        else:
            value = "search " + returnValue
            self.session.open(MyMenu2, "page", value)
            
            
    
         
                   
    def cancel(self):
        self.close(None)
        
    def Putlocker(self, fileUrl):                
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        req = urllib2.Request(fileUrl)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')

        response = ""
        html_doc =""
        try:response = urllib2.urlopen(req)
        except URLError, e:
            print e.reason
        except HTTPError, e:
            print e.reason
        if not response is "":
            try: html_doc = str(response.read())    
            except URLError, e:
                print e.reason
            except HTTPError, e:
                print e.reason
            response.close()
        
        plhash =""
        if not html_doc is "":
            plhash = (re.compile ('<input type="hidden" value="([0-9a-f]+?)" name="hash">').findall(html_doc))
            
        if plhash is "":
            self.session.open(MessageBox,_("Host Resolver > File not found error:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                        
        else:    
            time.sleep(7)
            data = {'hash': plhash[0], 'confirm':'Continue as Free User'}
            data = urllib.urlencode(data)
            req = urllib2.Request(fileUrl, data)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            html_doc = str(response.read())
            response.close()
            plplaylist = (re.compile ("playlist: \'/get_file.php\\?stream=(.+?)\'").findall(html_doc))
            if not plplaylist:
                self.session.open(MessageBox,_("Host Resolver > Unable to resolve:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                        
            else:
                print fileUrl
                if (fileUrl.find("http://www.putlocker.com/file/") > -1 ):
                    url = "http://www.putlocker.com/get_file.php?stream=" + plplaylist[0]
                elif (fileUrl.find("http://www.sockshare.com/file/") > -1 ):
                    url = "http://www.sockshare.com/get_file.php?stream=" + plplaylist[0]    
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                html_doc = str(response.read())
                response.close()

                plurl = (re.compile ('<media:content url="(.+?)" type="video/x-flv"').findall(html_doc))
                if not plurl:
                    self.session.open(MessageBox,_("Host Resolver > Unable to resolve:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                            
                else:
                    fileRef = eServiceReference(4097,0,plurl[0])
                    self.session.open(MoviePlayer, fileRef)
                    
###########################################################################
class MyMenu2(Screen):
    wsize = getDesktop(0).size().width() - 200
    hsize = getDesktop(0).size().height() - 300
    
    skin = """
        <screen position="100,150" size=\"""" + str(wsize) + "," + str(hsize) + """\" title="1channel" >
        <widget name="myMenu" position="10,10" size=\"""" + str(wsize - 20) + "," + str(hsize - 20) + """\" scrollbarMode="showOnDemand" />
        </screen>"""
            

        
    def __init__(self, session, action, value):
        
        self.session = session

        self.action = action
        
        self.value = value
        
        osdList = []
        
        if self.action is "page":
            if (value.find("search") > -1 ):
                value = value[7:]
                value = str(value.strip ())
                print value
                value = str(value.replace(" ", "+"))
                print value
                url = "http://www.1channel.ch/index.php"
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                htmlDoc = str(response.read())
                response.close()
                searchkey = (re.compile ('<input type="hidden" name="key" value="(.+?)" />').findall(htmlDoc))
                url = "http://www.1channel.ch/index.php?search_keywords=" + value + "&key=" + searchkey[0] + "&sort=alphabet&search_section=1"
                print htmlDoc
                restring = '<a href=.+?&page=([0-9]*)"> >> </a>'
                self.value = "search" + "-" + value + "-" + searchkey[0] 
            else:    
                page = self.value
                url = "http://www.1channel.ch/index.php?letter=" + page + "&sort=alphabet&page=1"
                restring = '<a href="/index.php\?letter=.+?&sort=alphabet&page=([0-9]*)"> >> </a>'
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            htmlDoc = str(response.read())
            response.close()
            pages = (re.compile (restring).findall(htmlDoc))
            
            
            
            if not pages:
                pages =["1"]
                
            page_x = 0     
            for page in range(int(pages[0]) / 5):
                page = int(page + 1) * 5
                if page < int(pages[0]):
                    page_str = str(page - 4) + " - " + str(page) 
                    osdList.append((_("Page " + page_str), self.value + "," + page_str))
                    page_x = page
            if int(pages[0]) - page_x is 1 or 2 or 3 or 4:
                page_str =  str(page_x + 1) + " - " + pages[0]
                osdList.append((_("Page " + page_str ), self.value + "," + page_str))        
                
               
        osdList.append((_("Help & About"), "help"))
        osdList.append((_("Exit"), "exit"))
        
        Screen.__init__(self, session)
        self["myMenu"] = MenuList(osdList)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
        "ok": self.go,
        "cancel": self.cancel
        }, -1)    
        
    
    def go(self):
        returnValue = self["myMenu"].l.getCurrentSelection()[1]
        
        if returnValue is "help":
            self.session.open(ShowHelp)
        elif returnValue is "exit":
            self.close(None)
        else:
            value = returnValue
            self.session.open(MovieList, "movielist", value)
            print value      
        
            
    def cancel(self):
        self.close(None)
                         
###########################################################################
class MovieList(Screen):
    wsize = getDesktop(0).size().width() - 200
    hsize = getDesktop(0).size().height() - 300
    
    skin = """
        <screen position="100,150" size=\"""" + str(wsize) + "," + str(hsize) + """\" title="1channel" >
        <widget name="myMenu" position="10,10" size=\"""" + str(wsize - 20) + "," + str(hsize - 20) + """\" scrollbarMode="showOnDemand" />
        </screen>"""
            

        
    def __init__(self, session, action, value):
        
        self.session = session

        self.action = action
        
        self.value = value
        
        osdList = []
        
        if self.action is "movielist":
            self.value = self.value.split(',')
            if (self.value[0].find("search") > -1 ):
                search = self.value[0].split('-')
                value = search[1]
                searchkey = search[2]
                url = "http://www.1channel.ch/index.php?search_keywords=" + value + "&key=" + searchkey + "&search_section=1&sort=alphabet&page="    
            else:
                letter = self.value[0]
                url = "http://www.1channel.ch/index.php?letter=" + letter + "&sort=alphabet&page="
            pages = self.value[1].split(' - ')
            page_a = pages[0]
            page_b = pages[1]
            pages = int(page_b) - int(page_a) + 1
            data = []
            for x in range (pages):
                page = int(page_a)
                page_a = int(page_a) + 1 
                pageurl = url + str(page)
                print url
                reString = '<div class="index_item index_item_ie"><a href="(.+?)" title="(.+?)"><img src="(.+?)" border="0" width="150" height="225" alt=".+?"><h2>(.+?)</h2>'

                req = urllib2.Request(pageurl)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                htmlDoc = str(response.read())
    	        response.close()
    	        data = data + (re.compile (reString, re.DOTALL,).findall(htmlDoc))
    	    x = 0
    	    for movie in data:
    	        osdList.append((_(movie[1][6:]), movie[0]))
    	        x = x +1
    	    print x
    	    
    	if not osdList:
    	    osdList.append((_("Sorry nothing found!"), "exit")) 
        
               
        osdList.append((_("Help & About"), "help"))
        osdList.append((_("Exit"), "exit"))
        
        Screen.__init__(self, session)
        self["myMenu"] = MenuList(osdList)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
        "ok": self.go,
        "cancel": self.cancel
        }, -1)    
        
    
    def go(self):
        returnValue = self["myMenu"].l.getCurrentSelection()[1]
        
        if returnValue is "help":
            self.session.open(ShowHelp)
        elif returnValue is "exit":
            self.close(None)
        else:
            value = returnValue
            self.session.open(MovieSource, "moviesource", value)      
        
        
            
            
         
                   
    def cancel(self):
        self.close(None)
                         
###########################################################################

###########################################################################
class MovieSource(Screen):
    wsize = getDesktop(0).size().width() - 200
    hsize = getDesktop(0).size().height() - 300
    
    skin = """
        <screen position="100,150" size=\"""" + str(wsize) + "," + str(hsize) + """\" title="1channel" >
        <widget name="myMenu" position="10,10" size=\"""" + str(wsize - 20) + "," + str(hsize - 20) + """\" scrollbarMode="showOnDemand" />
        </screen>"""
            

        
    def __init__(self, session, action, value):
        
        self.session = session

        self.action = action
        
        self.value = value
        
        osdList = []
        
        url = "http://www.1channel.ch" + self.value 
        #reString = '<div class="index_item index_item_ie"><a href="(.+?)" title=".+?"><img src="(.+?)" border="0" width="150" height="225" alt=".+?"><h2>(.+?)</h2>'

        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        htmlDoc = str(response.read())
        response.close()


        links = (re.compile ('<a href="(.+?)" onClick="return',).findall(htmlDoc))
        resolved = []
        for link in links:
            if (link.find("&domain=cHV0bG9ja2VyLmNvbQ==" ) > -1 ) or  (link.find("&domain=c29ja3NoYXJlLmNvbQ==") > -1 ):
                x = urllib2.urlopen("http://1channel.ch" + link)
                x = x.geturl()
                resolved.append(x)
        linksfound = 0
        for link in resolved:
            if (link.find("http://www.putlocker.com/file/") > -1 ):
                osdList.append((_("Putlocker: " + link[30:]), link))
                linksfound = linksfound + 1
                
            elif (link.find("http://www.sockshare.com/file/") > -1 ):
                osdList.append((_("Sockshare: " + link[30:]), link))
                linksfound = linksfound + 1
             
        
        if linksfound is 0:
            osdList.append((_("Sorry no usable links found!"), "exit"))
        
        
               
        osdList.append((_("Help & About"), "help"))
        osdList.append((_("Exit"), "exit"))
        
        Screen.__init__(self, session)
        self["myMenu"] = MenuList(osdList)
        self["myActionMap"] = ActionMap(["SetupActions"],
        {
        "ok": self.go,
        "cancel": self.cancel
        }, 
        -1)    
        
    
    def go(self):
        returnValue = self["myMenu"].l.getCurrentSelection()[1]
        
        if returnValue is "help":
            self.session.open(ShowHelp)
        elif returnValue is "exit":
            self.close(None)
        else:
            self.Putlocker(returnValue)      
        
        
            
            
         
                   
    def cancel(self):
        self.close(None)
        
    def Putlocker(self, fileUrl):                
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        req = urllib2.Request(fileUrl)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')

        response = ""
        html_doc =""
        try:response = urllib2.urlopen(req)
        except URLError, e:
            print e.reason
        except HTTPError, e:
            print e.reason
        if not response is "":
            try: html_doc = str(response.read())    
            except URLError, e:
                print e.reason
            except HTTPError, e:
                print e.reason
            response.close()
        
        plhash =""
        if not html_doc is "":
            plhash = (re.compile ('<input type="hidden" value="([0-9a-f]+?)" name="hash">').findall(html_doc))
            
        if plhash is "":
            self.session.open(MessageBox,_("Host Resolver > File not found error:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                        
        else:    
            time.sleep(7)
            data = {'hash': plhash[0], 'confirm':'Continue as Free User'}
            data = urllib.urlencode(data)
            req = urllib2.Request(fileUrl, data)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            html_doc = str(response.read())
            response.close()
            plplaylist = (re.compile ("playlist: \'/get_file.php\\?stream=(.+?)\'").findall(html_doc))
            if not plplaylist:
                self.session.open(MessageBox,_("Host Resolver > Unable to resolve:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                        
            else:
                print fileUrl
                if (fileUrl.find("http://www.putlocker.com/file/") > -1 ):
                    url = "http://www.putlocker.com/get_file.php?stream=" + plplaylist[0]
                elif (fileUrl.find("http://www.sockshare.com/file/") > -1 ):
                    url = "http://www.sockshare.com/get_file.php?stream=" + plplaylist[0]    
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3 Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                html_doc = str(response.read())
                response.close()

                plurl = (re.compile ('<media:content url="(.+?)" type="video/x-flv"').findall(html_doc))
                if not plurl:
                    self.session.open(MessageBox,_("Host Resolver > Unable to resolve:\n" + self["myMenu"].l.getCurrentSelection()[0]), MessageBox.TYPE_ERROR, timeout = 5)
                        
                else:
                    fileRef = eServiceReference(4097,0,plurl[0])
                    self.session.open(MoviePlayer, fileRef)
                         
###########################################################################

def main(session, **kwargs):
        
    
    
    action = "start"
    value = 0 
    burek = session.open(MyMenux, action, value)
        
                  
###########################################################################    

class MoviePlayer(MP_parent):
	def __init__(self, session, service):
		self.session = session
		self.WithoutStopClose = False
		MP_parent.__init__(self, self.session, service)
###########################################################################

def Plugins(**kwargs):
    return PluginDescriptor(
        name="1channel",
        description="1channel video on demand",
        where = [ PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU ],
        icon="./icon.png",
        fnc=main)


