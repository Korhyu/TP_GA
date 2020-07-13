import numpy as np
import random
import csv
import math
import matplotlib.pyplot as plt

from fun_log import log_time

def gen_signal(amp, per, fases, muestras):
    # Recibe las amplitudes, periodos y fases como vectores y el numero de muestras es un int.
    # devuelve la señal como suma de todos los senos usando los parametros antes dados.
    # Los periodos indicados son la cantidad de muestras necesarias para un ciclo de senoidal

    if len(amp) != len(per) and len(amp) != len(fases):
        #Verifico que los vectores sean del mismo tamaño
        print("Los vectores de amplitud, frecuencia y fase deben tener la misma cantidad de elementos")
        return None
    
    s = np.empty([len(amp), muestras]) 

    for i in range(len(amp)):
        for j in range(muestras):
            s[i,j] = amp[i] * math.sin((2 * math.pi * j / per[i]) + fases[i])

    st = np.empty(muestras) 
    for j in range(muestras):
        st[j] = sum(s[:,j])

    # Le monto una continua para ver si eso es lo que rompe el sigma
    #if st.min() < 0:
    #    st = st - st.min()


    return st


def add_noise(amp, s):
    #Agrega ruido aleatorio de amplitud especificada
    n = np.random.default_rng().uniform(low=-amp, high=amp, size=len(s))
    st = s + n

    #if st.min() < 0:
    #    st = st - st.min()

    return st


def FiltrodEWMA(param, data, Nmin, Nmax):
    '''
    Variable: Array a calcular, 
    N: factor de aprendizaje, 
    gama: Velocidad de adaptacion, 
    alfa: Coeficiente de estabilizacion, 
    Nmax y Nmin valores limite para N
    '''

    N = param[0]
    gama = param[1]
    alfa = param[2]
    sigma = param[3]
    #Nmax = param[4]
    #Nmin = param[5]

    variable = data


    dEWMA = np.array([variable[0]])
    Ns = [N]
    for j in range(1,len(variable)):
        #sigma = 2 * (dEWMA[j-1])**(1/2)
        #sigma = 2 * (abs(dEWMA[j-1]))**(1/2)
        #sigma = sigma / (2 * (dEWMA[j-1])**(1/2))
        error = abs(variable[j]-dEWMA[j-1])
        if error > sigma:
            N = (N/gama)
            if N < Nmin:
                N = Nmin
        if error < sigma/alfa: 
            N = (N * gama)
            if N > Nmax:
                N = Nmax
        Ns.append(N)
        a = dEWMA[j-1] +(variable[j]-dEWMA[j-1])/N
        dEWMA = np.append( dEWMA , np.array(a))


    #Desabilitado - Borrar
    #param[0] = N
    #param[1] = gama
    #param[2] = alfa
    #param[3] = sigma

    #plt.ylabel('Valor')
    #plt.xlabel('Muestras')
    #plt.title('Evol de Ns')
    #plt.plot(Ns)
    #plt.show()


    return [dEWMA, np.array(Ns)]


def FiltroFIR(N, variable):
    #Filtro FIR con N variable
    N = int(N)
    inicio = variable[0:N]
    FIR = np.zeros(N)
    FIR[N-1] = np.average(inicio)
    for j in range(0,len(variable)-N):
        a =FIR[N+j-1] +(variable[j+N]-variable[j])/N
        FIR = np.append( FIR , np.array(a ))
    return [FIR, N]


def FiltroEWMA(N, variable): 
    #Filtro EWMA con N variable
    N = int(N)
    EWMA = np.array([variable[0]])
    for j in range(1,len(variable)):
        a = EWMA[j-1] +(variable[j]-EWMA[j-1])/N
        EWMA = np.append( EWMA , np.array(a))
    return [EWMA, N]



def run_test(param, data, Nmin, Nmax):
    #Funcion que corre los 5 parametros recividos como lista en el filtro dEWMA
    #deve devolver la curva resultado del filtro
    #este filtro debe recivir el vector de valores de contagio del COVID

    return FiltrodEWMA(param, data, Nmin, Nmax)
    #return FiltroEWMA(param[0], data)
    #return FiltroFIR(param[0], data)



def score_pob(poblacion, error_maximo, error_minimo):
    #Esta funcion deberia tomar el error de la funcion eval_test y asignar un puntaje 

    delta_error = error_maximo - error_minimo

    for ind in range(len(poblacion)):
        #En la ultima columna se almacena el error
        mod = (poblacion[ind][-1] - error_minimo) / delta_error
        poblacion[ind][-1]= 1 * (mod**2)     #Relacion Exponencial 1
        
        #if mod > 0.000001 :
        #    poblacion[ind,-1]= 1 * (mod**2)     #Relacion Exponencial 1
        #else:
        #    poblacion[ind,-1]= 0.000001
        
        #error_punt[ind,1]= PUNTUACION_MAXIMA * (error_punt[ind,0] - error_minimo) / delta_error             #Relacion Exponencial 2
        #error_punt[ind,1]= PUNTUACION_MAXIMA - (error_punt[ind,0] * PUNTUACION_MAXIMA / error_maximo)       #Relacion lineal 1
        #if  error_punt[ind,1] < 0 :
        #    error_punt[ind,1]=0

    poblacion = np.array(sorted(poblacion, key=lambda a_entry: a_entry[-1]))

    return poblacion