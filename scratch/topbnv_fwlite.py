# Much of this is from the B2G data analysis school code

import ROOT, copy, sys, logging
from array import array
from DataFormats.FWLite import Events, Handle

from RecoEgamma.ElectronIdentification.VIDElectronSelector import VIDElectronSelector
# Cut-based...we should use this!
# https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Recipe80X
#from RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff import cutBasedElectronID_Summer16_80X_V1_loose
from RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff import cutBasedElectronID_Summer16_80X_V1_medium

# Need to do this globally because there's a warning associated with the attribute, isPOGApproved
# that doesn't need to be there but would get called every time we called this from the event
# loop!
selectElectron = VIDElectronSelector(cutBasedElectronID_Summer16_80X_V1_medium)

#import RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff.cutBasedElectronID-Summer16-80X-V1-loose as electron_loose
#import RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff.cutBasedElectronID-Summer16-80X-V1-medium as electron_medium
#import RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff.cutBasedElectronID-Summer16-80X-V1-tight as electron_tight

# MC values are for the 2016 data
muon_triggers_of_interest = [
    ["HLT_IsoMu24_v", "v4"],
    ["HLT_IsoTkMu24_v","v4"],
    ["HLT_IsoMu22_eta2p1_v","v4"],
    ["HLT_IsoTkMu22_eta2p1_v","v4"]
    ]

electron_triggers_of_interest = [
    ["HLT_Ele32_eta2p1_WPTight_Gsf_v", "v7"],
    ["HLT_Ele27_WPTight_Gsf_v", "v8"],
    ["HLT_Ele25_eta2p1_WPTight_Gsf_v", "v8"]
    ]

dilepmue_triggers_of_interest = [
    ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v", "v9"],
    ["HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v", "v4"]
]

dilepemu_triggers_of_interest = [
    ["HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v", "v9"],
    ["HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v", ""],
    ["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v", "v3"],
    ["HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v", "v4"]
]

dilepmumu_triggers_of_interest = [
    ["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v", "v7"],
    ["HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v", "v6"]
    ]

dilepee_triggers_of_interest = [
    ["HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v", "v9"],
    ["HLT_DoubleEle24_22_eta2p1_WPLoose_Gsf_v", "v8"]
    ]

triggers_of_interest = [
["SingleMuon",muon_triggers_of_interest],
["SingleElectron",electron_triggers_of_interest],
["DileptonMuE",dilepmue_triggers_of_interest],
["DileptonEMu",dilepemu_triggers_of_interest],
["DileptonMuMu",dilepmumu_triggers_of_interest],
["DileptonEE",dilepee_triggers_of_interest]
]


#####################################################################################
# Command line parsing
#####################################################################################
def getUserOptions(argv):
    from optparse import OptionParser
    parser = OptionParser()

    def add_option(option, **kwargs):
        parser.add_option('--' + option, dest=option, **kwargs)

    add_option('input',              default='',
        help='Name of file with list of input files')
    add_option('output',             default='output.root',
        help='Name of output file')
    add_option('verbose',            default=False, action='store_true',
        help='Print debugging info')
    add_option('maxevents',          default=-1,
        help='Number of events to run. -1 is all events')
    add_option('trigType',          default="SingleMuon",
        help='SingleMuon, SingleElectron, etc.')
    add_option('isMC',          default=False, action='store_true',
        help='Running over MC. We need this for the trigger and other stuff.')
    add_option('isCrabRun',          default=False, action='store_true',
        help='Use this flag when running with crab on the grid')
    add_option('localInputFiles',    default=False, action='store_true',
        help='Use this flag when running with with local files')

    (options, args) = parser.parse_args(argv)
    argv = []

    print ('===== Command line options =====')
    print (options)
    print ('================================')
    return options



#####################################################################################
def getInputFiles(options):
    result = []
    with open(options.input, 'r') as fpInput:
        for lfn in fpInput:
            print("lfn: ")
            print(lfn)
            lfn = lfn.strip()
            print(lfn)
            if lfn:
                if not options.isCrabRun:
                    if options.localInputFiles:
                        pfn = lfn
                        print('pfn: ')
                        print(pfn)
                    else:
                        #pfn = 'file:/pnfs/desy.de/cms/tier2/' + lfn
                        pfn = 'root://cmsxrootd-site.fnal.gov/' + lfn
                else:
                    #pfn = 'root://cmsxrootd-site.fnal.gov/' + lfn
                    pfn = 'root://xrootd-cms.infn.it/' + lfn
                print ('Adding ' + pfn)
                result.append(pfn)
    print(result)
    return result
#####################################################################################





#####################################################################################
def topbnv_fwlite(argv):
    ## _____________      __.____    .__  __             _________ __          _____  _____
    ## \_   _____/  \    /  \    |   |__|/  |_  ____    /   _____//  |_ __ ___/ ____\/ ____\
    ##  |    __) \   \/\/   /    |   |  \   __\/ __ \   \_____  \\   __\  |  \   __\\   __\
    ##  |     \   \        /|    |___|  ||  | \  ___/   /        \|  | |  |  /|  |   |  |
    ##  \___  /    \__/\  / |_______ \__||__|  \___  > /_______  /|__| |____/ |__|   |__|
    ##      \/          \/          \/             \/          \/

    options = getUserOptions(argv)
    ROOT.gROOT.Macro("rootlogon.C")

    #print argv
    #print options

    jets, jetLabel = Handle("std::vector<pat::Jet>"), "slimmedJets"
    muons, muonLabel = Handle("std::vector<pat::Muon>"), "slimmedMuons"
    electrons, electronLabel = Handle("std::vector<pat::Electron>"), "slimmedElectrons"
    #packedgens, packedgenLabel = Handle("std::vector<reco::packedGenParticle>"), "PACKEDgENpARTICLES"
    packedgens, packedgenLabel = Handle("std::vector<pat::PackedGenParticle>"), "packedGenParticles"
    genInfo, genInfoLabel = Handle("GenEventInfoProduct"), "generator"
    mets, metLabel = Handle("std::vector<pat::MET>"), "slimmedMETs"

    # NEED HLT2 for 80x 2016 (maybe only TTBar?
    # https://twiki.cern.ch/twiki/bin/view/CMS/TopTrigger#Summary_for_2016_Run2016B_H_25_n
    triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), ("TriggerResults","", "HLT")



    f = ROOT.TFile(options.output, "RECREATE")
    f.cd()

    outtree = ROOT.TTree("T", "Our tree of everything")

    def bookFloatBranch(name, default):
        tmp = array('f', [default])
        outtree.Branch(name, tmp, '%s/F' %name)
        return tmp
    def bookIntBranch(name, default):
        tmp = array('i', [default])
        outtree.Branch(name, tmp, '%s/I' %name)
        return tmp
    def bookLongIntBranch(name, default):
        tmp = array('l', [default])
        outtree.Branch(name, tmp, '%s/L' %name)
        return tmp

    # Jets
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideCMSDataAnalysisSchoolLPC2018Jets
    njet = array('i', [-1])
    outtree.Branch('njet', njet, 'njet/I')

    jetpt = array('f', 16*[-1.])
    outtree.Branch('jetpt', jetpt, 'jetpt[njet]/F')
    jeteta = array('f', 16*[-1.])
    outtree.Branch('jeteta', jeteta, 'jeteta[njet]/F')
    jetphi = array('f', 16*[-1.])
    outtree.Branch('jetphi', jetphi, 'jetphi[njet]/F')
    jetpx = array('f', 16*[-1.])
    outtree.Branch('jetpx', jetpx, 'jetpx[njet]/F')
    jetpy = array('f', 16*[-1.])
    outtree.Branch('jetpy', jetpy, 'jetpy[njet]/F')
    jetpz = array('f', 16*[-1.])
    outtree.Branch('jetpz', jetpz, 'jetpz[njet]/F')
    jete = array('f', 16*[-1.])
    outtree.Branch('jete', jete, 'jete[njet]/F')

    jetbtag = array('f', 16*[-1.])
    outtree.Branch('jetbtag', jetbtag, 'jetbtag[njet]/F')

    jetNHF = array('f', 16*[-1.])
    outtree.Branch('jetNHF', jetNHF, 'jetNHF[njet]/F')
    jetNEMF = array('f', 16*[-1.])
    outtree.Branch('jetNEMF', jetNEMF, 'jetNEMF[njet]/F')
    jetCHF = array('f', 16*[-1.])
    outtree.Branch('jetCHF', jetCHF, 'jetCHF[njet]/F')
    jetMUF = array('f', 16*[-1.])
    outtree.Branch('jetMUF', jetMUF, 'jetMUF[njet]/F')
    jetCEMF = array('f', 16*[-1.])
    outtree.Branch('jetCEMF', jetCEMF, 'jetCEMF[njet]/F')
    jetNumConst = array('f', 16*[-1.])
    outtree.Branch('jetNumConst', jetNumConst, 'jetNumConst[njet]/F')
    jetNumNeutralParticles = array('f', 16*[-1.])
    outtree.Branch('jetNumNeutralParticles', jetNumNeutralParticles, 'jetNumNeutralParticles[njet]/F')
    jetCHM = array('f', 16*[-1.])
    outtree.Branch('jetCHM', jetCHM, 'jetCHM[njet]/F')

    # Muons
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideCMSDataAnalysisSchoolLPC2018Muons
    # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2
    nmuon = array('i', [-1])
    outtree.Branch('nmuon', nmuon, 'nmuon/I')
    muonpt = array('f', 16*[-1.])
    outtree.Branch('muonpt', muonpt, 'muonpt[nmuon]/F')
    muoneta = array('f', 16*[-1.])
    outtree.Branch('muoneta', muoneta, 'muoneta[nmuon]/F')
    muonphi = array('f', 16*[-1.])
    outtree.Branch('muonphi', muonphi, 'muonphi[nmuon]/F')
    muonq = array('f', 16*[-1.])
    outtree.Branch('muonq', muonq, 'muonq[nmuon]/F')
    muonpx = array('f', 16*[-1.])
    outtree.Branch('muonpx', muonpx, 'muonpx[nmuon]/F')
    muonpy = array('f', 16*[-1.])
    outtree.Branch('muonpy', muonpy, 'muonpy[nmuon]/F')
    muonpz = array('f', 16*[-1.])
    outtree.Branch('muonpz', muonpz, 'muonpz[nmuon]/F')
    muone = array('f', 16*[-1.])
    outtree.Branch('muone', muone, 'muone[nmuon]/F')
    muonsumchhadpt = array('f', 16*[-1.])
    outtree.Branch('muonsumchhadpt', muonsumchhadpt, 'muonsumchhadpt[nmuon]/F')
    muonsumnhadpt = array('f', 16*[-1.])
    outtree.Branch('muonsumnhadpt', muonsumnhadpt, 'muonsumnhadpt[nmuon]/F')
    muonsumphotEt = array('f', 16*[-1.])
    outtree.Branch('muonsumphotEt', muonsumphotEt, 'muonsumphotEt[nmuon]/F')
    muonsumPUPt = array('f', 16*[-1.])
    outtree.Branch('muonsumPUPt', muonsumPUPt, 'muonsumPUPt[nmuon]/F')
    muonisLoose = array('i', 16*[-1])
    outtree.Branch('muonisLoose', muonisLoose, 'muonisLoose[nmuon]/I')
    muonisMedium = array('i', 16*[-1])
    outtree.Branch('muonisMedium', muonisMedium, 'muonisMedium[nmuon]/I')

    muonPFiso = array('f', 16*[-1.]); outtree.Branch('muonPFiso', muonPFiso, 'muonPFiso[nmuon]/F')


    # Electrons
    nelectron = array('i', [-1])
    outtree.Branch('nelectron', nelectron, 'nelectron/I')
    electronpt = array('f', 16*[-1.])
    outtree.Branch('electronpt', electronpt, 'electronpt[nelectron]/F')
    electroneta = array('f', 16*[-1.])
    outtree.Branch('electroneta', electroneta, 'electroneta[nelectron]/F')
    electronphi = array('f', 16*[-1.])
    outtree.Branch('electronphi', electronphi, 'electronphi[nelectron]/F')
    electronq = array('f', 16*[-1.])
    outtree.Branch('electronq', electronq, 'electronq[nelectron]/F')
    electronpx = array('f', 16*[-1.])
    outtree.Branch('electronpx', electronpx, 'electronpx[nelectron]/F')
    electronpy = array('f', 16*[-1.])
    outtree.Branch('electronpy', electronpy, 'electronpy[nelectron]/F')
    electronpz = array('f', 16*[-1.])
    outtree.Branch('electronpz', electronpz, 'electronpz[nelectron]/F')
    electrone = array('f', 16*[-1.])
    outtree.Branch('electrone', electrone, 'electrone[nelectron]/F')
    electronTkIso = array('f',16*[-1.])
    outtree.Branch('electronTkIso', electronTkIso, 'electronTkIso[nelectron]/F')
    electronHCIso = array('f',16*[-1.])
    outtree.Branch('electronHCIso', electronHCIso, 'electronHCIso[nelectron]/F')
    electronECIso = array('f',16*[-1.])
    outtree.Branch('electronECIso', electronECIso, 'electronECIso[nelectron]/F')

    # MET
    metpt = array('f', [-1])
    outtree.Branch('metpt', metpt, 'metpt/F')
    metphi = array('f', [-1])
    outtree.Branch('metphi', metphi, 'metphi/F')
    mete = array('f', [-1])
    outtree.Branch('mete',mete, 'mete/F')
    meteta = array('f',[-1])
    outtree.Branch('meteta', meteta, 'meteta/F')

    # Triggers
    # We'll record 4 muon trigger bits for 2016 data
    ntrig_muon = array('i', [-1])
    outtree.Branch('ntrig_muon', ntrig_muon, 'ntrig_muon/I')
    trig_muon = array('i',8*[-1])
    outtree.Branch('trig_muon', trig_muon, 'trig_muon[ntrig_muon]/I')

    ntrig_electron = array('i', [-1])
    outtree.Branch('ntrig_electron', ntrig_electron, 'ntrig_electron/I')
    trig_electron = array('i',8*[-1])
    outtree.Branch('trig_electron', trig_electron, 'trig_electron[ntrig_electron]/I')

    ntrig_dilepmue = array('i', [-1])
    outtree.Branch('ntrig_dilepmue', ntrig_dilepmue, 'ntrig_dilepmue/I')
    trig_dilepmue = array('i',8*[-1])
    outtree.Branch('trig_dilepmue', trig_dilepmue, 'trig_dilepmue[ntrig_electron]/I')

    ntrig_dilepemu = array('i', [-1])
    outtree.Branch('ntrig_dilepemu', ntrig_dilepemu, 'ntrig_dilepemu/I')
    trig_dilepemu = array('i',8*[-1])
    outtree.Branch('trig_dilepemu', trig_dilepemu, 'trig_dilepemu[ntrig_electron]/I')

    ntrig_dilepmumu = array('i', [-1])
    outtree.Branch('ntrig_dilepmumu', ntrig_dilepmumu, 'ntrig_dilepmumu/I')
    trig_dilepmumu = array('i',8*[-1])
    outtree.Branch('trig_dilepmumu', trig_dilepmumu, 'trig_dilepmumu[ntrig_electron]/I')

    ntrig_dilepee = array('i', [-1])
    outtree.Branch('ntrig_dilepee', ntrig_dilepee, 'ntrig_dilepee/I')
    trig_dilepee = array('i',8*[-1])
    outtree.Branch('trig_dilepee', trig_dilepee, 'trig_dilepee[ntrig_electron]/I')

    trigger_tree_branches = {
    "SingleMuon":trig_muon,
    "SingleElectron":trig_electron,
    "DileptonMuE":trig_dilepmue,
    "DileptonEMu":trig_dilepemu,
    "DileptonMuMu":trig_dilepmumu,
    "DileptonEE":trig_dilepee
    }


    #################################################################################
    ## ___________                    __    .____
    ## \_   _____/__  __ ____   _____/  |_  |    |    ____   ____ ______
    ##  |    __)_\  \/ // __ \ /    \   __\ |    |   /  _ \ /  _ \\____ \
    ##  |        \\   /\  ___/|   |  \  |   |    |__(  <_> |  <_> )  |_> >
    ## /_______  / \_/  \___  >___|  /__|   |_______ \____/ \____/|   __/
    ##         \/           \/     \/               \/            |__|


    # IMPORTANT : Run one FWLite instance per file. Otherwise,
    # FWLite aggregates ALL of the information immediately, which
    # can take a long time to parse.
    #################################################################################
    def processEvent(iev, event):

        genOut = "Event %d\n" % (iev)
        #print "GGGEEENNNNOUT...."
        #print genOut

        #event.getByLabel(triggerBitLabel, triggerBits)
        #event.getByLabel(metfiltBitLabel, metfiltBits)
        runnumber = event.eventAuxiliary().run()

        if options.verbose:
            print "\nProcessing %d: run %6d, lumi %4d, event %12d" % \
                  (iev,event.eventAuxiliary().run(), \
                  event.eventAuxiliary().luminosityBlock(), \
                  event.eventAuxiliary().event())

        ###############################################################
        # Triggers
        ###############################################################
        event.getByLabel(triggerBitLabel, triggerBits)

        trigger_names = event.object().triggerNames(triggerBits.product())

        # Get list of triggers that fired
        #firedTrigs = []
        ntrig_muon[0] = len(muon_triggers_of_interest)
        ntrig_electron[0] = len(electron_triggers_of_interest)
        ntrig_dilepmue[0] = len(dilepmue_triggers_of_interest)
        ntrig_dilepemu[0] = len(dilepemu_triggers_of_interest)
        ntrig_dilepmumu[0] = len(dilepmumu_triggers_of_interest)
        ntrig_dilepee[0] = len(dilepee_triggers_of_interest)


        #print("------- Triggers ---------")
        # Zero out the triggers
        for toi in triggers_of_interest:

            trigger_type = toi[0]
            trigger_bit_names = toi[1]

            for iname,name in enumerate(trigger_bit_names):
                trigger_tree_branches[trigger_type][iname] = 0 # Didn't fire!

        FLAG_passed_trigger = False
        for itrig in xrange(triggerBits.product().size()):

            if triggerBits.product().accept(itrig):
                trigname = trigger_names.triggerName(itrig)

                mc_selection = True

                for toi in triggers_of_interest:

                    trigger_type = toi[0]
                    trigger_bit_names = toi[1]

                    for iname,name in enumerate(trigger_bit_names):

                        if options.isMC:
                            mc_selection = trigname.find(name[1]) # This is the version


                        if trigname.find(name[0]) >= 0 and mc_selection:
                            #print(trigname,trigger_type)
                            #print(iname,trigger_tree_branches[trigger_type])
                            #print(iname,trigger_tree_branches[trigger_type].Name())
                            trigger_tree_branches[trigger_type][iname] = 1 # Fired!
                            if trigger_type == options.trigType:
                                FLAG_passed_trigger = True
                                #print("PASSED TRIGGER REQUIREMENT!")
                        #else:
                            #trigger_tree_branches[trigger_type][iname] = 0 # Didn't fire!

                    #firedTrigs.append( itrig )

        #print("PASSED!!!!!!!!!!!!!! --------------")
        # THIS SHOULD ONLY WRITE EVENTS THAT PASSED THE TRIGGER
        if not FLAG_passed_trigger:
            #print("NOT PASSING!")
            return -1

        ##      ____.       __      _________      .__                 __  .__
        ##     |    | _____/  |_   /   _____/ ____ |  |   ____   _____/  |_|__| ____   ____

        ##     |    |/ __ \   __\  \_____  \_/ __ \|  | _/ __ \_/ ___\   __\  |/  _ \ /    \
        ## /\__|    \  ___/|  |    /        \  ___/|  |_\  ___/\  \___|  | |  (  <_> )   |  \
        ## \________|\___  >__|   /_______  /\___  >____/\___  >\___  >__| |__|\____/|___|  /
        ##               \/               \/     \/          \/     \/                    \/

        #
        # In addition, we must perform "lepton-jet" cleaning.
        # This is because the PF leptons are actually counted in the
        # list of particles sent to the jet clustering.
        # Therefore, we need to loop over the jet constituents and
        # remove the lepton.

        # use getByLabel, just like in cmsRun
        event.getByLabel (jetLabel, jets)          # For b-tagging

        # loop over jets and fill hists
        ijet = 0

        # These will hold all of the jets we need for the selection
        ak4JetsGood = []
        ak4JetsGoodP4 = []
        ak4JetsGoodSysts = []

        # For selecting leptons, look at 2-d cut of dRMin, ptRel of
        # lepton and nearest jet that has pt > 30 GeV
        dRMin = 9999.0
        inearestJet = -1    # Index of nearest jet
        nearestJet = None   # Nearest jet


        ############################################
        # Get the AK4 jet nearest the lepton:
        ############################################
        njets2write = 0
        for i,jet in enumerate(jets.product()):
            # Get the jet p4
            jetP4Raw = ROOT.TLorentzVector( jet.px(), jet.py(), jet.pz(), jet.energy() )
            # Get the correction that was applied at RECO level for MINIADO
            jetJECFromMiniAOD = jet.jecFactor(0)
            # Remove the old JEC's to get raw energy
            jetP4Raw *= jetJECFromMiniAOD
            # Apply jet ID
            nhf = jet.neutralHadronEnergy() / jetP4Raw.E()
            nef = jet.neutralEmEnergy() / jetP4Raw.E()
            chf = jet.chargedHadronEnergy() / jetP4Raw.E()
            cef = jet.chargedEmEnergy() / jetP4Raw.E()
            nconstituents = jet.numberOfDaughters()
            nch = jet.chargedMultiplicity()

            # Is this the b-jet tagging?
            #print("B-tagging...: %f " % (jet.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")))
            goodJet = \
              nhf < 0.99 and \
              nef < 0.99 and \
              chf > 0.00 and \
              cef < 0.99 and \
              nconstituents > 1 and \
              nch > 0

            if goodJet:
                if njets2write<16:
                    i = njets2write
                    jetpt[i] = jet.pt()
                    jeteta[i] = jet.eta()
                    jetphi[i] = jet.phi()
                    jete[i] = jet.energy()
                    jetpx[i] = jet.px()
                    jetpy[i] = jet.py()
                    jetpz[i] = jet.pz()
                    jetbtag[i] = jet.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags")
                    # Do the loose flag.
                    jetNHF[i] = jet.neutralHadronEnergyFraction();
                    jetNEMF[i] = jet.neutralEmEnergyFraction();
                    jetCHF[i] = jet.chargedHadronEnergyFraction();
                    jetMUF[i] = jet.muonEnergyFraction();
                    jetCEMF[i] = jet.chargedEmEnergyFraction();
                    jetNumConst[i] = jet.chargedMultiplicity()+jet.neutralMultiplicity();
                    jetNumNeutralParticles[i] =jet.neutralMultiplicity();
                    jetCHM[i] = jet.chargedMultiplicity(); 

                    njets2write += 1



            if not goodJet:
                if options.verbose:
                    print ('bad jet pt = {0:6.2f}, y = {1:6.2f}, phi = {2:6.2f}, m = {3:6.2f}, bdisc = {4:6.2f}'.format (
                        jetP4Raw.Perp(), jetP4Raw.Rapidity(), jetP4Raw.Phi(), jetP4Raw.M(), jet.bDiscriminator( options.bdisc )
                        ))
                continue



            if options.verbose:
                print ('raw jet pt = {0:6.2f}, y = {1:6.2f}, phi = {2:6.2f}, m = {3:6.2f}, bdisc = {4:6.2f}'.format (
                    jetP4Raw.Perp(), jetP4Raw.Rapidity(), jetP4Raw.Phi(), jetP4Raw.M(), jet.bDiscriminator( options.bdisc )
                    ))


            # Remove the lepton from the list of constituents for lepton/jet cleaning
            # Speed up computation, only do this for DR < 0.6


        # OUR STUFF
        njet[0] = njets2write


        ########### MUONS ##################
        event.getByLabel( muonLabel, muons )
        nmuons2write = 0
        if len(muons.product()) > 0:
            for i,muon in enumerate( muons.product() ):
                #if muon.pt() > options.minMuonPt and abs(muon.eta()) < options.maxMuonEta and muon.isMediumMuon():
                if i<16: # This is because we are only storing 16 muons at a time
                   muonpt[i] = muon.pt()
                   muoneta[i] = muon.eta()
                   muonphi[i] = muon.phi()
                   muone[i] = muon.energy()
                   muonq[i] = muon.charge()
                   muonpx[i] = muon.px()
                   muonpy[i] = muon.py()
                   muonpz[i] = muon.pz()
                   #pfi  = muon.pfIsolationR03()
                   pfi  = muon.pfIsolationR04()
                   #print( pfi.sumChargedHadronPt, pfi.sumChargedParticlePt, pfi.sumNeutralHadronEt, pfi.sumPhotonEt, pfi.sumNeutralHadronEtHighThreshold, pfi.sumPhotonEtHighThreshold, pfi.sumPUPt)
                   muonsumchhadpt[i] = pfi.sumChargedHadronPt
                   muonsumnhadpt[i] = pfi.sumNeutralHadronEt
                   muonsumphotEt[i] = pfi.sumPhotonEt
                   muonsumPUPt[i] = pfi.sumPUPt
                   muonisLoose[i] = int(muon.isLooseMuon())
                   muonisMedium[i] = int(muon.isMediumMuon())

                   #(mu->pfIsolationR04().sumChargedHadronPt + max(0., mu->pfIsolationR04().sumNeutralHadronEt + mu->pfIsolationR04().sumPhotonEt - 0.5*mu->pfIsolationR04().sumPUPt))/mu->pt()

                   muonPFiso[i] = (muonsumchhadpt[i] + max(0., muonsumnhadpt[i] + muonsumphotEt[i] - 0.5*muonsumPUPt[i]))/muonpt[i]
                   nmuons2write += 1


        nmuon[0] = nmuons2write



        ##############################################################
        # Electrons
        ##############################################################
        #selectElectron = VIDElectronSelector(cutBasedElectronID_Summer16_80X_V1_loose)
        # Do we need this? Got this from...
        # https://github.com/ikrav/EgammaWork/blob/ntupler_and_VID_demos_7.4.12/FWLiteExamples/bin/FWLiteVIDElectronsDemo_cfg.py
        event.getByLabel( electronLabel, electrons )

        # Referencing
        # https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2
        # https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2#Working_points_for_2016_data_for
        # For when we look at 2017
        # https://twiki.cern.ch/twiki/bin/view/CMS/Egamma2017DataRecommendations
        #
        # Also look here
        # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCMSDataAnalysisSchoolLPC2018egamma
        # https://indico.cern.ch/event/662371/contributions/2704697/attachments/1514547/2496142/ShortExercise1.pdf
        # https://indico.cern.ch/event/662371/contributions/2704714/attachments/1514558/2496227/ShortExercise2.pdf
        # Do something like this for isolation?
        # https://twiki.cern.ch/twiki/bin/view/CMS/EgammaPFBasedIsolationRun2#Recipe_for_accessing_PF_isolatio




        ########### ELECTRONS ##################
        event.getByLabel( electronLabel, electrons )
        nelectrons2write = 0
        if len(electrons.product()) > 0:
            for i,electron in enumerate( electrons.product() ):


                #print("Here! ----  A")
                passSelection = selectElectron( electron, event )
                #print(passSelection,type(passSelection))
                #print("Here! ----  B")
                if passSelection and i<16: # we're only keeping 16 electrons
                   electronpt[i] = electron.pt()
                   electroneta[i] = electron.eta()
                   electronphi[i] = electron.phi()
                   electrone[i] = electron.energy()
                   electronq[i] = electron.charge()
                   electronpx[i] = electron.px()
                   electronpy[i] = electron.py()
                   electronpz[i] = electron.pz()
                   electronTkIso[i] = electron.dr03TkSumPt()
                   electronHCIso[i] = electron.dr03HcalTowerSumEt()
                   electronECIso[i] = electron.dr03EcalRecHitSumEt()

                   nelectrons2write += 1


        nelectron[0] = nelectrons2write

        #######################################################################
        # MET, Missing energy in transverse plane
        # https://indico.cern.ch/event/662371/contributions/2823187/attachments/1574267/2496977/PileupMET_DAS2018LPC.pdf
        # https://indico.cern.ch/event/662371/timetable/
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideCMSDataAnalysisSchoolLPC2018METandPileupExercise
        # SHOULD GO THROUGH THE EXERCISE! DO WE CORRECT? OR USE PUPPI????
        #######################################################################
        event.getByLabel( metLabel, mets )
        #met = mets.product()[0]
        met = mets.product().front()
        metpt[0] = met.pt()
        metphi[0] = met.phi()
        mete[0] = met.energy()
        meteta[0] = met.eta()
        #print("MET pt/phi: %f %f" % (metpt[0],metphi[0]))


        ## ___________.__.__  .__    ___________
        ## \_   _____/|__|  | |  |   \__    ___/______   ____   ____
        ##  |    __)  |  |  | |  |     |    |  \_  __ \_/ __ \_/ __ \
        ##  |     \   |  |  |_|  |__   |    |   |  | \/\  ___/\  ___/
        ##  \___  /   |__|____/____/   |____|   |__|    \___  >\___  >
        ##      \/                                          \/     \/
        outtree.Fill()

        return genOut



    #########################################
    # Main event loop

    #genoutputfile = open("generator_information.dat",'w')
    nevents = 0
    maxevents = int(options.maxevents)
    for ifile in getInputFiles(options):
        print ('Processing file ' + ifile)
        events = Events (ifile)
        if maxevents > 0 and nevents > maxevents:
            break

        # loop over events in this file
        for iev, event in enumerate(events):

            if maxevents > 0 and nevents > maxevents:
                break
            nevents += 1

            #if nevents % 1000 == 0:
            if nevents % 100 == 0:
                print ('===============================================')
                print ('    ---> Event ' + str(nevents))
            elif options.verbose:
                print ('    ---> Event ' + str(nevents))

            genOut = processEvent(iev, events)
            #print type(genOut)
            #print genOut
            #if genOut is not None:
                #genoutputfile.write(genOut)

    # Close the output ROOT file
    f.cd()
    f.Write()
    f.Close()

    #genoutputfile.close()
    


#####################################################################################
if __name__ == "__main__":
    topbnv_fwlite(sys.argv)



