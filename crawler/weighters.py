#!/usr/bin/python

from ContentExtractor import ContentExtractor
from KeyWords import KeyWords
import types
import re


class LinkWeighter:

    def __init__( self, kw = None ):
        self.kw = kw 
        if self.kw is None:
            self.kw = KeyWords()
            self.kw.loadLinkKW()    


    def weightLinksOnPage( self, bodySoup, winSize = 3 ):
        #print self.kw.words
        links= {}
        ce = ContentExtractor()
        mc = ce.extractMappedContentList(bodySoup)
        for i in mc[0]:
            if type(i) != types.IntType:
                continue
            link = mc[1][i].get('href')
            links[link] = self.weightWindowed( mc[0], i, winSize ) # max(...)
        return links

    def weightWindowed( self, MappedContent, linkId, winSize, method = 'link' ):
        if type(winSize) == types.IntType:
            winL = winSize
            winR = winSize
        else:
            winL = winSize[0]
            winR = winSize[1]
        if method == 'link':
            text = self.getTextInLinkWindow( MappedContent, linkId, winL, winR )
        elif method == 'char':
            text = self.getTextInLinkWindow( MappedContent, linkId,
                                                 winL, winR )
        else:
            raise AttributeError
        words = set(re.split('[ \t\n]', text.lower()))
        words = self.kw.words & words

        weight = 1.0
        for word in words:
            weight = weight + self.kw.keyWords[word] * (10 - weight) / 10
        return weight

    def getTextInCharWindow( self, MappedContent, linkId, 
                         winSizeL = 100, winSizeR = 100 ):
        winCenter = linkId * 2 + 1
        content_len = len(MappedContent)
        winCharSize = 0
        index = winCenter - 1
        lWin = ''
        rWin = ''
        while winCharSize < winSizeL and index >= 0:
            newStr = MappedContent[index] 
            lWin = newStr + lWin
            winCharSize += len(newStr)
            index -= 2
        index = winCenter + 1
        winCharSize = 0
        while winCharSize < winSizeR and index < content_len:
            newStr = MappedContent[index] 
            rWin += newStr
            winCharSize += len(newStr)
            index += 2
        return lWin + rWin

    def getTextInLinkWindow( self, MappedContent, linkId, 
                         winSizeL = 1, winSizeR = 1 ):
        winCenter = linkId * 2 + 1
        content_len = len(MappedContent)
        index = winCenter - 1
        lWin = ''
        rWin = ''
        while winSizeL != 0 and index >= 0:
            newStr = MappedContent[index]
            if type(newStr) == types.IntType:
                newStr = str(newStr)
            lWin = ''.join(newStr + lWin)

            index -= 2
            winSizeL -= 1
        index = winCenter + 1
        winSizeR += 1
        while winSizeR != 0 and index < content_len:
            newStr = MappedContent[index]
            if type(newStr) == types.IntType:
                newStr = str(newStr)
            rWin += newStr
            index += 2
            winSizeR -= 1
        return lWin + rWin

