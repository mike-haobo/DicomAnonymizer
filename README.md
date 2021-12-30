# Welcome to DICOM Anonymizer Page

Date: Dec. 24th, 2021

----
## Description
DICOM Anonymizer v1.0, a CLI/GUI toolbox to structure and anonymize DICOM files.

Developped by Beijing Intelligent Brain Cloud, Inc., Beijing, China.

## License
DICOM Anonymizer use GPLv3 license.

## Standalone Release
Standalone version have been released at [DICOM Anonymizer Release](https://github.com/mike-haobo/DicomAnonymizer/releases)

## Dependency
We developed DICOM Anonymizer based on the following library, however older version should also work.
* Python 3.6.9
* numpy >= 1.20.2
* pydicom >= 2.2.1

If you would like to use GUI version of DICOM Anonymizer
* PyQt5 >= 5.10.1

NOTE: If you would package DICOM Anonymizer by yourself, please visit [FBS](https://build-system.fman.io/)

## Usage
### Input
* DICOM Working Directory: The source path for unstructured DICOM files which have sensitive information (_e.g._ PatientName) included in header.
* Anonymized Dicom Output Directory: The output path for structed & anonymized DICOM files.
* Prefix of Anonymized DICOM Sub-Folders: User can set the prefix of all anonymized DICOM folders, _e.g._, if you set prefix to "patient", the anonymized DICOM folders would be _timestamp_\_patient\_0001, _timestamp_\_patient\_0002, ...
* Starting Number of Anonymized Dicom Sub-Folders: User can set the starting number of all anonymized DICOM folders, _e.g._, if you set starting number to 10, the anonymized DICOM folders would be _timestamp_\_patient\_0010, _timestamp_\_patient\_0011, ...

### CLI Usage
User can easily call Dicom Anonymizer in the Python3 environment:
```python
from coreFunction import DicomAnonymizer

# Init Dicom Anonymizer
da=DicomAnonymizer()

# Set All Input
da.SetDcmWorkDir("./test")
da.SetDcmOutDir("./sort")
da.SetDcmAnonyPrefix("Patient")
da.SetDcmAnonyStartP(1)

# Parse All DICOM Files and Build Output Folder Structure
da.ParseDicom()

# Anonymize All DICOM Files and Copy Them to Output Directory
da.AnonyDicom()

```

### GUI Usage
User can directly use GUI version of DICOM Anonymizer:
* 1 - Set All Input
* 2 - Click 'Export' Button and Execute

## Output
* Structured DICOM folders: the output DICOM files, with *timestamp*\_*prefix*\_*starting\_number*.
* Anonymized Subjects Mapping Table: the mapping table between raw *Patient_ID* to anonymized ones.
* Invalid DICOM files: all invalid files absolute path would be save in this list.

## File Lists
### Package
* coreFunction.py: codes to generate structured & anonymized DICOM files.
* mainWindow.py: codes build GUI application.
* main.py: codes for packaging interface.
### Icons
* Icons of Beijing Intelligent Brain Cloud, Inc., Beijing, China.

## Customized Packaging with FBS
Before packaging, please ensure you have installed FBS, and run:
```bash
mkdir Dist/
cd Dist
fbs startproject
cp ../Package/* src/main/python/
cp ../Icons/* src/main/icons/
fbs freeze
```
Then, you could acquire the freezed toolbox in *target* folder.
