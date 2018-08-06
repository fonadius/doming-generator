#!/usr/bin/python3
import mrcfile as mrc
import numpy as np
from scipy import misc
import sys

if __name__ == "__main__":
    path = sys.argv[1]
    if not path.endswith(".mrc"):
        raise ValueError("Not mrc file")
    newPath = path[:-4] + ".png"

    f = mrc.open(path)
    misc.imsave(newPath, f.data[0])
