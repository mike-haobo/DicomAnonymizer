import pydicom
import os
import re
import time

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
            
class DicomAnonymizer:
    def __init__(self):
        self.updateStep=50
        self.verbose=True
        
        ##
        self.SetDcmTotalNum()
        self.SetDcmSuccessNum()
        
        self.SetDcmInFullFileList()
        self.SetInvalidDcmInFullFileList()
        self.SetDcmCaseFile()
        self.SetDcmPatientID()
        self.SetDcmPatientName()
        
        self.SetDcmOutSubFileList()
        
        self.SetDcmWorkDir()
        self.SetDcmOutDir()
        
        self.SetDcmAnonyPrefix()
        self.SetDcmAnonyStartP()
        self.SetDcmAnonyAlias()

        self.SetState("Init")
        self.SetRunningFlag(True)
    
    def SetRunningFlag(self, runFlag):
        self.runFlag=runFlag

    def GetRunningFlag(self):
        return self.runFlag

    def SetState(self, taskState):
        self.taskState=taskState

    def GetState(self):
        return self.taskState

    def SetDcmWorkDir(self, workDir=None):
        self.dcmWorkDir=workDir
    
    def GetWorkDir(self):
        return self.dcmWorkDir
    
    def SetDcmOutDir(self, outDir=None):
        self.dcmOutDir=outDir
    
    def GetDcmOutDir(self):
        return self.dcmOutDir
        
    def SetDcmAnonyPrefix(self, prefix=None):
        self.dcmAnonyPrefix=prefix
        
    def GetDcmAnonyPrefix(self):
        return self.dcmAnonyPrefix
        
    def SetDcmAnonyStartP(self, num=1):
        self.dcmAnonyStartP=num
        
    def GetDcmAnonyStartP(self):
        return self.dcmAnonyStartP
    
    def SetDcmAnonyAlias(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()        
        self.dcmAnonyAlias=dcmDict
    
    def GetDcmAnonyAlias(self):
        return self.dcmAnonyAlias
        
    def GenAutoDcmAnonyAlias(self):
        dcmAnonyPrefix=self.GetDcmAnonyPrefix()
        dcmAnonyStartP=self.GetDcmAnonyStartP()
        dcmTotalNum=self.GetDcmTotalNum()
        
        autoDcmAnonyAlias=dict()
        if dcmAnonyPrefix is not None and dcmTotalNum:
            for key in dcmTotalNum:
                autoDcmAnonyAlias[key]="%s_%.4d" % (dcmAnonyPrefix, dcmAnonyStartP)
                dcmAnonyStartP+=1
        
        return autoDcmAnonyAlias
        
    def SetDcmTotalNum(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()
        self.dcmTotalNum=dcmDict
    
    def GetDcmTotalNum(self):
        return self.dcmTotalNum        

    def ClearDcmTotalNum(self):
        for key in self.dcmTotalNum:
            self.dcmTotalNum[key]=0
    
    def SetDcmSuccessNum(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()
        self.dcmSuccessNum=dcmDict
    
    def GetDcmSuccessNum(self):
        return self.dcmSuccessNum
    
    def ClearDcmSuccessNum(self):
        for key in self.dcmSuccessNum:
            self.dcmSuccessNum[key]=0    
    
    def SetDcmInFullFileList(self, fileList=None):
        if fileList is None:
            fileList=list()
        self.dcmInFullFileList=fileList
    
    def GetDcmInFullFileList(self):
        return self.dcmInFullFileList

    def SetInvalidDcmInFullFileList(self, fileList=None):
        if fileList is None:
            fileList=list()
        self.invalidDcmInFullFileList=fileList
    
    def GetInvalidDcmInFullFileList(self):
        return self.invalidDcmInFullFileList
    
    def SetDcmPatientName(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()
        self.dcmPatientName=dcmDict
        
    def GetDcmPatientName(self):
        return self.dcmPatientName
    
    def SetDcmPatientID(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()
        self.dcmPatientID=dcmDict
        
    def GetDcmPatientID(self):
        return self.dcmPatientID
    
    def SetDcmCaseFile(self, dcmDict=None):
        if dcmDict is None:
            dcmDict=dict()
        self.dcmCaseFile=dcmDict
        
    def GetDcmCaseFile(self):
        return self.dcmCaseFile
    
    def SetDcmOutSubFileList(self, fileList=None):
        if fileList is None:
            fileList=list()
        self.dcmOutSubFileList=fileList
    
    def GetDcmOutSubFileList(self):
        return self.dcmOutSubFileList
    
    def CheckXXorPS(self, dcmHandle):
        if isinstance(dcmHandle, pydicom.dataset.FileDataset):
            mediaUID=dcmHandle.file_meta.MediaStorageSOPClassUID
        elif isinstance(dcmHandle, pydicom.dataset.FileMetaDataset):
            mediaUID=dcmHandle.MediaStorageSOPClassUID
        elif isinstance(dcmHandle, str):
            metaHandle=pydicom.filereader.read_file_meta_info(dcmHandle)
            mediaUID=metaHandle.MediaStorageSOPClassUID
            
        if mediaUID=="1.2.840.10008.5.1.4.1.1.66" or \
            mediaUID=="1.3.46.670589.11.0.0.12.1" or \
            mediaUID=="1.3.46.670589.11.0.0.12.2" or \
            mediaUID=="1.3.46.670589.11.0.0.12.4" or \
            mediaUID=="1.2.840.10008.5.1.4.1.1.11.1" or \
            mediaUID=="1.2.840.10008.5.1.4.1.1.11.1": 
            return True
        else:
            return False
        
    def StoreInvalidDcmList(self, outName):
        invalidDcmList=self.GetInvalidDcmInFullFileList()
        with open(outName, "wb") as fid:
            for dcmFile in invalidDcmList:
                fid.write(("%s\n" % (str(dcmFile))).encode("utf8"))
                
    def StoreAnonyMapping(self, outName):    
        dcmAnonyAlias=self.GetDcmAnonyAlias()
        dcmPatientID=self.GetDcmPatientID()
        dcmPatientName=self.GetDcmPatientName()
        dcmSuccessNum=self.GetDcmSuccessNum()
        dcmTotalNum=self.GetDcmTotalNum()
        dcmCaseFile=self.GetDcmCaseFile()
        timeStamp=self.GetStartTime()
        with open(outName, "wb") as fid:
            fid.write(("Source Patient ID,Source Patient Name,Anonymized Patient ID,Anonymized Patient Name,Successful DICOM Files,Total DICOM Files,Source Path of DICOM Case\n").encode("utf8"))
            for uId, alias in dcmAnonyAlias.items():
                anonyPatientID="%s_%s" % (timeStamp, alias)
                anonyPatientName=alias
                fid.write(("%s,%s,%s,%s,%d,%d,%s\n" % (dcmPatientID[uId], dcmPatientName[uId], 
                                                  anonyPatientID, anonyPatientName, dcmSuccessNum[uId], dcmTotalNum[uId],
                                                  dcmCaseFile[uId]) ).encode("utf8"))
    
    def SetStartTime(self, startTime=time.time() ):
        self.startTime=time.strftime("%Y%m%d%H%M%S", time.localtime(startTime))
    
    def GetStartTime(self):
        return self.startTime
    
    def UpdateInfoTable(self): pass
    
    def ParseDicom(self):
        self.SetState("Parse")

        # Create Time Stamp
        self.SetStartTime()

        # Work Directory for DICOM Files
        dcmWorkDir=self.dcmWorkDir
        
        # Initialize Totol Number and Success Number of DICOM Files 
        dcmTotalNum=dict()
        dcmSuccessNum=dict()
        dcmPatientID=dict()
        dcmPatientName=dict()
        dcmCaseFile=dict()
        
        dcmInFullFileList=list()
        invalidDcmInFullFileList=list()
        dcmOutSubFileList=list()
        
        dcmDataStruct=dict()
        
        if self.verbose :
            print("Stat DICOM...")
            
        for (i, entry) in enumerate(scantree(dcmWorkDir)):
            if not self.GetRunningFlag():
                self.UpdateInfoTable()        
                self.SetState("ParseTerminate")

                if self.verbose: 
                    print("\nParse Terminated!")

                return

            try:
                header=pydicom.dcmread(entry.path, stop_before_pixels=True, 
                                     specific_tags=["PatientID", "PatientName", "StudyDate", "StudyTime", "SeriesNumber", "SeriesDescription"])
                if self.CheckXXorPS(header):
                    invalidDcmInFullFileList.append(entry.path)
                else:
                    # Generate Unique ID with Patient ID and Patient Name
                    rawPatientID=str(header.PatientID).encode('utf8').decode()
                    rawPatientName=str(header.PatientName).encode('utf8').decode()
                    uniqueID=re.sub('[^a-zA-Z0-9]', '_', rawPatientID)+"_"+re.sub('[^a-zA-Z0-9]', '_', rawPatientName)

                    if uniqueID in dcmTotalNum:
                        dcmTotalNum[uniqueID]+=1
                    else:                            
                        dcmTotalNum[uniqueID]=1
                        dcmSuccessNum[uniqueID]=0

                        dcmDataStruct[uniqueID]=dict()
                        
                        dcmPatientID[uniqueID]=header.PatientID
                        dcmPatientName[uniqueID]=header.PatientName.decode('GB18030').encode('utf8').decode()
                        dcmCaseFile[uniqueID]=entry.path

                    studyTimeStamp="%s_%s" % (header.StudyDate, header.StudyTime)
                    studyTimeStamp=re.sub('[^a-zA-Z0-9]', '_', studyTimeStamp)
                    if studyTimeStamp not in dcmDataStruct[uniqueID]:
                        dcmDataStruct[uniqueID][studyTimeStamp]=dict()

                    seriesInfo="%.5d_%s" % (header.SeriesNumber, header.SeriesDescription)
                    seriesInfo=re.sub('[^a-zA-Z0-9]', '_', seriesInfo)
                    if seriesInfo not in dcmDataStruct[uniqueID][studyTimeStamp]:
                        dcmDataStruct[uniqueID][studyTimeStamp][seriesInfo]=1
                    else:
                        dcmDataStruct[uniqueID][studyTimeStamp][seriesInfo]+=1

                    dcmFileExt=os.path.splitext(entry.path)[-1]
                    curIndexNumber=dcmDataStruct[uniqueID][studyTimeStamp][seriesInfo]
                    dcmOutSubFileName=os.path.join(studyTimeStamp, seriesInfo, 
                                                   "%.8d%s" % (curIndexNumber, dcmFileExt) )

                    dcmInFullFileList.append(entry.path)
                    dcmOutSubFileList.append(dcmOutSubFileName)
                    
                    # Print Info
                    self.SetDcmTotalNum(dcmDict=dcmTotalNum)
                    dcmAnonyAlias=self.GenAutoDcmAnonyAlias() ## Now Generate Automative Anony Alias by Prefix
                    
                    if dcmTotalNum[uniqueID]==1:
                        if "oldUniqueID" in vars() and self.verbose:
                            Txt="%s->%s (%.5d/%.5d)\n" % (oldUniqueID, dcmAnonyAlias[oldUniqueID], 
                                                          dcmSuccessNum[oldUniqueID], dcmTotalNum[oldUniqueID])
                            print(Txt, end="")
                        oldUniqueID=uniqueID
                            
                    if i%self.updateStep==0 and self.verbose:
                        Txt="%s->%s (%.5d/%.5d)\r" % (uniqueID, dcmAnonyAlias[uniqueID], 
                                                      dcmSuccessNum[uniqueID], dcmTotalNum[uniqueID])
                        print(Txt, end="")
                    
                    # GUI Display Reload Function
                    self.SetDcmTotalNum(dcmDict=dcmTotalNum)
                    self.SetDcmSuccessNum(dcmDict=dcmSuccessNum)
                    self.SetDcmAnonyAlias(dcmDict=dcmAnonyAlias)
                    self.SetDcmPatientID(dcmDict=dcmPatientID)
                    self.SetDcmPatientName(dcmDict=dcmPatientName)
                    self.SetDcmCaseFile(dcmDict=dcmCaseFile)
                    
                    if i%self.updateStep==0:
                        self.UpdateInfoTable()
                    
            except: # Except Info
            #except pydicom.errors.InvalidDicomError: # Except Info
                invalidDcmInFullFileList.append(entry.path)
        
        # Print Info     
        if "i" not in locals().keys():
            self.UpdateInfoTable()        
            self.SetState("ParseEmptyDir")
            return

        if "uniqueID" not in locals().keys():
            self.UpdateInfoTable()        
            self.SetState("ParseInvalidDir")
            return

        if self.verbose :
            Txt="%s->%s (%.5d/%.5d)\r" % (uniqueID, dcmAnonyAlias[uniqueID], 
                    dcmSuccessNum[uniqueID], dcmTotalNum[uniqueID])
            print(Txt, end="\n")
        
        self.SetDcmTotalNum(dcmDict=dcmTotalNum)
        self.SetDcmSuccessNum(dcmDict=dcmSuccessNum)
        
        self.SetDcmAnonyAlias(dcmDict=dcmAnonyAlias)
        self.SetDcmCaseFile(dcmDict=dcmCaseFile)
        
        self.SetDcmInFullFileList(dcmInFullFileList)
        self.SetInvalidDcmInFullFileList(invalidDcmInFullFileList)
        
        self.SetDcmOutSubFileList(dcmOutSubFileList)

        curTimeStamp=self.GetStartTime()
        dcmOutDir=self.GetDcmOutDir()
        self.StoreAnonyMapping(os.path.join(dcmOutDir, "%s_anonymized_subject_mapping.csv" % curTimeStamp))
        
        # GUI Display Reload Function
        self.UpdateInfoTable()        
        self.SetState("ParseFinish")

    def AnonyDicom(self):
        self.SetState("Anony")

        # Output Parent Directory
        dcmOutDir=self.GetDcmOutDir()
        curTimeStamp=self.GetStartTime()
        
        # Anony Alias
        dcmAnonyAlias=self.GetDcmAnonyAlias()
        if not dcmAnonyAlias:
            dcmAnonyAlias=self.GenAutoDcmAnonyAlias()
        
        # DICOM Input/Output File List
        dcmInFullFileList=self.GetDcmInFullFileList()
        dcmOutSubFileList=self.GetDcmOutSubFileList()
        
        # Number of DICOM Files
        dcmTotalNum=self.GetDcmTotalNum()
        self.ClearDcmSuccessNum()
        dcmSuccessNum=self.GetDcmSuccessNum()
        
        # Clear Output Directory
        if not os.path.exists(dcmOutDir):
            os.makedirs(dcmOutDir)
        
        if self.verbose:
            print("Anony DICOM...")
            
        for (i, dcmInFile) in enumerate(dcmInFullFileList):
            if not self.GetRunningFlag():
                self.UpdateInfoTable()        
                self.SetState("AnonyTerminate")

                if self.verbose: 
                    print("\nAnonymous Terminated!")

                return

            dataSet=pydicom.dcmread(dcmInFile, stop_before_pixels=False)
            
            # Generate Unique ID with Patient ID and Patient Name
            rawPatientID=str(dataSet.PatientID).encode('utf8').decode()
            rawPatientName=str(dataSet.PatientName).encode('utf8').decode()
            uniqueID=re.sub('[^a-zA-Z0-9]', '_', rawPatientID)+"_"+re.sub('[^a-zA-Z0-9]', '_', rawPatientName)
            
            anonyPatientID=dcmAnonyAlias[uniqueID]
                
            dataSet.PatientID="%s_%s" % (curTimeStamp, anonyPatientID)
            dataSet.PatientName=anonyPatientID
                
            dcmSuccessNum[uniqueID]+=1
                
            dcmOutFullFile=os.path.join(dcmOutDir, "%s_%s" % (curTimeStamp, anonyPatientID), 
                                        dcmOutSubFileList[i])    
            
            ensure_dir(dcmOutFullFile)
            dataSet.save_as(dcmOutFullFile)
            
            # Print Info
            if dcmSuccessNum[uniqueID]==1:
                if "oldUniqueID" in vars() and self.verbose:
                    Txt="%s->%s (%.5d/%.5d)\n" % (oldUniqueID, dcmAnonyAlias[oldUniqueID], 
                                                      dcmSuccessNum[oldUniqueID], dcmTotalNum[oldUniqueID])
                    print(Txt, end="")
                oldUniqueID=uniqueID
                    
            if i%self.updateStep==0 and self.verbose:
                Txt="%s->%s (%.5d/%.5d)\r" % (uniqueID, dcmAnonyAlias[uniqueID], 
                                                      dcmSuccessNum[uniqueID], dcmTotalNum[uniqueID])
                print(Txt, end="")
            
            # GUI Display Reload Function
            self.SetDcmTotalNum(dcmDict=dcmTotalNum)
            self.SetDcmSuccessNum(dcmDict=dcmSuccessNum)
            
            if i%self.updateStep==0:
                self.UpdateInfoTable()
                self.StoreAnonyMapping(os.path.join(dcmOutDir, "%s_anonymized_subject_mapping.csv" % curTimeStamp))
        
        # Print Info
        if self.verbose:
            Txt="%s->%s (%.5d/%.5d)\n" % (uniqueID, dcmAnonyAlias[uniqueID], 
                    dcmSuccessNum[uniqueID], dcmTotalNum[uniqueID])
            print(Txt, end="")
            
        self.SetDcmSuccessNum(dcmDict=dcmSuccessNum)
        self.SetDcmAnonyAlias(dcmDict=dcmAnonyAlias)
        
        self.StoreInvalidDcmList(os.path.join(dcmOutDir, "%s_invalid_dicom_files.list" % curTimeStamp))
        self.StoreAnonyMapping(os.path.join(dcmOutDir, "%s_anonymized_subject_mapping.csv" % curTimeStamp))
        
        self.UpdateInfoTable()

        self.SetState("AnonyFinish")
        if self.verbose:
            print("Finished!")
        
if __name__=="__main__":
    start=time.time()
    da=DicomAnonymizer()
    da.SetDcmWorkDir("./test")
    da.SetDcmOutDir("./sort")
    da.SetDcmAnonyPrefix("Patient")
    da.SetDcmAnonyStartP(1)
    da.ParseDicom()
    da.AnonyDicom()
    end=time.time()
    print(end-start)
