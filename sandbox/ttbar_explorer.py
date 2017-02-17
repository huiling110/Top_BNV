import ROOT
import sys

import numpy as np
import matplotlib.pylab as plt

# Might need to comment this if lichen is not installed
import lichen.lichen as lch


f = ROOT.TFile(sys.argv[1])

tree = f.Get("TreeSemiLept")

# Uncomment this if you just want to see what is stored
# in the file.
# print("In the file...")
# f.ls()
# print("In the TTree....")
#tree.Print()
#exit()

nentries = tree.GetEntries()

values = []
valuesjet = []

for nentry in range(nentries):

    output = "Event: %d\n" % (nentry)
    tree.GetEntry(nentry)

    nmuon = tree.nmuon
    njet = tree.njet

    for i in range(nmuon):
        v = tree.muonpx[i]
        print(v)
        values.append(v)

    for i in range(njet):
        v = tree.jetpx[i]
        print(v)
        valuesjet.append(v)

plt.figure()
lch.hist_err(values)

plt.figure()
lch.hist_err(valuesjet)

plt.show()
