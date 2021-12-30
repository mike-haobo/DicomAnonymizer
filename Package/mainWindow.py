import sys, os
import random
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtWidgets import QGroupBox, QLabel, QTableView, QHeaderView, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, QVariant, QAbstractTableModel, Qt, QModelIndex, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor

from coreFunction import DicomAnonymizer

class TagTransfer:
    def __init__(self, lang="en"):
        # Init Tag Alias for CN & EN
        tag_dict=dict()
        tag_dict["en"]=dict()
        tag_dict["cn"]=dict()
        tag_dict["en"]["SourcePatientID"]="Source Patient ID"
        tag_dict["cn"]["SourcePatientID"]="源Patient ID"
        tag_dict["en"]["SourcePatientName"]="Source Patient Name"
        tag_dict["cn"]["SourcePatientName"]="源Patient Name"
        tag_dict["en"]["AnonyPatientID"]="Anonymized Patient ID"
        tag_dict["cn"]["AnonyPatientID"]="脱敏Patient ID"
        tag_dict["en"]["AnonyPatientName"]="Anonymized Patient Name"
        tag_dict["cn"]["AnonyPatientName"]="脱敏Patient Name"
        tag_dict["en"]["SuccessNumber"]="Successful DICOM Files"
        tag_dict["cn"]["SuccessNumber"]="已完成文件数"
        tag_dict["en"]["TotalNumber"]="Total DICOM Files"
        tag_dict["cn"]["TotalNumber"]="总文件数"
        tag_dict["en"]["PathCase"]="Source Path of DICOM Cases"
        tag_dict["cn"]["PathCase"]="源文件示例路径"

        tag_dict["en"]["WinTitle"]="DICOM Anonymizer"
        tag_dict["cn"]["WinTitle"]="DICOM脱敏和结构化工具"
        tag_dict["en"]["ParseFrame"]="Parse Configure:"
        tag_dict["cn"]["ParseFrame"]="解析配置："
        tag_dict["en"]["WorkDirLab"]="Work Directory:"
        tag_dict["cn"]["WorkDirLab"]="工作路径："
        tag_dict["en"]["PrefixLab"]="Anonymized Prefix:"
        tag_dict["cn"]["PrefixLab"]="匿名化前缀："
        tag_dict["en"]["StartNumLab"]="Anonymized Starting Number:"
        tag_dict["cn"]["StartNumLab"]="匿名化起始编号："
        tag_dict["en"]["ParseBtn"]="Parse DICOM Folders..."
        tag_dict["cn"]["ParseBtn"]="开始解析"
        tag_dict["en"]["OutputFrame"]="Output Configure:"
        tag_dict["cn"]["OutputFrame"]="输出配置："
        tag_dict["en"]["OutputDirLab"]="Output Directory:"
        tag_dict["cn"]["OutputDirLab"]="输出路径："
        tag_dict["en"]["ExportBtn"]="Anonymize and Export DICOM Folders..."
        tag_dict["cn"]["ExportBtn"]="开始匿名化并导出"
        tag_dict["en"]["ProgressTable"]="Anonymizing Progress"
        tag_dict["cn"]["ProgressTable"]="匿名化进度"
        tag_dict["en"]["StopBtn"]="Suspend..."
        tag_dict["cn"]["StopBtn"]="中止..."

        self.tag_dict=tag_dict
        self.lang=lang
    
    def GetLang(self):
        return self.lang

    def SetLang(self, lang="en"):
        self.lang=lang

    def Alias(self, tag_name):
        lang_tag=self.tag_dict[self.lang]
        return lang_tag[tag_name]

class GuiDcmAnonymizer(DicomAnonymizer, QThread):
    # Custom Signal
    updateSignal=pyqtSignal(str, list)

    def __init__(self):
        super(QThread, self).__init__()
        DicomAnonymizer.__init__(self)

    def run(self):
        self.ParseDicom()
        if self.GetState()=="ParseFinish":
            self.AnonyDicom()

    def UpdateInfoTable(self):
        dcmPatientID=self.GetDcmPatientID()
        dcmPatientName=self.GetDcmPatientName()
        dcmAnonyAlias=self.GetDcmAnonyAlias()
        dcmCaseFile=self.GetDcmCaseFile()
        dcmTotalNum=self.GetDcmTotalNum()
        dcmSuccessNum=self.GetDcmSuccessNum()

        timeStamp=self.GetStartTime()
        state=self.GetState()

        infoList=list()
        for (uId, pId) in dcmPatientID.items():
            apId="%s_%s" % (timeStamp, dcmAnonyAlias[uId])
            apName=dcmAnonyAlias[uId]
            infoLine=[str(pId), str(dcmPatientName[uId]), str(apId), str(apName),
                    str(dcmSuccessNum[uId]), str(dcmTotalNum[uId]),
                    str(dcmCaseFile[uId])]
            infoList.append(infoLine)
        self.updateSignal.emit(state, infoList)

class InfoTableModel(QAbstractTableModel):
    """Model"""
    def __init__(self, lang="en"):
        super(InfoTableModel, self).__init__()
        tag=TagTransfer(lang=lang)
        
        self._data = []
        self._headers = ['  %s  ' % tag.Alias("SourcePatientID"), '  %s  ' %  tag.Alias("SourcePatientName"),
                '  %s  ' % tag.Alias("AnonyPatientID"), '  %s  ' % tag.Alias("AnonyPatientName"),
                '  %s  ' % tag.Alias("SuccessNumber"), '  %s  ' % tag.Alias("TotalNumber"),
                '  %s  ' % tag.Alias("PathCase")]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def data(self, index, role):
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return QVariant()
   
        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return self._data[row][col]
        elif role == Qt.ToolTipRole:
            if col==6:
                return self._data[row][col]
        elif role == Qt.TextAlignmentRole:
            if col==4 or col==5:
                return Qt.AlignRight
            else:
                return Qt.AlignLeft

        return QVariant()

class DcmMainWidget(QWidget):
    def __init__(self, lang="cn"):
        super(DcmMainWidget, self).__init__()
        tag=TagTransfer(lang=lang)
        self.tag=tag

        # DICOM Anonymizer Sub-Class
        dcmAnonymizer=GuiDcmAnonymizer()

        # Main Vertical Layout
        mainVBox=QVBoxLayout()
        self.setLayout(mainVBox)

        # Parsing Configure
        parseGroupBox=QGroupBox(tag.Alias("ParseFrame"))
        mainVBox.addWidget(parseGroupBox)

        parseMainLayout=QVBoxLayout()
        parseGroupBox.setLayout(parseMainLayout)

        ## Work Directory
        workDirLayout=QHBoxLayout()
        parseMainLayout.addLayout(workDirLayout)

        workDirLab=QLabel(tag.Alias("WorkDirLab"))
        workDirLayout.addWidget(workDirLab)

        workDirEty=QLineEdit()
        workDirLayout.addWidget(workDirEty)

        workDirBtn=QPushButton("...")
        workDirLayout.addWidget(workDirBtn)

        ## Anony Prefix & Start Number Button
        parseInfoLayout=QHBoxLayout()
        parseMainLayout.addLayout(parseInfoLayout)

        anonyPrefixLab=QLabel(tag.Alias("PrefixLab"))
        parseInfoLayout.addWidget(anonyPrefixLab)

        anonyPrefixEty=QLineEdit()
        parseInfoLayout.addWidget(anonyPrefixEty)

        startNumberLab=QLabel(tag.Alias("StartNumLab"))
        parseInfoLayout.addWidget(startNumberLab)

        startNumberEty=QLineEdit()
        parseInfoLayout.addWidget(startNumberEty)

        ## Parse Button
        parsePerformBtn=QPushButton(tag.Alias("ParseBtn"))
        #parseMainLayout.addWidget(parsePerformBtn)

        # Output Configure
        outputGroupBox=QGroupBox(tag.Alias("OutputFrame"))
        mainVBox.addWidget(outputGroupBox)

        outputMainLayout=QVBoxLayout()
        outputGroupBox.setLayout(outputMainLayout)

        ## Output Directory
        outputDirLayout=QHBoxLayout()
        outputMainLayout.addLayout(outputDirLayout)

        outputDirLab=QLabel(tag.Alias("OutputDirLab"))
        outputDirLayout.addWidget(outputDirLab)

        outputDirEty=QLineEdit()
        outputDirLayout.addWidget(outputDirEty)

        outputDirBtn=QPushButton("...")
        outputDirLayout.addWidget(outputDirBtn)

        exportFileBtn=QPushButton(tag.Alias("ExportBtn"))
        #outputMainLayout.addWidget(exportFileBtn)
        mainVBox.addWidget(exportFileBtn)

        # DICOM Info Table Panel
        dcmTableGroupBox=QGroupBox(tag.Alias("ProgressTable"))
        mainVBox.addWidget(dcmTableGroupBox)

        dcmTableMainLayout=QVBoxLayout()
        dcmTableGroupBox.setLayout(dcmTableMainLayout)

        ## DICOM Table Model
        dcmTableView=QTableView()
        dcmTableMainLayout.addWidget(dcmTableView)
        dcmTableModel=InfoTableModel(lang=lang)
        dcmTableView.setModel(dcmTableModel)

        dcmTableHeader=dcmTableView.horizontalHeader()
        dcmTableHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        dcmTableHeader.setSectionResizeMode(6, QHeaderView.Stretch)

        # Init
        workDirStr=os.getcwd()
        workDirEty.setText(workDirStr)
        workDirEty.setToolTip(workDirStr)

        self.workDirStr=workDirStr
        self.workDirEty=workDirEty
        self.workDirBtn=workDirBtn

        anonyPrefixStr="Patient"
        anonyPrefixEty.setText(anonyPrefixStr)
        anonyPrefixEty.setToolTip(anonyPrefixStr)

        self.anonyPrefixEty=anonyPrefixEty
        self.anonyPrefixStr=anonyPrefixStr

        startNumberStr="1"
        startNumberEty.setText(startNumberStr)
        startNumberEty.setToolTip(startNumberStr)

        self.startNumberEty=startNumberEty
        self.startNumberStr=startNumberStr

        self.parsePerformBtn=parsePerformBtn
        
        outputDirStr=os.getcwd()
        outputDirEty.setText(outputDirStr)
        outputDirEty.setToolTip(outputDirStr)

        self.outputDirStr=outputDirStr
        self.outputDirEty=outputDirEty
        self.outputDirBtn=outputDirBtn
        
        self.exportFileBtn=exportFileBtn

        self.dcmTableView=dcmTableView
        self.dcmTableModel=dcmTableModel

        self.dcmAnonymizer=dcmAnonymizer

        self.SetState(1)

        # Signal Connection
        dcmAnonymizer.updateSignal.connect(self.UpdateInfoTable)
        dcmAnonymizer.finished.connect(self.RunFinish)

        workDirBtn.clicked.connect(self.OnClickedWorkDirBtn)
        workDirEty.textChanged.connect(
                self.OnTextChangedWorkDirEty
                )
        workDirEty.editingFinished.connect(
                self.OnEditingFinishedWorkDirEty
                )

        parsePerformBtn.clicked.connect(self.OnClickedParsePerformBtn)

        anonyPrefixEty.textChanged.connect(
                self.OnTextChangedAnonyPrefixEty
                )
        anonyPrefixEty.editingFinished.connect(
                self.OnEditingFinishedAnonyPrefixEty
                )

        startNumberEty.textChanged.connect(
                self.OnTextChangedStartNumberEty
                )
        startNumberEty.editingFinished.connect(
                self.OnEditingFinishedStartNumberEty
                )

        outputDirBtn.clicked.connect(self.OnClickedOutputDirBtn)
        outputDirEty.textChanged.connect(
                self.OnTextChangedOutputDirEty
                )
        outputDirEty.editingFinished.connect(
                self.OnEditingFinishedOutputDirEty
                )

        exportFileBtn.clicked.connect(self.OnClickedExportFileBtn)

    def GetState(self):
        return self.state

    def SetState(self, state):
        """
        state 1: Init
        state 2: Parse DICOM
        state 3: Anony DICOM
        state 4: Finish
        """
        tag=self.tag
        
        if state==1 or state==4:
            isDisabled=False
        else:
            isDisabled=True

        self.workDirEty.setDisabled(isDisabled)
        self.workDirBtn.setDisabled(isDisabled)
        self.anonyPrefixEty.setDisabled(isDisabled)
        self.startNumberEty.setDisabled(isDisabled)

        self.outputDirEty.setDisabled(isDisabled)
        self.outputDirBtn.setDisabled(isDisabled)

        if state==1: # Init
            self.exportFileBtn.setDisabled(False)
            self.exportFileBtn.setText(tag.Alias("ExportBtn"))
        elif state==2: # Parse DICOM
            self.exportFileBtn.setDisabled(False)
            self.exportFileBtn.setText(tag.Alias("StopBtn"))
        elif state==3: # Anony DICOM
            self.exportFileBtn.setDisabled(False)
            self.exportFileBtn.setText(tag.Alias("StopBtn"))
        elif state==4: # Finish
            self.exportFileBtn.setDisabled(False)
            self.exportFileBtn.setText(tag.Alias("ExportBtn"))

        self.state=state

    #Slot
    def UpdateInfoTable(self, runFlag, infoList):
        self.dcmTableModel._data=infoList
        self.dcmTableModel.modelReset.emit()

    def OnClickedWorkDirBtn(self):
        workDirStr=QFileDialog.getExistingDirectory(self,
                "Choose Directory", self.workDirStr,
                QFileDialog.ShowDirsOnly|QFileDialog.DontUseNativeDialog)
        if workDirStr:
            self.workDirEty.setText(workDirStr)
            self.workDirEty.setToolTip(workDirStr)
            self.workDirStr=workDirStr

    def OnEditingFinishedWorkDirEty(self):
        workDirStr=self.workDirEty.text()
        if os.path.exists(workDirStr):
            self.workDirStr=workDirStr
        else:
            QMessageBox.warning(self, 'Invalid Path',
                    'Invalid Path "%s", please check!' % workDirStr)
            self.workDirEty.setText(self.workDirStr)

    def OnTextChangedWorkDirEty(self):
        self.workDirEty.setToolTip(self.workDirEty.text())

    def OnEditingFinishedAnonyPrefixEty(self):
        curStr=self.anonyPrefixEty.text()
        if len(curStr)==len(re.sub('[^a-zA-Z0-9_]', '', curStr)):
            self.anonyPrefixStr=curStr
            self.anonyPrefixEty.setToolTip(curStr)
        else:
            QMessageBox.warning(self, 'Invalid Prefix',
                    'Invalid Prefix "%s", please check!' % curStr)
            self.anonyPrefixEty.setText(self.anonyPrefixStr)
            self.anonyPrefixEty.setToolTip(self.anonyPrefixStr)

    def OnTextChangedAnonyPrefixEty(self):
        self.anonyPrefixEty.setToolTip(self.anonyPrefixEty.text())

    def OnEditingFinishedStartNumberEty(self):
        curStr=self.startNumberEty.text()
        if len(curStr)==len(re.sub('[^0-9]', '', curStr)):
            self.startNumberStr=curStr
            self.startNumberEty.setToolTip(curStr)
        else:
            QMessageBox.warning(self, 'Invalid Start Number',
                    'Invalid Start Number "%s", please check!' % curStr)
            self.startNumberEty.setText(self.startNumberStr)
            self.startNumberEty.setToolTip(self.startNumberStr)

    def OnTextChangedStartNumberEty(self):
        self.startNumberEty.setToolTip(self.startNumberEty.text())

    def OnClickedParsePerformBtn(self):
        state=self.GetState()
        if state==1 or state==3:
            self.SetState(2)
        elif state==2:
            self.SetState(1)
        elif state==4:
            pass

        print("WorkDir: " + self.workDirStr)
        print("Prefix: " + self.anonyPrefixStr)

    def OnClickedOutputDirBtn(self):
        outputDirStr=QFileDialog.getExistingDirectory(self,
                "Choose Directory", self.outputDirStr,
                QFileDialog.ShowDirsOnly|QFileDialog.DontUseNativeDialog)
        if outputDirStr:
            self.outputDirEty.setText(outputDirStr)
            self.outputDirEty.setToolTip(outputDirStr)
            self.outputDirStr=outputDirStr

    def OnEditingFinishedOutputDirEty(self):
        outputDirStr=self.outputDirEty.text()
        if os.path.exists(outputDirStr):
            self.outputDirStr=outputDirStr
        else:
            QMessageBox.warning(self, 'Invalid Path',
                    'Invalid Path "%s", please check!' % outputDirStr)
            self.outputDirEty.setText(self.outputDirStr)

    def OnTextChangedOutputDirEty(self):
        self.outputDirEty.setToolTip(self.outputDirEty.text())

    def RunFinish(self):
        if self.dcmAnonymizer.isFinished():
            if self.dcmAnonymizer.GetState()=="AnonyFinish":
                QMessageBox.information(self, 'Anonymous Finished',
                        'Anonymous finished, you could find results in %s!' % self.outputDirStr)
                self.SetState(4)
            elif self.dcmAnonymizer.GetState()=="ParseEmptyDir":
                QMessageBox.warning(self, 'Empty Work Directory',
                        'Empty work directory "%s", please check!' % self.workDirStr)
                self.SetState(1)
            elif self.dcmAnonymizer.GetState()=="ParseInvalidDir":
                QMessageBox.warning(self, 'Invalid Work Directory',
                        'Invalid work directory "%s", no DICOM files in this directory, please check!' % self.workDirStr)
                self.SetState(1)
            elif self.dcmAnonymizer.GetState()=="Anony":
                QMessageBox.warning(self, 'Anonymous Problem',
                        'Anonymous unknown error!')
                self.SetState(1)
            elif self.dcmAnonymizer.GetState()=="ParseTerminate":
                QMessageBox.warning(self, 'Parse Terminated',
                        'Parse terminated!')
                self.SetState(1)
            elif self.dcmAnonymizer.GetState()=="AnonyTerminate":
                QMessageBox.warning(self, 'Anonymous Terminated',
                        'Anonymous terminated!')
                self.SetState(1)

    def OnClickedExportFileBtn(self):
        state=self.GetState()
        if state==1 or state==4:
            self.SetState(2)
            dcmAnonymizer=self.dcmAnonymizer
            dcmAnonymizer.SetState("Init")
            dcmAnonymizer.SetRunningFlag(True)
            dcmAnonymizer.SetDcmWorkDir(self.workDirStr)
            dcmAnonymizer.SetDcmOutDir(self.outputDirStr)
            dcmAnonymizer.SetDcmAnonyPrefix(self.anonyPrefixStr)
            dcmAnonymizer.SetDcmAnonyStartP(int(self.startNumberStr))
            dcmAnonymizer.start()
        elif state==2 or state==3:
            self.SetState(1)
            dcmAnonymizer=self.dcmAnonymizer
            if dcmAnonymizer.isRunning():
                dcmAnonymizer.SetRunningFlag(False)
                dcmAnonymizer.quit()
                dcmAnonymizer.wait()

class DcmMainWindow(QMainWindow):
    def __init__(self, lang="en", width=850, height=400):
        super().__init__()
        tag=TagTransfer(lang=lang)

        self.setWindowTitle(tag.Alias("WinTitle"))
        mainWidget=DcmMainWidget(lang=lang)
        self.setCentralWidget(mainWidget)

        self.setMinimumSize(width, height)

if __name__ == '__main__':
    app=QApplication(sys.argv)
    
    win=DcmMainWindow()
    win.show()

    sys.exit(app.exec_())
