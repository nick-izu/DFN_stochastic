import os, sys
from time import time
from pydfnworks import * 
import subprocess
import numpy as np

define_paths()
main_time = time()
DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()

# Getting the seed from the input file to set the 
# numpy seed for the semi-correlated transmissivity relationship later
infile = DFN.local_dfnGen_file
seed = [ int(l.split(':')[-1].split('/')[0].strip()) 
    for l in list(open(infile)) if 'seed' in l and not l.startswith('//') ][0]

DFN.create_network()
#DFN.mesh_network() # uncomment to get the visualization of the fractures.
#DFN.output_report() # uncomment to dump diagnostic plots about dfn, e.g. frac. size dist.

"""
Correlated model for T
"""
# Assign hydraulic properties by family, which depends on layer
# Parameter dictionaries for the correlated transmissivity model
variable = "transmissivity"
function = "correlated"
# First dict is for the user-defined fractures.
# The rest are defined by the 9 families making 
# up the 3 depth zones.
T_models = [ 
    # Non-standard fracture families:
    #   User-defined ellipses = 0
    #   User-defined rectangles = -1
    #   
    # Otherwise the fracture families are in the order they 
    # are defined in the input deck. (1 will be the fracture 
    # family associated with the first set of properties specified
    # in the input deck, etc)
    ( 0,"correlated", {"alpha":2.2e-9, "beta":0.7} ), # POSIVA WR-2012-42 CHUW EW dz3
    ( 1, "correlated", {"alpha":8.0e-9, "beta":0.8} ),
    ( 2, "correlated", {"alpha":1.5e-8, "beta":0.8} ),
    ( 3, "correlated", {"alpha":1.2e-8, "beta":0.8} ),
    ( 4, "correlated", {"alpha":2.2e-9, "beta":0.7} ),
    ( 5, "correlated", {"alpha":6.0e-9, "beta":0.6} ),
    ( 6, "correlated", {"alpha":2.0e-9, "beta":1.2} ),
    ( 7, "correlated", {"alpha":7.0e-11, "beta":0.7} ),
    ( 8, "correlated", {"alpha":8.0e-11, "beta":0.9} ),
    ( 9, "correlated", {"alpha":6.0e-11, "beta":1.0} )
    ]

"""
Semi-correlated model for T
"""
#function = "semi-correlated"
## First dict is for the user-defined fractures.
## We want these to be deterministic since they
## are supposed to be observed and fixed. Middle DZ properties
## are used for the user-defined faults.
## The rest are defined by the 9 families making 
## up the 3 depth zones.
#T_models = [
#   ( -1, "correlated", {"alpha":1.6*10**(-9), "beta":0.8} ),
#   ( 1, "semi-correlated", {"alpha":6.3*10**(-9), "beta":1.3, "sigma": 1.0} ),
#   ( 2, "semi-correlated", {"alpha":6.3*10**(-9), "beta":1.3, "sigma": 1.0} ),
#   ( 3, "semi-correlated", {"alpha":6.3*10**(-9), "beta":1.3, "sigma": 1.0} ),
#   ( 4, "semi-correlated", {"alpha":1.3*10**(-9), "beta":0.5, "sigma": 1.0} ),
#   ( 5, "semi-correlated", {"alpha":1.3*10**(-9), "beta":0.5, "sigma": 1.0} ),
#   ( 6, "semi-correlated", {"alpha":1.3*10**(-9), "beta":0.5, "sigma": 1.0} ),
#   ( 7, "semi-correlated", {"alpha":5.3*10**(-11), "beta":0.5, "sigma": 1.0} ),
#   ( 8, "semi-correlated", {"alpha":5.3*10**(-11), "beta":0.5, "sigma": 1.0} ),
#   ( 9, "semi-correlated", {"alpha":5.3*10**(-11), "beta":0.5, "sigma": 1.0} )
#    ]
## Setting numpy seed to the one used for dfn generation 
## so we have reproducibility in transmissivity too
#np.random.seed(seed)

""" 
Computing the hydraulic properties
"""

b_list = [] 
perm_list = []
T_list = []

# Computing the transmissivity for each of the fracture
# families
for (family_id, function_type, param_dict) in T_models:
  b, perm, T = DFN.generate_hydraulic_values(
      variable, function_type, param_dict, family_id=family_id )
  b_list.append(b)
  perm_list.append(perm)
  T_list.append(T)

b = np.sum(b_list, axis=0)
perm = np.sum(perm_list, axis=0)
T = np.sum(T_list, axis=0)
DFN.dump_hydraulic_values( b, perm, T )

main_elapsed = time() - main_time
timing = 'Time Required: %0.2f Minutes'%(main_elapsed/60.0)
f = open("time.txt",'w')
f.write("{0}\n".format(main_elapsed))
f.close()
print("*"*80)
print(DFN.jobname+' complete')
print("Thank you for using dfnWorks")
print("*"*80)
