# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Program Files\Python 2.7.3\Bulk_Renamer\V1.1\SecretOps.ui'
#
# Created: Wed Oct 09 19:20:04 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Secret(object):
    def setupUi(self, Secret):
        Secret.setObjectName(_fromUtf8("Secret"))
        Secret.resize(154, 69)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/textfield.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Secret.setWindowIcon(icon)
        Secret.setSizeGripEnabled(False)
        Secret.setModal(False)
        self.gridLayout = QtGui.QGridLayout(Secret)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Secret)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.NumberStartInput = QtGui.QSpinBox(Secret)
        self.NumberStartInput.setMinimumSize(QtCore.QSize(30, 20))
        self.NumberStartInput.setMaximumSize(QtCore.QSize(50, 20))
        self.NumberStartInput.setAlignment(QtCore.Qt.AlignCenter)
        self.NumberStartInput.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.NumberStartInput.setMaximum(2000000001)
        self.NumberStartInput.setProperty("value", 0)
        self.NumberStartInput.setObjectName(_fromUtf8("NumberStartInput"))
        self.gridLayout.addWidget(self.NumberStartInput, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Secret)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.FileExtenInput = QtGui.QLineEdit(Secret)
        self.FileExtenInput.setMinimumSize(QtCore.QSize(30, 20))
        self.FileExtenInput.setMaximumSize(QtCore.QSize(50, 20))
        self.FileExtenInput.setText(_fromUtf8(""))
        self.FileExtenInput.setAlignment(QtCore.Qt.AlignCenter)
        self.FileExtenInput.setObjectName(_fromUtf8("FileExtenInput"))
        self.gridLayout.addWidget(self.FileExtenInput, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Secret)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 2)

        self.retranslateUi(Secret)
        QtCore.QMetaObject.connectSlotsByName(Secret)

    def retranslateUi(self, Secret):
        Secret.setWindowTitle(QtGui.QApplication.translate("Secret", "SECRET OPTIONS", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setWhatsThis(QtGui.QApplication.translate("Secret", "Allows you number files starting from other than 1.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Secret", "Start Numbering at:", None, QtGui.QApplication.UnicodeUTF8))
        self.NumberStartInput.setWhatsThis(QtGui.QApplication.translate("Secret", "Allows you number files starting from other than 1.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setWhatsThis(QtGui.QApplication.translate("Secret", "Allows you to rename the file extension.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Secret", "Rename File Extension:", None, QtGui.QApplication.UnicodeUTF8))
        self.FileExtenInput.setToolTip(QtGui.QApplication.translate("Secret", "Must have the . in front!", None, QtGui.QApplication.UnicodeUTF8))
        self.FileExtenInput.setWhatsThis(QtGui.QApplication.translate("Secret", "Allows you to rename the file extension.", None, QtGui.QApplication.UnicodeUTF8))
        self.FileExtenInput.setPlaceholderText(QtGui.QApplication.translate("Secret", "*.*", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setWhatsThis(QtGui.QApplication.translate("Secret", "I\'m not here! You never saw me! Never saw me!", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Secret", "Don\'t tell anyone I\'m here!", None, QtGui.QApplication.UnicodeUTF8))

import rename_rc
