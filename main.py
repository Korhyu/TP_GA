import random as rd
import numpy as np
import math
import matplotlib.pyplot as plt
import statistics


#from fun_GA import select_ind, mate_ind,mutac_ind, buscarnegativos
from fun_sys import run_test, gen_signal, add_noise, score_pob
from fun_sys import FiltroFIR, FiltroEWMA
from fun_log import log_clear, log_ind, log_ind_csv, log_time, log_time_total, plot_error, plot_best_ind, plot_clear, plot_comparacion, plot_comparacion_triple
from fun_gen import seleccion, mutacion, mutacion_rnd, cruza
#from fun_log save_ind, load_data, plot_filtrados, plot_error, plot_comparacion, plot_best_indN, plot_in_out



# Parametros del GA ----------------------------------------------------------------------------------------------------------------------
nGen = 100                   #Generaciones a correr
pDim = 50                     #Tamaño de la poblacion
pMuta = 0.5                     #Probabilidad de que un individuo mute expresade en %
pCruza = 10                    #probabilidad de cruza porcentual
dMuta = 50                    #delta de Muta, osea cuanto puede variar en la mutacion expresado en %

corridas_totales = 5


# Parametros del dEWMA -------------------------------------------------------------------------------------------------------------------
lim_alfa = [1.01, 5]
lim_gamma = [1.01, 10]
lim_sigma = [0.1, 4]
Nmax = 50
Nmin = 1
lim_N = [Nmin, Nmax]


#lim_Nmax = [200, 200]             #Hay que revisar estos limites porque el filtro dEWMA ya hace una estimacion de N usando estos valores
#lim_Nmin = [5, 5]              #Quiza estos parametros hay que incluirlos en los limites de arriba, para pensar



# Parametros de la señal de prueba -------------------------------------------------------------------------------------------------------
amp = [10]              #Amplitudes de cada tono
per = [600]           #Periodos de cada tono
fase = [0]          #Fases de cada tono
muestras = 2000                 #Tamaño de la señal total

amp_noise = 0                  #Amplitud del ruido

""" Originales
amp = [20, 10, 15]              #Amplitudes de cada tono
per = [400, 250, 530]           #Periodos de cada tono
fase = [0, 0.78, 1.57]          #Fases de cada tono

#"Trapezoide"
amp = [-9.12, -2.28, 0, -0.57, -0.36]              #Amplitudes de cada tono
per = [1000, 800, 250, 125, 62]           #Periodos de cada tono
fase = [0.785, 0.785, 0.785, 0.785, 0.785]          #Fases de cada tono
"""


# Parametros de filtros de comparacion ---------------------------------------------------------------------------------------------------
eq_FIR = 10                 #Valor N del filtro "equivalente" FIR
eq_EWMA = 10                #Valor N del filtro "equivalente" EWMA




# Comentarios de desarollo ---------------------------------------------------------------------------------------------------------------
""" El individuo poseera 5 columnas (4 parametros + puntaje), el puntaje comienza como error pero luego se reemplaza por puntaje"""





# Funciones ------------------------------------------------------------------------------------------------------------------------------
def param_rand():
    #Genera los parametros aleatorios y los devuelve en una lista
    # N - gamma - alfa - sigma - puntaje(fuera de esta funcion)
    param = [0, 0, 0, 0, 0]

    #param[0] = rd.randint(lim_N[0], lim_N[1])               #Numeros enteros
    
    param[0] = rd.uniform(lim_N[0], lim_N[1])               #Numeros con coma
    param[1] = rd.uniform(lim_gamma[0], lim_gamma[1])
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

    return np.array(poblacion)



def eval_salida(pura, filtrada):
    #Toma la curva filtrada y la curva del contagio
    #comparando las 2 y haciendo la evaluacion (error cuadratico medio o error medio)
    #devuelve un valor como resultado de esa comparacion
    #quiza la suma de todos los errores o alguna otra metrica a considerar
    #Se descarta el primer 5% de las muestras del vector por considerarse estabilizacion del filtro

    errores_parciales = []
    largo_total = len(filtrada)
    punto_inicial = round(largo_total * 0.05)

    for i in range(punto_inicial, largo_total):
        errores_parciales.append((pura[i]-filtrada[i]) ** 2)
        
    err = sum(errores_parciales) / len(filtrada)

    return err









# main ---------------------------------------------------------------------------------------------------------------------------
def main():

    log_time_total()

    #Limpio de una posible corrida anterior
    plot_clear()
    log_clear()


    # Generacion de datos --------------------------------------------------------------------------------------
    #datos_orig = load_data()                           #Obtengo los datos de contagio
    datos_puros = gen_signal(amp, per, fase, muestras)  #Genero la señal de prueba
    datos_orig = add_noise(amp_noise, datos_puros)
        
    filtrada_FIR = FiltroFIR(eq_FIR, datos_orig)        #Filtradas de comparacion
    filtrada_EWMA = FiltroEWMA(eq_EWMA, datos_orig)

    error_FIR = eval_salida(datos_puros, filtrada_FIR[0])           
    error_EWMA = eval_salida(datos_puros, filtrada_EWMA[0])
    # -----------------------------------------------------------------------------------------------------------


    # Lazo de corridas ----------
    print('Se van a realizar',corridas_totales,'corridas totales')
    for corrida in range(corridas_totales):
        print('Corrida numero',corrida,'de',corridas_totales)

        
        # Variables auxiliares ----------------------------------------------------------------------------------------------------------------------
        #poblacion_actual = []           #Array con la poblacion actual 
        #poblacion_nueva = []            #Array donde se van volcando los individuos de la proxima poblacion
        salida_filtro = []              #Array de las salidas del filtro con cada set de parametros
        evol_error_medio = []  
        error_max = np.zeros(nGen)      #Evolucion del error en funcion de las generaciones
        error_min = np.zeros(nGen)
        error_med = np.zeros(nGen)
        error_minomorum = np.zeros(nGen)

        error_superman = 10000          #Error del mejor individuo de todas las generaciones

        # Generacion de la poblacion   
        poblacion_actual = create_pop(pDim)

        #Lazo de generaciones -------------------------------
        for gen in range(nGen):
            print('Generacion ',gen, 'de ', nGen)

            poblacion_nueva = []                            #Reinicio la poblacion nueva
        
            error_minimo = 10000                            #Maximizo el minimo para encontrar el primer minimo de la poblacion
            error_maximo = 0                                #Minimizo el maximo para encontrar el primer maximo de la poblacion
            error_promedio_gen = 0                          #Vuelvo a 0 los valores de la generacion
            ind_minimo_err = 0
            ind_maximo_err = 0

            
            # Evaluo cada individuo y le asigno el error
            log_time("Filtrado dEWMA")
            for ind in range(len(poblacion_actual)):
                #Aplicar  filtro a los tipitos
                [salida_filtro, Ns] =  run_test(poblacion_actual[ind], datos_orig, Nmin, Nmax)
        
                #Evaluacion de la salida del filtro
                error_actual = eval_salida(datos_puros, salida_filtro)
                poblacion_actual[ind][-1] = error_actual                 #Cargo el error en la ultima columna de la poblacion
                error_promedio_gen = error_promedio_gen + error_actual

                #Busco el error minimo de la generacion
                if error_actual < error_minimo:
                    error_minimo = error_actual
                    ind_minimo_err = ind
                    error_min[gen]=error_actual

                #Busco el error maximo de la generacion
                if error_actual > error_maximo:
                    error_maximo = error_actual
                    ind_maximo_err = ind
                    
                #Descubriendo a Superman
                if error_superman > error_minimo:
                    gen_superman = gen
                    superman = poblacion_actual[ind]                    #Guardo los parametros
                    agujero_techo = salida_filtro                       #Guardo surespuesta al filtro
                    crec_superman = Ns                                  #Guardo su evolucion de Ns
                    error_superman = error_actual                       #Guardo el error para ver si sigue siendo superman
            log_time("Filtrado dEWMA")
            
            #Para ploteo de errores minimo y maximo
            error_min[gen] = error_minimo
            error_max[gen] = error_maximo
            error_minomorum[gen] = error_superman

            #Calculo el error promedio de la generacion
            error_promedio_gen = error_promedio_gen / len(poblacion_actual)
            error_med[gen] = error_promedio_gen
            
            #Asignacion de puntajes
            log_time("Puntuacion")
            poblacion_actual = score_pob(poblacion_actual, error_maximo, error_minimo)
            log_time("Puntuacion")

            #Seleccion
            log_time("Seleccion")
            poblacion_actual= seleccion(poblacion_actual)
            log_time("Seleccion")

            #Cruza
            log_time("Cruza")
            poblacion_actual= cruza(poblacion_actual,pCruza)
            log_time("Cruza")
            
            #Mutacion
            log_time("Mutacion")
            #poblacion_actual= mutacion(poblacion_actual,pMuta,dMuta)
            poblacion_actual= mutacion_rnd(poblacion_actual,pMuta)
            log_time("Mutacion")

        log_ind(superman,gen_superman,corrida)
        log_ind_csv(superman, corrida)
        plot_error(error_min, error_max, error_med, error_minomorum, error_FIR, error_EWMA, corrida)
        plot_best_ind(datos_puros, crec_superman, corrida)
        plot_best_ind(datos_puros, crec_superman, corrida, [1400, 1800])

    plot_comparacion(datos_orig, datos_puros, filtrada_FIR[0], "FIR")
    plot_comparacion(datos_orig, datos_puros, filtrada_EWMA[0], "EWMA")
    plot_comparacion(datos_orig, datos_puros, agujero_techo, "dEWMA")

    plot_comparacion(datos_orig, datos_puros, filtrada_FIR[0], "FIR parcial", [1400, 1800])
    plot_comparacion(datos_orig, datos_puros, filtrada_EWMA[0], "EWMA parcial", [1400, 1800])
    plot_comparacion(datos_orig, datos_puros, agujero_techo, "dEWMA parcial", [1400, 1800])

    plot_comparacion_triple(agujero_techo, filtrada_FIR[0], filtrada_EWMA[0], datos_puros, [1400, 1800])

    log_time_total()



if __name__ == '__main__':
    main()