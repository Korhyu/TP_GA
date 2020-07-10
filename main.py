import random as rd
import numpy as np
import math
import matplotlib.pyplot as plt
import statistics


from fun_GA import select_ind, mate_ind,mutac_ind, buscarnegativos
from fun_sys import run_test, plot_filtrados, load_data, gen_signal, add_noise, plot_error
from fun_sys import FiltroFIR, plot_comparacion, FiltroEWMA, plot_best_indN, plot_in_out, save_ind


PUNTUACION_MAXIMA = 100

# Parametros del GA ----------------------------------------------------------------------------------------------------------------------
nGen = 51                    #Generaciones a correr
pDim = 40                     #Tamaño de la poblacion
pMuta = 3                     #Probabilidad de que un individuo mute expresade en %
dMuta = 50                    #delta de Muta, osea cuanto puede variar en la mutacion expresado en %
pCruza = 40                   #probabilidad de cruza porcentual

corridas_totales = 20


# Parametros del dEWMA -------------------------------------------------------------------------------------------------------------------
lim_gamma = [0.5, 40]
lim_alfa = [1, 30]
lim_sigma = [4, 8]             #Actualmente no se utiliza y el filtro calcula su sigma propio
lim_Nmax = [200, 200]             #Hay que revisar estos limites porque el filtro dEWMA ya hace una estimacion de N usando estos valores
lim_Nmin = [5, 5]              #Quiza estos parametros hay que incluirlos en los limites de arriba, para pensar
lim_N = [lim_Nmin[0], lim_Nmax[1]]


# Variables auxiliares ----------------------------------------------------------------------------------------------------------------------
poblacion_actual = []           #Array con la poblacion actual 
poblacion_nueva = []            #Array donde se van volcando los individuos de la proxima poblacion
salida_filtro = []              #Array de las salidas del filtro con cada set de parametros
evol_error_medio = []  
error_max = np.zeros(nGen)               #Evolucion del error en funcion de las generaciones
error_min = np.zeros(nGen)
error_minomorum = np.zeros(nGen)



# Parametros de la señal de prueba -------------------------------------------------------------------------------------------------------
amp = [20, 10, 15]              #Amplitudes de cada tono
per = [400, 250, 530]           #Periodos de cada tono
fase = [0, 0.78, 1.57]          #Fases de cada tono
muestras = 2000                 #Tamaño de la señal total

amp_noise = 6                  #Amplitud del ruido


# Parametros de filtros de comparacion ---------------------------------------------------------------------------------------------------
eq_FIR = 6                 #Valor N del filtro "equivalente" FIR
eq_EWMA = 6                #Valor N del filtro "equivalente" EWMA




# Comentarios de desarollo ---------------------------------------------------------------------------------------------------------------
""" El individuo poseera 5 columnas (4 parametros + puntaje), el puntaje comienza como error pero luego se reemplaza por puntaje"""





# Funciones ------------------------------------------------------------------------------------------------------------------------------
def param_rand():
    #Genera los parametros aleatorios y los devuelve en una lista
    param = [0, 0, 0, 0, 0]

    param[0] = rd.randint(lim_N[0], lim_N[1])               #Numeros enteros
    
    param[1] = rd.uniform(lim_gamma[0], lim_gamma[1])       #Numeros con coma
    param[2] = rd.uniform(lim_alfa[0], lim_alfa[1])
    param[3] = rd.uniform(lim_sigma[0], lim_sigma[1])

    # Los limites no corren mas en forma aleatoria - Borrar
    #param[4] = rd.randint(lim_Nmax[0], lim_Nmax[1])
    #param[5] = rd.randint(lim_Nmin[0], lim_Nmin[1])
    # Verifico que el maximo no sea inferior al minimo
    #if param[4] < param[5]:
    #    param[5] = param[4] - 1

    return param


def create_pop(num_ind):
    #Funcion que crea una poblacion de individuos aleatoria

    parametros = param_rand()
    poblacion = np.array(parametros)

    for cont in range(num_ind-1):
        parametros = np.array(param_rand())
        poblacion = np.vstack((poblacion,parametros))

    return poblacion
