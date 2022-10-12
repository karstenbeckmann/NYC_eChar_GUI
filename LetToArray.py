import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import Agilent as ag 

import numpy as np



def createLetterArray(l,n,m):

    ar = np.zeros((n,m))

    if l == "A":

        ar[1,1] = 1
        ar[1,2] = 1
        ar[1,3] = 1
        ar[1,4] = 1
        ar[1,5] = 1
        ar[1,6] = 1

        ar[2,1] = 1
        ar[2,2] = 1
        ar[2,5] = 1
        ar[2,6] = 1
        
        ar[3,1] = 1
        ar[3,2] = 1
        ar[3,5] = 1
        ar[3,6] = 1
        
        ar[4,1] = 1
        ar[4,2] = 1
        ar[4,3] = 1
        ar[4,4] = 1
        ar[4,5] = 1
        ar[4,6] = 1
        
        ar[5,1] = 1
        ar[5,2] = 1
        ar[5,5] = 1
        ar[5,6] = 1
        
        ar[6,1] = 1
        ar[6,2] = 1
        ar[6,5] = 1
        ar[6,6] = 1

        ar[7,1] = 1
        ar[7,2] = 1
        ar[7,5] = 1
        ar[7,6] = 1

    elif "B" == l:

        ar[1,1] = 1
        ar[1,2] = 1
        ar[1,3] = 1
        ar[1,4] = 1
        ar[1,5] = 1

        ar[2,1] = 1
        ar[2,2] = 1
        ar[2,5] = 1
        ar[2,6] = 1
        
        ar[3,1] = 1
        ar[3,2] = 1
        ar[3,5] = 1
        ar[3,6] = 1
        
        ar[4,1] = 1
        ar[4,2] = 1
        ar[4,3] = 1
        ar[4,4] = 1
        ar[4,5] = 1
        
        ar[5,1] = 1
        ar[5,2] = 1
        ar[5,5] = 1
        ar[5,6] = 1
        
        ar[6,1] = 1
        ar[6,2] = 1
        ar[6,5] = 1
        ar[6,6] = 1

        ar[7,1] = 1
        ar[7,2] = 1
        ar[7,3] = 1
        ar[7,4] = 1
        ar[7,5] = 1

    elif l == "F":

        ar[1,1] = 1
        ar[1,2] = 1
        ar[1,3] = 1
        ar[1,4] = 1
        ar[1,5] = 1
        ar[1,6] = 1

        ar[2,1] = 1
        ar[2,2] = 1
        ar[2,3] = 1
        ar[2,4] = 1
        ar[2,5] = 1
        ar[2,6] = 1
        
        ar[3,1] = 1
        ar[3,2] = 1
        
        ar[4,1] = 1
        ar[4,2] = 1
        ar[4,3] = 1
        ar[4,4] = 1
        ar[4,5] = 1
        
        ar[5,1] = 1
        ar[5,2] = 1
        ar[5,3] = 1
        ar[5,4] = 1
        ar[5,5] = 1
        
        ar[6,1] = 1
        ar[6,2] = 1

        ar[7,1] = 1
        ar[7,2] = 1

    elif "R" == l:

        ar[1,1] = 1
        ar[1,2] = 1
        ar[1,3] = 1
        ar[1,4] = 1
        ar[1,5] = 1

        ar[2,1] = 1
        ar[2,2] = 1
        ar[2,5] = 1
        ar[2,6] = 1
        
        ar[3,1] = 1
        ar[3,2] = 1
        ar[3,5] = 1
        ar[3,6] = 1
        
        ar[4,1] = 1
        ar[4,2] = 1
        ar[4,3] = 1
        ar[4,4] = 1
        ar[4,5] = 1
        
        ar[5,1] = 1
        ar[5,2] = 1
        ar[5,4] = 1
        ar[5,5] = 1
        ar[5,6] = 1
        
        ar[6,1] = 1
        ar[6,2] = 1
        ar[6,5] = 1
        ar[6,6] = 1

        ar[7,1] = 1
        ar[7,2] = 1
        ar[7,5] = 1
        ar[7,6] = 1

    elif "L" == l:

        ar[1,1] = 1
        ar[1,2] = 1

        ar[2,1] = 1
        ar[2,2] = 1
        
        ar[3,1] = 1
        ar[3,2] = 1
        
        ar[4,1] = 1
        ar[4,2] = 1
        
        ar[5,1] = 1
        ar[5,2] = 1
        
        ar[6,1] = 1
        ar[6,2] = 1
        ar[6,3] = 1
        ar[6,4] = 1
        ar[6,5] = 1

        ar[7,1] = 1
        ar[7,2] = 1
        ar[7,3] = 1
        ar[7,4] = 1
        ar[7,5] = 1

    return ar
