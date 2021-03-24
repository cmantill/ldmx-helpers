#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
from LDMX.Biasing import target
from LDMX.Biasing import particle_filter
from LDMX.SimCore import bias_operators
from LDMX.Biasing import include as includeBiasing
from LDMX.Biasing import filters
from LDMX.Biasing import util

p.libraries.append("libSimCore.so")

from LDMX.Ecal import EcalGeometry
geom = EcalGeometry.EcalGeometryProvider.getInstance()
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Hcal import HcalGeometry
geom = HcalGeometry.HcalGeometryProvider.getInstance()

from LDMX.Ecal import digi as ecal_digi
from LDMX.Hcal import digi as hcal_digi

kaon_filter = particle_filter.PhotoNuclearProductsFilter("kaons_filter")
kaon_filter.pdg_ids = [130, # K_L^0
                       310, # K_S^0
                       311, # K^-
                       321  # K^+   
]

sim = simulator.simulator("target_photonNuclear")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "ECal photo-nuclear, xsec bias 1.1e9"
sim.beamSpotSmear = [20., 80., 0.]
sim.generators.append(generators.single_4gev_e_upstream_tagger())

sim.biasing_operators = [ bias_operators.PhotoNuclear('target',1.1e9,2500.,only_children_of_primary=True) ]
includeBiasing.library()
sim.actions.extend([
     filters.TaggerVetoFilter(),
     filters.TargetBremFilter(),
     filters.TargetPNFilter(),   
     util.TrackProcessFilter.photo_nuclear(),
     kaon_filter,
    ])

p.sequence=[ sim,
             ecal_digi.EcalDigiProducer(),
             ecal_digi.EcalRecProducer(),
             hcal_digi.HcalDigiProducer(),
             hcal_digi.HcalRecProducer(),
             ]

### Configurable parameters
# 100k for 327 events in 4 minutes
# 1M for 3233 in 26 minutes
nEvents=100*1000
seed=1
outfile='out.root'
env = os.environ
if 'BATCH_SEEDOFFSET' in env: seed += int(env['BATCH_SEEDOFFSET'])
if 'LSB_JOBINDEX' in env: seed += int(env['LSB_JOBINDEX'])
if 'BATCH_NEVENTS' in env: nEvents = int(env['BATCH_NEVENTS'])
if 'BATCH_OUTFILE' in env: outfile = env['BATCH_OUTFILE']

print('Setting random seed to:', seed)
print('Processing #events:', nEvents)
print('Writing output file to:', outfile)

p.run = seed
sim.randomSeeds = [ 2*p.run , 2*p.run+1 ]
p.outputFiles=[outfile]
p.maxEvents = nEvents

with open('parameterDump.json', 'w') as out_pamfile:
     json.dump(p.parameterDump(),  out_pamfile, indent=4)

