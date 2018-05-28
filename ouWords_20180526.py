#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog, QApplication
from PyQt5.Qt import *
import pyautogui
import re
import win32com.client
import configparser


MAC = "qt_mac_set_native_menubar" in dir()
pattern = '([0-9a-zA-Z]+)'

def autohotkey(index, value):
    with open('zh.ahk', 'r', encoding = 'utf-8', errors='ignore') as f:
        contents = f.readlines()

    contents.insert(index, value)
    
    with open('zh.ahk', 'w', encoding = 'utf-8', errors='ignore') as f:
        contents = "".join(contents)
        f.write(contents)

def activatewin():
    config = configparser.ConfigParser()
    config.read('ouWords.ini')
    last_win = config['section']['win'] 
    name_last_win = last_win[1:-1]
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.AppActivate(name_last_win)
    shell.SendKeys("^v", 0)

class StringListDlg(QDialog):

    def __init__(self, name, stringlist=None, parent=None):
        super(StringListDlg, self).__init__(parent)

        self.name = name
        self.result = ""
        self.resize(400, 900)
        self.move(1500, 20)
#       快速鍵！
        self.shortcut = QShortcut(QKeySequence(Qt.Key_A), self)
        self.shortcut.activated.connect(self.on_open)
        
        self.listWidget = QListWidget()
        if stringlist is not None:
            self.listWidget.addItems(stringlist)
            self.listWidget.setCurrentRow(0)
        buttonLayout = QVBoxLayout()
        for text, slot in (("&Add...", self.add),
                           ("&Edit...", self.edit),
                           ("&Remove...", self.remove),
                           ("&Up", self.up),
                           ("&Down", self.down),
                           ("&Sort", self.listWidget.sortItems),
                           ("&Refresh", self.refresh),
                           ("&Save", self.filesave),
                           ("Close", self.accept)):
            button = QPushButton(text)
            if not MAC:
                button.setFocusPolicy(Qt.NoFocus)
            if text == "Close":
                buttonLayout.addStretch()
            buttonLayout.addWidget(button)
            button.clicked.connect(slot)

        layout = QHBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        self.setWindowTitle("Edit %s List" % self.name)
        ##########
        self.listWidget.itemActivated.connect(self.returnValue)

    @pyqtSlot()
    def on_open(self):
        self.Autoadd()

    def Autoadd(self):
        strs = []
        try:
            string = QApplication.clipboard().text()
            if len(string)<12:
                m = re.search('([0-9a-zA-Z]+)', string)
                if m: 
                    strNew = m.group(0)+"：" + string[:m.start()]  #轉換成元件符號說明的元件格式
                    num, strNew = m.group(0), string
                    strs.append((num, strNew))
                else:
                    strNew = string 
#                   num 沒有值會出現異常，但是在try內所以還是能夠正常運作。                    
                self.listWidget.insertItem(0, strNew)
            else:
                Wore_Re= re.compile('[。，該個一的及\s\t](\D+)([0-9a-zA-Z]+)')
                string = re.sub(r'[（(].*?[)）]', '', string)
                for m in Wore_Re.finditer(string):
                    strNew = m.group(2)+"：" + m.group(1)
                    self.listWidget.insertItem(0, strNew)
                    num, strNew = m.group(2), m.group(1)+m.group(2)
                    strs.append((num, strNew))
#                    autohotkey(m.group(2),m.group(1)+m.group(2))
            index = 6
            value = ''
#           num 沒有值會出現異常，但在try內能正常運作，剛好跳過呼叫autohotkey。                    
            for num, strNew in strs:
                value = value + ':*:{}/::\n\tsend {}\n\treturn\n'.format(num, strNew)
#            print(index, num, value)
            autohotkey(index, value)
        except:
            print ('Could not call Autoadd().')









    def add(self):
        row = self.listWidget.currentRow()
        title = "Add %s" % self.name
        string, ok = QInputDialog.getText(self, title, title)
        if ok and string:
        #if ok :
            self.listWidget.insertItem(row, string)


    def edit(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        if item is not None:
            title = "Edit %s" % self.name
            string, ok = QInputDialog.getText(self, title, title,
                                QLineEdit.Normal, item.text())
            if ok and string:
                item.setText(string)


    def remove(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        if item is None:
            return
        reply = QMessageBox.question(self, "Remove %s" % self.name,
                        "Remove %s `%s'?" % (
                        self.name, str(item.text())),
                        QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            item = self.listWidget.takeItem(row)
            del item


    def up(self):
        row = self.listWidget.currentRow()
        if row >= 1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row - 1, item)
            self.listWidget.setCurrentItem(item)


    def down(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count() - 1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row + 1, item)
            self.listWidget.setCurrentItem(item)

    def reject(self):
        self.accept()


    def accept(self):
        self.stringlist = list()
        for row in range(self.listWidget.count()):
            self.stringlist.append(self.listWidget.item(row).text())
        QDialog.accept(self)
   
    def returnValue(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.item(row)
        #print(self.listWidget.currentItem().text())
        self.result = item.text()
        try:
            i = self.result.split("：")   #轉換成說明書的元件格式
            if len(i)>1:
                i = i[1]+i[0]
            else:
                i = i[0]                    #轉換成說明書的元件格式
            clipboard = QApplication.clipboard()
            clipboard.setText(i)
        except:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.result)
            #print ('Could not copy data to clipboard.')

        try:
            activatewin()
        except:
#            shell = win32com.client.Dispatch("WScript.Shell")
#            shell.SendKeys("%{TAB}", 0)
#            WScript.Sleep( 800)
#            shell.SendKeys("^v", 0)
#            pass
#        finally:
            pyautogui.hotkey('alt', 'tab')  #, interval=0.1)
            pyautogui.PAUSE = 0.2
            pyautogui.hotkey('ctrl', 'v')      
           
        return self.result

    def refresh(self):
        with open('workfile.txt', 'r', encoding = 'utf-8') as f:
            stringlist = f.read().splitlines()
        if stringlist is not None:
            self.listWidget.clear()
            self.listWidget.addItems(stringlist)
            self.listWidget.setCurrentRow(0)

    def filesave(self):
        reply = QMessageBox.question(None, "警告",
                        "舊資料表會被清空後，才儲存新資料表，故請先備份！！",
                        QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            itemsTextList =  (str(self.listWidget.item(i).text()) 
                                for i in range(self.listWidget.count()))
            with open('workfile.txt', 'w', encoding = 'utf-8') as f:
                f.write("\n".join([str(x) for x in itemsTextList]))
        

if __name__ == "__main__":
  
    fruit = []
# =============================================================================
#     with open('default.txt', 'r', encoding = 'utf-8') as f:
#         fruit = fruit +f.read().splitlines()
# =============================================================================
    with open('workfile.txt', 'r', encoding = 'utf-8') as f:
        fruit = fruit + f.read().splitlines()

    app = QApplication(sys.argv)
    form = StringListDlg("Fruit", fruit)
    form.exec_()
    with open('workfile.txt', 'w', encoding = 'utf-8') as f:
        f.write("\n".join([str(x) for x in form.stringlist]))
#         print("\n".join([str(x) for x in form.stringlist]))  