import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from astropy import wcs
from astropy.wcs import WCS
from astropy.io import fits
import sys
import math
import os
import glob
import sys
from sortedcontainers import SortedDict
import datetime as dt
import imageio
import os
from PIL import Image
from matplotlib.colors import LogNorm
from astropy.nddata.utils import Cutout2D
from astropy import units as u

###################-------- Please Entre your Parametres FOR CANVIS subs ---------#######################

# -- Run in format month year eg june18 

run = 'june18'

# -- date of run 

run_date = '18060*'

# -- Path to the candidate list for the choosen run 

translist_path = '/fred/oz100/swebb/open_cands/transients_coo_DWFJun18_RT.txt'

# ---- Starting number and end number of candidates you want to run through canvis ----################

start_num = 1
end_num = 2

#objects = [36402, 37635, 48373, 36820, 36812, 43784, 38074, 36856, 37653, 7475, 8508, 7419, 8535, 19429, 8617]

###################-------- Definitions for SkyCoord unit converstions ---------#######################


def RAdec_to_RAsex(fRAdec):
    fratotsec = (math.fabs(float(fRAdec))*3600.0)
    frah2 = (math.modf(fratotsec/3600.0)[1])
    fram2 = (math.modf((fratotsec-(frah2*3600.0))/60.0)[1])
    fras2 = (fratotsec-(frah2*3600.0)-(fram2*60.0))
    if round(fras2, 2) == 60.00:
        fram2 = fram2 + 1
        fras2 = 0
        if round(fram2, 2) == 60.00:
            frah2 = frah2 + 1
            fram2 = 0
    if round(fram2, 2) == 60.00:
        frah2 = frah2 + 1
        fram2 = 0
    if int(frah2) == 24 and (int(fram2) != 0 or int(fras2) != 0):
        frah2 = frah2 - 24
    fRAsex = '%02i' % frah2 + ' ' + '%02i' % fram2 + ' ' + ('%.3f' % float(fras2)).zfill(6)
    return fRAsex



def DEdec_to_DEsex(fDEdec):
    fdetotsec = (math.fabs(float(fDEdec))*3600.0)
    fded2 = (math.modf(fdetotsec/3600.0)[1])
    fdem2 = (math.modf((fdetotsec-(fded2*3600.0))/60.0)[1])
    fdes2 = (fdetotsec-(fded2*3600.0)-(fdem2*60.0))
    if float(fDEdec) < 0:
        fded2sign = '-'
    else:
        fded2sign = '+'
    fDEsex = fded2sign + '%02i' % fded2 + ' ' + '%02i' % fdem2 + ' ' + ('%.2f' % float(fdes2)).zfill(5)
    return fDEsex
    
    
def RAsex_to_RAdec(fRAsex):
    frah = float(fRAsex[0:2])
    fram = float(fRAsex[3:5])
    fras = float(fRAsex[6:])
    fRAdec = (frah*3600.0+fram*60.0+fras)/3600.0
    return fRAdec

def DEsex_to_DEdec(fDEsex):
    fded = float(fDEsex[0:3])
    fdem = float(fDEsex[4:6])
    fdes = float(fDEsex[7:])    
    fDEdec = (math.fabs(fded)*3600.0+fdem*60.0+fdes)/3600.0
    if fDEsex[0] == '-':
        fDEdec = fDEdec * -1
    return fDEdec
    
    

###################-------- Candidate Visualisation  ---------#######################    

# Create array of candidates to use CANVIS on
objects = np.arange(start_num, end_num) 

ra_list = []
dec_list = []
field_list = []
ccd_num_list = []

with open(translist_path) as f:
    for line in f:
        line = line.split()
        if(int(line[0]) in objects):
            ra_list.append(str(line[1]))
            dec_list.append(str(line[2]))
            field_list.append(str(line[3]))
            ccd_num_list.append(str(line[6]))

for objid, ra, dec, field, ccd_num in zip(objects, ra_list, dec_list,
                                          field_list, ccd_num_list):
    print(ra, dec, field, ccd_num)


    path ='/fred/oz100/pipes/DWF_PIPE/MARY_SUB/'+ field + '_'+ run_date +'_mrt1_*/' + field +'_'+run_date+ '_mrt1_*_sub_ccd' + ccd_num +'pos.fits' 

    fitsfileslist = glob.glob(path)
    print(fitsfileslist)
    mydic = SortedDict()

    for path in fitsfileslist:
        with fits.open(path) as hdulist:
            w = WCS(hdulist[0].header)
            head = hdulist[0].header
            xlim = head['NAXIS1']
            ylim = head['NAXIS2']
            date = dt.datetime.strptime(head['DATE'], '%Y-%m-%dT%H:%M:%S')
            
            pixcrd = np.array([[ra, dec]], np.float_)
            #print(pixcrd)
            
            worldpix = w.wcs_world2pix(pixcrd, 1)
            pixx, pixy = worldpix[0][0], worldpix[0][1]
            #print(pixx, pixy)
            
            if pixy < ylim and pixy > 0 and pixx < xlim and pixx > 0:
                mydic[date] = [path, pixx, pixy]

    for i, (key, (path, pixx, pixy)) in enumerate(mydic.items()):
        path_cand = '/fred/oz100/CANVIS/cand_images/'+ run + '/cand_'+format(objid, '05')+'_sub_'+ field +'_'+ run +'/'
        path_cutout = '/fred/oz100/CANVIS/cand_images/'+ run +'/cand_'+format(objid, '05')+'_sub_'+ field +'_'+ run +'/cand_'+format(objid, '05')+'_'+run+'_cutout_'+format(i, '03')+'.fits'  
        if not os.path.exists(path_cand):
            os.mkdir(path_cand, 0o755)
        else:
            pass
        # pos = [float(ra), float(dec)]
        # print(pos)
        size = 200
        with fits.open(path) as hdu:
            # wcs = WCS(hdu.header)
            w = WCS(hdu[0].header)
            cutout = Cutout2D(hdu[0].data, (pixx, pixy), size, wcs= w)
            hdu[0].data = cutout.data
            hdu[0].header['CRPIX1'] = cutout.wcs.wcs.crpix[0]
            hdu[0].header['CRPIX2'] = cutout.wcs.wcs.crpix[1]
            hdu.writeto(path_cutout, overwrite = True)

            # w = WCS(cut_hdu[0].header)
            #plt.subplot(projection = w)
            plt.axis('off')
            plt.imshow(hdu[0].data, cmap='gray', vmin=-1, vmax=15)
            #plt.show()
            plt.savefig('/fred/oz100/CANVIS/cand_images/'+ run +'/cand_'+format(objid, '05')+'_sub_'+ field +'_'+ run +'/cand_'+format(objid, '05')+'_'+run+'_'+format(i, '03')+'_sub.png')

    path_vid = '/fred/oz100/CANVIS/cand_images/'+run+'/cand_{0:05d}_sub_{1}_{2}/'.format(objid, field, run)
    filelist = []
    files = []
    print(path_vid)
    for filename in os.listdir(path_vid):
        if filename.endswith('sub.png'):
            files.append(filename)
    writer = imageio.get_writer('/fred/oz100/CANVIS/cand_vids/'+run+'/cand_sub_'+format(objid, '05')+'_'+run+'sci.mpeg', fps = 3)
    for im in files:
        candipath = path_vid + im
        print(candipath)
        writer.append_data(imageio.imread(path_vid + im))
    writer.close()
