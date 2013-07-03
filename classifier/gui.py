#!/usr/bin/python
# -*- coding: utf-8 -*-
from tag_manager import Tag_manager
import sys, signal
from PyQt4.QtGui import *
from PyQt4.QtCore import *
MAX_NUM = 5
MAX_DIFF = 2

class Clgui(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        self.inpfield = QTextEdit(self)
        self.outpfield = QTextEdit(self)
        self.outpfield.setReadOnly(True)
        hbox.addWidget(self.inpfield)
        hbox.addWidget(self.outpfield)
        vbox.addItem(hbox)
        hbox = QHBoxLayout()
        self.loadbutton = QPushButton('load', self)
        self.checkbutton = QPushButton('check', self)
        hbox.addWidget(self.checkbutton)
        hbox.addWidget(self.loadbutton)
        vbox.addItem(hbox)
        hbox = QHBoxLayout()
        self.wordfield = QTextEdit(self)
        hbox.addWidget(self.wordfield)
        self.pairfield = QTextEdit(self)
        hbox.addWidget(self.pairfield)
        self.wordfield.setReadOnly(True)
        self.pairfield.setReadOnly(True)
        vbox.addItem(hbox)
        self.genrebox = QComboBox(self)
        vbox.addWidget(self.genrebox)
        self.setLayout(vbox)
        self.cls = Tag_manager()
        self.connect(self.loadbutton, SIGNAL('clicked()'),
            self.load)
        self.connect(self.checkbutton, SIGNAL('clicked()'),
            self.check)
        self.connect(self.genrebox, SIGNAL('currentIndexChanged(QString)'),
            self.showwords)


    def load(self):
        self.loadbutton.setDisabled(True)
        self.genrebox.clear()
        self.cls.get_data('ru')
        self.genrebox.addItem('')
        for tag in sorted(self.cls.data):
            self.genrebox.addItem(tag)

    def check(self):
        text = unicode(self.inpfield.toPlainText())
        pre_tags = self.cls.find_tags(text, 'ru')
        tags = {}
        temptags = {}
        for tag in (sorted(pre_tags, key = pre_tags.get, reverse = True))[0:20]:
            if ((pre_tags[tag] * MAX_DIFF) >= pre_tags[sorted(pre_tags, key = pre_tags.get, reverse = True)[0]]):
                tags[tag] = pre_tags[tag]
            temptags[tag] = pre_tags[tag]
        if len(tags) > MAX_NUM:
            tags = {}
        outp = ""
        for t in sorted(temptags, key = temptags.get, reverse = True):
            outp += (str(temptags[t]) + ' - ' + t + "\n")
        self.outpfield.setPlainText(outp)

    def showwords(self, tag):
        tag = unicode(tag)
        if tag != '':
            self.wordfield.clear()
            self.pairfield.clear()
            for w in sorted(self.cls.data[tag], key = lambda x: 1.0*self.cls.data[tag][x].nonzero * self.cls.data[''][x].num/(self.cls.data[''][x].nonzero * self.cls.data[tag][x].num + self.cls.data[tag][x].nonzero * self.cls.data[''][x].num), reverse=True):
                self.wordfield.append(str(1.0*self.cls.data[tag][w].nonzero * self.cls.data[''][w].num/(self.cls.data[''][w].nonzero * self.cls.data[tag][w].num + self.cls.data[tag][w].nonzero * self.cls.data[''][w].num)) + ' - ' + w)
            for w in sorted(self.cls.pairdata[tag], key = lambda x: 1.0*self.cls.pairdata[tag][x].nonzero * self.cls.pairdata[''][x].num/(self.cls.pairdata[''][x].nonzero * self.cls.pairdata[tag][x].num + self.cls.pairdata[tag][x].nonzero * self.cls.pairdata[''][x].num), reverse=True):
                self.pairfield.append(str(1.0*self.cls.pairdata[tag][w].nonzero * self.cls.pairdata[''][w].num/(self.cls.pairdata[''][w].nonzero * self.cls.pairdata[tag][w].num + self.cls.pairdata[tag][w].nonzero * self.cls.pairdata[''][w].num)) + ' - ' + w)
        self.wordfield.verticalScrollBar().setValue(self.wordfield.verticalScrollBar().minimum())
        self.pairfield.verticalScrollBar().setValue(self.pairfield.verticalScrollBar().minimum())




app = QApplication(sys.argv)

g = Clgui()
g.show()
signal.signal(signal.SIGINT, signal.SIG_DFL)

sys.exit(app.exec_())

