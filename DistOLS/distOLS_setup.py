import warnings as w
# These warnings are caused by numpy updates and should not be
# output.
w.simplefilter(action = 'ignore', category = FutureWarning)
import numpy as np
import subprocess
import warnings
import resource
import nibabel as nib
import sys
import os
import shutil
from DistOLS import distOLS_defaults
import yaml

def main(*args):

    print('active')
    print(len(args))

    # Change to distOLS directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # If X and Y weren't given we look in defaults for all arguments.
    if len(args)<2:

        inputs = distOLS_defaults.main()

        print(os.getcwd())

        print(repr(inputs))
        with open('distOLS_defaults.yml', 'r') as stream:
            print(repr(yaml.load(stream)))

        MAXMEM = inputs[0]

        with open(inputs[1]) as a:

            Y_files = []
            i = 0
            for line in a.readlines():

                Y_files.append(line.replace('\n', ''))

        X = np.loadtxt(inputs[2], delimiter=',') 

        SVFlag = inputs[3]

    # else Y_files is the first input and X is the second.
    elif len(args)==2:

        Y_files = args[0]
        X = args[1]

        inputs = distOLS_defaults.main()
        MAXMEM = inputs[0]
        SVFlag = inputs[3]

    # And MAXMEM may be the third input
    else:

        Y_files = args[0]
        X = args[1]
        MAXMEM = args[2]        

        inputs = distOLS_defaults.main()
        SVFlag = inputs[3]

    # Load in one nifti to check NIFTI size
    try:
        Y0 = nib.load(Y_files[0])
    except Exception as error:
        raise ValueError('The NIFTI "' + Y_files[0] + '"does not exist')

    d0 = Y0.get_data()
    Y0aff = Y0.affine

    # Get the maximum memory a NIFTI could take in storage. 
    NIFTIsize = sys.getsizeof(np.zeros(d0.shape,dtype='uint64'))

    # Initial checks for NIFTI compatability.
    for Y_file in Y_files:

        try:
            Y = nib.load(Y_file)
        except Exception as error:
            raise ValueError('The NIFTI "' + Y_file + '"does not exist')

        d = Y.get_data()
        
        # Check NIFTI images have the same dimensions.
        if not np.array_equal(d.shape, d0.shape):
            raise ValueError('Input NIFTI "' + Y_file + '" has ' +
                             'different dimensions to "' +
                             Y_files[0] + '"')

        # Check NIFTI images are in the same space.
        if not np.array_equal(Y.affine, Y0aff):
            raise ValueError('Input NIFTI "' + Y_file + '" has a ' +
                             'different affine transformation to "' +
                             Y_files[0] + '"')

    # Similar to blksize in SwE, we divide by 8 times the size of a nifti
    # to work out how many blocks we use.
    blksize = np.floor(MAXMEM/8/NIFTIsize);

    # Make a temporary directory for batch inputs
    if os.path.isdir('binputs'):
        shutil.rmtree('binputs')
    os.mkdir('binputs')
    # Loop through blocks
    for i in range(0, len(Y_files), int(blksize)):

        # Lower and upper block lengths
        blk_l = i
        blk_u = min(i+int(blksize), len(Y_files))
        index = int(i/int(blksize) + 1)
        
        with open(os.path.join("binputs","Y" + str(index) + ".txt"), "w") as a:

            # List all y for this batch in a file
            for f in Y_files[blk_l:blk_u]:
                a.write(str(f) + os.linesep) 

        np.savetxt(os.path.join("binputs","X" + str(index) + ".csv"), 
                   X[blk_l:blk_u], delimiter=",") 
    
    w.resetwarnings()

if __name__ == "__main__":
    main()
