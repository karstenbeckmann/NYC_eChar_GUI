"""
Written by: Karsten Beckmann and Maximillian Liehr
Institution: SUNY Polytechnic Institute
Date: 6/12/2018

For more information please use the Keysight E5260 remote control manual.
"""
import numpy as np 
import pyvisa as vs 
import datetime as dt 
import types as tp
import time as tm

#8 slot SMU mainframe: 
#8 Medium Power Source Measurement Units (MPSMUs) are isntalled (model #E5281A)
from E5274A import *
from B1500A import *
from B1530A import *
from PG1110A import *

#