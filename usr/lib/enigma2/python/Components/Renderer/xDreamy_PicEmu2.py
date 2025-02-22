#!/usr/bin/python
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------------------------------------
# es wird noch nicht der richtige pfad gefunden , er hat immer etc/emu , wenn da die files sind geht er
# --------------------------------------------------------------------------------------------------------
from __future__ import print_function
from Components.Pixmap import Pixmap
from Components.Renderer.Renderer import Renderer
from enigma import iServiceInformation
from enigma import ePixmap
from Tools.Directories import fileExists, SCOPE_CURRENT_SKIN,resolveFilename
from Components.Element import cached
from Components.Converter.Poll import Poll
import os
ablauf = " 1234 "
#open("/tmp/PicEmu1", "w").write(ablauf)

class xDreamy_PicEmu2(Renderer, Poll):

    __module__ = __name__
    if fileExists('/usr/lib64'):
        searchPaths = (
            '/data/%s/',
            '/usr/share/enigma2/%s/',
            '/usr/lib64/enigma2/python/Plugins/Extensions/%s/',
            '/media/sde1/%s/',
            '/media/cf/%s/',
            '/media/sdd1/%s/',
            '/media/hdd/%s/',
            '/media/usb/%s/',
            '/media/ba/%s/',
            '/mnt/ba/%s/',
            '/media/sda/%s/',
            '/etc/%s/',
            )
    else:
        searchPaths = (
            '/data/%s/',
            '/usr/share/enigma2/%s/',
            '/usr/lib/enigma2/python/Plugins/Extensions/%s/',
            '/media/sde1/%s/',
            '/media/cf/%s/',
            '/media/sdd1/%s/',
            '/media/hdd/%s/',
            '/media/usb/%s/',
            '/media/ba/%s/',
            '/mnt/ba/%s/',
            '/media/sda/%s/',
            '/etc/%s/',
            )

    def __init__(self):
        Poll.__init__(self)
        Renderer.__init__(self)
        self.path = 'emu'
        self.nameCache = { }
        self.pngname = ' '
        self.picon_default = 'picon_default.png'
		#path = 'Malek-FHD/iconsinfo/cams/'
		
		
    def applySkin(self, desktop, parent):
        attribs = [ ]
        #open("/tmp/PicEmuattribs", "w").write(attribs)
        for (attrib, value) in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            elif attrib == 'picon_default':
                self.picon_default = value
            else:
                attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    @cached
    def getText(self):
        #open("/tmp/PicEmuPath", "w").write(path)
        service = self.source.service
        info = service and service.info()
        if not service:
            #open("/tmp/PicEmuservice", "w").write(ablauf)
            return None
        camd = ' '
        serlist = None
        camdlist = None
        nameemu = [ ]
        nameser = [ ]
        if not info:
            #open("/tmp/PicEmuinfo", "w").write(ablauf)
            return ' '
        if fileExists('/etc/init.d/softcam') \
            or fileExists('/etc/init.d/cardserver'):
            try:
                #open("/tmp/PicEmuFile", "w").write(ablauf)
                for line in open('/etc/init.d/softcam'):
                    if 'echo' in line:
                        nameemu.append(line)
                camdlist = '%s' % nameemu[1].split('"')[1]
                #open("/tmp/PicEmucamdlist", "w").write(camdlist)
            except:
                pass
            try:
                for line in open('/etc/init.d/cardserver'):
                    if 'echo' in line:
                        nameser.append(line)
                serlist = '%s' % nameser[1].split('"')[1]
                #open("/tmp/PicEmuserlist", "w").write(serlist)
            except:
                pass
            if serlist is not None and camdlist is not None:
                return '%s %s' % (serlist, camdlist)
            elif camdlist is not None:
                return '%s' % camdlist
            elif serlist is not None:
                return '%s' % serlist
            return ' '

        if serlist is not None:
            try:
                cardserver = ' '
                for current in serlist.readlines():
                    cardserver = current
                serlist.close()
            except:
                pass
        else:
            cardserver = ' '

        if camdlist is not None:
            try:
                emu = ' '
                #open("/tmp/PicEmuEmu", "w").write(emu)
                for current in camdlist.readlines():
                    emu = current
                camdlist.close()
            except:
                pass
        else:
            emu = ' '

        return '%s %s' % (cardserver.split('\n')[0], emu.split('\n')[0])

    text = property(getText)

    def changed(self, what):
        self.poll_interval = 50
        self.poll_enabled = True
        if self.instance:
            pngname = ' '
            if what[0] is not self.CHANGED_CLEAR:
                sname = 'oscam'
                service = self.source.service
                if service:
                    info = service and service.info()
                    if info:
                        caids = \
                            info.getInfoObject(iServiceInformation.sCAIDs)
                        if fileExists('/tmp/ecm.info'):
                            try:
                                value = self.getText()
                                value = value.lower()  # change value to small letters
                                if value is None:
                                    print('[PicEmu2] no emu installed')
                                    sname = ' '
                                else:

                                    # # Should write name be small letters
                                    #open("/tmp/PicEmuSname", "w").write(sname)
                                    if 'ncam' in value:
                                        sname = 'ncam'
                                    elif 'oscam' in value:
                                        sname = 'oscam'
                                    elif 'mgcamd' in value:
                                        sname = 'Mgcamd'
                                    elif 'gosatplus' in value:
                                        sname = 'gosatplus'
                                    elif 'wicard' in value or 'wicardd' \
    in value:
                                        sname = 'Wicardd'
                                    elif 'gbox' in value:
                                        sname = 'Gbox'
                                    elif 'camd3' in value:
                                        sname = 'Camd3'
                                    elif fileExists('/tmp/ecm.info'):
                                        try:
                                            f = open('/tmp/ecm.info',
        'r')
                                            content = f.read()
                                            f.close()
                                        except:
                                            content = ' '
                                        contentInfo = content.split('\n'
        )
                                        for line in contentInfo:
                                            if 'address' in line:
                                                sname = 'CCcam'
                            except:
                                print(' ')

                        if caids:
                            if len(caids) > 0:
                                for caid in caids:
                                    caid = self.int2hex(caid)
                                    if len(caid) is 3:
                                        caid = '0%s' % caid
                                    caid = caid[:2]
                                    caid = caid.upper()
                                    if caid is not ' ' and sname is ' ':
                                        sname = 'Unknown'

                pngname = self.nameCache.get(sname, ' ')
                if pngname is ' ':
                    pngname = self.findPicon(sname)
                    if pngname is not ' ':
                        self.nameCache[sname] = pngname

            if pngname is ' ':
                pngname = self.nameCache.get('Fta', ' ')
                if pngname is ' ':
                    pngname = self.findPicon('Fta')
                    if pngname is ' ':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN,
                                'picon_default.png')
                        if fileExists(tmp):
                            pngname = tmp
                        self.nameCache['default'] = pngname

            if self.pngname is not pngname:
                self.pngname = pngname
                self.instance.setPixmapFromFile(self.pngname)

    def int2hex(self, int):
        return '%x' % int

    def findPicon(self, serviceName):
        for path in self.searchPaths:
            pngname = path % self.path + serviceName + '.png'
            #open("/tmp/PicEmuPngname", "w").write(pngname)
            if fileExists(pngname):
                return pngname
        return ' '