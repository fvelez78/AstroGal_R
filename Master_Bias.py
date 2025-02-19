# Importacion de paquetes necesarios
from pathlib import Path
import os

from astropy.nddata import CCDData
from astropy.stats import mad_std

import ccdproc as ccdp
import matplotlib.pyplot as plt
import numpy as np

from convenience_functions import show_image

# Lectura de archivos
#---------------------------------------------------------------------
Ruta_Bias=Path('T_Calibracion/Bias/ISO100')
Imagenes=ccdp.ImageFileCollection(Ruta_Bias)

bias=Imagenes.files_filtered(imagetyp='bias',include_path=True)

master_bias=ccdp.combine([ccdp.CCDData.read(f, unit='adu') for f in bias],
                         method='average',
                         sigma_clip=True,sigma_clip_low_thresh=5, sigma_clip_high_thresh=5,
                         sigma_clip_func=np.ma.median, sigma_clip_dev_func=mad_std,
                         mem_limit=350e6
                         )

master_bias.meta['combined']=True

master_bias.write(Ruta_Bias/'Master_bias.fit')


fig, (ax1, ax2)=plt.subplots(1,2,figsize=(20,10))

show_image(CCDData.read(bias[0],unit='adu').data,cmap='gray',ax=ax1,fig=fig,percl=90)
ax1.set_title('Bias individual')
show_image(master_bias.data,cmap='gray',ax=ax2,fig=fig,percl=90)
ax2.set_title('{} bias combinados'.format(len(bias)))
