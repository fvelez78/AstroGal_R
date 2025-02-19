def Vrf_modulos(Modulos_Req):
    import sys
    modulos_faltantes = [
        modulo for modulo in Modulos_Req 
        if modulo not in sys.modules
    ]
    
    if modulos_faltantes:
        print(f"Módulos no importados: {modulos_faltantes}")
        return False
    return True
#-------------------------------------------------------------------------
def read_noise(shape,amount,gain=1,seed=234):
    """
    Generacion de una imagen con ruido de lectura simulado

    Argumentos de la funcion
    ------------------------------------
     shape: tupla
           Tupla que indica el tamano de la imagen a la cual se le introduce el ruido de lectura simulado
    amount:float
           Cantidad de ruido dado en electrones
      gain: float, opcional
            Ganancia de la camara en unidades de electron/ADU

    """ 

    Modulos = ['numpy']
    
    if not Vrf_modulos(Modulos):
        raise ImportError("Faltan módulos por importar")

    noise_rng=np.random.default_rng(seed)
    image=np.zeros(shape)
    noise=noise_rng.normal(scale=amount/gain,size=shape)
    image_rn=image+noise

    return image_rn
#-------------------------------------------------------------------------
def bias(image,value,realistic=False,seed=34347):

    """
    Generacion de un Bais simulado

    Argumentos de la funcion
    ------------------------------------
        image: numpy array
               Imagen creada previamente de ruido
        value: float
               Valor medio del bias
    realistic: logic, opcional
               Variable logica para agregar columnas(True) de mayor intensidad al bias           
         seed: Integer, opcional
               Valor de la semilla para la generacion de valores aleatorios
    """
    
    Modulos = ['numpy']
    if not Vrf_modulos(Modulos):
        raise ImportError("Faltan módulos por importar")

    # Se crea el bais inicial con valor constante
    bias_im=np.zeros_like(image)+value
    
    # Tamano de la imagen inicial
    shape=image.shape
    # Numero de columnas que se recrearan en el bias
    N_Cols_Medio=5
    
    if realistic:

        rng=np.random.RandomState(seed=seed)
        # Se genera aleatoriamente el numero de columas finales del bias
        N_columnas=rng.randint(0,shape[1],size=N_Cols_Medio)
        
        # Se genera el ruido que tendran las columnas agregadas al bias
        Ruido_Col=rng.randint(0,int(0.1*value),size=shape[0])

        # Se agregan las columnas a la imagen bias simulada
        for c in N_columnas:
            bias_im[:,c]=value+Ruido_Col
        
        return bias_im
#--------------------------------------------------------------------------------        
def dark_current(image,current,exposure_time,gain=1,hot_pixels=True,seed=9823):

    """
    Generacion de un Bais simulado

    Argumentos de la funcion
    ------------------------------------
        image: numpy array
               Imagen creada previamente de ruido
      current: float
               Valor medio de la corriente de oscuridad dada en electrones por pixel por segundo
               (e/px/sec), generalemente indicada por el fabricante de la camara.
    exposure_time: float
               Tiempo simulado de exposicion een segundos
         gain: float, opcional
               Ganancia de la camara en unidades de electron/ADU      
    hot_pixels: logic, opcional
               Variable logica para agregar pixeles asociados a rayos cosmicos
         seed: Integer, opcional
               Valor de la semilla para la generacion de valores aleatorios
    """
    
    Modulos = ['numpy']
    if not Vrf_modulos(Modulos):
        raise ImportError("Faltan módulos por importar")
    
    # Corriente de oscuridad base para cada pixel
    base_current=current*exposure_time/gain

    noise_rng=np.random.default_rng(seed)
    
    # Se genera el ruido poison asociado a la exposicion similada
    dark_im=noise_rng.poisson(base_current,size=image.shape)

    if hot_pixels:

        y_max, x_max=dark_im.shape
        
        # Numero de hot pixels a recrear en la imagen
        n_hot=int(0.0001*x_max*y_max)

        # Se fija una semmilla diferente para las posiciones de los hot pixels
        rng=np.random.RandomState(84726253)
        hot_x=rng.randint(0,x_max,size=n_hot)
        hot_y=rng.randint(0,y_max,size=n_hot)
        
        # Se fija el valor de corriente de oscuridad para los hot pixels por un 
        # factor exagerado para facilitar su visualizacion
        hot_current=10000*current

        dark_im[hot_x,hot_y]=hot_current*exposure_time/gain

        return dark_im
#--------------------------------------------------------------------------------        
def sky_backbround(image,sky_count,gain=1,seed=9823):

    """
    Generacion del fondo del cielo

    Argumentos de la funcion
    ------------------------------------
        image: numpy array
               Imagen creada previamente de ruido
      sky_count: float
               Valor medio del numero de cuentas debidas al fond0 del cielo
         gain: float, opcional
               Ganancia de la camara en unidades de electron/ADU      
         seed: Integer, opcional
               Valor de la semilla para la generacion de valores aleatorios
    """
    
    Modulos = ['numpy']
    if not Vrf_modulos(Modulos):
        raise ImportError("Faltan módulos por importar")
    
    noise_rng=np.random.default_rng(seed)
    
    # Se genera el ruido poison asociado a la exposicion similada
    sky_im=noise_rng.poisson(sky_count*gain,size=image.shape)/gain

    return sky_im
#--------------------------------------------------------------------------------
def stars(image,number,max_counts=1000,gain=1):

    from photutils.datasets import make_model_params, make_gaussian_sources_image

    flux_range=[max_counts/10,max_counts]

    y_max, x_max =image.shape
    xmean_range =[0.1*x_max,0.9*x_max]
    ymean_range =[0.1*y_max,0.9*y_max]
    xstddev_range=[4,4]
    ystddev_range=[4,4]
    params=dict([('amplitude',flux_range),
                  ('x_mean',xmean_range),
                  ('y_mean',ymean_range),
                  ('x_stddev',xstddev_range),
                  ('y_stddev',ystddev_range),
                  ('theta',[0,2*np.pi])])
    sources=make_gaussian_sources_image(number,params,seed=12345)

    stars_im=make_gaussian_sources_image(image.shape,sources)

    return stars_im
#--------------------------------------------------------------------------------
from ipywidgets import interactive, interact

# @interact(bias_level=(1000,1200,10), dark+(0.01,1,0.01),sky_counts=(0,300,10),
#            gain(0.5,3.0,0.1),read=(0,50,2.0),
#            exposure=(0,300,10))

def complete_image(bias_level=1100,read=10.0,gain=1, dark=0.1,
                   exposure=30,hot_pixels=True,sky_counts=200):
    imagen=np.zeros([500,500])
    show_image(imagen+
               read_noise(imagen.shape,read)+
               bias(imagen,bias_level,realistic=True)+
               dark_current(imagen,dark,exposure,hot_pixels=hot_pixels)+
               sky_backbround(imagen,sky_counts),
               cmap='gray',
               figsize=None)
    
i=interactive(complete_image,bias_level=(1000,3200,10), 
                                  dark=(0.01,1,0.01),
                            sky_counts=(0,300,10),
                                  gain=(0.5,3.0,0.1),
                                  read=(0,50,5.0),
                              exposure=(0,300,10))

for kid in i.children:
    try:
        kid.continuous_update=False
    except KeyError:
        pass

i




#--------------------------------------------------------------------------------        
import matplotlib.pyplot as plt
import numpy as np
from convenience_functions import show_image

# Ejemplo 1:  Creacion de una imagen de valor cosntante y su correspondiente con ruido
#--------------------------------------------------------------------------------------
imagen=np.zeros([1000,1000]) 
imagen_rn=read_noise((1000,1000),10)

show_image(imagen,cmap='gray',figsize=(10,10))
plt.title('Imagen sintetica constante')
show_image(imagen_rn,cmap='gray',figsize=(10,10))
plt.title('Imagen con ruido de lectura simulado')

# Ejemplo 2:  Creacion de una imagen bias con valor constante y con ruido incluyendo 
#             columnas de mayor intensidad
#--------------------------------------------------------------------------------------
 
bias_c=bias(imagen,1100,realistic=True)

bias_rn=imagen_rn+bias_c

show_image(bias_c,cmap='gray',figsize=(10,10))
plt.title('Bias simulado constante')
show_image(bias_rn,cmap='gray',figsize=(10,10))
plt.title('Bias simulado con ruido y columnas')

# Ejemplo 3:  Creacion de una imagen dark y su adicion de ruido (bias)
#--------------------------------------------------------------------------------------

t_exposure=100
dark_cur=0.1

dark=dark_current(imagen,dark_cur,t_exposure,hot_pixels=True)
dark_rn=dark+bias_rn

show_image(dark,cmap='gray',figsize=(10,10))
title='Corriente de oscuridad simulada,{dark_cur},$e^-$/sec/pix\n{t_exposure} segundos de exposicion'.format(dark_cur=dark_cur,t_exposure=t_exposure)
plt.title(title,fontsize='20')
show_image(dark_rn,cmap='gray',figsize=(10,10))
plt.title('Dark Frame simulado con bias')

# Ejemplo 4:  Creacion de una imagen dark incluyendo fondo de cielo
#--------------------------------------------------------------------------------------

sky_level=20
sky=sky_backbround(imagen,sky_level)


show_image(sky,cmap='gray',figsize=(10,10))
title='Fondo del cielo simulado a {sky_level} cuentas'.format(sky_level=sky_level)
plt.title(title,fontsize='20')

dark_rn_sky=dark_rn+sky
show_image(dark_rn_sky,cmap='gray',figsize=(10,10))
title='Bias + Dark + Fondo del cielo \n (Simulacion realista de un Dark)'
plt.title(title,fontsize='20')


# Ejemplo 5:  Imagen simulada de un campo estelar
#--------------------------------------------------------------------------------------

star_im=stars(imagen,50,max_counts=2000)
show_image(star,cmap='gray',percu=99.9)


from mpl_toolkits.mplot3d import Axes3D

fig=plt.figure()
Ax=Axes3D(fig)

x=np.linspace(0,999,1000)
y=np.linspace(0,999,1000)

X, Y=np.meshgrid(x,y)

Z=imagen_rn

Ax.plot(X,Y,Z)
plot.show()