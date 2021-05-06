
import argparse
parser = argparse.ArgumentParser(description='')

parser.add_argument('--run_number',type=int,default=1,help='ID number for this run.')
parser.add_argument('--batch_job' ,type=int,default=1, help='Batch ID Number in the bsub system.')

args = parser.parse_args() 

from LDMX.Framework import ldmxcfg

p=ldmxcfg.Process("sim")
p.run = args.run_number
p.maxEvents = 1000*1000 #  0.1M

from LDMX.SimCore import simulator
from LDMX.SimCore import generators
from LDMX.Biasing import target
from LDMX.Biasing import particle_filter
from LDMX.SimCore import bias_operators
from LDMX.Biasing import include as includeBiasing
from LDMX.Biasing import filters
from LDMX.Biasing import util
from LDMX.SimCore import examples

p.libraries.append("libSimCore.so")

from LDMX.Ecal import EcalGeometry
geom = EcalGeometry.EcalGeometryProvider.getInstance()
import LDMX.Ecal.ecal_hardcoded_conditions

from LDMX.Hcal import HcalGeometry
geom = HcalGeometry.HcalGeometryProvider.getInstance()
import LDMX.Hcal.hcal_hardcoded_conditions

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

p.outputFiles = [ 'pn_kaonfilter_1M_events_r%04d_b%d.root'%(p.run,args.batch_job) ]
