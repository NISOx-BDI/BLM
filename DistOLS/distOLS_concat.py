import numpy as np
import subprocess
import warnings
import resource
import nibabel as nib
import sys
import os
import glob
import shutil

def main():

    # Change to distOLS directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Work out which files we need.
    XtX_files = glob.glob("XtX*")
    XtY_files = glob.glob("XtY*")

    # Read the matrices from the first batch.
    sumXtX = np.loadtxt(os.path.join("binputs","XtX1.csv"), 
                        delimiter=",")
    sumXtY = np.loadtxt(os.path.join("binputs","XtY1.csv"), 
                        delimiter=",")

    # Cycle through batches and add together results.
    for batchNo in range(2,(len(XtX_files)+1)):

        # Sum the batches.
        sumXtX = sumXtX + np.loadtxt(
            os.path.join("binputs","XtX" + str(batchNo) + ".csv"), 
                         delimiter=",")

        sumXtY = sumXtY + np.loadtxt(
            os.path.join("binputs","XtY" + str(batchNo) + ".csv"), 
                         delimiter=",")

    # Dimension bug handling
    if np.ndim(sumXtX) == 0:
        sumXtX = np.array([[sumXtX]])
    elif np.ndim(sumXtX) == 1:
        sumXtX = np.array([sumXtX])

    if np.ndim(sumXtY) == 0:
        sumXtY = np.array([[sumXtY]])
    elif np.ndim(sumXtY) == 1:
        sumXtY = np.array([sumXtY])

    # np linalg inverse doesn't handle dim=[1,1]
    if np.ndim(sumXtX) == 1:
        isumXtX = 1/sumXtX
    else:
        isumXtX = np.linalg.inv(sumXtX)

    # Read in the nifti size.
    NIFTIsize = np.loadtxt(os.path.join("binputs","NIFTIsize.csv"), 
                        delimiter=",")

    beta = np.dot(isumXtX, sumXtY)

    # Cycle through betas and output results.
    for i in range(0,beta.shape[0]):

        betai = beta[i,:].reshape(int(NIFTIsize[0]),
                                  int(NIFTIsize[1]),
                                  int(NIFTIsize[2]))

        # tmp code to output nifti
        nifti = nib.load('/well/nichols/users/kfh142/data/IMAGEN/spmstatsintra/000070830069/SessionB/EPI_short_MID/swea/con_0010.nii')

        betaimap = nib.Nifti1Image(betai,
                                   nifti.affine,
                                   header=nifti.header)
        nib.save(betaimap, 'beta' + str(i) + '.nii')


if __name__ == "__main__":
    main()
