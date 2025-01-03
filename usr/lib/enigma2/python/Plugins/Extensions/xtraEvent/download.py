# -*- coding: utf-8 -*-
# by digiteng...06.2020, 11.2020, 11.2021
from __future__ import absolute_import
from Components.AVSwitch import AVSwitch
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.ActionMap import ActionMap
from enigma import eEPGCache, eTimer, getDesktop, ePixmap, ePoint, eSize, loadJPG, loadPNG
from Components.config import config
from ServiceReference import ServiceReference
from Screens.MessageBox import MessageBox
import Tools.Notifications
import requests
from requests.utils import quote
import os
import re
import json
from PIL import Image
import socket
from . import xtra
from datetime import datetime
import time
import threading
from Components.ProgressBar import ProgressBar
import io
from Plugins.Extensions.xtraEvent.skins.xtraSkins import *

from .xtra import version

import inspect
# --------------------------- Logfile -------------------------------


from datetime import datetime, timedelta
from shutil import copyfile
from os import remove
from os.path import isfile



########################### log file loeschen ##################################

myfile="/tmp/xtraevent-Download.log"

## If file exists, delete it ##
if isfile(myfile):
    remove(myfile)
############################## File copieren ############################################
# fuer py2 die int und str anweisung raus genommen und das Grad zeichen

###########################  log file anlegen ##################################
# kitte888 logfile anlegen die eingabe in logstatus

if config.plugins.xtraEvent.logFiles.value == True:
    logstatus = "on"
else:
    logstatus = "off"

# ________________________________________________________________________________

def write_log(msg):
    if logstatus == ('on'):
        with open(myfile, "a") as log:

            log.write(datetime.now().strftime("%Y/%d/%m, %H:%M:%S.%f") + ": " + msg + "\n")

            return
    return

# ****************************  test ON/OFF Logfile ************************************************


def logout(data):
    if logstatus == ('on'):
        write_log(data)
        return
    return

logout(data=str(config.plugins.xtraEvent.logFiles.value))
# ----------------------------- so muss das commando aussehen , um in den file zu schreiben  ------------------------------
#logout(data="start 6.77")
logout(data=str(version))

#                                    bei 1570 google abfrage einbauen

if config.plugins.xtraEvent.tmdbAPI.value != "":
    tmdb_api = config.plugins.xtraEvent.tmdbAPI.value
else:
    tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
if config.plugins.xtraEvent.tvdbAPI.value != "":
    tvdb_api = config.plugins.xtraEvent.tvdbAPI.value
else:
    tvdb_api = "a99d487bb3426e5f3a60dea6d3d3c7ef"
if config.plugins.xtraEvent.fanartAPI.value != "":
    fanart_api = config.plugins.xtraEvent.fanartAPI.value
else:
    fanart_api = "6d231536dea4318a88cb2520ce89473b"

try:
    import sys
    PY3 = sys.version_info[0]
    if PY3 == 3:
        from builtins import str
        from builtins import range
        from builtins import object
        from configparser import ConfigParser
        from _thread import start_new_thread
        from urllib.parse import quote, urlencode
        from urllib.request import urlopen, Request
        from _thread import start_new_thread


    else:
        from ConfigParser import ConfigParser
        from thread import start_new_thread
        from urllib2 import urlopen, quote
        from thread import start_new_thread
except:
    pass

try:
    from Components.Language import language
    logout(data="language try")
    lang = language.getLanguage()
    lang = lang[:2]
    logout(data=str(lang))
except:
    try:
        lang = config.osd.language.value[:-3]
        logout(data="config.osd")
        logout(data=str(lang))
    except:
        logout(data="default")
        lang = "en"
        logout(data=str(lang))

logout(data="---------------------- language is -------------------------------------------")
logout(data=str(lang))

lang_path = r"/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/languages"
try:
    lng = ConfigParser()
    if PY3 == 3:
        lng.read(lang_path,  encoding='utf8')
    else:
        lng.read(lang_path)
    lng.get(lang, "0")
except:
    try:
        lang="en"
        lng = ConfigParser()
        if PY3 == 3:
            lng.read(lang_path,  encoding='utf8')
        else:
            lng.read(lang_path)
    except:
        pass

epgcache = eEPGCache.getInstance()
pathLoc =  "{}xtraEvent/".format(config.plugins.xtraEvent.loc.value)
logout(data="-------------------------------------------------------------- pathLoc")
logout(data=str(pathLoc))
desktop_size = getDesktop(0).size().width()
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
REGEX = re.compile(
        r'([\(\[]).*?([\)\]])|'
        r'(: odc.\d+)|'
        r'(\d+: odc.\d+)|'
        r'(\d+ odc.\d+)|(:)|'
        
        r'!|'
        r'/.*|'
        r'\|\s[0-9]+\+|'
        r'[0-9]+\+|'
        r'\s\d{4}\Z|'
        r'([\(\[\|].*?[\)\]\|])|'
        r'(\"|\"\.|\"\,|\.)\s.+|'
        r'\"|:|'
        r'\*|'
        r'Премьера\.\s|'
        r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
        r'(х|Х|м|М|т|Т|д|Д)/с\s|'
        r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
        r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
        r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
        r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)

class downloads(Screen):
    logout(data="------------------------------------------------------------------------------------------------------- class download screen")
    caller_frame = inspect.currentframe().f_back
    caller_name = inspect.getframeinfo(caller_frame).function
    log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
    logout(data=str(log_message))
    # --------------------------------------------------------------------------- wird von module aufgerufen

    def __init__(self, session):
        logout(data="init")
        Screen.__init__(self, session)
        self.session = session
        if desktop_size <= 1280:
            if config.plugins.xtraEvent.skinSelect.value == 'skin_1':
                self.skin = download_720
            if config.plugins.xtraEvent.skinSelect.value == 'skin_2':
                self.skin = download_720_2
        else:
            if config.plugins.xtraEvent.skinSelect.value == 'skin_1':
                self.skin = download_1080
            if config.plugins.xtraEvent.skinSelect.value == 'skin_2':
                self.skin = download_1080_2
        self.titles = ""
        self['status'] = Label()
        self['info'] = Label()
        self['infoposter'] = Label()
        self['infobackdrop'] = Label()
        self['infobanner'] = Label()
        self['infoinfos'] = Label()
        self['infologo'] = Label()
        self['info2'] = Label()
        self['Picture'] = Pixmap()
        self['Picture2'] = Pixmap()
        self['int_statu'] = Label()
        self['key_red'] = Label(_('Back'))
        self['key_green'] = Label(_('Download'))
        # self['key_yellow'] = Label(_('Show'))
        self['key_yellow'] = Label(_('Delete All'))
        self['key_1'] = Label(_('Delete Poster             :1'))
        self['key_2'] = Label(_('Delete Backdrop        :2'))
        self['key_3'] = Label(_('Delete Banner            :3'))
        self['key_4'] = Label(_('Delete Infos               :4'))
        self['key_5'] = Label(_('Delete Noinfos           :5'))
        self['key_blue'] = Label(_(lng.get(lang, '66')))
        self['actions'] = ActionMap(['xtraEventAction'],

        {
        'cancel': self.close,
        'red': self.close,
        'ok':self.save,
        'green':self.save,
        # 'yellow':self.ir,
        'yellow': self.deletfilesall,
        '1': self.deletfilesposter,
        '2': self.deletfilesbackdrop,
        '3': self.deletfilesbanner,
        '4': self.deletfilesinfos,
        '5': self.deletfilesnoinfos,
        'blue':self.showhide
        }, -2)
        # ---------------------------- hier anzahl der dateien einbauen anzahl bei 1540 ----------------------------------

        self.countposter = 0
        self['infoposter'].setText(str(self.countposter))
        self.countbackdrop = 0
        self['infobackdrop'].setText(str(self.countbackdrop))
        self.countbanner = 0
        self['infobanner'].setText(str(self.countbanner))
        self.countinfos = 0
        self['infoinfos'].setText(str(self.countinfos))
        self.countlogo = 0
        self['infologo'].setText(str(self.countlogo))
        # -----------------------------------------------------------------------------------------------
        self['progress'] = ProgressBar()
        self['progress'].setRange((0, 100))
        self['progress'].setValue(0)
        self.setTitle(_("░ {}".format(lng.get(lang, '45'))))
        self.screen_hide = False
        # -------------------------------------------------------------------------------------------------
        # ------------------------------------------------------------ hier anzahl files abrufen
        self.anzahlfiles_in_poster()
        self['infoposter'].setText(str(self.countposter))
        self.anzahlfiles_in_backdrop()
        self['infobackdrop'].setText(str(self.countbackdrop))
        self.anzahlfiles_in_banner()
        self['infobanner'].setText(str(self.countbanner))
        self.anzahlfiles_in_infos()
        self['infoinfos'].setText(str(self.countinfos))
        self.anzahlfiles_in_logo()
        self['infologo'].setText(str(self.countlogo))
        # --------------------------------------------------------------------------------------------------
        testver = version
        self.testver = testver
        self["testver"] = Label()
        self["testver"].setText("%s " % (self.testver))
        self.onLayoutFinish.append(self.showFilm)
        self.onLayoutFinish.append(self.intCheck)


    def anzahlfiles_in_poster(self):
        logout(data="anzahl poster ")
        directory = "{}poster".format(pathLoc)
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                count += 1
        self.countposter = count
        logout(data=str(self.countposter))
        self['infoposter'].setText(str(self.countposter))

    def anzahlfiles_in_backdrop(self):
        logout(data="anzahl backdrop")
        directory = "{}backdrop".format(pathLoc)
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                count += 1
        self.countbackdrop = count
        logout(data=str(self.countbackdrop))
        self['infobackdrop'].setText(str(self.countbackdrop))


    def anzahlfiles_in_banner(self):
        logout(data="anzahl banner")
        directory = "{}banner".format(pathLoc)
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                count += 1
        self.countbanner = count
        logout(data=str(self.countbanner))
        self['infobanner'].setText(str(self.countbanner))

    def anzahlfiles_in_infos(self):
        logout(data="anzahl infos")
        directory = "{}infos".format(pathLoc)
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                count += 1
        self.countinfos = count
        logout(data=str(self.countinfos))
        self['infoinfos'].setText(str(self.countinfos))

    def anzahlfiles_in_logo(self):
        logout(data="anzahl logo ")
        directory = "{}logo".format(pathLoc)
        count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                count += 1
        self.countlogo = count
        logout(data=str(self.countlogo))
        self['infologo'].setText(str(self.countlogo))

    def intCheck(self):
        logout(data="intCheck")
        try:
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            self['int_statu'].setText("☻")
            return True
        except:
            self['int_statu'].hide()
            self['status'].setText(lng.get(lang, '68'))
            return False

    def searchLanguage(self):
        logout(data="searchLanguage")
        try:
            from Components.Language import language
            lang = language.getLanguage()
            lang = lang[:2]
        except:
            try:
                lang = config.osd.language.value[:-3]
            except:
                lang = "en"
        return lang

    def showhide(self):
        logout(data="showhide")
        if self.screen_hide:
            Screen.show(self)
        else:
            Screen.hide(self)
        self.screen_hide = not (self.screen_hide)

    def save(self):
        logout(data="save")
        # ---------------------------------------------------------- wird von xtra startDownload augerufen
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=str(log_message))

        if config.plugins.xtraEvent.searchMOD.value == lng.get(lang, '14'):
            logout(data="save - gehe zu currentCHEpgs")
            self.currentChEpgs()
        if config.plugins.xtraEvent.searchMOD.value == lng.get(lang, '13'):
            logout(data="save - gehe zu selBouquets")
            self.selBouquets()

    def deletfilesall(self):
        logout(data="delete Files")
        self.deletfilesposter()
        self.deletfilesbackdrop()
        self.deletfilesbanner()
        self.deletfilesinfos()
        self.deletfilesnoinfos()
        self.deletfileslogo()
        self.deletfilesinfossterne()
        self.deletfilesinfosomdbsterne()
        self.deletfilesinfosomdb()

    def deletfilesposter(self):
        logout(data="deletfilesposter")
        directoryposter = "{}poster".format(pathLoc)
        files = os.listdir(directoryposter)
        for file in files:
            file_path = os.path.join(directoryposter, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_poster()

    def deletfileslogo(self):
        logout(data="deletfileslogo")
        directoryposter = "{}logo".format(pathLoc)
        files = os.listdir(directoryposter)
        for file in files:
            file_path = os.path.join(directoryposter, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_logo()

    def deletfilesbackdrop(self):
        logout(data="deletfilesbackdrop")
        directorybackdrop = "{}backdrop".format(pathLoc)
        files = os.listdir(directorybackdrop)
        for file in files:
            file_path = os.path.join(directorybackdrop, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_backdrop()

    def deletfilesbanner(self):
        logout(data="deletfilesbanner")
        directorybanner = "{}banner".format(pathLoc)
        files = os.listdir(directorybanner)
        for file in files:
            file_path = os.path.join(directorybanner, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_banner()

    def deletfilesinfos(self):
        logout(data="deletfilesinfos")
        directoryinfos = "{}infos".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_infos()

    def deletfilesnoinfos(self):
        logout(data="deletfilesinfos")
        directoryinfos = "{}noinfos".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_infos()

    def deletfilesinfosomdb(self):
        logout(data="deletfilesinfosomdb")
        directoryinfos = "{}infosomdb".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_infos()

    def deletfilesinfosomdbsterne(self):
        logout(data="deletfilesinfosomdbsterne")
        directoryinfos = "{}infosomdbsterne".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_infos()

    def deletfilesinfossterne(self):
        logout(data="deletfilesinfossterne")
        directoryinfos = "{}infossterne".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_infos()

    def deletfiles(self):
        logout(data="deletfiles")
        directoryposter = "{}poster".format(pathLoc)
        files = os.listdir(directoryposter)
        for file in files:
            file_path = os.path.join(directoryposter, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directorybackdrop = "{}backdrop".format(pathLoc)
        files = os.listdir(directorybackdrop)
        for file in files:
            file_path = os.path.join(directorybackdrop, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directorybanner = "{}banner".format(pathLoc)
        files = os.listdir(directorybanner)
        for file in files:
            file_path = os.path.join(directorybanner, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directoryinfos = "{}infos".format(pathLoc)
        files = os.listdir(directoryinfos)
        for file in files:
            file_path = os.path.join(directoryinfos, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directorylogo = "{}logo".format(pathLoc)
        files = os.listdir(directorylogo)
        for file in files:
            file_path = os.path.join(directorylogo, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directoryinfosomdb = "{}infosomdb".format(pathLoc)
        files = os.listdir(directoryinfosomdb)
        for file in files:
            file_path = os.path.join(directoryinfosomdb, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directoryinfossterne = "{}infossterne".format(pathLoc)
        files = os.listdir(directoryinfossterne)
        for file in files:
            file_path = os.path.join(directoryinfossterne, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directoryinfosomdbsterne = "{}infosomdbsterne".format(pathLoc)
        files = os.listdir(directoryinfosomdbsterne)
        for file in files:
            file_path = os.path.join(directoryinfosomdbsterne, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        directoryinfosomdbrated = "{}infosomdbrated".format(pathLoc)
        files = os.listdir(directoryinfosomdbrated)
        for file in files:
            file_path = os.path.join(directoryinfosomdbrated, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.anzahlfiles_in_poster()
        self.anzahlfiles_in_backdrop()
        self.anzahlfiles_in_banner()
        self.anzahlfiles_in_infos()
        self.anzahlfiles_in_logo()
        logout(data="------------------ def delet")


    def currentChEpgs(self):
        logout(data="currentChEpgs")
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=str(log_message))

        events = None
        import NavigationInstance
        ref = NavigationInstance.instance.getCurrentlyPlayingServiceReference().toString()
        events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
        if events:
            try:
                n = config.plugins.xtraEvent.searchNUMBER.value
                titles = []
                for i in range(int(n)):
                    try:
                        title = events[i][4]
                        title = REGEX.sub('', title).strip()
                        titles.append(title)
                    except:
                        continue
                    if i == n:
                        break
                self.titles = list(dict.fromkeys(titles))
                start_new_thread(self.downloadEvents, ())
            except Exception as err:
                with open("/tmp/xtraEvent.log", "a+") as f:
                    f.write("currentChEpgs, %s\n"%(err))

    def selBouquets(self):
        logout(data="--------------------------------------------------------------------------------------------------- selBouquets")
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=str(log_message))

        if os.path.exists("{}bqts".format(pathLoc)):
            logout(data="-----------------------------------------------    selBouquets file exits")
            with open("{}bqts".format(pathLoc), "r") as f:
                logout(data="selBouquets open file")
                refs = f.readlines()
            nl = len(refs)
            eventlist=[]
            for i in range(nl):
                ref = refs[i]
                try:
                    events = epgcache.lookupEvent(['IBDCTSERNX', (ref, 1, -1, -1)])
                    n = config.plugins.xtraEvent.searchNUMBER.value
                    for i in range(int(n)):
                        title = events[i][4]

                        # hier live: entfernen
                        Name = title.replace('\xc2\x86', '').replace('\xc2\x87', '').replace("live: ", "").replace(
                            "LIVE ", "")
                        title = Name.replace("live: ", "").replace("LIVE ", "").replace("LIVE: ", "").replace("live ",
                                                                                                             "")
                        #logout(data="name live rausnehmen")
                        #logout(data=title)

                        # hier versuch name nur vor dem :
                        name1 = title.split(": ", 1)
                        Name = name1[0]
                        #logout(data="name   : abtrennen ")
                        #logout(data=Name)

                        title = Name
                        # -------------------------------



                        title = REGEX.sub('', title).strip()
                        eventlist.append(title)
                except:
                    pass
            self.titles = list(dict.fromkeys(eventlist))
            #----------------------------------------------- sollte ja thread sein -------------------------
            logout(data="--------------------------------  selBouquets zu downloadEvents")
            #start_new_thread(self.downloadEvents, ())
            import _thread
            _thread.start_new_thread(self.downloadEvents, ())
            logout(data="--------------------------------  selBouquets von downloadEvents zurueck")
            # ----------------------------------------------------------------------------------------------
        else:
            logout(data="-----------------------------------------------    selBouquets file not exits")

########################################################################################################################
    def downloadEvents(self):
        logout(data="-------------------------------------------------------------------------------------------------- downloadEvents")
        # geht wohl im thread nicht ----------------------------------------------------
        #caller_frame = inspect.currentframe().f_back
        #caller_name = inspect.getframeinfo(caller_frame).function
        #log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        #logout(data=str(log_message))

        dwnldFile=""
        self.title = ""
        self['progress'].setValue(0)
        lang = None
        now = datetime.now()
        st = now.strftime("%d/%m/%Y %H:%M:%S ")
        tmdb_poster_downloaded = 0
        tvdb_poster_downloaded = 0
        maze_poster_downloaded = 0
        fanart_poster_downloaded = 0
        tmdb_backdrop_downloaded = 0
        tvdb_backdrop_downloaded = 0
        fanart_backdrop_downloaded = 0
        banner_downloaded = 0
        extra_downloaded = 0
        extra2_downloaded = 0
        self.extra3_poster_downloaded = 0
        self.extra3_info_downloaded = 0
        info_downloaded = 0
        self.anzahldownloads = 0
        title_search = 0
        title = ""
        infs = {}
        imdb_id = None
        Year = ""
        Rating=""
        Rated=""
        glist=""
        Duration=""
        description=""
        Type=""

        # ------------------------------------------  hier def delete files einbauen
        logout(data="-------------------------------------------------- zu delete old files bei  1842 ")
        self.delete_oldfilesposter()
        self.delete_oldfilesbackdrop()
        self.delete_oldfilesbanner()
        self.delete_oldfilesinfos()
        self.delete_oldfilesnoinfos()
        self.delete_oldfilesinfosomdb()
        self.delete_oldfilesinfosomdbsterne()
        self.delete_oldfilesinfossterne()
        logout(data="-------------------------------------------------- zurueck von delete old files")
        #---------------------------------
        logout(data="xtra  on-off abfrage")
        if config.plugins.xtraEvent.onoff.value:
            logout(data="xtraEvent ist aktiv auf ON ")

            if config.plugins.xtraEvent.extra3.value == True:
                logout(data="--------------------------------------------------- Extra 3 ist an ")
                # elcinema(en) #################################################################

                Type = ""
                Genre = ""
                Language = ""
                Country = ""
                imdbRating = ""
                Rated = ""
                Duration = ""
                Year = ""
                Director = ""
                Writer = ""
                Actors = ""
                Plot = ""
                setime = ""
                try:
                    logout(data="extra3 true1")
                    if not os.path.exists("/tmp/urlo.html"):
                        logout(data="extra3 true1a")
                        url = "https://elcinema.com/en/tvguide/"
                        logout(data="extra3 true1a URL")
                        logout(data=str(url))
                        urlo = requests.get(url)
                        urlo = urlo.text.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', 'and').replace('(', '').replace(')', '')
                        #logout(data=str(urlo))             # info jede menge
                        with io.open("/tmp/urlo.html", "w", encoding="utf-8") as f:
                            f.write(urlo)
                            logout(data="extra3 true1a URL fertig")
                    if os.path.exists("/tmp/urlo.html"):
                        logout(data="extra3 true 1b")
                        with io.open("/tmp/urlo.html", "r", encoding="utf-8") as f:
                            urlor = f.read()
                            logout(data="extra3 urlor")
                            #logout(data=str(urlor))
                        titles = re.findall('<li><a title="(.*?)" href="/en/work', urlor)
                        #logout(data="extra3 true 1c")
                        logout(data="extra3 true 1c, Anzahl der Titel: " + str(len(titles)))
                    n = len(titles)
                except Exception as err:
                    logout(data="extra3 true 2")
                    with open("/tmp/xtraEvent.log", "a+") as f:
                        f.write("elcinema urlo, %s, %s\n"%(title, err))
                for title in titles:

                    try:
                        logout(data="download try")
                        title = REGEX.sub('', title).strip()
                        logout(data="download try title ")
                        logout(data=str(title))
                        dwnldFile = "{}poster/{}.jpg".format(pathLoc, title)
                        logout(data="download try dwnldFile save poster jpg")
                        logout(data=str(dwnldFile))
                        info_files = "{}infos/{}.json".format(pathLoc, title)
                        logout(data="download try info files save json ")
                        logout(data=str(info_files))
                        tid = re.findall('title="%s" href="/en/work/(.*?)/"'%title, urlor)[0]
                        logout(data="download try tid ist wohl die id aber nur fuers poster kein logo")
                        logout(data=str(tid))
                        self.setTitle(_("{}".format(title)))

                        if not os.path.exists(dwnldFile):
                            logout(data="download poster 370")
                            turl =	"https://elcinema.com/en/work/{}/".format(tid)
                            logout(data=str(turl))
                            jurlo = requests.get(turl.strip(), stream=True, allow_redirects=True, headers=headers)
                            jurlo = jurlo.text.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', 'and').replace('(', '').replace(')', '')
                            # poster elcinema
                            img = re.findall('<img src="(.*?).jpg" alt=""', jurlo)[0]
                            open(dwnldFile, "wb").write(requests.get("{}.jpg".format(img), stream=True, allow_redirects=True).content)
                            self['info'].setText("► {}, EXTRA3, POSTER".format(title.upper()))
                            self.extra3_poster_downloaded += 1
                            downloaded = self.extra3_poster_downloaded
                            self.prgrs(downloaded, n)
                            self.showPoster(dwnldFile)
                    except Exception as err:
                        with open("/tmp/xtraEvent.log", "a+") as f:
                            f.write("elcinema poster, %s, %s\n"%(title, err))
                    #info elcinema,
                    if not os.path.exists(info_files):
                        logout(data="download json 388")
                        turl =	"https://elcinema.com/en/work/{}/".format(tid)
                        logout(data=str(turl))
                        jurlo = requests.get(turl.strip(), stream=True, allow_redirects=True, headers=headers)
                        jurlo = jurlo.text.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', 'and').replace('(', '').replace(')', '')
                        try:
                            setime = urlor.partition('title="%s"'%title)[2].partition('</ul>')[0].strip()
                            setime = re.findall("(\d\d\:\d\d) (.*?) - (\d\d\:\d\d) (.*?)</li>", setime)
                            setime = setime[0][0]+setime[0][1]+" - "+setime[0][2]+setime[0][3]
                        except:
                            pass
                        try:
                            Category = jurlo.partition('<li>Category:</li>')[2].partition('</ul>')[0].strip()
                            Category = Category.partition('<li>')[2].partition('</li>')[0].strip()
                        except:
                            pass
                        try:
                            glist=[]
                            Genre = (jurlo.partition('<li>Genre:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")
                            for i in range(len(Genre)-1):
                                Genre = (jurlo.partition('<li>Genre:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")[i]
                                Genre = Genre.partition('">')[2].strip()
                                glist.append(Genre)
                        except:
                            pass
                        try:
                            llist=[]
                            Language = (jurlo.partition('<li>Language:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")
                            for i in range(len(Language)-1):
                                Language = (jurlo.partition('<li>Language:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")[i]
                                Language = Language.partition('">')[2].strip()
                                llist.append(Language)
                        except:
                            pass
                        try:
                            clist=[]
                            Country = (jurlo.partition('<li>Country:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")
                            for i in range(len(Country)-1):
                                Country = (jurlo.partition('<li>Country:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")[i]
                                Country = Country.partition('">')[2].strip()
                                clist.append(Country)
                        except:
                            pass
                        try:
                            Rating = re.findall("class='fa fa-star'></i> (.*?) </span><div", jurlo)[0]
                            Rated = jurlo.partition('<li>MPAA</li><li>')[2].partition('</li></ul></li>')[0].strip()
                            if Rated =="":
                                Rated = jurlo.partition('class="censorship purple" title="Censorship:')[2].partition('"><li>')[0].strip()
                        except:
                            pass
                        try:
                            Year = jurlo.partition('href="/en/index/work/release_year/')[2].partition('/"')[0].strip()
                        except:
                            pass
                        try:
                            Duration = re.findall("<li>(.*?) minutes</li>", jurlo)[0]
                        except:
                            pass
                        try:
                            dlist=[]
                            Director = (jurlo.partition('<li>Director:</li>')[2].partition('</ul>')[0]).strip().split('</a>')
                            for i in range(len(Director)-1):
                                Director = (jurlo.partition('<li>Director:</li>')[2].partition('</ul>')[0]).strip().split('</a>')[i]
                                Director = Director.partition('/">')[2].strip()
                                dlist.append(Director)
                        except:
                            pass
                        try:
                            wlist=[]
                            Writer = (jurlo.partition('<li>Writer:</li>')[2].partition('</ul>')[0]).strip().split('</a>')
                            for i in range(len(Writer)-1):
                                Writer = (jurlo.partition('<li>Writer:</li>')[2].partition('</ul>')[0]).strip().split('</a>')[i]
                                Writer = Writer.partition('/">')[2].strip()
                                wlist.append(Writer)
                        except:
                            pass
                        try:
                            calist=[]
                            Cast = (jurlo.partition('<li>Cast:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")
                            for i in range(len(Cast)-1):
                                Cast = (jurlo.partition('<li>Cast:</li>')[2].partition('</ul>')[0]).strip().split("</a> </li>")[i]
                                Cast = Cast.partition('">')[2].strip()
                                calist.append(Cast)
                        except:
                            pass
                        try:
                            Description1 = re.findall("<p>(.*?)<a href='#' id='read-more'>...Read more</a><span class='hide'>", jurlo)[0]
                            Description2 = re.findall("<a href='#' id='read-more'>...Read more</a><span class='hide'>(.*?)\.", jurlo)[0]
                            Description = "{}{}".format(Description1, Description2)
                        except:
                            try:
                                Description = re.findall("<p>(.*?)</p>", jurlo)[0]
                            except:
                                pass
                        try:
                            ej = {
                            "Title": "%s"%title,
                            "Start-End Time": "%s"%setime,
                            "Type": "%s"%Category,
                            "Year": "%s"%Year,
                            "imdbRating": "%s"%Rating,
                            "Rated": "%s"%Rated,
                            "Genre": "%s"%(', '.join(glist)),
                            "Duration": "%s min."%Duration,
                            "Language": "%s"%(', '.join(llist)),
                            "Country": "%s"%(', '.join(clist)),
                            "Director": "%s"%(', '.join(dlist)),
                            "Writer": "%s"%(', '.join(wlist)),
                            "Actors": "%s"%(', '.join(calist)),
                            "Plot": "%s"%Description,
                            }
                            open(info_files, "w").write(json.dumps(ej))

                            if os.path.exists(info_files):
                                self.extra3_info_downloaded += 1
                                downloaded = self.extra3_info_downloaded
                                self.prgrs(downloaded, n)
                                self['info'].setText("► {}, EXTRA3, INFO".format(title.upper()))
                            if os.path.exists(dwnldFile):
                                self.showPoster(dwnldFile)

                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("elcinema ej, %s, %s\n"%(title, err))
                    logout(data=" hier timeout von 1 sec ")
                    time.sleep(1)  # war 5 sec mal neuer versuch


            logout(data=" ------------------------------------------------------bqts in xtraevent - liste der titel zum downloaden")
            n = len(self.titles)
            self.anzahldownloads = n
            logout(data=str(n))
            logout(data=" ------------------------------------------------------ liste der titel zum downloaden")
            logout(data=str(self.titles))  # Hier wird die gesamte Liste self.titles ausgegeben , sind nicht doppelt drin
            # in selBouquets wir : split gemacht und alles zu Live

            logout(data=" ")
            for i in range(n):
                title = self.titles[i]
                title = title.strip()
                self.setTitle(_("{}".format(title)))

########################################################################################################################
# ----------------------------------------  hier anfang ablauf ----------------------
########################################################################################################################
                evntNm=title
                pstrNm = "{}poster/{}.jpg".format(pathLoc, title)
                logout(data=" 885 ---------------------------------------------- zu neue tmdb ablauf ---------------------------------------------- ")

########################################################################################################################
                self.download_tmdb(evntNm, pstrNm)
########################################################################################################################
                logout(data=" ------------------------------------ von neue tmdb ablauf zurueck ")

                logout(data=" ------------------------------------ ist Poster download auf ON ")

                if config.plugins.xtraEvent.poster.value == True:           # abfrage poster ja/nein
                    logout(data=str(config.plugins.xtraEvent.poster.value))
                    dwnldFile = "{}poster/{}.jpg".format(pathLoc, title)
                    logout(data=" Poster download JA , path")
                    logout(data=str(dwnldFile))

                    logout(data=" ------------------------------------ ist Poster download vom TMDB auf ON ")
                    if config.plugins.xtraEvent.tmdb.value == True:         # abfrage soll von tmdb geholt werden
                        logout(data=" Poster von Tmdb holen auf JA ")
                        if not os.path.exists(dwnldFile):                   # ist das poster schon vorhanden
                            logout(data="------------------------------------------------------------------------------- Poster file ist nicht vorhanden also download")



# --------------------------------------  suchen json info ---------------------------------------------------------------------------------------------------
                            try:                                            # das poster ist nicht vorhanden
                                srch = "movie"                              # wie gesucht wird , es gibt auch tv und movie
                                #srch = config.plugins.xtraEvent.searchType.value
                                logout(data=str(srch))
                                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
                                url_tmdbnew=url_tmdb
                                logout(data=" URL 1 title ")
                                logout(data=str(url_tmdb))

                                if config.plugins.xtraEvent.searchLang.value == True:
                                    logout(data=" URL ")
                                    url_tmdb += "&language={}".format(self.searchLanguage())          # nochmal anfragen mir language
                                    url_tmdblng = url_tmdb
                                    logout(data=" URL language")
                                    logout(data=str(url_tmdblng))

                                    # abfrage ist total result 0 keine json vorhanden dann nochmal anfragen
                                    response = requests.get(url_tmdblng)
                                    data = response.json()
                                    total_results = data.get("total_results", 0)
                                else:
                                    response = requests.get(url_tmdbnew)
                                    data = response.json()
                                    total_results = data.get("total_results", 0)

                                # abfrage ist total result 0 keine json vorhanden dann nochmal anfragen

                                if total_results == 0:
                                    logout(data=" json  total results ist 0 keine daten im tv json")
                                    url_tmdb= "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote)
                                    url_tmdblng = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote)
                                    logout(data=" URL 2 ohne title")
                                    logout(data=str(url_tmdb))
                                # ------------------------  check od daten ok sind total resulst muss groesser 0 sein

                                    response = requests.get(url_tmdblng)
                                    data = response.json()
                                    total_results = data.get("total_results", 0)
                                    logout(data=" json total results vom json")
                                    logout(data=str(total_results))


                                    if total_results == 0:
                                        logout(data=" json total results ist 0 keine daten im json")
                                        response = requests.get(url_tmdb)
                                        data = response.json()
                                        total_results = data.get("total_results", 0)
                                        logout(data=" json total results vom json")
                                        logout(data=str(total_results))
                                        if total_results == 0:
                                            logout(data=" json total results ist 0 keine daten im json")
                                    else:
                                        logout(data=" json total results daten im json")


# ------------------------------------------------- wenn mit multi nichts gefunden dann nochmal mit tv suchen -----------------------------------------------
                                    if srch == "multi":
                                        logout(data=" nochmal anfragen mit tv")
                                        srch = "tv"
                                        logout(data=str(srch))
                                        url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
                                        url_tmdbnew = url_tmdb
                                        logout(data=" URL 1 title ")
                                        logout(data=str(url_tmdb))

                                        if config.plugins.xtraEvent.searchLang.value == True:
                                            logout(data=" URL ")
                                            url_tmdb += "&language={}".format(
                                                self.searchLanguage())  # nochmal anfragen mir language
                                            url_tmdblng = url_tmdb
                                            logout(data=" URL language")
                                            logout(data=str(url_tmdblng))

                                            # abfrage ist total result 0 keine json vorhanden dann nochmal anfragen
                                            response = requests.get(url_tmdblng)
                                            data = response.json()
                                            total_results = data.get("total_results", 0)
                                        else:
                                            response = requests.get(url_tmdbnew)
                                            data = response.json()
                                            total_results = data.get("total_results", 0)

                                        # abfrage ist total result 0 keine json vorhanden dann nochmal anfragen

                                        if total_results == 0:
                                            logout(data=" json  total results ist 0 keine daten im tv json")
                                            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(
                                                srch, tmdb_api, quote)
                                            url_tmdblng = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(
                                                srch, tmdb_api, quote)
                                            logout(data=" URL 2 ohne title")
                                            logout(data=str(url_tmdb))
                                            # ------------------------  check od daten ok sind total resulst muss groesser 0 sein

                                            response = requests.get(url_tmdblng)
                                            data = response.json()
                                            total_results = data.get("total_results", 0)
                                            logout(data=" json total results vom json")
                                            logout(data=str(total_results))

                                            if total_results == 0:
                                                logout(data=" json total results ist 0 keine daten im json")
                                                response = requests.get(url_tmdb)
                                                data = response.json()
                                                total_results = data.get("total_results", 0)
                                                logout(data=" json total results vom json")
                                                logout(data=str(total_results))
                                                if total_results == 0:
                                                    logout(data=" json total results ist 0 keine daten im json")
                                            else:
                                                logout(data=" json total results daten im json")

                                # -------------------------------------------------------------------------------------------------------------------------------------------

                                else:
                                    # -----------------------   als json datei speichern
                                    response = requests.get(url_tmdb)
                                    if response.status_code == 200:
                                        logout(data=" json json info OK titel und path")
                                        # Dateipfad im temporären Verzeichnis erstellen
                                        #file_path = os.path.join('/tmp', 'poster.json')
                                        logout(data=str(title))
                                        logout(data=str(pathLoc))
                                        file_path = "{}infos/{}.json".format(pathLoc, title)
                                        logout(data=" json path kpl zum schreiben ")
                                        logout(data=str(file_path))

                                        # JSON-Daten speichern
                                        with open(file_path, 'w') as file:
                                            json.dump(response.json(), file)
                                            logout(data=" json geschrieben ")
                                    # --------------------------  file geschrieben wenn auch keine info drin ist -------------------------------
                                    # -------------------------- jetzt poster url suchen  wird aus dem results 0 geholt --------------------------------------------------------
                                    poster = ""
                                    id_nummer = ""

                                    poster = requests.get(url_tmdb).json()['results'][0]['poster_path']
                                    id_nummer = requests.get(url_tmdb).json()['results'][0]['id']
                                    #abfrage logo download , wenn nein id nummer auf None dadurch kein download

                                    logout(data=" poster url aus json holen ")
                                    logout(data=str(poster))
                                    #original_title = requests.get(url_tmdb).json()['results'][0]['poster_path']
                                    #logout(data=str(original_title))
                                    p_size = config.plugins.xtraEvent.TMDBpostersize.value
                                    logout(data=str(p_size))
                                    logout(data=" URL start download poster")
                                    url = "https://image.tmdb.org/t/p/{}{}".format(p_size, poster)
                                    logout(data=str(url))
                                    logout(data=" URL ende download von dieser url poster  ")


                                    if poster != "":
                                        logout(data="----------------------------------------------- poster url vorhanden ")
                                        open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                        #time.sleep (5)
                                    if os.path.exists(dwnldFile):
                                        logout(data="----------------------------------------------- if os.path exist download hochzaehlen")
                                        self['info'].setText("►  {}, TMDB, POSTER".format(title.upper()))
                                        tmdb_poster_downloaded += 1
                                        downloaded = tmdb_poster_downloaded
                                        self.prgrs(downloaded, n)


                                    backdrop = ""
                                    backdrop = requests.get(url_tmdb).json()['results'][0]['backdrop_path']
                                    p_size = 300
                                    logout(data=" URL start download backdrop")
                                    url = "https://image.tmdb.org/t/p/w{}{}".format(p_size, backdrop)
                                    logout(data=str(url))
                                    logout(data=" URL ende download von dieser url backdrop ")

                                    dwnldFile_backdrop = "{}backdrop/{}.jpg".format(pathLoc, title)
                                    logout(data=str(dwnldFile_backdrop))
                                    if backdrop != "":
                                        logout(data="----------------------------------------------- poster vorhanden ")
                                        open(dwnldFile_backdrop, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)


                                    if os.path.exists(dwnldFile):
                                        logout(data="----------------------------------------------- if os.path exist")
                                        self['info'].setText("►  {}, TMDB, POSTER".format(title.upper()))
                                        tmdb_backdrop_downloaded += 1
                                        downloaded = tmdb_backdrop_downloaded
                                        self.prgrs(downloaded, n)


                                    logout(data=" ------------------------------------------------ abfrage Logo Download -------------------------------- ")
                                    logout(data=str(config.plugins.xtraEvent.logoFiles.value))
                                    if config.plugins.xtraEvent.logoFiles.value == False:
                                        logout(data=" id nummer auf None ")
                                        id_nummer = ""
                                    logout(data=" id nummer ist ")
                                    logout(data=str(id_nummer))
                                    # ------------------------------------------ versuch logo ----------------------------------------------------------------
                                    if id_nummer != "":
                                        logout(data="")
                                        logout(data="-------------------------------------------------------------------------------------------------- Gefundene id nummer:")
                                        logout(data=str(id_nummer))
                                        lng = self.searchLanguage()
                                        logout(data=str(lng))
                                        url_tmdb = "https://api.themoviedb.org/3/movie/{}/images?api_key={}".format(id_nummer, tmdb_api)
                                        logout(data=(url_tmdb))
                                        # so url - http://api.themoviedb.org/3/movie/672/images?api_key=3c3efcf47c3577558812bb9d64019d65
                                        # json laden in data
                                        response = requests.get(url_tmdb)
                                        data = response.json()
                                        logout(data="check json daten")

                                        if "id" in data and data["id"] == id_nummer:
                                            logout(data="json hat eine id")
                                            logout(data=str(lng))
                                            if not data["logos"]:
                                                logout(data="json hat keine logo daten")
                                            else:
                                                logout(data="json hat infos daten")
                                                for file_path in data["logos"]:

                                                    if file_path["iso_639_1"] == lng:
                                                        url_logo = file_path["file_path"]
                                                        logout(data="logo")
                                                        logout(data=url_logo)
                                                        break
                                                else:
                                                    # Wenn kein deutsches logo gefunden wurde, nach einem ohne Sprachcode suchen
                                                    for file_path in data["logos"]:
                                                        if file_path["iso_639_1"] == "en":
                                                            url_logo = file_path["file_path"]
                                                            # Weitere Verarbeitung des Datei-Pfads
                                                            logout(data="url Logo ohne sprache gefunden")
                                                            logout(data=url_logo)
                                                            break
                                                    else:
                                                        url_logo = None
                                                        logout(
                                                            data="Kein deutsches oder sprachunabhaengiges logo gefunden.")
                                                logosize = "300"
                                                if not url_logo == None:
                                                    pathLogo = "{}logo/".format(pathLoc)
                                                    url_logo_down = "https://image.tmdb.org/t/p/w{}{}".format(logosize, url_logo)
                                                    logout(data=str(url_logo_down))
                                                    logout(data="logo - open file")
                                                    dwn_logo = pathLogo + "{}.png".format(title)
                                                    logout(data=str(dwn_logo))
                                                    logout(data="--------------------------------------------------------------------------------------- logo - zu save")
                                                    self.savePoster(dwn_logo, url_logo_down)
                                                    logout(data="--------------------------------------------------------------------------------------- logo - von save zurueck ende logo_path")
                                                    dwnldFile = dwn_logo
                                                    self.showLogo(dwnldFile)
                                                    logout(data="---------------------------------------------------------------------------------------- logo ende")
                                                    logout(data="")
                                                else:
                                                    logout(data="")
# ----------------------------------------------------------------------------------------------------------------------
                                        self.showPoster(dwnldFile)
                                        #continue
                                    try:
                                        logout(data=" poster try ")
                                        img = Image.open(dwnldFile)
                                        img.verify()
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            logout(data=" poster deleted xtraEvent file ")
                                            f.write("deleted tmdb poster: %s.jpg\n"%title)
                                        try:
                                            logout(data=" poster remove ")
                                            os.remove(dwnldFile)
                                        except:
                                            pass


                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("tmdb poster, %s, %s\n"%(title, err))

                        logout(data="---------------------------------------------------------------- Poster file vorhanden download fertig ")
        # ---------------------- abfrage if file schon vorhanden ein download reicht ja ---------------------------------------------
        # tvdb_Poster() ######################## wenn file vorhanden hier nicht mehr noetig #########################################

                    logout(data=" ------------------------------------------------------------------ Poster tvdb Download auf ON")
                    if config.plugins.xtraEvent.tvdb.value == True:
                        logout(data=" Poster download tvdb")
                        try:
                            img = Image.open(dwnldFile)
                            logout(data=" Poster img tvdb")
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                logout(data=" Poster tvdb deleted 659")
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                logout(data=" Poster tvdb remove")
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            logout(data=" Poster dwnldfile ist nicht vorhanden")
                            try:
                                logout(data="url 596")
                                url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
                                logout(data=str(url_tvdb))
                                logout(data="url tvdb")
                                url_read = requests.get(url_tvdb).text
                                series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
                                if series_id:
                                    logout(data="url id")
                                    url_tvdb = "https://thetvdb.com/api/{}/series/{}/{}".format(tvdb_api, series_id, self.searchLanguage())
                                    logout(data=str(url_tvdb))
                                    logout(data="url tvdb")
                                    url_read = requests.get(url_tvdb).text




                                    poster = ""
                                    poster = re.findall('<poster>(.*?)</poster>', url_read)[0]

                                    if poster != '':
                                        logout(data="url artworks ")
                                        url = "https://artworks.thetvdb.com/banners/{}".format(poster)
                                        logout(data=str(url))
                                        logout(data="url ")
                                        if config.plugins.xtraEvent.TVDBpostersize.value == "thumbnail":
                                            url = url.replace(".jpg", "_t.jpg")
                                            logout(data=str(url))
                                        open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                        if os.path.exists(dwnldFile):
                                            self['info'].setText("►  {}, TVDB, POSTER".format(title.upper()))
                                            tvdb_poster_downloaded += 1
                                            downloaded = tvdb_poster_downloaded
                                            self.prgrs(downloaded, n)
                                            self.showPoster(dwnldFile)
                                            #continue
                                            try:
                                                img = Image.open(dwnldFile)
                                                img.verify()
                                            except Exception as err:
                                                with open("/tmp/xtraEvent.log", "a+") as f:
                                                    f.write("deleted tvdb poster: %s.jpg\n"%title)
                                                try:
                                                    os.remove(dwnldFile)
                                                except:
                                                    pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("tvdb poster, %s, %s\n"%(title, err))
        # maze_Poster() #################################################################
                    if config.plugins.xtraEvent.maze.value == True:

                        logout(data="----------------------------------------------------------------------------------- maze ")
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            url_maze = "http://api.tvmaze.com/search/shows?q={}".format(quote(title))
                            logout(data=str(url_maze))
                            try:
                                url = requests.get(url_maze).json()[0]['show']['image']['medium']
                                logout(data=str(url))
                                open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                if os.path.exists(dwnldFile):
                                    self['info'].setText("►  {}, MAZE, POSTER".format(title.upper()))
                                    maze_poster_downloaded += 1
                                    downloaded = maze_poster_downloaded
                                    self.prgrs(downloaded, n)
                                    self.showPoster(dwnldFile)
                                    try:
                                        img = Image.open(dwnldFile)
                                        img.verify()
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            f.write("deleted maze poster: %s.jpg\n"%title)
                                        try:
                                            os.remove(dwnldFile)
                                        except:
                                            pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("maze poster, %s, %s\n"%(title, err))
        # fanart_Poster() #################################################################
                    if config.plugins.xtraEvent.fanart.value == True:
                        logout(data="----------------------------------------------------------------------------------  fanart")
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            try:
                                url = None
                                #srch = "multi"
                                srch = config.plugins.xtraEvent.searchType.value
                                logout(data="fanart tmdb 810")
                                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
                                logout(data=str(url_tmdb))
                                bnnr = requests.get(url_tmdb, verify=False).json()
                                tmdb_id = (bnnr['results'][0]['id'])
                                if tmdb_id:
                                    m_type = (bnnr['results'][0]['media_type'])
                                    if m_type == "movie":
                                        m_type = (bnnr['results'][0]['media_type'])
                                        m_type = "{}+s".format(m_type)
                                    else:
                                        mm_type = m_type
                                    logout(data="fanart maze 822")
                                    url_maze = "http://api.tvmaze.com/singlesearch/shows?q={}".format(quote(title))
                                    logout(data=str(url_maze))
                                    mj = requests.get(url_maze, verify=False).json()
                                    tvdb_id = (mj['externals']['thetvdb'])
                                    if tvdb_id:
                                        logout(data="fanart fanart 828")
                                        url_fanart = "https://webservice.fanart.tv/v3/{}/{}?api_key={}".format(m_type, tvdb_id, fanart_api)
                                        logout(data=str(url_fanart))
                                        fjs = requests.get(url_fanart, verify=False).json()
                                        if fjs:
                                            if m_type == "movies":
                                                mm_type = (bnnr['results'][0]['media_type'])
                                            else:
                                                mm_type = m_type
                                            if mm_type == "tv":
                                                url = fjs['tvposter'][0]['url']
                                            elif mm_type == "movies":
                                                url = fjs['movieposter'][0]['url']
                                            if url:
                                                open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True, verify=False).content)
                                            if os.path.exists(dwnldFile):
                                                self['info'].setText("►  {}, FANART, POSTER".format(title.upper()))
                                                fanart_poster_downloaded += 1
                                                downloaded = fanart_poster_downloaded
                                                self.prgrs(downloaded, n)
                                                self.showPoster(dwnldFile)
                                                try:
                                                    img = Image.open(dwnldFile)
                                                    img.verify()
                                                except Exception as err:
                                                    with open("/tmp/xtraEvent.log", "a+") as f:
                                                        f.write("deleted fanart poster: %s.jpg\n"%title)
                                                    try:
                                                        os.remove(dwnldFile)
                                                    except:
                                                        pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("fanart poster, %s, %s\n"%(title, err))
                logout(data="------------------------------------------------------------------------------------------ backdrop abfrage ob downloaden auf ON")
                logout(data=str(config.plugins.xtraEvent.backdrop.value))


    #                                       backdrop() #################################################################


                if config.plugins.xtraEvent.backdrop.value == True:
                    logout(data="backdrop ON downloaden")
                    dwnldFile = "{}backdrop/{}.jpg".format(pathLoc, title)
                    if config.plugins.xtraEvent.extra.value == True:
                        logout(data="extra ja downloaden ")
                        if not os.path.exists(dwnldFile):
                            try:
                                logout(data="backdrop extra url ")
                                url = "http://capi.tvmovie.de/v1/broadcasts/search?q={}&page=1&rows=1".format(title.replace(" ", "+"))
                                logout(data=str(url))
                                logout(data="backdrop extra url ")
                                try:
                                    logout(data="url ")
                                    url = requests.get(url).json()['results'][0]['images'][0]['filepath']['android-image-320-180']
                                    logout(data=str(url))
                                    logout(data="url ")
                                except:
                                    pass
                                open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                if os.path.exists(dwnldFile):
                                    self['info'].setText("►  {}, EXTRA, BACKDROP".format(title.upper()))
                                    extra_downloaded += 1
                                    downloaded = extra_downloaded
                                    self.prgrs(downloaded, n)
                                    self.showBackdrop(dwnldFile)
                                    try:
                                        img = Image.open(dwnldFile)
                                        img.verify()
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            f.write("deleted extra poster: %s.jpg\n"%title)
                                        try:
                                            os.remove(dwnldFile)
                                        except:
                                            pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("extra, %s, %s\n"%(title, err))


                    if config.plugins.xtraEvent.tmdb_backdrop.value == True:
                        logout(data="---------------------------------------------------------------------------------- backdrop tmdb ON")
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            #srch = "multi"
                            srch = config.plugins.xtraEvent.searchType.value
                            logout(data="url ")
                            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
                            logout(data="url ")
                            logout(data=str(url_tmdb))
                            if config.plugins.xtraEvent.searchLang.value:
                                logout(data="url ")
                                url_tmdb += "&language={}".format(self.searchLanguage())
                                logout(data="url ")
                                logout(data=str(url_tmdb))
                            try:
                                backdrop = requests.get(url_tmdb).json()['results'][0]['backdrop_path']
                                if backdrop:
                                    backdrop_size = config.plugins.xtraEvent.TMDBbackdropsize.value
                                    # backdrop_size = "w300"
                                    logout(data="url ")
                                    url = "https://image.tmdb.org/t/p/{}{}".format(backdrop_size, backdrop)
                                    logout(data="url ")
                                    logout(data=str(url))
                                    open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                    if os.path.exists(dwnldFile):
                                        self['info'].setText("►  {}, TMDB, BACKDROP".format(title.upper()))
                                        tmdb_backdrop_downloaded += 1
                                        downloaded = tmdb_backdrop_downloaded
                                        self.prgrs(downloaded, n)
                                        self.showBackdrop(dwnldFile)
                                        try:
                                            img = Image.open(dwnldFile)
                                            img.verify()
                                        except Exception as err:
                                            with open("/tmp/xtraEvent.log", "a+") as f:
                                                f.write("deleted tmdb backdrop: %s.jpg\n"%title)
                                            try:
                                                os.remove(dwnldFile)
                                            except:
                                                pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("tmdb-backdrop, %s, %s\n"%(title, err))


                    if config.plugins.xtraEvent.tvdb_backdrop.value == True:
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            try:
                                logout(data="url ")
                                url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
                                logout(data="url ")
                                logout(data=str(url_tvdb))
                                url_read = requests.get(url_tvdb).text
                                series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
                                if series_id:
                                    logout(data="url ")
                                    url_tvdb = "https://thetvdb.com/api/{}/series/{}/{}.xml".format(tvdb_api, series_id, self.searchLanguage())
                                    logout(data="url ")
                                    logout(data=str(url_tvdb))
                                    url_read = requests.get(url_tvdb).text
                                    backdrop = re.findall('<fanart>(.*?)</fanart>', url_read)[0]
                                    if backdrop:
                                        logout(data="url ")
                                        url = "https://artworks.thetvdb.com/banners/{}".format(backdrop)
                                        logout(data="url ")
                                        logout(data=str(url))
                                        if config.plugins.xtraEvent.TVDBbackdropsize.value == "thumbnail":
                                            url = url.replace(".jpg", "_t.jpg")
                                        open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                        if os.path.exists(dwnldFile):
                                            self['info'].setText("►  {}, TVDB, BACKDROP".format(title.upper()))
                                            tvdb_backdrop_downloaded += 1
                                            downloaded = tvdb_backdrop_downloaded
                                            self.prgrs(downloaded, n)
                                            self.showBackdrop(dwnldFile)
                                            try:
                                                img = Image.open(dwnldFile)
                                                img.verify()
                                            except Exception as err:
                                                with open("/tmp/xtraEvent.log", "a+") as f:
                                                    f.write("deleted tvdb backdrop: %s.jpg\n"%title)
                                                try:
                                                    os.remove(dwnldFile)
                                                except:
                                                    pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("tvdb-backdrop, %s, %s\n"%(title, err))


                    if config.plugins.xtraEvent.extra2.value == True:
                        logout(data="")
                        logout(data="---------------------------------------------------------------------------------- download Extra2 ist ON")
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            try:
                                logout(data="---------------------------------------------------extra2 download bing")
                                logout(data="url ")
                                url = "https://www.bing.com/images/search?q={}".format(title.replace(" ", "+"))
                                logout(data="url ")
                                logout(data=str(url))
                                if config.plugins.xtraEvent.PB.value == "posters":
                                    logout(data="url ")
                                    url += "+poster"
                                else:
                                    logout(data="url ")
                                    url += "+backdrop"
                                logout(data="url hier ca 500 ms 1000")
                                ff = requests.get(url, stream=True, headers=headers).text
                                logout(data="url ")
                                p = ',&quot;murl&quot;:&quot;(.*?)&'
                                logout(data="url ")
                                url = re.findall(p, ff)[0]
                                logout(data="url ")
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    logout(data="url 1009")
                                    f.write("bing-backdrop, %s, %s\n"%(title, err))
                                try:
                                    logout(data="---------------------------------------------------extra2 download google")
                                    logout(data="url ")
                                    url = "https://www.google.com/search?q={}&tbm=isch&tbs=sbd:0".format(title.replace(" ", "+"))
                                    logout(data="url 1014")
                                    logout(data=str(url))
                                    if config.plugins.xtraEvent.PB.value == "posters":
                                        logout(data="url 1017")
                                        url += "+poster"
                                    else:
                                        logout(data="url ")
                                        url += "+backdrop"
                                    logout(data="url 1022")
                                    ff = requests.get(url, stream=True, headers=headers).text
                                    logout(data="url 1024")
                                    p = re.findall('\],\["https://(.*?)",\d+,\d+]', ff)[0]
                                    logout(data="url 1026")
                                    url = "https://{}".format(p)
                                    logout(data="url 1028")
                                except Exception as err:
                                    with open("/tmp/xtraEvent.log", "a+") as f:
                                        logout(data="google open ")
                                        f.write("google-backdrop, %s, %s\n"%(title, err))
                            try:
                                logout(data="try extra2 ")
                                with open(dwnldFile, 'wb') as f:
                                    f.write(requests.get(url, stream=True, allow_redirects=True).content)
                                if os.path.exists(dwnldFile):
                                    logout(data="try extra2 ")
                                    self['info'].setText("►  {}, EXTRA2, BACKDROP".format(title.upper()))
                                    logout(data="try extra2 ")
                                    extra2_downloaded += 1
                                    downloaded = extra2_downloaded
                                    self.prgrs(downloaded, n)
                                    logout(data="try extra2 ")
                                    self.showBackdrop(dwnldFile)
                                    logout(data="try extra2 ")
                                    try:
                                        img = Image.open(dwnldFile)
                                        logout(data="verivy extra2 ")
                                        img.verify()
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            logout(data="deleted extra2 ")
                                            f.write("deleted extra2 backdrop: %s.jpg\n"%title)
                                        try:
                                            logout(data="remove extra2 ")
                                            #os.remove(dwnldFile)
                                        except:
                                            pass
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("extra2 backdrop, %s, %s\n"%(title, err))

    # banner() #################################################################
                if config.plugins.xtraEvent.banner.value == True:
                    logout(data="------------------------------------------------------------------- Banner download ist ON")
                    dwnldFile = "{}banner/{}.jpg".format(pathLoc, title)
                    try:
                        img = Image.open(dwnldFile)
                        img.verify()
                    except Exception as err:
                        with open("/tmp/xtraEvent.log", "a+") as f:
                            f.write("deleted : %s.jpg\n"%title)
                        try:
                            os.remove(dwnldFile)
                        except:
                            pass
                    if config.plugins.xtraEvent.tvdb_banner.value == True:
                        if not os.path.exists(dwnldFile):
                            try:
                                banner_img = ""
                                url = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(quote(title))
                                url = requests.get(url).text
                                banner_img = re.findall('<banner>(.*?)</banner>', url, re.I)[0]
                                if banner_img:
                                    url = "https://artworks.thetvdb.com{}".format(banner_img)
                                    if url:
                                        open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True).content)
                                        if os.path.exists(dwnldFile):
                                            self['info'].setText("►  {}, TVDB, BANNER".format(title.upper()))
                                            banner_downloaded += 1
                                            downloaded = banner_downloaded
                                            self.prgrs(downloaded, n)
                                            self.showBanner(dwnldFile)
                                            try:
                                                img = Image.open(dwnldFile)
                                                img.verify()
                                            except Exception as err:
                                                with open("/tmp/xtraEvent.log", "a+") as f:
                                                    f.write("deleted extra2 backdrop: %s.jpg\n"%title)
                                                try:
                                                    os.remove(dwnldFile)
                                                except:
                                                    pass
                                            scl = 1
                                            im = Image.open(dwnldFile)
                                            scl = config.plugins.xtraEvent.TVDB_Banner_Size.value
                                            im1 = im.resize((im.size[0] // int(scl), im.size[1] // int(scl)), Image.ANTIALIAS)
                                            im1.save(dwnldFile)
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("tvdb banner, %s, %s\n"%(title, err))
                    if config.plugins.xtraEvent.fanart_banner.value == True:
                        try:
                            img = Image.open(dwnldFile)
                            img.verify()
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("deleted : %s.jpg\n"%title)
                            try:
                                os.remove(dwnldFile)
                            except:
                                pass
                        if not os.path.exists(dwnldFile):
                            try:
                                url = "https://api.themoviedb.org/3/search/multi?api_key={}&query={}".format(tmdb_api, quote(title))
                                jp = requests.get(url, verify=False).json()
                                tmdb_id = (jp['results'][0]['id'])
                                print(tmdb_id)
                                if tmdb_id:
                                    m_type = (jp['results'][0]['media_type'])
                                    if m_type == "movie":
                                        m_type = (jp['results'][0]['media_type'])
                                        m_type = "{}+s".format(m_type)
                                    else:
                                        mm_type = m_type
                                if m_type == "movies":
                                    url = "https://webservice.fanart.tv/v3/{}/{}?api_key={}".format(m_type, tmdb_id, fanart_api)
                                    fjs = requests.get(url, verify=False, timeout=5).json()
                                    url = fjs["moviebanner"][0]["url"]
                                    if url:
                                        open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True, verify=False, timeout=5).content)
                                        if os.path.exists(dwnldFile):
                                            self['info'].setText("►  {}, FANART, BANNER".format(title.upper()))
                                            banner_downloaded += 1
                                            downloaded = banner_downloaded
                                            self.prgrs(downloaded, n)
                                            self.showBanner(dwnldFile)
                                            try:
                                                img = Image.open(dwnldFile)
                                                img.verify()
                                            except Exception as err:
                                                with open("/tmp/xtraEvent.log", "a+") as f:
                                                    f.write("deleted fanart banner: %s.jpg\n"%title)
                                                try:
                                                    os.remove(dwnldFile)
                                                except:
                                                    pass
                                            scl = 1
                                            im = Image.open(dwnldFile)
                                            scl = config.plugins.xtraEvent.FANART_Banner_Size.value
                                            im1 = im.resize((im.size[0] // int(scl), im.size[1] // int(scl)), Image.ANTIALIAS)
                                            im1.save(dwnldFile)
                                else:
                                    try:
                                        url_maze = "http://api.tvmaze.com/singlesearch/shows?q={}".format(quote(title))
                                        mj = requests.get(url_maze, verify=False).json()
                                        tvdb_id = mj['externals']['thetvdb']
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            f.write("fanart maze banner2, %s, %s\n"%(title, err))
                                    try:
                                        if tvdb_id:
                                            url = "https://webservice.fanart.tv/v3/tv/{}?api_key={}".format(tvdb_id, fanart_api)
                                            fjs = requests.get(url, verify=False, timeout=5).json()
                                            url = fjs["tvbanner"][0]["url"]
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            f.write("fanart banner3, %s, %s\n"%(title, err))
                                    try:
                                        if url:
                                            open(dwnldFile, 'wb').write(requests.get(url, stream=True, allow_redirects=True, verify=False).content)
                                            if os.path.exists(dwnldFile):
                                                self['info'].setText("►  {}, FANART, BANNER".format(title.upper()))
                                                banner_downloaded += 1
                                                downloaded = banner_downloaded
                                                self.prgrs(downloaded, n)
                                                self.showBanner(dwnldFile)
                                                try:
                                                    img = Image.open(dwnldFile)
                                                    img.verify()
                                                except Exception as err:
                                                    with open("/tmp/xtraEvent.log", "a+") as f:
                                                        f.write("deleted fanart banner: %s.jpg\n"%title)
                                                    try:
                                                        os.remove(dwnldFile)
                                                    except:
                                                        pass
                                                scl = 1
                                                im = Image.open(dwnldFile)
                                                scl = config.plugins.xtraEvent.FANART_Banner_Size.value
                                                im1 = im.resize((im.size[0] // int(scl), im.size[1] // int(scl)), Image.ANTIALIAS)
                                                im1.save(dwnldFile)
                                    except Exception as err:
                                        with open("/tmp/xtraEvent.log", "a+") as f:
                                            f.write("fanart banner4 end, %s, %s\n"%(title, err))
                            except Exception as err:
                                with open("/tmp/xtraEvent.log", "a+") as f:
                                    f.write("fanart maze banner1, %s, %s\n"%(title, err))
# infos #################################################################
                if config.plugins.xtraEvent.info.value == True:
                    logout(data=" --------------------------------------------------------------------------------------  download info ist ON")
                    Title=None
                    Type = None
                    Genre = None
                    Language = None
                    Country = None
                    imdbRating = None
                    imdbID = None
                    Rated = None
                    Duration = None
                    Year = None
                    Released=None
                    Director = None
                    Writer = None
                    Actors = None
                    Awards=None
                    Plot = ""
                    Description = None
                    Rating = ""
                    glist=[]
                    data = {}



                    info_files = "{}infosomdb/{}.json".format(pathLoc, title)
                    if config.plugins.xtraEvent.omdbAPI.value:
                        omdb_api_input = config.plugins.xtraEvent.omdbAPI.value
                        logout(data="omdb_apis Eingabe")
                        logout(data=str(omdb_api_input))
                        omdb_apis = [str(omdb_api_input)]
                        logout(data=str(omdb_apis))
                    else:
                        logout(data="omdb_apis default")
                        omdb_apis = ["a8834925", "550a7c40", "8ec53e6b"]                 # kann schnell sein das limit erreicht zum download weil alle nutzen
						
                    if not os.path.exists(info_files):
                        logout(data=" -----------------  info no json 1184 -----------------------------------")
                        try:
                            try:
                                #srch = "multi"
                                srch = config.plugins.xtraEvent.searchType.value
                                logout(data="url")
                                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(title))
                                logout(data="url")
                                logout(data=str(url_tmdb))
                                title = requests.get(url_tmdb).json()['results'][0]['original_title']   # ?????? warum
                            except:
                                pass
                            for omdb_api in omdb_apis:                                              # kann schnell sein das limit erreicht zum download weil alle nutzen
                                try:
                                    logout(data="urlstartomdb")
                                    logout(data=str(omdb_apis))
                                    logout(data=str(omdb_api))
                                    url = "http://www.omdbapi.com/?apikey={}&t={}".format(omdb_api, title)
                                    logout(data="url ombd ")
                                    logout(data=str(url))
                                    info_omdb = requests.get(url, timeout=5)
                                    if info_omdb.status_code == 200:
                                        logout(data=" -----------------  omdb json gefunden -----------------------------------")
                                        Title = info_omdb.json()["Title"]
                                        Year = info_omdb.json()["Year"]
                                        Rated = info_omdb.json()["Rated"]
                                        Duration = info_omdb.json()["Runtime"]
                                        Released = info_omdb.json()["Released"]
                                        logout(data="url variablen ")
                                        Genre = info_omdb.json()["Genre"]
                                        Director = info_omdb.json()["Director"]
                                        Writer = info_omdb.json()["Writer"]
                                        Actors = info_omdb.json()["Actors"]
                                        if not config.plugins.xtraEvent.searchLang.value:
                                            Plot = info_omdb.json()["Plot"]
                                        logout(data="url variablen 2")
                                        Country = info_omdb.json()["Country"]
                                        Awards = info_omdb.json()["Awards"]
                                        imdbRating = info_omdb.json()["imdbRating"]
                                        imdbID = info_omdb.json()["imdbID"]
                                        Type = info_omdb.json()["Type"]
                                        logout(data="url variablen 3")
                                        #                                                      save json datei in infosomdb

                                        # Speichere die JSON-Datei in infosomdb
                                        info_files = "{}infosomdb/{}.json".format(pathLoc, title)
                                        logout(data=str(info_files))
                                        # Stelle sicher, dass der Zielordner existiert
                                        os.makedirs(os.path.dirname(info_files), exist_ok=True)

                                        # Schreibe die Daten in die Ausgabedatei
                                        with open(info_files, "w") as f:
                                            json.dump(info_omdb.json(), f, indent=4)
                                            logout(data="url ombd json schreiben")

                                        if Rated != "N/A":
                                            rated_files = "{}infosomdbrated/{}.json".format(pathLoc, title)
                                            rated_data = {
                                                "Rated": Rated
                                            }
                                            os.makedirs(os.path.dirname(rated_files), exist_ok=True)
                                            with open(rated_files, "w") as f:
                                                json.dump(rated_data, f, indent=4)

                                        if float(imdbRating) > 1.0:
                                            sterne_files = "{}infosomdbsterne/{}.json".format(pathLoc, title)
                                            sterne_data = {
                                                "vote_average": imdbRating
                                            }
                                            os.makedirs(os.path.dirname(sterne_files), exist_ok=True)
                                            with open(sterne_files, "w") as f:
                                                json.dump(sterne_data, f, indent=4)

                                except:
                                    pass
                            logout(data="------------------------------------------------------------------------------- url imbd 1821")
                            url_find = 'https://m.imdb.com/find?q={}'.format(title)
                            logout(data=str(url_find))
                            ff = requests.get(url_find).text
                            rc = re.compile('<a href="/title/(.*?)/"', re.DOTALL)
                            imdbID = rc.search(ff).group(1)
                            logout(data="url 1159")
                            url= "https://m.imdb.com/title/{}/?ref_=fn_al_tt_0".format(imdbID)
                            logout(data=str(url))
                            ff = requests.get(url).text
                            try:
                                rtng = re.findall('"aggregateRating":{(.*?)}',ff)[0] #ratingValue":8.4
                                imdbRating = rtng.partition('ratingValue":')[2].partition('}')[0].strip()
                                if Rated == None:
                                    Rated = ff.partition('contentRating":"')[2].partition('","')[0].replace("+", "").strip() # "contentRating":"18+","genre":["Crime","Drama","Thriller"],"datePublished":"2019-10-04"
                                glist=[]
                                genre = ff.partition('genre":[')[2].partition('],')[0].strip().split(",")
                                for i in genre:
                                    genre=(i.replace('"',''))
                                    glist.append(genre)
                                if Genre == None:
                                    Genre = ", ".join(glist)
                                if Year == None:
                                    Year = ff.partition('datePublished":"')[2].partition('"')[0].strip()
                                if Type == None:
                                    Type = ff.partition('class="ipc-inline-list__item">')[2].partition('</li>')[0].strip().split(" ")
                                    if Type[0].lower() == "tv":
                                        Type = "Tv Series"
                                    else:
                                        Type = "Movie"
                            except:
                                pass
                            try:
                                if Duration == None:
                                    Duration = re.findall('\d+h \d+min', ff)[0]
                            except:
                                try:
                                    if Duration == None:
                                        Duration = re.findall('\d+min', ff)[0]
                                except:
                                    pass
                            try:
                                if config.plugins.xtraEvent.searchLang.value == True:
                                    #srch = "multi"
                                    srch = config.plugins.xtraEvent.searchType.value
                                    logout(data="url 1198")
                                    url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(title), self.searchLanguage())
                                    logout(data=str(url_tmdb))
                                    Plot = requests.get(url_tmdb).json()['results'][0]['overview']
                                    if Plot == "":
                                        logout(data="url 1203")
                                        url_tvdb = "https://thetvdb.com/api/GetSeries.php?seriesname={}".format(title)
                                        logout(data=str(url_tvdb))
                                        url_read = requests.get(url_tvdb).text
                                        series_id = re.findall('<seriesid>(.*?)</seriesid>', url_read)[0]
                                        if series_id:
                                            logout(data="url 1209")
                                            url_tvdb = "https://thetvdb.com/api/{}/series/{}/{}".format(tvdb_api, series_id, self.searchLanguage())
                                            logout(data=str(url_tvdb))
                                            url_read = requests.get(url_tvdb).text
                                            Plot = re.findall('<Overview>(.*?)</Overview>', url_read)[0]
                            except:
                                pass
                            data = {
                            "Title": Title,
                            "Year": Year,
                            "imdbRating": imdbRating,
                            "Rated": Rated,
                            "Released":Released,
                            "Genre": Genre,
                            "Duration": Duration,
                            "Country": Country,
                            "Director": Director,
                            "Writer": Writer,
                            "Actors": Actors,
                            "Awards": Awards,
                            "Type": Type,
                            "Plot": Plot,
                            "imdbID": imdbID,
                            }
                            js = json.dumps(data, ensure_ascii=False)
                            with open(info_files, "w") as f:
                                f.write(js)

                            if os.path.exists(info_files):
                                info_downloaded += 1
                                downloaded = info_downloaded
                                self.prgrs(downloaded, n)
                                self['info'].setText("►  {}, IMDB, INFO".format(title.upper()))
                            continue
                        except Exception as err:
                            with open("/tmp/xtraEvent.log", "a+") as f:
                                f.write("infos, %s, %s\n"%(title, err))
# --------------------------------  report nach dem download ---------------------------------------------------------
            logout(data="")
            logout(data="")
            logout(data="---------------------------------------------------------------------------------------------  report ausgabe ")
            logout(data=str(tmdb_poster_downloaded))
            posterdownloads = tmdb_poster_downloaded + tvdb_poster_downloaded + maze_poster_downloaded + fanart_poster_downloaded
            backdropdownloads = tmdb_backdrop_downloaded + tvdb_backdrop_downloaded + fanart_backdrop_downloaded + extra_downloaded + extra2_downloaded
            self.anzahlfiles_in_poster()
            self.anzahlfiles_in_backdrop()
            self.anzahlfiles_in_banner()
            self.anzahlfiles_in_infos()
            self.anzahlfiles_in_logo()
            logout(data="zu datetime")
            now = datetime.now()
            logout(data="zurueck datetime")
            extra3_poster_downloaded=self.extra3_poster_downloaded
            extra3_info_downloaded = self.extra3_info_downloaded
            dt = now.strftime("%d/%m/%Y %H:%M:%S")
            report = "\n\nSTART : {}\nEND : {}\
                \n\nDownloads All             :    {}\
                \nDownloads Poster      :    {}\
                \nDownloads Backdrop :    {}\
                \n \
                \nPOSTER; Tmdb :{}, Tvdb :{}, Maze :{}, Fanart :{}\
                \nBACKDROP; Tmdb :{}, Tvdb :{}, Fanart :{}, Extra :{}, Extra2 :{}\
                \nBANNER :{}\
                \nINFOS :{}\
                \nEXTRA3 ; Poster :{}, Info :{}".format(st, dt,
                str(self.anzahldownloads),str(posterdownloads),str(backdropdownloads),
                str(tmdb_poster_downloaded), str(tvdb_poster_downloaded), str(maze_poster_downloaded), str(fanart_poster_downloaded),
                str(tmdb_backdrop_downloaded), str(tvdb_backdrop_downloaded), str(fanart_backdrop_downloaded),
                str(extra_downloaded), str(extra2_downloaded),
                str(banner_downloaded),
                str(info_downloaded),
                str(extra3_poster_downloaded), str(extra3_info_downloaded))

            self['info2'].setText(report)
            self.report = report
            logout(data=" report ")
            try:
                if os.path.exists("/tmp/urlo.html"):
                    os.remove("/tmp/urlo.html")
            except:
                pass
            with open("/tmp/xtra_report", "a+") as f:
                f.write("%s"%report)
            logout(data="report aisgabe ende 1")
            Screen.show(self)
            logout(data="report aisgabe ende 2")
            self.brokenImageRemove()
            logout(data="report aisgabe ende 3")
            self.brokenInfoRemove()
            logout(data="report aisgabe ende 4")
            self.cleanRam()
            return
# ---------------------------------------------------------------------------------------------------------------------------




# ---------------------------------------------------------------------------------------------------------------------------
    def delete_oldfilesposter(self):
        # --------  hier alte files loeschen poster -------------------------
        logout(data="------------------------------------------------ delete old files - poster")
        #logout(data=str(config.plugins.xtraEvent.deletFiles.value))
        # Verzeichnispfad angeben
        if config.plugins.xtraEvent.deletFiles.value == True:
            directory = "{}poster".format(pathLoc)
            logout(data=str(directory))
            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)
            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete files ende poster")
        else:
            logout(data="delete files off")


    def delete_oldfilesbackdrop(self):
        # --------  hier alte files loeschen backdrop -------------------------
        logout(data="------------------------------------------------ delete old files - backdrop")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}backdrop".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)
            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende backdrop")
        else:
            logout(data="delete old files off")

    def delete_oldfilesbanner(self):
        # --------  hier alte files loeschen backdrop -------------------------
        logout(data="--------------------------------------------- delete old files - banner")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}banner".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)
            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende banner")

        else:
            logout(data="delete old files off")

    def delete_oldfilesinfos(self):
        # --------  hier alte files loeschen infos json -------------------------
        logout(data="------------------------------------------ delete old files - infos")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}infos".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)

            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende infos")

        else:
            logout(data="delete old files off")

    def delete_oldfilesnoinfos(self):
            # --------  hier alte files loeschen infos json -------------------------
            logout(data="------------------------------------------------ delete files start infos")
            if config.plugins.xtraEvent.deletFiles.value == True:
                # Verzeichnispfad angeben
                directory = "{}noinfos".format(pathLoc)
                logout(data=str(directory))

                # Aktuelles Datum erhalten
                heute = datetime.today().date()
                zwei_tage_ago = heute - timedelta(days=2)

                # Alle Dateien im Verzeichnis durchlaufen
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    # Überprüfen, ob es sich um eine Datei handelt
                    if os.path.isfile(filepath):
                        # Das Änderungsdatum der Datei abrufen
                        mtime = os.path.getmtime(filepath)
                        modified_date = datetime.fromtimestamp(mtime).date()
                        # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                        if modified_date < zwei_tage_ago:
                            # Datei löschen
                            os.remove(filepath)
                            logout(data="delete files ende infos")

            else:
                logout(data="delete files off")

    def delete_oldfilesinfosomdb(self):
        # --------  hier alte files loeschen infos json -------------------------
        logout(data="------------------------------------------ delete old files - infosomdb")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}infosomdb".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)

            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende infosomdb")

        else:
            logout(data="delete old files off")

    def delete_oldfilesinfossterne(self):
        # --------  hier alte files loeschen infos json -------------------------
        logout(data="------------------------------------------ delete old files - infossterne")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}infossterne".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)

            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende infossterne")

        else:
            logout(data="delete old files off")

    def delete_oldfilesinfosomdbsterne(self):
        # --------  hier alte files loeschen infos json -------------------------
        logout(data="------------------------------------------ delete old files - infosomdbsterne")
        if config.plugins.xtraEvent.deletFiles.value == True:
            # Verzeichnispfad angeben
            directory = "{}infosomdbsterne".format(pathLoc)
            logout(data=str(directory))

            # Aktuelles Datum erhalten
            heute = datetime.today().date()
            zwei_tage_ago = heute - timedelta(days=2)

            # Alle Dateien im Verzeichnis durchlaufen
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                # Überprüfen, ob es sich um eine Datei handelt
                if os.path.isfile(filepath):
                    # Das Änderungsdatum der Datei abrufen
                    mtime = os.path.getmtime(filepath)
                    modified_date = datetime.fromtimestamp(mtime).date()
                    # Überprüfen, ob das Änderungsdatum älter als das aktuelle Datum ist

                    if modified_date < zwei_tage_ago:
                        # Datei löschen
                        os.remove(filepath)
                        logout(data="delete old files ende infosomdbsterne")

        else:
            logout(data="delete old files off")

#########################################################################################################################################
    def prgrs(self, downloaded, n):
        logout(data="------------------------------------------------------------------------------------------------------- def prgrs start")
        self['status'].setText("Download : {} / {}".format(downloaded, n))
        self['progress'].setValue(int(100*downloaded//n))

    def showPoster(self, dwnldFile):
        logout(data="------------------------------------------------------------------------------------------------------- def showPoster start")
        if config.plugins.xtraEvent.onoff.value:
            if not config.plugins.xtraEvent.timerMod.value:
                self["Picture2"].hide()
                self["Picture"].setPixmap(loadJPG(dwnldFile))
                self["Picture"].setScale(1)
                self["Picture"].show()
                if desktop_size <= 1280:
                    self["Picture"].resize(eSize(185,278))
                    self["Picture"].move(ePoint(955,235))
                    self["Picture"].setScale(1)
                else:
                    self["Picture"].setScale(1)
                    self["Picture"].resize(eSize(185,278))
                    self["Picture"].move(ePoint(1450,400))

    def showBackdrop(self, dwnldFile):
        logout(data="------------------------------------------------------------------------------------------------------- def showBackdrop start")
        if config.plugins.xtraEvent.onoff.value:
            if not config.plugins.xtraEvent.timerMod.value:
                self["Picture2"].hide()
                self["Picture"].setPixmap(loadJPG(dwnldFile))
                if desktop_size <= 1280:
                    self["Picture"].resize(eSize(300,170))
                    self["Picture"].move(ePoint(895,280))
                    self["Picture"].setScale(1)
                else:
                    self["Picture"].setScale(1)
                    self["Picture"].resize(eSize(300,170))
                    self["Picture"].move(ePoint(1400,400))

    def showBanner(self, dwnldFile):
        logout(data="------------------------------------------------------------------------------------------------------- def showBanner start")
        if config.plugins.xtraEvent.onoff.value:
            if not config.plugins.xtraEvent.timerMod.value:
                self["Picture2"].hide()
                self["Picture"].setPixmap(loadJPG(dwnldFile))
                if desktop_size <= 1280:
                    self["Picture"].resize(eSize(400,80))
                    self["Picture"].move(ePoint(845,320))
                    self["Picture"].setScale(1)
                    self["Picture"].setZPosition(10)
                else:
                    self["Picture"].setScale(1)
                    self["Picture"].resize(eSize(400,90))
                    self["Picture"].move(ePoint(1400,400))

    def showFilm(self):
        logout(data="------------------------------------------------------------------------------------------------------- def showFilm start")
        self["Picture2"].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent/pic/film2.png")
        self["Picture2"].instance.setScale(1)
        self["Picture2"].show()

    def brokenImageRemove(self):
        logout(data="------------------------------------------------------------------------------------------------------- def brokenImageRemove start")
        b = os.listdir(pathLoc)
        rmvd = 0
        try:
            for i in b:
                bb = "{}{}/".format(pathLoc, i)
                fc = os.path.isdir(bb)
                if fc != False:
                    for f in os.listdir(bb):
                        if f.endswith('.jpg'):
                            try:
                                img = Image.open("{}{}".format(bb, f))
                                img.verify()
                            except:
                                try:
                                    os.remove("{}{}".format(bb, f))
                                    rmvd += 1
                                except:
                                    pass
        except:
            pass

    def brokenInfoRemove(self):
        logout(data="------------------------------------------------------------------------------------------------------- def brokenInfoRemove start")
        try:
            infs = os.listdir("{}infos".format(pathLoc))
            for i in infs:
                with open("{}infos/{}".format(pathLoc, i)) as f:
                    rj = json.load(f)
                if rj["Response"] == "False":
                    os.remove("{}infos/{}".format(pathLoc, i))
        except:
            pass

    def cleanRam(self):
        logout(data="------------------------------------------------------------------------------------------------------- def cleanRam")
        os.system("echo 1 > /proc/sys/vm/drop_caches")
        os.system("echo 2 > /proc/sys/vm/drop_caches")
        os.system("echo 3 > /proc/sys/vm/drop_caches")


    def savePoster(self, dwn_path, url):
        from urllib.request import urlopen
        logout(data="")
        logout(data="")
        logout(data="------------------------------------------------------------------------------------------------------- def saveposter start")
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=log_message)
        logout(data="save poster - open file")
        logout(data=str(dwn_path))
        logout(data=str(url))

        with open(dwn_path, 'wb') as f:
            logout(data="with open")
            f.write(urlopen(url).read())
            logout(data="write ")
            # Überprüfe, ob das Schreiben abgeschlossen ist
            f.flush()
            f.close()
            # Überprüfe die Dateigröße
            file_size = os.path.getsize(dwn_path)
            if file_size == 0:
                # Lösche die Datei, wenn sie 0 Byte groß ist
                os.remove(dwn_path)
                logout(data="wurde geloescht, da sie 0 Byte war.")
            else:
                logout(data="Datei wurde erfolgreich gespeichert ")
        logout(data="-------------------------------------------------------------------------------------------------------  def saveposter ende")
        logout(data="")
        return

    def showLogo(self, dwnldFile):
        logout(data="------------------------------------------------------------------------------------------------------- def showLogo")
        #if config.plugins.xtraEvent.onoff.value:
        if not config.plugins.xtraEvent.timerMod.value:
            self["Picture2"].hide()
            self["Picture"].setPixmap(loadPNG(dwnldFile))
            if desktop_size <= 1280:
                self["Picture"].resize(eSize(300, 170))
                self["Picture"].move(ePoint(895, 280))
                self["Picture"].setScale(1)
            else:
                self["Picture"].setScale(1)
                self["Picture"].resize(eSize(300, 170))
                self["Picture"].move(ePoint(1400, 400))


#########################################################################################################################################


    def download_tmdb(self, evntNm, pstrNm):
        logout(data="")
        logout(data="")
        logout(data=" ------------------------------------------------- def download tmdb  ablauf start ------------------------------------------- ")
        start_time = time.time()
        logout(data="")
        logout(data=str(evntNm))
        logout(data=str(pstrNm))
        self.anfrageohne=0
        logout(data="***********************************************************************************************************************************")
        logout(data="----------------------------------- Sendungsname :         '{}' ".format(evntNm))
        logout(data="************************************************************************************************************************************")
        if '-' in evntNm:
            evntNm_orginal = evntNm  # damit man anfragen machen kann ohne untertitle nach dem - , name - xxxxxxx
            logout(data=str(pstrNm))
            anfrageohne = 1  # auf 1 gesetzt das wir beim save dann den evntNm_orginal nehmen
            # hier versuch name nur vor dem -
            name1 = evntNm.split("- ", 1)
            Name = name1[0].strip()
            logout(data="name   - abtrennen ")
            logout(data=Name)
            evntNm_minus = Name  # jetzt suchen wir nur mit dem vor dem - , wir muessen aber den save mit machen
        else:
            evntNm_minus=evntNm
            evntNm_orginal=evntNm

        lng = '{}'.format(self.searchLanguage())
        logout(data=str(lng))

        if not os.path.exists(pstrNm):
            logout(data="file nicht vorhanden start multi")
            self.multi(evntNm, pstrNm, start_time, lng, evntNm_minus, evntNm_orginal)
            if not os.path.exists(pstrNm):
                logout(data="file nicht vorhanden start movie")
                self.movie(evntNm, pstrNm, start_time, lng)
                if not os.path.exists(pstrNm):
                    logout(data="file nicht vorhanden start tv")
                    self.tv(evntNm, pstrNm, start_time, lng)
                    if not os.path.exists(pstrNm):
                        logout(
                            data="****************** download_tmdb - vom download zurueck keine json gefunden *******************")
                        logout(data="")
                        return
                    else:
                        logout(data="****************** download_tmdb tv - ist vorhanden *******************")
                        return
                else:
                    logout(data="****************** download_tmdb movie - ist vorhanden *******************")
                    return
            else:
                logout(data="****************** download_tmdb multi - ist vorhanden *******************")
                return
        else:
            logout(data="****************** kein download_tmdb - ist vorhanden *******************")
            return

    def movie(self, evntNm, pstrNm, start_time, lng):
        srch = "movie"
        logout(data="")
        logout(data="------------------- 111111111111 ------------------ download_tmdb -  gehe zu download , mit srch movie , language")
        logout(data="")
        url_tmdb_lng = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(evntNm), lng)
        logout(data=(url_tmdb_lng))
        logout(data="")
        anfrageohne = 0
        evntNm_orginal = evntNm
        self.download_json(evntNm, url_tmdb_lng, start_time, anfrageohne, evntNm_orginal)

        if not os.path.exists(pstrNm):
            logout(data="**************** 1111111111111 ********************************* ist nicht vorhanden von movie ohne language")
            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(evntNm))
            logout(data=(url_tmdb))
            logout(data="")
            anfrageohne = 0
            evntNm_orginal = evntNm
            self.download_json(evntNm, url_tmdb, start_time, anfrageohne, evntNm_orginal)

        logout(data="-------------------------------------------------------------------------------------------------------  download_tmdb - vom download movie zurück")
        # hier weitere downloads einbauen

        if os.path.exists(pstrNm):
            logout(data="*************** 1111111111111 ************************************************************** ist vorhanden von movie")

        # --------------------------------- hier url download einbauen und url uebergeben

    def tv(self, evntNm, pstrNm, start_time, lng):
        srch = "tv"
        logout(data="")
        logout(data="------------------ 22222222222 ------------    download_tmdb - Poster nicht vorhanden , gehe zu download , mit srch tv , language")
        url_tmdb_lng = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(evntNm), lng)
        logout(data=(url_tmdb_lng))
        logout(data="")
        anfrageohne = 0
        evntNm_orginal = evntNm
        self.download_json(evntNm, url_tmdb_lng, start_time, anfrageohne, evntNm_orginal)

        if not os.path.exists(pstrNm):
            logout(data="*************** 22222222222 ******************************************************************* ist nicht vorhanden von tv , ohne language")
            logout(data="")
            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(evntNm))
            logout(data=(url_tmdb))
            logout(data="")
            anfrageohne = 0
            evntNm_orginal = evntNm
            self.download_json(evntNm, url_tmdb, start_time, anfrageohne, evntNm_orginal)

        logout(data="--------------------------------------------------------------------------------------------------- download_tmdb - vom download tv zurueck")

        if os.path.exists(pstrNm):
            logout(
                data="download_tmdb Poster *********** 22222222222 ************************** ist vorhanden von tv")


    def multi(self, evntNm, pstrNm, start_time, lng, evntNm_minus, evntNm_orginal):
        srch = "multi"
        logout(data="")
        logout(data="------------- 3333333333 --------------    download_tmdb - Poster nicht vorhanden , gehe zu download , mit srch multi , language")
        url_tmdb_lng = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote(evntNm), lng)
        logout(data=(url_tmdb_lng))
        logout(data="")
        anfrageohne = 0
        evntNm_orginal = evntNm
        self.download_json(evntNm, url_tmdb_lng, start_time, anfrageohne, evntNm_orginal)

        if not os.path.exists(pstrNm):
            logout(data="**************** 3333333333 *************************************************************** ist nicht vorhanden von multi , ohne language")
            url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(evntNm))
            logout(data=(url_tmdb))
            logout(data="")
            anfrageohne = 0
            evntNm_orginal = evntNm
            self.download_json(evntNm, url_tmdb, start_time, anfrageohne, evntNm_orginal)
        logout(data="----------------------------------------------------------------------------------------------- download_tmdb - vom download movie zurueck")

        if os.path.exists(pstrNm):
            logout(data="download_tmdb Poster ************* 3333333333 ************** ist vorhanden von multi")
            logout(data="")

        else:
            if not os.path.exists(pstrNm):
                print("33333333333333333 - minus , lng")
                logout(data="**************** 3333333333 ********************** minus ***************************** ist nicht vorhanden von multi , ohne language")
                url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}&language={}".format(srch, tmdb_api, quote( evntNm_minus), lng)
                logout(data=(url_tmdb))
                logout(data="")
                anfrageohne = 1
                self.download_json(evntNm_minus, url_tmdb, start_time, anfrageohne, evntNm_orginal)
            logout(data="----------------------------------------------------------------------------------------------- download_tmdb - vom download movie zurueck")

            if os.path.exists(pstrNm):
                logout(data="download_tmdb Poster ************* 3333333333 ************** ist vorhanden von multi")
                logout(data="")

            else:
                if not os.path.exists(pstrNm):
                    print("33333333333333333 - minus")
                    logout(data="**************** 3333333333 **************** minus *********************************** ist nicht vorhanden von multi , ohne language")
                    url_tmdb = "https://api.themoviedb.org/3/search/{}?api_key={}&query={}".format(srch, tmdb_api, quote(evntNm_minus))
                    logout(data=(url_tmdb))
                    logout(data="")
                    anfrageohne = 1
                    self.download_json(evntNm_minus, url_tmdb, start_time, anfrageohne, evntNm_orginal)
                logout(
                    data="----------------------------------------------------------------------------------------------- download_tmdb - vom download movie zurueck")

                if os.path.exists(pstrNm):
                    logout(data="download_tmdb Poster ************* 3333333333 ************** ist vorhanden von multi")
                    logout(data="")

    ########################################################################################################################



    def download_json(self, evntNm, url, start_time, anfrageohne, evntNm_orginal):
        logout(data="")
        logout(data=" -------------------------------------- def download json start ----------------------------------- ")
        logout(data="")
        pathPoster = "{}poster/".format(pathLoc)
        pathBackdrop = "{}backdrop/".format(pathLoc)
        pathLogo = "{}logo/".format(pathLoc)
        pathJsonTmdb = "{}infos/".format(pathLoc)
        pathJsonOmdb = "{}infosomdb/".format(pathLoc)
        pathBanner = "{}banner/".format(pathLoc)

        postersize = "185"
        backdropsize = "300"
        logosize = "300"

        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=log_message)

        # Anfrage senden und Daten abrufen
        response = requests.get(url)
        data = response.json()

        total_results = data["total_results"]  # Gesamtzahl der Ergebnisse erhalten
        logout(data="download json 2 total results anzahl")
        logout(data=str(total_results))
        json_data = data
        time_url = time.time() - start_time
        log_time = f" zeit von start bis json download :{time_url} sekunden."
        logout(data=log_time)
        logout(data="")
        if total_results == 0:
            logout(data="Keine Informationen gefunden.")
            pass
        else:
            for result in data["results"]:
                name = "none"
                original_name = "none"
                title = "none"
                original_title = "none"
                # check ist der sendungsname in der json

                if "name" in result:
                    logout(data="---------------------------------------- name in der json")
                    Name = result["name"]
                    name = self.eventname(Name)
                    logout(data=str(name))
                    logout(data ="---------------------------------------- name in der json")
                else:
                    logout(data="---------------------------------------- keine name in der json")

                if "original_name" in result:
                    logout(data="---------------------------------------- orginal_name in der json")
                    original_name = result["original_name"]
                    Name = original_name
                    original_name = self.eventname(Name)
                    logout(data=str(original_name))
                    logout(data="---------------------------------------- orginal_name in der json")
                else:
                    logout(data="---------------------------------------- keine original name in der json")

                if "title" in result:
                    logout(data="---------------------------------------- title in der json")
                    title = result["title"]
                    Name = title
                    title = self.eventname(Name)
                    logout(data=str(title))
                    logout(data="---------------------------------------- title in der json")
                else:
                    logout(data="---------------------------------------- keine title in der json")

                if "original_title" in result:
                    logout(data="---------------------------------------- orginal_title in der json")
                    original_title = result["original_title"]
                    Name = original_title
                    original_title = self.eventname(Name)
                    logout(data=str(original_title))
                    logout(data="---------------------------------------- orginal_title in der json")

                else:
                    logout(data="---------------------------------------- keine original title in der json")

                # Teile den Sendungsnamen an den Trennzeichen "-" auf
                evntNm_erster_namen = evntNm.split(" - ")
                # Nimm den ersten Teil als den eigentlichen Sendungstitel
                evntNmkurz = evntNm_erster_namen[0]
                logout(data="")
                logout(data="name von der sendung kurz")
                logout(data=str(evntNmkurz))
                logout(data="")
                logout(data="name von der sendung")
                logout(data=str(evntNm))
                logout(data="")
                time_name = time.time() - start_time
                log_time = f"zeit von start bis namen aus json :{time_name} sekunden."
                logout(data=log_time)
                logout(data="namen von der sendung in der json , name , orginal_name , title , orginal_title")
                logout(data=str(name))
                logout(data=str(original_name))
                logout(data=str(title))
                logout(data=str(original_title))
                logout(data="")

                #   ------------------------------------ ist der name von der json einmal gleich mit der sendung -------------------------
                # wenn der name gleich ist holt man sich die id vom movie

                if (evntNm.lower() == name.lower() or
                        evntNm.lower() == original_name.lower() or
                        evntNm.lower() == original_title.lower() or
                        evntNm.lower() == title.lower() or
                        evntNmkurz.lower() == original_title.lower()):
                    logout(data="")
                    logout(
                        data="************************************ name von der sendung ist gleich mit json *****************")
                    logout(data="")
                    poster_url=""
                    backdrop_url=""
                    id_nummer=""

                    if anfrageohne == 1:  # auf 1 gesetzt das wir beim save dann den evntNm_orginal nehmen
                        evntNm = evntNm_orginal
                        logout(
                            data="************************************ name von der sendung auf orginal *****************")
                        logout(data=str(evntNm))

                    if "results" in data and len(data["results"]) > 0:
                        logout(data="------------- result vorhnaden")
                        result = data["results"][0]
                        if "known_for" in result:
                            logout(data="------------- result vorhnaden known_for --------------------------------------")
                            known_for = result["known_for"]
                            if len(known_for) > 0:
                                item = known_for[0]
                                if "poster_path" in item:
                                    poster_url = item["poster_path"]
                                    logout(data="------------- known_for poster")
                                    logout(data=str(poster_url))
                                if "backdrop_path" in item:
                                    backdrop_url = item["backdrop_path"]
                                    logout(data="------------- known_for backdrop")
                                    logout(data=str(backdrop_url))
                                if "id" in item:
                                    id_nummer = item["id"]
                                    logout(data="------------- known_for id")
                                    logout(data=str(id_nummer))


                        else:
                            logout(data="------------- result vorhnaden standart ---------------------------------------")
                            first_result = data["results"][0]
                            if "poster_path" in first_result:
                                poster_url = first_result["poster_path"]
                                logout(data="------------- poster")
                                logout(data=str(poster_url))
                            if "backdrop_path" in first_result:
                                backdrop_url = first_result["backdrop_path"]
                                logout(data="------------- backdrop")
                                logout(data=str(backdrop_url))

                            if "id" in first_result:
                                id_nummer = first_result["id"]
                                logout(data="------------- id")
                                logout(data=str(id_nummer))

                            if "vote_average" in first_result:
                                vote_average = first_result["vote_average"]
                                logout(data="------------- vote_average")
                                logout(data=str(vote_average))

                                if float(vote_average) > 1.0:
                                    logout(data="------------- path sterne save")
                                    sterne2_files = "{}infossterne/{}.json".format(pathLoc, evntNm)
                                    logout(data="------------- path json sterne")
                                    logout(data=str(sterne2_files))
                                    sterne_data = {
                                        "vote_average": vote_average
                                    }
                                    logout(data=str(sterne_data))
                                    os.makedirs(os.path.dirname(sterne2_files), exist_ok=True)
                                    with open(sterne2_files, "w") as f:
                                        logout(data="------------- path sterne save file")
                                        json.dump(sterne_data, f, indent=4)
                                    f.close()  # Datei schließen


                        # Schreibe den JSON-Inhalt in die Datei
                        dwn_json = pathJsonTmdb + "{}.json".format(evntNm)
                        logout(data="------------- path json save")
                        logout(data=str(dwn_json))

                        with open(dwn_json, "w") as file:
                            json.dump(json_data, file, indent=4)
                            time_nameok = time.time() - start_time
                            log_time = f" zeit von start bis json geschrieben :{time_nameok} sekunden."
                            logout(data=log_time)
                            logout(data="")

                else:
                    logout(
                        data="********************************** Name in josn nicht gleich , mann kann es doch nicht nehmen ???")
                    logout(data="")

                    return

                logout(data="****************************** sendungsname save datei ************************************ ")
                logout(data=str(evntNm))
                logout(data="*******************************************************************************************")

                logout(data="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% poster url:")
                if poster_url is not None:
                    if poster_url != "null":
                        logout(data="")
                        # Poster-Pfad gefunden, nicht null
                        logout(data="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Gefundene poster url:")
                        logout(data=str(poster_url))
                        logout(data=str(postersize))
                        url_poster = "https://image.tmdb.org/t/p/w{}{}".format(postersize, poster_url)
                        logout(data=(url_poster))
                        logout(data="poster_path - open file")
                        dwn_poster = pathPoster + "{}.jpg".format(evntNm)
                        logout(data=(dwn_poster))
                        logout(data="poster_path - down poster name file")
                        logout(data="poster_path - zu save ")
                        self.savePoster(dwn_poster, url_poster)
                        logout(data="poster_path - von save zurueck ")

                        time_url = time.time() - start_time
                        log_time = f" zeit von start bis save poster :{time_url} sekunden."
                        logout(data=log_time)
                        logout(data="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% save Poster ende")
                        logout(data="")
                    else:
                        logout(data="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Poster-Url: ist Null")
                        break
                else:
                    logout(data="%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Poster-Url: ist None")
                    break

                logout(data="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< backdrop url:")
                if backdrop_url is not None:
                    if backdrop_url != "null":
                        # backdrop-Pfad gefunden, nicht null
                        logout(data="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Gefundene backdrop url:")
                        logout(data=str(backdrop_url))
                        logout(data=str(backdropsize))
                        url_poster = "https://image.tmdb.org/t/p/w{}{}".format(backdropsize, backdrop_url)
                        logout(data=(url_poster))
                        logout(data="backdrop_path - open file")
                        dwn_poster = pathBackdrop + "{}.jpg".format(evntNm)
                        logout(data=(dwn_poster))
                        logout(data="backdrop_path - down poster name file")
                        logout(data="backdrop_path - zu save ")
                        self.savePoster(dwn_poster, url_poster)
                        logout(data="backdrop_path - von save zurueck")
                        time_url = time.time() - start_time
                        log_time = f" zeit von start bis save backdrop :{time_url} sekunden."
                        logout(data=log_time)
                        logout(data="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< save Backdrop ende")
                        logout(data="")
                    else:
                        logout(data="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Backdrop-Url: ist null")
                        break
                else:
                    logout(data="<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Backdrop-Url: ist None")
                    break

                logout(data=" ------------------------------------------------ abfrage Logo Download -------------------------------- ")
                logout(data=str(config.plugins.xtraEvent.logoFiles.value))
                if config.plugins.xtraEvent.logoFiles.value == False:
                    logout(data=" id nummer auf None ")
                    id_nummer = None
                logout(data=" id nummer ist ")
                logout(data=str(id_nummer))
                logout(data="=================================================================================== id nummer:")
                if id_nummer is not None:
                    if id_nummer != "null":
                        start_time2 = time.time()
                        logout(data="")
                        # Poster-Pfad gefunden, nicht null
                        logout(data="=================================================================================== Gefundene id nummer:")
                        logout(data=str(id_nummer))
                        url_tmdb = "https://api.themoviedb.org/3/movie/{}/images?api_key={}".format(id_nummer, tmdb_api)
                        logout(data=(url_tmdb))
                        # so url - http://api.themoviedb.org/3/movie/672/images?api_key=3c3efcf47c3577558812bb9d64019d65
                        # json laden in data
                        response = requests.get(url_tmdb)
                        data = response.json()
                        logout(data="check json daten")
                        time_url = time.time() - start_time2
                        log_time = f" zeit id 1:{time_url} sekunden."
                        logout(data=log_time)
                        if "id" in data and data["id"] == id_nummer:
                            logout(data="json hat eine id")
                            logout(data=str(lng))
                            if not data["logos"]:
                                logout(data="json hat keine logo daten")
                                return
                            else:
                                logout(data="json hat infos daten")
                                for file_path in data["logos"]:
                                    if file_path["iso_639_1"] == lng:
                                        url_logo = file_path["file_path"]
                                        logout(data="logo")
                                        logout(data="url logo lng gefunden")
                                        logout(data=url_logo)
                                        break
                                else:
                                    # Wenn kein deutsches logo gefunden wurde, nach einem ohne Sprachcode suchen
                                    for file_path in data["logos"]:
                                        if file_path["iso_639_1"] == "en":
                                            url_logo = file_path["file_path"]
                                            # Weitere Verarbeitung des Datei-Pfads
                                            logout(data="url Logo en sprache gefunden")
                                            logout(data=url_logo)
                                            break
                                    else:
                                        url_logo = None
                                        logout(data="Kein deutsches oder sprachunabhaengiges logo gefunden.")
                                        return
                                time_url = time.time() - start_time2
                                log_time = f" zeit id 2:{time_url} sekunden."
                                logout(data=log_time)

                                if not url_logo == None:
                                    url_logo_down = "https://image.tmdb.org/t/p/w{}{}".format(logosize, url_logo)
                                    logout(data=str(url_logo_down))
                                    logout(data="logo - open file")
                                    dwn_logo = pathLogo + "{}.png".format(evntNm)
                                    logout(data=str(dwn_logo))
                                    logout(
                                        data="====================================================================== zu save")
                                    self.savePoster(dwn_logo, url_logo_down)
                                    logout(data="====================================================================== von save zurueck ende logo_path")

                                    time_url = time.time() - start_time2
                                    log_time = f" json ca 200 ms save pmg ca 170 ms - zeit id ende :{time_url} sekunden."
                                    logout(data=log_time)
                                    time_url = time.time() - start_time
                                    log_time = f"1 x json ca 200 ms - 2 x save jpg ca 45 ms id json und save ca 375 ms - zeit von start bis save logo :{time_url} sekunden."
                                    logout(data=log_time)
                                    logout(data="")
                                    return
                                else:
                                    return
                        else:
                            logout(data="=============================================================================== json hat keine id daten")
                            return
                    else:
                        logout(data="=================================================================================== json id ist null")
                        return
                else:
                    logout(data="======================================================================================= json id ist none")
                    return

    # in dwn_poster muss der path sein und in url wo man es downloadet
    import os
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError

    def savePoster(self, dwn_path, url):
        start_time5 = time.time()
        logout(data="")
        logout(data="")
        logout(data="++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ def saver start")
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=log_message)
        logout(data="save poster - open file")
        logout(data=str(dwn_path))
        logout(data=str(url))
        try:
            with open(dwn_path, 'wb') as f:
                logout(data="with open")
                f.write(urlopen(url).read())
                logout(data="write ")
                # Überprüfe, ob das Schreiben abgeschlossen ist
                f.flush()
                f.close()
                # Überprüfe die Dateigröße
                file_size = os.path.getsize(dwn_path)
                if file_size == 0:
                    # Lösche die Datei, wenn sie 0 Byte groß ist
                    os.remove(dwn_path)
                    logout(data="wurde geloescht, da sie 0 Byte war.")
                else:
                    logout(data="Datei wurde erfolgreich gespeichert ")
            save_time = time.time() - start_time5
            log_time = f" zeit save  :{save_time} sekunden."
            logout(data=log_time)
            logout(data="+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  def save ende")
            logout(data="")
            return url
        except OSError as e:
            logout(data="OS error")
            logout(data=str(e))

        #except URLError as e:
        #    print("URL error")
        #    logout(data=f"Fehler beim Herunterladen der Datei: {e}")

        #except HTTPError as e:
        #    print("HTTP error")
        #    logout(data=f"HTTP-Fehler beim Herunterladen der Datei: {e}")
        except Exception as e:
            logout(data="Exception")
            #print(f"Unerwarteter Fehler beim Herunterladen der Datei: {e}")
            logout(data=str(e))


    def eventname(self, Name):
        logout(data="")
        logout(
            data=">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     name aus der json in eventname start umwandelen")
        caller_frame = inspect.currentframe().f_back
        caller_name = inspect.getframeinfo(caller_frame).function
        log_message = f"Die Funktion getText() wurde von {caller_name} aufgerufen."
        logout(data=log_message)

        logout(data=Name)
        # hier live: entfernen
        Name = Name.replace('\xc2\x86', '').replace('\xc2\x87', '').replace("live: ", "").replace("LIVE ", "")
        Name = Name.replace("live: ", "").replace("LIVE ", "").replace("LIVE: ", "").replace("live ", "")
        logout(data="name live rausnehmen")
        logout(data=Name)
        # hier versuch name nur vor dem :
        name1 = Name.split(": ", 1)
        Name = name1[0]
        logout(data="name   : abtrennen ")
        logout(data=Name)

        Name = REGEX.sub('', Name).strip()
        logout(data=Name)

        #Name = Name.replace("&", "und")
        Name = Name.replace("ß", "ss")
        Name = Name.lower()
        logout(data=Name)
        logout(
            data=">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    name aus der json in eventname ende umgewandelt")
        logout(data="")
        return Name  # liefert dem aufruf das zurueck