import uproot
import awkward as ak
import os
import psutil

Target_attrs = ['e','pt']
TargetKaon_attrs = ['px','py','pz','e','pt','pdgID','electron_e']
TSPKaondau_attrs = ['e','px','py','pz','pdgID','mompdgID','electrone','mome','gd']
SimKaon_attrs = ['pdgID','trkID','px','py','pz','e','mass','ndau','vx','vy','vz','decay']

branches = {
    "Proc": ['id'],
    "Sim_Kaon": SimKaon_attrs,
    "Target_Electron": Target_attrs,
    "Target_Photon": Target_attrs,
    "Target_Kaon": TargetKaon_attrs,
    "TSP_Kaon_dau1": TSPKaondau_attrs,
    "TSP_Kaon_dau2": TSPKaondau_attrs,
    "TSP_Kaon_dau3": TSPKaondau_attrs,
    "TSP_Kaon_dau4": TSPKaondau_attrs,

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
