#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Pootling
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (29 December 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details. 
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on Project of Catatog File.


from PyQt4 import QtCore, QtGui
from pootling.ui.Ui_NewProject import Ui_NewProject
from pootling.modules import FileDialog
from translate.lang import common
import translate.lang.data as data
import pootling.modules.World as World
import os

class newProject(QtGui.QDialog):
    """
        This module implementation with newProject, openProject and openrecentProject
    """
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_NewProject()
        self.ui.setupUi(self)
        self.setWindowTitle("New Project of Catalog Manager")  
        self.ui.projectName.setFocus()
        self.ui.btnNext.setEnabled(False)
        self.ui.btnBack.setEnabled(False)
        self.ui.btnFinish.setEnabled(False)
        self.ui.lblprojecttype.hide()
        self.ui.cbxProject.hide()
        self.value = True
        self.fileExtension = ".ini"

        self.connect(self.ui.btnCancel, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("reject()"))
        self.connect(self.ui.btnBack, QtCore.SIGNAL("clicked()"), self.backButton)
        self.connect(self.ui.btnNext, QtCore.SIGNAL("clicked()"), self.nextButton)
        self.connect(self.ui.btnFinish, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("accept()"))
        self.connect(self.ui.btnFinish, QtCore.SIGNAL("clicked()"), self.finishButton)
        self.connect(self.ui.projectName, QtCore.SIGNAL("textChanged(QString)"), self.projectNameAvailable)
        self.connect(self.ui.configurationFile, QtCore.SIGNAL("textChanged(QString)"), self.projectNameAvailable)

        # call dialog box of FileDialog
        self.connect(self.ui.btnBrowse, QtCore.SIGNAL("clicked()"), self.showFileDialog)
        self.connect(self.ui.btnAdd, QtCore.SIGNAL("clicked()"), self.showFileDialog)
        self.filedialog = FileDialog.fileDialog(self)
        self.connect(self.filedialog, QtCore.SIGNAL("location"), self.addLocation)
        self.connect(self.ui.btnClear, QtCore.SIGNAL("clicked()"), self.clearLocation)
        self.connect(self.ui.btnMoveUp, QtCore.SIGNAL("clicked(bool)"), self.moveUp)
        self.connect(self.ui.btnMoveDown, QtCore.SIGNAL("clicked(bool)"), self.moveDown)

        # add item to project type
        self.ui.cbxProject.addItem(self.tr("KDE"))
        self.ui.cbxProject.addItem(self.tr("GNOME"))
        self.ui.cbxProject.addItem(self.tr("Other"))

        # language code of the country
        language = []
        for langCode, langInfo in data.languages.iteritems():
            language.append(langInfo[0])
            language.sort()
        self.ui.cbxLanguages.addItems(language)

    def showFileDialog(self):
        self.filedialog.show()
        if (self.value == True):
            self.filedialog.setWindowTitle("Choosing path of filename")
            self.value = False
        else:
            self.filedialog.setWindowTitle("Choosing file or a directory")
            self.value = True

    def projectNameAvailable(self):
          if (self.ui.projectName.text() and self.ui.configurationFile.text()):
              self.ui.btnNext.setEnabled(True)
              self.value = False
          else:
              self.ui.btnNext.setEnabled(False)

    def addLocation(self, text):
        if (self.value == False):
            data = QtGui.QListWidgetItem(text)
            self.ui.configurationFile.setText(data.text())
        else:
            item = QtGui.QListWidgetItem(text)
            items = self.ui.listWidget.findItems(text, QtCore.Qt.MatchCaseSensitive)
            if (not items):
                self.ui.listWidget.addItem(item)
                self.value = False
                self.ui.btnFinish.setEnabled(True)

    def clearLocation(self):
        self.ui.listWidget.clear()
        self.ui.btnFinish.setEnabled(False)
        self.value = False
        self.catalogModified = True
        self.ui.chbDiveIntoSubfolders.setChecked(False)

    def moveItem(self, distance):
        '''move an item up or down depending on distance
        @param distance: int'''
        currentrow = self.ui.listWidget.currentRow()
        currentItem = self.ui.listWidget.item(currentrow)
        distanceItem = self.ui.listWidget.item(currentrow + distance)
        if (distanceItem):
            temp = distanceItem.text()
            distanceItem.setText(currentItem.text())
            currentItem.setText(temp)
            self.ui.listWidget.setCurrentRow(currentrow + distance)

    def moveUp(self):
        '''move item up'''
        self.moveItem(-1)

    def moveDown(self):
        '''move item down'''
        self.moveItem(1)

    def backButton(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.btnNext.setEnabled(True)
        self.ui.btnBack.setEnabled(False)
        self.ui.btnFinish.setEnabled(False)
        self.ui.projectName.setFocus()

    def nextButton(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.btnNext.setEnabled(False)
        self.ui.btnBack.setEnabled(True)
        if (self.ui.listWidget.count()):
            self.ui.btnFinish.setEnabled(True)
        else:
            self.ui.btnFinish.setEnabled(False)

    def addItemToDict(self):
        name = self.ui.projectName.text().toAscii()
        projectname = name + self.fileExtension
        configure = self.ui.configurationFile.text()
        # Concatenate string between directory path and filename
        path = os.path.join(configure + os.path.sep + projectname)
        language = self.ui.cbxLanguages.currentText()
        projectType = self.ui.cbxProject.currentText()
        self.projectInfo = {}
        self.projectInfo['path'] = path 
        self.projectInfo['lang'] = language
        self.projectInfo['project'] = projectType

    def finishButton(self ):
        # In case project name is empty, next button can not go to... 
        stringlist = QtCore.QStringList()
        for i in range(self.ui.listWidget.count()):
            stringlist.append(self.ui.listWidget.item(i).text())
        self.addItemToDict()
        self.projectInfo['itemList'] = stringlist
        self.projectInfo['diveIntoSubCatalog'] = self.ui.chbDiveIntoSubfolders.isChecked()
        self.storeDataToNewFile()
        self.clearStackedWidget()

    def storeDataToNewFile(self):
        proSettings = QtCore.QSettings(self.projectInfo['path'], QtCore.QSettings.IniFormat)
        proSettings.setValue("itemList", QtCore.QVariant(self.projectInfo['itemList']))
        proSettings.setValue("lang", QtCore.QVariant(self.projectInfo['lang']))
        proSettings.setValue("project", QtCore.QVariant(self.projectInfo['project']))
        proSettings.setValue("diveIntoSubCatalog", QtCore.QVariant(self.projectInfo['diveIntoSubCatalog']))

    def clearStackedWidget(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.projectName.setText("") 
        self.ui.configurationFile.setText("")
        self.ui.cbxProject.clear()
        self.ui.listWidget.clear()
        self.ui.chbDiveIntoSubfolders.setChecked(False)
        self.ui.btnBack.setEnabled(False)
        self.ui.btnFinish.setEnabled(False)

    def openProject(self):
        fileOpen = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                        QtCore.QDir.homePath(),
self.tr("IniFormat Files(*.ini)"))
        if not fileOpen.isEmpty():
            proSettings = QtCore.QSettings(fileOpen, QtCore.QSettings.IniFormat)
            itemList = proSettings.value("itemList").toStringList()
            includeSub = proSettings.value("itemList").toBool()
            self.emit(QtCore.SIGNAL("updateCatalog"), itemList,  includeSub)
        self.emit(QtCore.SIGNAL("pathOfFileName"),  fileOpen)


if __name__ == "__main__":
    import os, sys
    app = QtGui.QApplication(sys.argv)
    Newpro = newProject(None)
    Newpro.show()
    sys.exit(Newpro.exec_())
