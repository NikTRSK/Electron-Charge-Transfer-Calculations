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

def findLUMOEnergy(MO):
  with open(MO, 'r') as file:
    for line in file:
      # Extract the first LUMO orbital energy
      if "Alpha virt. eigenvalues --" in line:
        return line.split('Alpha virt. eigenvalues --')[1].split()[0]
      
# Process command line arguments
parser = argparse.ArgumentParser(description='input parameters.')
parser.add_argument('-f', '--fock', dest = 'fock', type = str, required = True, help = 'fock matrix')
parser.add_argument('-mo1', '--MO1', dest = 'MO1', type = str, required = True, help = 'molecular orbitals for molecule 1')
parser.add_argument('-mo2', '--MO2', dest = 'MO2', type = str, required = True, help = 'molecular orbitals for molecule 2')
parser.add_argument('-l1', '--LUMO1', dest = 'l1', type = int, choices=set((0,1)), required = True, help = '0 - extract LUMO orbital, 1 - extract HOMO orbital; for molecule 1')
parser.add_argument('-l2', '--LUMO2', dest = 'l2', type = int, choices=set((0,1)), required = True, help = '0 - extract LUMO orbital, 1 - extract HOMO orbital; for molecule 2')
args = parser.parse_args()

# Load matrices
fock_matrix = numpy.loadtxt(args.fock)
molecule1_matrix = numpy.loadtxt(args.MO1)
molecule2_matrix = numpy.loadtxt(args.MO2)

k = fock_matrix.shape[0]/2

# Get the start of the lumo orbitals
mo1_cols = findStartOfLUMO(args.MO1[:-3] + "com.log")
mo2_cols = findStartOfLUMO(args.MO2[:-3] + "com.log")

# Choose between HOMO and LUMO orbitals for each molecule
if args.l1 == 1:
  mo1_cols -= 1
if args.l2 == 1:
  mo2_cols -= 1

LUMO1 = molecule1_matrix[:,mo1_cols]
LUMO2 = molecule2_matrix[:,mo2_cols]

result = 0
for i in range(len(LUMO1)):
  for j in range(len(LUMO2)):
    result += LUMO1[i]*LUMO2[j]*fock_matrix[i][j+len(LUMO1)]

print "J: ", result*627.51, "kcal"
LUMO1Energy = float(findLUMOEnergy(args.MO1[:-3] + "com.log"))
LUMO2Energy = float(findLUMOEnergy(args.MO2[:-3] + "com.log"))
dG = LUMO2Energy - LUMO1Energy
print "Molecule 1 energy: ", LUMO1Energy, "hartrees"
print "Molecule 2 energy: ", LUMO2Energy, "hartrees"
print "dG: ", dG*627.51, "kcal"