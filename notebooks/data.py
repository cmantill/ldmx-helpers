import uproot
import awkward as ak
import os
import psutil

# for Chloe's studies
SimParticle_attrs = ['pdgID','trkID','px','py','pz','e','mass','ndau','vx','vy','vz','decay']
SimParticle_dau_attrs = ['pdgID','z','px','py','pz','e','mompdgID','mome','momdecay']
SimPNParticle_attrs = ['pdgID','px','py','pz','e','mass','vx','vy','vz','electrone']
SimPNParticle_dau_attrs = ['pdgID','z','px','py','pz','e','mompdgID','mome','momdecay','electrone']

# for Lukas's studies
SimParticle_attrs = ['pdgID','trkID','mass','e','kine','px','py','pz','endx','endy','endz','vx','vy','vz']
EcalRecHit_attrs = ['amp','e','t','x','y','z']
EcalInfo_attrs = ['frontmaxSP_e','frontmaxSP_p','backmaxSP_e','backmaxSP_p']
HcalRecHit_attrs = ['layer','strip','section','e','x','y','z','PE']
HcalInfo_attrs = ['sumPE']
                    
branches = {
    #"Proc": ['id'],
    #"n": ['Sim_PNParticle'],
    #"Sim_PNParticle": SimPNParticle_attrs,
    #"Sim_PNParticle_dau1": SimPNParticle_dau_attrs,
    #"Sim_PNParticle_dau2": SimPNParticle_dau_attrs,
    "Sim_Particle": SimParticle_attrs,
    "Ecal_RecHit": EcalRecHit_attrs,
    "Hcal_RecHit": HcalRecHit_attrs,
    "Ecal": EcalInfo_attrs,
    "Hcal": HcalInfo_attrs,
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
