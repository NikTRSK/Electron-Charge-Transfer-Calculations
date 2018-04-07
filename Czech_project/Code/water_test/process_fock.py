import sys
import argparse
import logging
import re
from datetime import datetime
import shutil
from subprocess import Popen, PIPE
import os
import csv

global fileList
fileList = []

global chkFiles
chkFiles = []

global matrixList
matrixList = []

# global writer
# writer

def main():
  # Process command line arguments
  parser = argparse.ArgumentParser(description='input parameters.')
  parser.add_argument('-i', '--input', dest = 'input', type = str, action = 'append', required = True, help = 'input file for the whole molecule')
  args = parser.parse_args()

  createDirStructure(args.input)

  # Check if file has the right extension (all files)
  for file in range(len(args.input)):
    if not args.input[file].lower().endswith('.com'):
      logging.debug ("Wrong file extensions. Terminatng...")
      sys.exit()
    createFockFile(str(args.input[file]))
  
  for file in range(len(fileList)):
    callGaussian(str(fileList[file]))

  extractMainFockMatrix(fileList[1])  
  extractMolecularOrbitals(chkFiles)

  calcFock()

  logging.info("Process finished running succesfully")

def createFockFile(src):
  logging.info("Preparing: %s" % src) # logging info
  # Load files
  # Get destination
  dst = src[:-4] + "_fockM.com" # Already checked for valid extension so just extract
  # Make a copy of the file for the fock matrix
  try:
    srcFile = open(src, "r+wb") # open file in r mode
    srcFileTmp = open((src+".tmp"), "wb")
    dstFile = open(dst, "wb") # open file in w mode
  except IOError as e:
    logging.debug("Error opening file: %s" % e)
    exit

  # Generate fockMatrix file if it's only the whole molecule
  edited = False # For checking whether the file has been edited
  print "file list"
  print fileList
  if (len(fileList) == 0):
    fockParams = "Iop(5/33=3) Iop(3/33=1) "
    guess = "guess=read"
  else:
    edited = True # If doesn't need to be edited change the edited flag

  for line in srcFile:
    # extract checkpoint file
    if (line.startswith('%chk')):
      chkFiles.append(str(src[:-4]) + ".chk")
      #print chkFiles
      line = ("%chk=" + str(src[:-4]) + ".chk\n")

    srcFileTmp.write(line)

    if (edited == False):
      if (line in ['\n', '\r\n']):
        line = "#P " + fockParams + guess + '\n\n'
        edited = True

    dstFile.write(line)

  srcFile.close()
  dstFile.close()
  # Overwrite original file
  srcFileTmp.close()
  os.remove(src)
  os.rename(src + ".tmp", src)

  # append files to fileList for further processing
  fileList.append(src)
  fileList.append(dst)

  logging.info("\t- Completed creating fock Matrix file: %s" % dst)

# Runs Gaussian with the file list first without printing fock matrix
# and then with print fock matrix option
def callGaussian(file):
  logging.info('Running Gaussian on %s' % file)
  # exitCode = os.system("python matrix.py -f 1 -mo1 2 -mo2 3 -k 490 -c 167")
  exitCode = os.system("G09 %s" % file)
  # 0 - completed successfully, 1 - error
  if (exitCode == 0):
    logging.info("\t%s processed succesfully" % file)
  elif (exitCode == 1):
    logging.debug("Error processing file: %s" % file)

# Converts .chk file to .fchk file and runs readMO to extract Molecular orbital matrices
# Assumes the first inputed file is the whole molecule
def extractMolecularOrbitals(moFiles):
  logging.info("****Getting Molecular Orbitals from .chk files****")
  for file in moFiles[1:]:
    logging.info("Converting %s" % file)
    exitCode = os.system("/usr/local/g09/formchk %s" % file)
    # 0 - completed successfully, 1 - error
    if (exitCode == 0):
      logging.info("\t%s processed succesfully" % file)
    elif (exitCode == 1):
      logging.debug("Error processing file: %s" % file)

  # get the molecular orbital matrix using readMO perl script
  for file in moFiles[1:]:
    logging.info("Getting molecular orbital matrix from %s" % file)
    fchk = str(file[:-4]) + ".fchk"
    txt = str(file[:-4]) + ".txt"
    matrixList.append(txt)
    print "FCHK: %s" % fchk
    exitCode = os.system("perl ../readMO %s" % str(fchk) + (" >> %s" % str(txt)))
    # 0 - completed successfully, 1 - error
    if (exitCode == 0):
      logging.info("\tMolecular Orbital Matrix succesfully extracted")
    elif (exitCode == 1):
      logging.debug("Error extracting Molecular Orbital")

# Converts .chk file to .fchk file and runs readMO to extract Molecular orbital matrices
# Assumes the first inputed file is the whole molecule
def extractMainFockMatrix(comlog):
  logging.info("****Getting Fock Matrix from .chk files****")
# get the molecular orbital matrix using readMO perl script
  logging.info("Extracting fock matrix from com.log file %s" % comlog)
  txt = comlog[:-10] + ".txt"
  matrixList.append(txt)
  exitCode = os.system("perl ../readfock %s" % str(comlog + ".log") + (" >> %s" % txt))
  # 0 - completed successfully, 1 - error
  if (exitCode == 0):
    logging.info("\tFock Matrix succesfully extracted")
  elif (exitCode == 1):
    logging.debug("Error extracting Fock Matrix")

def createDirStructure(files):
  currTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  # enable logging
  logging.basicConfig(filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.DEBUG)
  # create dir
  path = "job" + currTime
  os.mkdir(path, 0755)
  # move files
  for file in files:
    shutil.copy(file, path)
  # change dir
  os.chdir(path)

def calcFock():
  logging.info("**** CALCULATING ENERGY LEVELS ****")
  num = 0
  output = Popen(str(("python ../calcJ.py -f %s" % matrixList[0]) + (" -mo1 %s" % matrixList[1]) + (" -mo2 %s" % matrixList[2]) + (" -l1 %i" % num) + (" -l2 %i" % num)), stdout=PIPE, shell=True)
  J = (output.communicate()[0].split('\n')[1])[:-4]
  dG = (output.communicate()[0].split('\n')[4])[:-4]
  print J
  print dG
  # J = (output.communicate()[0].split('\n')[1])[:-4]
  # try:
  #   float(J)
  #   logging.info("J (kcal) %f" float(J))
  #   print J
  # except ValueError as e:
  #   logging.debug("Problem in calculating J value. Rerun calcMatrix.py manually: %s" % e)

if __name__ == '__main__':
  main()