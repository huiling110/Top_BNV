# Following instructions here
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookCRAB3Tutorial

from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

#dataset = ["DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8",
datasets = ['/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM',
            '/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v2/MINIAODSIM',
            '/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM',
]


dataset = datasets[0]

request_name = "bellis_topbnv_%s" % (dataset[1:20])

#config.General.requestName = 'bellis_topbnv_TT_TUNE'
#config.General.requestName = 'bellis_topbnv_RSGluonToTT'
config.General.requestName = request_name
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'

config.Data.inputDataset = dataset
#config.Data.inputDataset = '/RSGluonToTT_M-3000_TuneCUETP8M1_13TeV-pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM'
#config.Data.inputDataset = '/GenericTTbar/HC-CMSSW_5_3_1_START53_V5-v1/GEN-SIM-RECO'
#config.Data.inputDataset = '/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'
#config.Data.inputDataset = '/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'

config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1

config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())

# This selecting some of the data
config.Data.publication = False

config.Site.storageSite = 'T3_US_FNALLPC'

config.JobType.scriptExe = 'execute_for_crab.sh'

config.JobType.outputFiles = ['output.root']
config.JobType.sendExternalFolder = True

# We need that FrameworkJobReport.xml file for the output.
config.JobType.inputFiles = ['execute_for_crab.py', 'topbnv_fwlite.py', 'FrameworkJobReport.xml']

