import ROOT
import sys

import topbnv_tools as tbt

import numpy as np
import math
import matplotlib.pylab as plt

import pickle

import argparse

from array import array

import lichen.lichen as lch

tag = "DEFAULT"


################################################################################
def main(filenames,outfilename=None):

    jet_csv = []
    jet_eta = []
    jet_pt = []

    tree = ROOT.TChain("Tskim")

    for ifile,infile in enumerate(filenames):
        print("Opening file %s %d of %d" % (infile,ifile,len(filenames)))
        tree.AddFile(infile)
    tree.Print()

    filetag = filenames[0].split('/')[-1].split('.root')[0]
    print( filenames[0].split('/')[-1])
    print(filetag)

    nentries = tree.GetEntries()
    print("Will run over %d entries" % (nentries))

    nentries = 100000

    for i in range(nentries):

        if i%10000==0:
            output = "Event: %d out of %d" % (i,nentries)
            print(output)

        tree.GetEntry(i)

        jetptcut = 0

        njet = tree.njet
        csv = tree.jetcsv
        eta = tree.jeteta
        pt = tree.jetpt

        for n in range(njet):
            jet_csv.append(csv[n])
            jet_eta.append(eta[n])
            jet_pt.append(pt[n])

    jet_csv = np.array(jet_csv)
    jet_eta = np.array(jet_eta)
    jet_pt = np.array(jet_pt)

    #############################################################
    plt.figure(figsize=(16,8))

    plt.subplot(2,3,1)
    plt.hist(jet_csv,range=(-11,2),bins=100)
    plt.xlabel('CSV output',fontsize=14)

    plt.subplot(2,3,2)
    plt.hist(jet_csv,range=(0,1.1),bins=100)
    plt.xlabel('CSV output (zoomed in)',fontsize=14)

    plt.subplot(2,3,3)
    plt.hist(jet_csv,range=(-15,-5),bins=100)
    plt.xlabel('CSV output (zoomed in)',fontsize=14)

    plt.subplot(2,3,4)
    plt.hist(jet_eta,bins=100)
    plt.xlabel(r'$\eta$',fontsize=14)

    idx = jet_csv>=0
    plt.subplot(2,3,5)
    plt.hist(jet_eta[idx],bins=100)
    plt.xlabel(r'$\eta$ for CSV>=0',fontsize=14)

    idx = jet_csv<0
    plt.subplot(2,3,6)
    plt.hist(jet_eta[idx],bins=100)
    plt.xlabel(r'$\eta$ for CSV<0',fontsize=14)

    plt.tight_layout()

    plt.savefig('CSV_and_eta.png')


    #############################################################
    idx_pt = jet_pt>30

    plt.figure(figsize=(16,8))

    plt.subplot(2,3,1)
    plt.hist(jet_csv[idx_pt],range=(-11,2),bins=100)
    plt.xlabel('CSV output',fontsize=14)

    plt.subplot(2,3,2)
    plt.hist(jet_csv[idx_pt],range=(0,1.1),bins=100)
    plt.xlabel('CSV output (zoomed in)',fontsize=14)

    plt.subplot(2,3,3)
    plt.hist(jet_csv[idx_pt],range=(-15,-5),bins=100)
    plt.xlabel('CSV output (zoomed in)',fontsize=14)

    plt.subplot(2,3,4)
    plt.hist(jet_eta[idx_pt],bins=100)
    plt.xlabel(r'$\eta$',fontsize=14)

    idx = jet_csv>=0
    idx *= idx_pt
    plt.subplot(2,3,5)
    plt.hist(jet_eta[idx],bins=100)
    plt.xlabel(r'$\eta$ for CSV>=0',fontsize=14)

    idx = jet_csv<0
    idx *= idx_pt
    plt.subplot(2,3,6)
    plt.hist(jet_eta[idx],bins=100)
    plt.xlabel(r'$\eta$ for CSV<0',fontsize=14)

    plt.tight_layout()

    plt.savefig('CSV_and_eta_for_pt_gt_30.png')



    plt.show()

################################################################################
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some files for top BNV search.')
    parser.add_argument('--outfile', dest='outfile', default=None, help='Name of output file.')
    parser.add_argument('infiles', action='append', nargs='*', help='Input file name(s)')
    args = parser.parse_args()

    print(args)

    main(args.infiles[0],args.outfile)


    plt.show()

################################################################################
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some files for top BNV search.')
    parser.add_argument('--outfile', dest='outfile', default=None, help='Name of output file.')
    parser.add_argument('infiles', action='append', nargs='*', help='Input file name(s)')
    args = parser.parse_args()

    print(args)

    main(args.infiles[0],args.outfile)
