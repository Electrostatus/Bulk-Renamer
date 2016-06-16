from PyQt4 import QtCore, QtGui#, uic
from ui_SecretOps import Ui_Secret
import sys

##GUIForm2, baseClass2 = uic.loadUiType('SecretOps.ui')

class Sssh(QtGui.QDialog, Ui_Secret):#Ui_Secret):#GUIForm):
    SecretSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(Sssh, self).__init__(parent); self.setupUi(self)
        self.FileExtenInput.setMaxLength(10); hide = self.NumberStartInput
    
        self.label.hide(); hide.hide(); hide.setEnabled(False)
        self.resize(self.sizeHint())

    def closeEvent(self, event):
        self.SecretSignal.emit(self.FileExtenInput.text())

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = Sssh(); w.show(); sys.exit(app.exec_())
