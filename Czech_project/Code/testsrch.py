inFile = open("PD1_PD2_v5_PD1.com.log", "r")

for line in inFile:
  if "alpha electrons" in line:
    mo_cols = line.split(None, 1)[0]
    print mo_cols # accounts for 0 base