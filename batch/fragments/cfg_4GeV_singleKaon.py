#!/bin/python3
import os
import json

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("v12")

import LDMX.Ecal.EcalGeometry
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
p.libraries.append("libSimCore.so")


### Particle Gun
# all kaon names: kaon+, kaon-, kaon0, kaon0L, kaon0S,
myGun = generators.gun('myGun')
myGun.particle = 'kaon0S'
myGun.position = [ 0., 0., -1.2 ]  # mm
myGun.direction = [ 0., 0., 1] 
myGun.energy = 4.0 # GeV

sim = simulator.simulator("SingleKaon")
sim.setDetector( 'ldmx-det-v12' , True )
sim.runNumber = 0
sim.description = "Single kaon gun"
sim.beamSpotSmear = [20., 80., 0.] #mm
sim.generators.append(myGun)

p.sequence=[ sim ]

### Configurable parameters
nEvents=10000
seed=0
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

