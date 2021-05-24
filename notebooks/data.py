import uproot
import awkward as ak
import os
import psutil

SPHit_attrs= ['x', 'y', 'z', 'px', 'py', 'pz', 'e', 'id', 'pdgID', 'trackID']
EcalRecHit_attrs = ['amp','e','t','x','y','z','isNoise']
EcalSimHit_attrs = ['edep','e','t','x','y','z','layer']
HcalRecHit_attrs = ['amp','e','x','y','z','pe','section','layer','strip','isNoise']
HcalSimHit_attrs = ['edep','e','x','y','z','layer','section','strip']
Target_attrs = ['e','pt']
TargetKaon_attrs = ['px','py','pz','e','pt','pdgID','electron_e','decay']
TargetKaondau_attrs = ['e','px','py','pz','pdgID','mompdgID','electrone','mome','momdecay']
SimKaon_attrs = ['pdgID','trkID','px','py','pz','e','mass','ndau','vx','vy','vz','decay']
SimKaon_dau_attrs = ['pdgID','momtrkID','px','py','pz','e']

branches = {
    "Proc": ['id'],
    "Sim_Kaon": SimKaon_attrs,
    "Sim_Kaon_dau": SimKaon_dau_attrs,
    "Target_Electron": Target_attrs,
    "Target_Photon": Target_attrs,
    "Target_Kaon": TargetKaon_attrs,
    "Target_Kaon_dau1": TargetKaondau_attrs,
    "Target_Kaon_dau2": TargetKaondau_attrs,
    "Target_Kaon_dau3": TargetKaondau_attrs,
    "TargetSPHit": SPHit_attrs,
    #"ECalSPHit": SPHit_attrs,
    #"ECalRecHit": EcalRecHit_attrs,
    #"ECalSimHit": EcalSimHit_attrs,
    #"HCalRecHit": HcalRecHit_attrs,
    #"HCalSimHit": HcalSimHit_attrs,
}

def getData(fnames="", treeName="Events", chunks=False):
    branchlist = []
    for collection, attrs in branches.items():
        branchlist += [collection+"_"+attr for attr in attrs]
    if chunks: ldmx_dict = uproot.iterate(fnames+":"+treeName, branchlist)
    else: ldmx_dict = uproot.lazy(fnames+":"+treeName, branchlist)
    return ldmx_dict

def repackage(ldmx_dict):
    evt_dict={}
    for collection in branches:    
        coll_dict={}
        for attr in branches[collection]:
            bname = "{}_{}".format(collection, attr)
            coll_dict[attr] = ldmx_dict[bname]
        evt_dict[collection] = ak.zip(coll_dict)        
    ldmx_events = ak.zip(evt_dict, depth_limit=1)
    return ldmx_events
