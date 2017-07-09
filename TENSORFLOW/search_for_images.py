import tensorflow as tf
import sys
import os
import magic
import zipfile
import zlib
import shutil
import subprocess
import shlex
import logging
import datetime
import operator
 
IMAGE_FORMATS = ['image/jpeg', 'image/png', 'image/gif']
ARCHIVE_FILE_EXTENSIONS = ['zip', 'xlsx', 'docx']

class Labeler(object):
    def __init__(self, timed=False, logname="Log_File.txt"):
        self.timed = timed
        self.logger = logging.getLogger("SATURN")
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.suspects = list()
        self.nonsuspects = list()

    def labelImage(self, fullPath, archiveFileName=None):
        self.logger.warning("Found an image file \"{0}\"\n".format(fullPath))
        labelProc = subprocess.Popen(args=shlex.split("python label_image.py \"{0}\"".format(fullPath)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = labelProc.communicate()
        self.logger.warning("Output: \"{0}\"\n".format(output))

        if errors is not None and "TensorFlow library wasn't compiled to use" not in errors.strip():
            self.logger.warning(errors)
            print(errors)
            return False

        if "not suspect" in output:
            if archiveFileName is not None:
                pass
            else:
                if output.strip() != "":
                    outputParts = [_ for _ in output[0:-1].split(",")]
                    parts = dict()
                    parts["file name"] = outputParts[0]
                    parts["label"] = outputParts[1]
                    parts["score"] = outputParts[2]
                    self.nonsuspects.append(parts)
        else:
            if archiveFileName is not None:
                if output.strip() != "":
                    parts = {"file name" : archiveFileName}
                    outputParts = [_ for _ in output[0:-1].split(",")]
                    parts["label"] = outputParts[1]
                    parts["score"] = outputParts[2]
                    self.suspects.append(parts)
                else:
                    self.logger.warning("Couldn't get output for \"{0}\"\n".format(fullPath))
            else:
                if output.strip() != "":
                    outputParts = [_ for _ in output[0:-1].split(",")]
                    parts = dict()
                    parts["file name"] = outputParts[0]
                    parts["label"] = outputParts[1]
                    parts["score"] = outputParts[2]
                    self.suspects.append(parts)
                else:
                    self.logger.warning("Couldn't get output for \"{0}\"\n".format(fullPath))

        return True

    def labelArchiveFile(self, fullPath, imageFormats=IMAGE_FORMATS):
        archive = zipfile.ZipFile(fullPath)
        fileNames = archive.namelist()
        for fileName in fileNames:
            try:
                newFileName = archive.extract(fileName)
                headerType = magic.from_file(newFileName, mime=True)
                if headerType in imageFormats:
                    assert(self.labelImage(newFileName, fullPath))
                os.remove(newFileName)
            except zlib.error as ze:
                self.logger.warning("WARNING: Encountered zlib error: \"{0}\"\n".format(str(ze)))
                print("WARNING: Encountered zlib error: \"{0}\"\n".format(str(ze)))
            except zipfile.BadZipfile as bzf:
                self.logger.warning("WARNING: Encountered bad zip file error: \"{0}\"\n".format(str(bzf)))
                print("WARNING: Encountered bad zip file error: \"{0}\"\n".format(str(bzf)))
            except Exception as e:
                self.logger.warning("Encountered exception {0}".format(str(e)))
                print("Encountered exception {0}".format(str(e)))

        for directory in ['word', 'xl', 'docProps', '_rels']:
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def searchDir(self, sharedDir, imageFormats=IMAGE_FORMATS,
archiveFileExtensions=ARCHIVE_FILE_EXTENSIONS):
        for rootPath, directories, files in os.walk(sharedDir):
            for ithFile in files:
                fullPath = os.path.join(rootPath, ithFile)

                try:
                    headerType = magic.from_file(fullPath, mime=True)
                except IOError as ioe:
                    self.logger.warning("Could not scan file \"{0}\" because {1}\n".format(fullPath, str(ioe)))

                if headerType in imageFormats:
                    self.logger.warning("Found an image file \"{0}\"\n".format(fullPath))
                    assert(self.labelImage(fullPath))
                else:
                    isArchiveFile = False
                    for fileExt in archiveFileExtensions:
                        if fullPath.endswith(fileExt):
                            isArchiveFile = True
                            break
                    if isArchiveFile:
                        self.logger.warning("Found an archive file \"{0}\"\n".format(fullPath))
                        self.labelArchiveFile(fullPath, IMAGE_FORMATS)

    def searchSharedDirs(self, sharedDirRoot="/media"):
        if self.timed:
            print("Started processing at {0} in UTC time.".format(datetime.datetime.now()))
            self.logger.warning("Started processing at {0} in UTC time.".format(datetime.datetime.now()))
        for directory in os.listdir(sharedDirRoot):
            fullPath = os.path.join(sharedDirRoot, directory)
            #Only search shared folders.
            if not os.path.isfile(fullPath) and directory.startswith("sf_"):
                print("Searching \"{0}\"\n".format(fullPath))
                self.logger.warning("Searching \"{0}\"\n".format(fullPath))
                self.searchDir(fullPath)
            else:
                print("Not searching \"{0}\"\n".format(fullPath))
                self.logger.warning("Not searching \"{0}\"\n".format(fullPath))

        self.suspects.sort(key=operator.itemgetter("score"), reverse=True)
        for suspectTuple in self.suspects:
            self.logger.warning("Suspected picture: {0},{1},{2}\n".format(suspectTuple["file name"], suspectTuple["label"], suspectTuple["score"]))

        self.nonsuspects.sort(key=operator.itemgetter("score"), reverse=True)
        for nonSuspectTuple in self.nonsuspects:
            self.logger.warning("Not-suspected picture: {0},{1},{2}\n".format(nonSuspectTuple["file name"], nonSuspectTuple["label"], nonSuspectTuple["score"]))

        if self.timed:
            self.logger.warning("Ended processing at {0} in UTC time".format(datetime.datetime.now()))
            print("Ended processing at {0} in UTC time".format(datetime.datetime.now()))

def main():
    labeler = Labeler(timed=True, logname="Log_File_{0}.txt".format(datetime.datetime.now()))
    labeler.searchSharedDirs()

if __name__ == "__main__":
    main()
