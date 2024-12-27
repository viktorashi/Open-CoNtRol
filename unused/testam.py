import tellurium as te

import numpy as np
import matplotlib.pylab as plt

# Load a model and carry out a simulation generating 100 points
r = te.loada ('S1 -> S2; k1*S1; k1 = 0.1; S1 = 10')
r.draw(width=100,output_fileName = 'fileName.png')
