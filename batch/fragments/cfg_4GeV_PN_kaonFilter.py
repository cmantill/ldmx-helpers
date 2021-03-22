#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
from LDMX.Biasing import target
from LDMX.Biasing import particle_filter
p.libraries.append("libSimCore.so")

kaon_filter = particle_filter.PhotoNuclearProductsFilter()
kaon_filter.pdg_ids = [130, # K_L^0
                       310, # K_S^0
                       ]

targ_pn = target.photo_nuclear('ldmx-det-v12', generators.single_4gev_e_upstream_tagger())
targ_pn.actions.extend([kaon_filter])
sim = targ_pn

p.sequence=[ sim ]

### Configurable parameters
 # 1M for 20 events in 10 minutes
nEvents=10# 1000*1000
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

