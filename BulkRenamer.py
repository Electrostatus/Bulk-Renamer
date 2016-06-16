from BulkRenameSecret import Sssh
from PyQt4 import QtCore, QtGui
from random import randint
from PIL import Image
import sys, os, time

Loadui = False  # set to false if making .exe, update the Ui_Renamer first
Version = 1.2

if Loadui:
    from PyQt4 import uic
    GUIForm, baseClass = uic.loadUiType('BulkRename.ui')
else:
    from ui_BulkRename import Ui_Renamer
    GUIForm, baseClass = Ui_Renamer, QtGui.QWidget
# icons from freeiconsweb.com, specifically Marcis Gasuns (http://led24.de/iconset/)

class Control(baseClass, GUIForm):
    lockRequest = QtCore.pyqtSignal(object)
    emitProgess = QtCore.pyqtSignal(object)
    emitIssue = QtCore.pyqtSignal(object)
    
    def __init__(self,parent=None):
        super(Control,self).__init__(parent)
        self.setupUi(self); self.Started = False

        self.setGeometry(QtCore.QRect(0, 0, 545, 670))  # set current size
        self.setMinimumSize(QtCore.QSize(540, 620))  # set min size
        self.centerOnScreen()
        
        # connect to signals
        self.lockRequest.connect(self._lock_program)
        self.emitProgess.connect(self._inform_progress)
        self.emitIssue.connect(self._inform_issue)
        
        self.Pref_CB.stateChanged.connect(self.Prefix_Settings)
        self.Suff_CB.stateChanged.connect(self.Suffix_Settings)
        self.Locate_Button.clicked.connect(self.getFolder)
        self.Rename_Button.clicked.connect(self.ReNameExe)
        self.Opts_Button.clicked.connect(self.AccessOpts)
        self.More_Button.clicked.connect(self.MoreOpts)
        self.CurrentView.itemSelectionChanged.connect(self.selected)

        self.PreStart_SB.valueChanged.connect(self.selected)
        self.SufStart_SB.valueChanged.connect(self.selected)
        self.NumStart_SB.valueChanged.connect(self.selected)
        self.PreAddDig_SB.valueChanged.connect(self.selected)
        self.SufAddDig_SB.valueChanged.connect(self.selected)
        self.AddDig_SB.valueChanged.connect(self.selected)

        self.Prefix_lineEdit.textEdited.connect(self.validate)
        self.Suffix_lineEdit.textEdited.connect(self.validate)
        self.NewName_lineEdit.textEdited.connect(self.validate)
        self.PreSep_lineEdit.textEdited.connect(self.validate)
        self.SufSep_lineEdit.textEdited.connect(self.validate)
        self.NumSep_lineEdit.textEdited.connect(self.validate)

        chkboxs = [self.PreNam_RB, self.PreNum_RB, self.PreAlp_RB,
           self.SufNam_RB, self.SufNum_RB, self.SufAlp_RB,
           self.AlphaNum_CB, self.NameDate_CB]
        for cb in chkboxs:
            cb.clicked.connect(self._RB_catch)               
            cb.hide()

        self.preboxed = QtGui.QButtonGroup()
        self.preboxed.addButton(self.PreNam_RB)
        self.preboxed.addButton(self.PreNum_RB)
        self.preboxed.addButton(self.PreAlp_RB)
        self.preboxed.setExclusive(True)

        self.sufboxed = QtGui.QButtonGroup()
        self.sufboxed.addButton(self.SufNam_RB)
        self.sufboxed.addButton(self.SufNum_RB)
        self.sufboxed.addButton(self.SufAlp_RB)
        self.sufboxed.setExclusive(True)
        self.PreNam_RB.setChecked(True)
        self.SufNam_RB.setChecked(True)

        self.AlphaNum_CB.show()
        self.NameDate_CB.show()
        
        self.OpsBox.setEnabled(False)
        self.OpsBox.hide()
        self.Prefix_lineEdit.setEnabled(False)
        self.Suffix_lineEdit.setEnabled(False)
        self.Prefix_lineEdit.hide()
        self.Suffix_lineEdit.hide()
        self.SubSets_Frame.hide()

        self.More_frame.hide()
        self.PreAddDig_SB.hide()
        self.SufAddDig_SB.hide()
        self.HrForm_CB.hide()
        self.MilliSec_CB.hide()
        self.Time_Sep_line.hide()
        self.NumSep_lineEdit.setText(' ')
        
        self.SufAddDig_SB.hide()
        self.SufStart_SB.hide()
        self.SufSep_lineEdit.hide()
        self.PreAddDig_SB.hide()
        self.PreStart_SB.hide()
        self.PreSep_lineEdit.hide()
        self.Issue_label.hide()
        self.AlphaFrame.resize(125, 90)
        self._fixes_labels()
        
        self.fld = ''  # current folder
        self.locked = False # bool flag for if program is locked or not
        self.files = []  # currently selected files
        self.dates = {}  # dates of selected files
        self.ext_types = []  # extensions of selected files
        self.ext_totals = {}  # extension: number of files with that extension
        self._time_fmt = "%Y-%m-%d %H.%M.%S.%f"  # self explanatory
        self._newExt = ''  # new extension

        # time stuff
        self.ChangeFormat(0); self.DateFormatCoB.hide()
        for i in sorted(self.DateFormats, key=len): self.DateFormatCoB.addItem(i)
        self.DateFormatCoB.currentIndexChanged[str].connect(self.ChangeFormat)
        self.HrForm_CB.stateChanged.connect(self.ChangeFormat)
        self.MilliSec_CB.stateChanged.connect(self.ChangeFormat)
        
        # color coding
        self.cols = {0: QtCore.Qt.black, 1: QtCore.Qt.darkGreen,
            2: QtCore.Qt.darkCyan, 3: QtCore.Qt.darkBlue, 4: QtCore.Qt.darkRed,
            5: QtCore.Qt.darkYellow, 6: QtCore.Qt.darkMagenta,
            7: QtCore.Qt.darkYellow, 8: QtCore.Qt.darkGray, 9: QtCore.Qt.green,
            10: QtCore.Qt.cyan, 11: QtCore.Qt.blue, 12: QtCore.Qt.red,
            13: QtCore.Qt.magenta, 14: QtCore.Qt.yellow,  # first 17 colors
            15: QtCore.Qt.lightGray, 16: QtCore.Qt.gray}  # are set

        # for fun
        icons = ([":/newPrefix/drive_rename.png"] +
                 [":/newPrefix/textfield_rename.png"]*8 +
                 [":/newPrefix/textfield.png"]); icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(icons[randint(0,len(icons))-1]),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        easter_display = randint(0, 34)
        if not easter_display % 5:
            info = 'Bulk File Renamer\nFrom Orthallelous'
            self.Current_Location_Label.setText(info)
        self.Started = True

    def getFolder(self, refresh=False):
        "locate what folder to load and view"
        if not refresh:
            fld = QtGui.QFileDialog().getExistingDirectory(directory=self.fld)
            self.Current_Location_Label.setText(fld)
            self.Current_Location_Label.setToolTip(fld)
            
            if fld == '': return
            encod = sys.getfilesystemencoding()
            self.fld = unicode(fld, encod)
        else: pass

        self.lockRequest.emit(True)
        listdir = os.listdir(self.fld)
        tot = float(len(listdir))
        
        files, dates = [], {}
        for i, fn in enumerate(listdir, 1):
            app.processEvents()  # app is defined at bottom of this file
            prog = 'Gathering files... {:06.2%}'.format(i / tot)
            self.emitProgess.emit(prog)
            
            name = unicode(fn)#, encod)
            if os.path.isdir(os.path.join(self.fld, name)): continue  # folder
            if os.path.splitext(fn)[1]:  # add only files with extensions
                files.append(name)
                dates[name] = self.oldest(name)

        # bookkeeping
        self.emitProgess.emit('Sorting...'); app.processEvents()
        ext_types, ext_totals = self.tally(files)
        
        self.files, self.dates = files, dates
        self.ext_types, self.ext_totals = ext_types, ext_totals
        self.populate_current_table(self.sorter(files))
        self.lockRequest.emit(False); app.processEvents()

    def tally(self, lst):
        "count number of file types from selected files"
        totals = {}
        for fn in lst:
            ext = os.path.splitext(fn)[1]
            if ext not in totals: totals[ext] = 0
            totals[ext] += 1

        sorted_ext = sorted(totals.keys(), key=totals.get)
        sorted_ext.reverse()
        return sorted_ext, totals
            
    def sorter(self, lst):
        "returns a sorted list of file names"
        # as a separate function so a custom sorting function can be done
        dateFirst = True
        
        types, totals = self.ext_types, self.ext_totals
        if dateFirst:  # sort by date, then extensions
            lst = sorted(lst, key=self.dates.get)
            lst = sorted(lst, key=lambda x:totals.get(os.path.splitext(x)[1]),
                         reverse=True)
        else:  # have the newest files first instead
            lst = sorted(lst, key=lambda x:
                         (totals.get(os.path.splitext(x)[1]),
                          self.dates.get(x)), reverse=True)       
        return lst

    def imgDate(self, fn):
        "returns the image date from image (if available)"
        std_fmt = '%Y:%m:%d %H:%M:%S.%f'
        tags = [(36867, 37521),  # (DateTimeOriginal, SubsecTimeOriginal)
                (36868, 37522),  # (DateTimeDigitized, SubsecTimeOriginal)
                (306, 37520), ]  # (DateTime, SubsecTime)
        try: exif = Image.open(fn)._getexif()
        except: return None
        if type(exif) != dict: return None
        
        for t in tags:
            dat_stmp = exif.get(t[0])
            sub_stmp = exif.get(t[1], '0')
            
            # PIL.PILLOW_VERSION >= 3.0 returns a tuple now (why?!)
            dat_stmp = dat_stmp[0] if type(dat_stmp) == tuple else dat_stmp
            sub_stmp = sub_stmp[0] if type(sub_stmp) == tuple else sub_stmp
            if dat_stmp != None: break
            
        if dat_stmp == None: return None
        full = '{}.{}'.format(dat_stmp, sub_stmp)
        T = time.mktime(time.strptime(full, std_fmt)) + float('0.' + sub_stmp)
        return T

    def oldest(self, fn):
        "returns the oldest date for a file"
        name = os.path.join(self.fld, fn)
        
        cd = os.path.getctime(name)  # creation time 
        md = os.path.getmtime(name)  # modified time
        ad = os.path.getatime(name)  # accessed time
        dates = [cd, md, ad]

        # until PIL/Pillow gets a function that returns all valid image
        #  extensions, this will have to do
        # https://pillow.readthedocs.org/en/3.1.x/handbook/image-file-formats.html
        valid_imgs = ('.jpg', '.jpeg',# '.jpe', '.jif', '.jfif', '.jfi',
                      )#'.png', '.tiff', '.gif', '.bmp', '.tif', )
        
        # if file is an image, extract date from image's metadata
        # note: this is extremely slow for when a folder contains thousands
        #       of valid images, might be best to not have it at all?
        if os.path.splitext(name)[1].lower() in valid_imgs:
            pd = self.imgDate(name)
            if pd != None: dates.append(pd)  # only add it if successful
        return sorted(dates)[0] 
        
    def ReNameExe(self):
        items = self.CurrentView.selectedItems()
        names =[unicode(i.text()) for i in items]
        
        new_names = self._NAMINGFUNCTION(names)
        self.OLDN, self.NEWN = names, new_names

        # check if no name has been given
        noName = (self.NewName_lineEdit.text() == '' and
                  self.NameDate_CB.isChecked() == False)
        if noName:
            alert = QtGui.QMessageBox(QtGui.QMessageBox.Warning, 'Alert',
                                      'No name has been given.')
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/newPrefix/drive_rename.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            alert.setWindowIcon(icon)
            alert.exec_(); return
            
        # ask to continue, no undo option after this!
        mbox = QtGui.QMessageBox(QtGui.QMessageBox.Question, 'Continue?',
                'Do you wish to continue?\nThere is no undo after this!')
        mbox.setStandardButtons(QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/newPrefix/textfield.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        mbox.setWindowIcon(icon)
        
        ques = mbox.exec_()
        if ques == 0x00010000: return  # no, stop!
        elif ques == 0x00004000: pass  # yes, continue!
        else: return  # something has gone horribly wrong! don't do anything!

        fld, old, new = self.fld, self.OLDN, self.NEWN
        if fld == '': return
        total = float(len(new))
        
        self.lockRequest.emit(True); self.emitIssue.emit('CLEAR')
        for i, n in enumerate(new):
            old_name =os.path.join(fld, old[i])
            new_name =os.path.join(fld, n)
            app.processEvents()

            try: os.rename(old_name, new_name)
            except: self.emitIssue.emit(old_name)

            self.emitProgess.emit('{:06.2%}'.format((i+1) / total))

        self.getFolder(True)  # refresh file list
        self.lockRequest.emit(False)
        
    def _inform_issue(self, fil):
        "slot for informing user if there was an issue renaming a file"
        if fil == 'CLEAR':
            self.Issue_label.hide()
            self.Issue_label.setText('')
            self.Issue_label.setToolTip('')
            self.Current_Location_Label.setText(self.fld)
        else: 
            self.Current_Location_Label.setText('Renaming issue with ' + fil)
            self.Issue_label.show()
            self.Issue_label.setText('Renaming issue with ' + fil)
            self.Issue_label.setToolTip('Renaming issue with ' + fil)

    def _inform_progress(self, prog):
        "slot for informing the progress (%) of the renaming thread"
        self.NewName_lineEdit.setText(prog)

    def _lock_program(self, lock):
        "slot for locking/unlocking the program"
        if lock: self._lock()
        else: self._unlock()
        
    def _lock(self):
        "lock the program"
        self.locked = True
        tolock = self._lockables()
        
        for lock in tolock:
            lock.blockSignals(True)
            lock.setEnabled(False)

        self.NewName_lineEdit.show()
        self.DateFormatCoB.hide()
        self.NameDate_CB.setCheckState(0)

    def _lockables(self):
        "returns the list of items to block"
        tolock = [self.PreNam_RB, self.PreNum_RB, self.PreAlp_RB,
                  self.SufNam_RB, self.SufNum_RB, self.SufAlp_RB,
                  self.AlphaNum_CB, self.NameDate_CB, self.Locate_Button,
                  self.Rename_Button, self.Prefix_lineEdit, self.Pref_CB,
                  self.Suffix_lineEdit, self.NewName_lineEdit, self.Suff_CB,
                  self.AddDig_SB, self.PreAddDig_SB, self.SufAddDig_SB,
                  self.HrForm_CB, self.MilliSec_CB, self.OpsBox,
                  self.Time_Sep_line, self.SufStart_SB, self.SufSep_lineEdit,
                  self.PreStart_SB, self.PreSep_lineEdit, self.Opts_Button,
                  self.More_Button, self.CurrentView, self.PreView,
                  self.More_frame, ]
        return tolock
            
    def _unlock(self):
        "unlock the program"
        tolock = self._lockables()
        for unlock in tolock:
            unlock.blockSignals(False)
            unlock.setEnabled(True)

        self.NewName_lineEdit.setText('')
        self.Prefix_lineEdit.setText('')
        self.locked = False
        
    def populate_current_table(self, names):
        "populate the current table view with files from selected folder"
        self.CurrentView.clearContents()
        self.CurrentView.setRowCount(len(names))
        self.CurrentView.setColumnCount(1)

        if names == []:  # no files in this folder, inform user
            self.CurrentView.setRowCount(1)
            empty = QtGui.QTableWidgetItem()
            empty.setText('This folder has no files')
            empty.setToolTip('<FONT COLOR=red>This folder has no files</FONT>')

            empty.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
            empty.setTextColor(QtCore.Qt.red); empty.setFlags(QtCore.Qt.NoItemFlags)

            self.CurrLabel.setText('Current (<FONT COLOR=red>No files</FONT>)')
            self.CurrLabel.setToolTip('Current (<FONT COLOR=red>No files</FONT>)')
            self.CurrentView.setItem(0, 0, empty); return

        types, totals, dates = self.ext_types, self.ext_totals, self.dates
        tot = float(len(names))

        for i, n in enumerate(names):
            prog = 'Populating table... {:06.2%}'.format((i+1)/tot)
            self.emitProgess.emit(prog)
            app.processEvents()  # app is defined at bottom of this file
            
            item = QtGui.QTableWidgetItem()
    
            item.setText(n)
            item.setToolTip(n + '\n' + time.ctime(dates.get(n, '')))
            
            ext = os.path.splitext(n)[1]
            col_id = types.index(ext)

            try: color = self.cols[col_id]
            except:  # generate new color and add for use in the preview
                r, g, b = randint(0, 255), randint(0, 255), randint(0, 255)
                color = QtGui.QColor(r, g, b)
                
                while color in self.cols.values():  # no repeats
                    r,g,b = randint(0, 255), randint(0, 255), randint(0, 255)
                    color = QtGui.QColor(r, g, b)

                self.cols[col_id] = color
    
            item.setTextColor(color)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.CurrentView.setItem(i, 0, item)  # row, column, widgetItem

        self.emitProgess.emit('')
        # current label
        num, tnum = len(names), len(totals)
        fil, are, typ = 'files', 'are', 'types'
        if num == 1: FIl, are, typ = 'file', 'is', 'type'
        header = 'There {} {:,} {}:'.format(are, num, fil)
        sub = '\n({:,} file type{})'.format(tnum, '' if tnum == 1 else 's')
        
        for t in sorted(totals, key=totals.get, reverse=True):
            tot = totals[t]
            fil, are, typ = 'files', 'are', 'types'
            if tot == 1: fil, are, typ = 'file', 'is', 'type'
            line = '\n   {:,} {} {}'.format(tot, t, fil)
            header = header + line

        self.CurrLabel.setToolTip(header + sub)
        self.CurrLabel.setText('Current ({:,} file{})'.format(num,
                                            '' if num == 1 else 's'))

    def validate(self, text):
        "verify the text does not contain invalid characters"
        invalid = ['\\', '/', '|', ':', '*', '"', '?', '<', '>']
        for i in invalid: text = text.replace(i, '')
        
        self.sender().setText(text)
        self.sender().setToolTip(text)
        self.selected()

    def selected(self):
        "prepare file names from selected list for preview table"
        items = self.CurrentView.selectedItems()
        names = [unicode(i.text()) for i in items]

        if names: self.populate_preview_table(names)
        else: return  # nothing selected

    def populate_preview_table(self, names):
        "populate preview table with selected files with their new names"
        self.PreView.clearContents()
        self.PreView.setRowCount(len(names))
        self.PreView.setColumnCount(1)

        nnames=self._NAMINGFUNCTION(names)
        types, totals, dates = self.ext_types, self.ext_totals, self.dates

        for i, n in enumerate(names):
            item = QtGui.QTableWidgetItem()

            ext = os.path.splitext(n)[1]
            color = self.cols[types.index(ext)]
            
            item.setText(nnames[i])
            item.setToolTip(n + '\n' + time.ctime(self.dates.get(n, '')))

            item.setTextColor(color)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            self.PreView.setItem(i, 0, item)  # row, column, widgetItem

        num = len(names)
        if num:  # preview label
            fil = 'file' if num == 1 else 'files'
            self.PrevLabel.setToolTip('{:,} selected {}'.format(num, fil))
            self.PrevLabel.setText('Preview ({:,} {})'.format(num, fil))

    def _NAMINGFUNCTION(self, names):
        "Rename a list of files, called by PerTable or ReNameExe def's"
        new_name_list = []
        tot = len(names); dates = self.dates
        ext_types, ext_tot = self.tally(names)

        root_num = {}  # root name counter for each file type
        pre_num  = {}  # prefix counter for each file type
        suf_num  = {}  # suffix counter for each file type
        dateCatch ={}  # counter for files with exact same dates
        
        # date formatting
        fb = "%Y-%m-%d %H.%M.%S.%f"  # fallback
        choice = str(self.DateFormatCoB.currentText())
        fmt = self.DateFormats.get(choice, fb)
        self._time_fmt = fmt
        
        # initialize counters
        for u in ext_types: root_num[u] = self.NumStart_SB.value()
        for u in ext_types: pre_num[u] = self.PreStart_SB.value()
        for u in ext_types: suf_num[u] = self.SufStart_SB.value()
        for u in ext_types: dateCatch[u] = 0

        pre_sep = str(self.PreSep_lineEdit.text())  # prefix separator
        suf_sep = str(self.SufSep_lineEdit.text())  # suffix separator
        num_sep = str(self.NumSep_lineEdit.text())  # name - number separator

        datenames = []
        for fn in names:
            # main counter
            ext = os.path.splitext(fn)[1]
            r_count = root_num[ext]
            r_fill = len(str(ext_tot[ext])) + self.AddDig_SB.value()
            
            c = str(r_count).zfill(r_fill)
            if self.AlphaNum_CB.isChecked():
                r_fill = (len(self.alph(ext_tot[ext]))
                          + self.AddDig_SB.value())
                c = self.alph(r_count).zfill(r_fill)
            root_num[ext] += 1

            pre, suf = '', ''  # prefix and suffix stuff
            if self.Pref_CB.isChecked():  # handle prefix
                p_fill = len(str(ext_tot[ext])) + self.PreAddDig_SB.value()
                p_count = pre_num[ext]
                
                if self.PreNam_RB.isChecked():  # prefix name
                    pre = unicode(self.Prefix_lineEdit.text()) + pre_sep
                    
                elif self.PreNum_RB.isChecked():  # prefix number
                    pre = str(p_count).zfill(p_fill) + pre_sep

                elif self.PreAlp_RB.isChecked():  # prefix alphanumeric
                    p_fill = (len(self.alph(ext_tot[ext]))
                              + self.PreAddDig_SB.value())
                    pre = self.alph(p_count).zfill(p_fill) + pre_sep
                else: raise  # wuh oh
                pre_num[ext] += 1

            if self.Suff_CB.isChecked():  # handle suffix
                s_fill = len(str(ext_tot[ext])) + self.SufAddDig_SB.value()
                s_count = suf_num[ext]
                
                if self.SufNam_RB.isChecked():  # suffix name
                    suf = suf_sep + unicode(self.Suffix_lineEdit.text())
                    
                elif self.SufNum_RB.isChecked():  # suffix number
                    suf = suf_sep + str(s_count).zfill(s_fill)

                elif self.SufAlp_RB.isChecked():  # suffix alphanumeric
                    s_fill = (len(self.alph(ext_tot[ext]))
                              + self.SufAddDig_SB.value())
                    suf = suf_sep + self.alph(s_count).zfill(s_fill)
                else: raise  # something went wrong here
                suf_num[ext] += 1
                
            # assign new name
            NEW_NAME = unicode(self.NewName_lineEdit.text())
            if NEW_NAME == '': NEW_NAME = 'UNNAMED'
            if self._newExt: ext = str(self._newExt)
            NEW_NAME = pre + NEW_NAME + suf + num_sep + c + ext
            
            # date code
            if self.NameDate_CB.isChecked():
                dt = dates[fn]; tmp_fmt = fmt

                if '%f' in fmt:
                    mil = (dt - int(dt)) * 1000  # adjust here for nanosecs
                    tmp_fmt = fmt.replace('%f', '{:03.0f}'.format(mil))
                    
                time_name = time.strftime(tmp_fmt, time.localtime(dt))
                tmp = time_name + ext

                if tmp in datenames:  # if files made at same time
                    ch = dateCatch[ext]
                    filler = len(str(ext_tot[ext]))# + self.AddDig_SB.value()
                    time_name = time_name + num_sep + str(ch).zfill(filler)
                    dateCatch[ext] += 1

                NEW_NAME = pre + time_name + suf + ext
                datenames.append(tmp)

            new_name_list.append(NEW_NAME)
        return new_name_list
            
    def alph(self, num):
        "converts a positive integer from base 10 to base 36 (alphanumeric)"
        val, chars, num = [], "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", abs(num)
        while num:
            num, d = divmod(num, 36)
            val.append(d)
        val.reverse()
        return "".join(chars[i] for i in val)

    def ChangeFormat(self, signal):
        "called by date related ui features"
        if type(signal) != int: self.sender().setToolTip(signal)
        
        milli = ''
        if self.MilliSec_CB.isChecked(): milli = '.%f'

        hms = '%I.%M.%S{} %p'.format(milli)
        if self.HrForm_CB.isChecked(): hms = '%H.%M.%S{}'.format(milli)
            
        # http://docs.python.org/2/library/time.html#time.strftime
        self.DateFormats = {  # readable string: strftime form
            'YYYY-MM-DD HH.MM.SS': '%Y-%m-%d ' + hms,
            'MM-DD-YYYY HH.MM.SS ': '%m-%d-%Y ' + hms,
            'DD-MM-YYYY HH.MM.SS ': '%d-%m-%Y ' + hms,
            'YYYY-DD-MM HH.MM.SS ': '%Y-%d-%m ' + hms,
            'YYYY.MM.DD.HH.MM.SS ': '%Y.%m.%d.' + hms,
            'Day-abbr. DD-MM-YYYY HH.MM.SS': '%a %d-%m-%Y ' + hms,
            'Day-abbr. Month-abbr. DD HH.MM.SS YYYY': '%a %b %d ' + hms + ' %Y',
            'Day-full Month-full DD HH.MM.SS YYYY': '%A %B %d ' + hms + ' %Y',
            }
        fb = "%Y-%m-%d %H.%M.%S.%f"  # fallback
        fmt = self.DateFormats.get(str(self.DateFormatCoB.currentText()), fb)
        self._time_fmt = fmt
        self.selected()

    def MoreOpts(self):
        'show more options'
        self.More_Button.hide()
        self.More_Button.resize(0, 0)
        self.More_frame.show()
        self.Suffix_Settings()
        self.Prefix_Settings()

    def AccessOpts(self):
        "show/hide options box"
        if self.Opts_Button.isChecked():
            self.OpsBox.setEnabled(True)
            self.OpsBox.show()
        else:
            self.OpsBox.setEnabled(False)
            self.OpsBox.hide()
            
    def Prefix_Settings(self):
        "show/hide prefix options"
        if self.Pref_CB.isChecked():
            self.Prefix_lineEdit.setEnabled(True)
            self.Prefix_lineEdit.show()
            self.PreSep_lineEdit.show()

            if self.More_Button.isChecked():
                self.PreNam_RB.show()
                self.PreNum_RB.show()
                self.PreAlp_RB.show()
                
                self.PreAddDig_SB.show()
                self.PreSep_lineEdit.show()
                self.PreStart_SB.show() 
        else:
            self.Prefix_lineEdit.setEnabled(False)
            self.Prefix_lineEdit.hide()
            self.PreSep_lineEdit.hide()
            
            if self.More_Button.isChecked(): 
                self.PreNam_RB.hide()
                self.PreNum_RB.hide()
                self.PreAlp_RB.hide()
                
                self.PreAddDig_SB.hide()
                self.PreSep_lineEdit.hide()
                self.PreStart_SB.hide()
        self._fixes_labels()
            
    def _fixes_labels(self):
        "resize options box based on what is currently being shown"
        self._RB_catch()
        if not self.Suff_CB.isChecked() and not self.Pref_CB.isChecked():
            self.SubSets_Frame.hide()
            self.Alp_Lab.hide()
            self.Nam_Lab.hide()
            self.Num_Lab.hide()
        else:
            if self.More_Button.isChecked():
                self.SubSets_Frame.show()
                self.Alp_Lab.show()
                self.Nam_Lab.show()
                self.Num_Lab.show()
        #self.resize(self.sizeHint())

    def Suffix_Settings(self):
        "show/hide suffix settings"
        if self.Suff_CB.isChecked():
            self.Suffix_lineEdit.setEnabled(True)
            self.Suffix_lineEdit.show()
            if self.More_Button.isChecked():  # this is in the more options
                self.SufNam_RB.show()
                self.SufNum_RB.show()
                self.SufAlp_RB.show()

                self.SufAddDig_SB.show()
                self.SufStart_SB.show()
                self.SufSep_lineEdit.show()
        else:
            self.Suffix_lineEdit.setEnabled(False)
            self.Suffix_lineEdit.hide()
            self.SufSep_lineEdit.hide()
            if self.More_Button.isChecked():
                self.SufNam_RB.hide()
                self.SufNum_RB.hide()
                self.SufAlp_RB.hide()

                self.SufAddDig_SB.hide()
                self.SufStart_SB.hide()
                self.SufSep_lineEdit.hide()
            
        self._fixes_labels()

    def _RB_catch(self):
        "show/hide prefix, suffix radio boxes"
        # suffix
        if not self.SufNam_RB.isChecked():
            self.Suffix_lineEdit.setEnabled(False)
            self.SufAddDig_SB.setEnabled(True)
            self.SufStart_SB.setEnabled(True)
        else:
            self.Suffix_lineEdit.setEnabled(True)
            self.SufAddDig_SB.setEnabled(False)
            self.SufStart_SB.setEnabled(False) 
			
        # prefix
        if not self.PreNam_RB.isChecked():
            self.Prefix_lineEdit.setEnabled(False)
            self.PreAddDig_SB.setEnabled(True)
            self.PreStart_SB.setEnabled(True)
        else:
            self.Prefix_lineEdit.setEnabled(True)
            self.PreAddDig_SB.setEnabled(False)
            self.PreStart_SB.setEnabled(False)
            
        # date namer
        if self.NameDate_CB.isChecked():
            self.DateFormatCoB.show()
            self.NewName_lineEdit.hide()
            self.NewName_lineEdit.setEnabled(False)
            self.AddDig_SB.setEnabled(False)
            self.AlphaNum_CB.setEnabled(False)
            self.AlphaNum_CB.setCheckState(0)
            self.NumStart_SB.setEnabled(False)
            self.NumSep_lineEdit.setEnabled(False)
            self.HrForm_CB.show()
            self.MilliSec_CB.show()
            self.Time_Sep_line.show()
        else:
            self.NewName_lineEdit.show()
            self.NewName_lineEdit.setEnabled(True)
            self.DateFormatCoB.hide()
            self.AddDig_SB.setEnabled(True)
            self.AlphaNum_CB.setEnabled(True)
            self.NumStart_SB.setEnabled(True)
            self.NumSep_lineEdit.setEnabled(True)
            self.HrForm_CB.hide()
            self.MilliSec_CB.hide()
            self.Time_Sep_line.hide()
            
        if self.Started != 0: self.selected()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and not self.locked:                    
            SOps = Sssh(); SOps.SecretSignal.connect(self._setSecrets)
            pos = SOps.pos()
            pos.setX(event.globalX()); pos.setY(event.globalY())
            SOps.move(pos); SOps.exec_()

    def _setSecrets(self, Ex):
        #print 'sneakrets!', Ex
        Ex, inv = unicode(Ex), '\\/|:*"?<>' + os.path.extsep
        for i in inv: Ex = Ex.replace(i, '')
        if len(Ex): Ex = os.path.extsep + Ex
        self._newExt = Ex

    def centerOnScreen(self):
        # from http://bashelton.com/2009/06/pyqt-center-on-screen/
        res = QtGui.QDesktopWidget().screenGeometry()
        self.move((res.width() / 2) - (self.frameSize().width() / 2),
                  (res.height() / 2) - (self.frameSize().height() / 2))

if __name__ == '__main__':
    global app
    app = QtGui.QApplication(sys.argv)  # note: app is used within Control
    w = Control(); w.show()
    sys.exit(app.exec_())
