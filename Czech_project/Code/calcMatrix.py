import sys
import argparse
import logging
from datetime import datetime
import numpy

def findStartOfLUMO(mo):
  moFile = open(mo, "r")

  for line in moFile:
    if "alpha electrons" in line:
      return int(line.split(None, 1)[0])

# Process command line arguments
parser = argparse.ArgumentParser(description='input parameters.')
parser.add_argument('-f', '--fock', dest = 'fock', type = str, required = True, help = 'fock matrix')
parser.add_argument('-mo1', '--MO1', dest = 'MO1', type = str, required = True, help = 'molecular orbitals for molecule 1')
parser.add_argument('-mo2', '--MO2', dest = 'MO2', type = str, required = True, help = 'molecular orbitals for molecule 2')
#parser.add_argument('-k', '--k', dest = 'k', type = str, required = True, help = 'upper bound for the orbitals')
#parser.add_argument('-c', '--MO_COLS', dest = 'cols', type = str, required = True, help = 'number of columns')
args = parser.parse_args()

# Load matrices
fock_matrix = numpy.loadtxt(args.fock)
molecule1_matrix = numpy.loadtxt(args.MO1)
molecule2_matrix = numpy.loadtxt(args.MO2)

#mo_cols = int(args.cols) - 1 # account for zero base (in the example 167)
#k = int(args.k) # in the example 490
#mo_cols = molecule1_matrix.shape[0]/2 # this is wrong. How do you get 167
k = fock_matrix.shape[0]/2

print args.MO1[:-3] + "com.log"
mo1_cols = findStartOfLUMO(args.MO1[:-3] + "com.log")
mo2_cols = findStartOfLUMO(args.MO2[:-3] + "com.log")

LUMO1 = molecule1_matrix[:,mo1_cols]
LUMO2 = molecule2_matrix[:,mo2_cols]

result = 0
for i in range(len(LUMO1)):
  for j in range(len(LUMO2)):
    result += LUMO1[i]*LUMO2[j]*fock_matrix[i][j+k]

print result*627.51, "kcal"