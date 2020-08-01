import numpy as np
import random
import csv
import math
import matplotlib.pyplot as plt
import os, glob
import time


log_individuos = "Log/Individuos.txt"
log_funciones = "Log/Funciones.csv"
log_csv = "Log/Individuos.csv"


tiempo_pas = 0



def log_clear():
    #Borra los archivos de log anteriores
    open(log_individuos, 'w').close()
    open(log_csv, 'w').close()

    #Escribo los encabezados del CSV
    with open(log_csv, mode='w') as csv_file:
        fieldnames = ['N', 'gamma', 'alfa', 'sigma', 'corrida']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

    with open(log_funciones, mode='w') as csv_file:
        fieldnames = ['Funcion', 'Tiempo_ms']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        


def plot_clear():
    #Borra los archivos de imagenes anteriores
    files = [f for f in glob.glob("Imagenes/*.png")]
    for f in files:
        os.remove(f)



def log_ind (individuo, generacion, corrida):
    #Funcion que registra en un archivo el individuo junto con la corrida y la generacion
    string = "C:" + str(corrida) + "   G:" + str(generacion) + "   Parametros:" + str(individuo)
    with open(log_individuos, "a") as file:
        file.write(str(string))
        file.write('\n')
        file.close()


    
def log_ind_csv (individuo, corrida):
    #Escribe el individuo en el log CSV
    
    with open(log_csv, mode='a') as csv_file:
        fieldnames = ['N', 'gamma', 'alfa', 'sigma', 'corrida']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({fieldnames[0]: individuo[0], fieldnames[1]: individuo[1], fieldnames[2]: individuo[2], fieldnames[3]: individuo[3], fieldnames[4]: corrida})



def log_time (funcion):
    #funcion para registar el tiempo que demora la funcion

    global tiempo_pas

    if tiempo_pas == 0:
        tiempo_pas = time.time()
    
    else:
        tiempo_act = time.time() - tiempo_pas
        tiempo_pas = 0

        with open(log_funciones, "a") as file:
            fieldnames = ['Funcion', 'Tiempo_ms']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({fieldnames[0]: funcion, fieldnames[1]: tiempo_act})
    



def plot_error(error_min, error_max, error_medio, error_super, error_FIR, error_EWMA, corrida):
    #Ploteo la evolucion del error a lo largo de una generacion 

    plt.figure(figsize=(14, 10))

    #Error medio y minimo
    plt.subplot(311)
    plt.plot(error_medio, label='Medio generacional')
    plt.plot(error_min, label='Minimo generacional')
    plt.ylabel('Error')
    plt.xlabel('Generacion')
    plt.grid(True)
    plt.legend(loc=1)

    
    #Error minimo comparado con FIR y EWMA
    plt.subplot(312)
    error_FIR = np.ones(len(error_min)) * error_FIR
    error_EWMA = np.ones(len(error_min)) * error_EWMA
    plt.plot(error_min, label='Minimo generacional')
    plt.plot(error_FIR, label='Filtro FIR')
    plt.plot(error_EWMA, label='Filtro EWMA')
    plt.ylabel('Error')
    plt.xlabel('Generacion')
    plt.grid(True)
    plt.legend(loc=1)


    #Comparacion error minimo y error superman
    plt.subplot(313) 
    plt.plot(error_min, label='Minimo generacional')
    plt.plot(error_super, label='Minimo minimorum')
    plt.suptitle('Evolucion del error generacional')
    plt.ylabel('Error')
    plt.xlabel('Generacion')
    plt.grid(True)
    plt.legend(loc=1)


    img_file = "Imagenes/Error_" + str(corrida) + ".png"
    plt.savefig(img_file)
    plt.close()



def plot_best_ind (signal, Ns, corrida, vent = None):
    #Plotea la señal de salida del mejor individuo junto con la evolucion del N del mismo

    #Eje izquierdo
    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.set_xlabel('Muestras')
    ax1.set_ylabel('N [muestras]', color=color)

    if vent is None:
        ax1.plot(Ns, color=color)
        ax1.tick_params(axis='y', labelcolor=color)
    else:
        ax1.plot(Ns[vent[0] : vent[1]], color=color)
        ax1.tick_params(axis='y', labelcolor=color)

    #Eje derecho
    ax2 = ax1.twinx()                               # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Señal Entrada', color=color)    # we already handled the x-label with ax1
    
    if vent is None:
        ax2.plot(signal, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        img_file = "Imagenes/Superman_" + str(corrida) + ".png"
    else:
        ax2.plot(signal[vent[0] : vent[1]], color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        img_file = "Imagenes/Superman_" + str(corrida) + "_vent.png"

    

    fig.tight_layout()                              # otherwise the right y-label is slightly clipped
    #fig = plt.figure(figsize=(12,10))
    #plt.figure(figsize=(12,10))


    plt.grid(True)
    plt.savefig(img_file)
    plt.close()



def plot_in_out (signal, out, filtro):
    #Ploteo comparacion entre entrada y salida de un filtro

    titulo = "Señal de entrada y salida del filtro " + str(filtro)
    archivo = "Imagenes/In_Out_" + str(filtro) + ".png"
    fig = plt.figure(figsize=(12,6))
    plt.ylabel('Valor')
    plt.xlabel('Muestras')
    plt.plot(signal, label = "Entrada")
    plt.plot(out, label = "Salida")
    plt.title(titulo)
    plt.legend(loc=4)
    plt.savefig(archivo)
    plt.grid(True)
    plt.close()


def plot_comparacion (original, pura, filtrada, nombre_filtro, vent = None):

    titulo = "Rendimiento filtro " + str(nombre_filtro)
    archivo = "Imagenes/Comparacion_" + nombre_filtro + ".png"

    fig = plt.figure(figsize=(12,6))
    plt.ylabel('Valor')
    plt.xlabel('Muestras')

    if vent is None:
        plt.plot(original, label = "Entrada a filtro")
        plt.plot(pura, label = "Señal pura")
        plt.plot(filtrada, label = "Salida del filtro")
    else:
        plt.plot(original[vent[0] : vent[1]], label = "Entrada a filtro")
        plt.plot(pura[vent[0] : vent[1]], label = "Señal pura")
        plt.plot(filtrada[vent[0] : vent[1]], label = "Salida del filtro")
    
    plt.title(titulo)
    plt.legend(loc=1)
    plt.grid(True)
    plt.savefig(archivo)
    plt.close()


def plot_comparacion_triple (filtro_dEWMA, filtro_FIR, filtro_EWMA, pura, vent = None):

    titulo = "Comparacion entre filtros"
    archivo = "Imagenes/Comparacion_Triple.png"

    fig = plt.figure(figsize=(12,6))
    plt.ylabel('Valor')
    plt.xlabel('Muestras')

    if vent is None:
        plt.plot(pura, label = "Señal Pura")
        plt.plot(filtro_dEWMA, label = "dEWMA")
        plt.plot(filtro_FIR, label = "FIR")
        plt.plot(filtro_EWMA, label = "EWMA")
    else:
        plt.plot(pura[vent[0] : vent[1]], label = "Señal Pura")
        plt.plot(filtro_dEWMA[vent[0] : vent[1]], label = "dEWMA")
        plt.plot(filtro_FIR[vent[0] : vent[1]], label = "FIR")
        plt.plot(filtro_EWMA[vent[0] : vent[1]], label = "EWMA")

    
    plt.title(titulo)
    plt.legend(loc=1)
    plt.grid(True)
    plt.savefig(archivo)
    plt.close()