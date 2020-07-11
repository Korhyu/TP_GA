#Los de chaca son todos putos pero como tiran Flechas!!!

import numpy as np
import random

def seleccion(poblacion_actual): #Recibo la los parametros del filtro (poblacion_actual) y su puntuacion (seguda columna de error_punt)
    #Funcion que toma la poblacion y los errores y puntajes y realiza la seleccion, mientras mas puntos mayor la seleccion de ese individuo
    pob_sel=np.copy(poblacion_actual) #creo una matriz auxiliar para ir cargando la poblacion seleccionada
    for pob in range(int(len(poblacion_actual[:,0]))):
        rd=random.random()
        for aux in range(int(len(poblacion_actual[:,0]))):
            
            if rd > poblacion_actual[aux,4]:
                if aux == 0:
                    pob_sel=poblacion_actual[aux,:]
                else:
                    pob_sel=poblacion_actual[aux-1,:]
                break
      
    return pob_sel

def cruza(poblacion_nueva,pCruza):
    #Funcion de cruza de la poblacion
    aux = np.arange(6) # auxiliar para las cruzas
    aux_pasa = np.arange(6) #auxiliar para los que no se cruzan
    cant_cruza=0
    for cruza in range(int(len(poblacion_nueva[:,0]))): #en este for se elige quienes se cruzan 
        if pCruza > (random.randrange(0, 1000, 1))/10: #comparacion de la probabilidad de cruce
            cant_cruza=cant_cruza+1
            aux=np.vstack((aux, poblacion_nueva[cruza,:])) #agrego al "padre a cruzar"
        else:
            aux_pasa=np.vstack((aux_pasa, poblacion_nueva[cruza,:])) # agrego a los individuos que no se van a cruzar
    print('Cantidad de cruzas: ', cant_cruza)
    if np.ndim(aux) > 1: #pregrunto si hay alguno para cruzar
        i=len(aux[:,0])-1 
        if i%2 != 0 : #si hay una cantidad impar hago pasar directoa un padre. 
            aux_pasa=np.vstack((aux_pasa, aux[i,:])) #copio el ultimo padre directo
            i=i-1
        aux_cruz=np.arange(float(6)) #auxiliar pa la cruza
        while i>=2:
            pQuiebre=random.randrange(0,4,1) #calculo el punto de quiebre para la cruza
            for pQ in range(pQuiebre):
                aux_cruz[pQ]=aux[i,pQ] #lleno los paramatro hasta el punto de quiebre (padre i)
            for pQ in range(pQuiebre,4):
                 aux_cruz[pQ]=aux[i-1,pQ] #lleno los parametro despues del punto de quiebre (padre i-1)
            aux_pasa=np.vstack((aux_pasa, aux_cruz)) # Guardo al primer hijo
            for pQ in range(pQuiebre):
                aux_cruz[pQ]=aux[i-1,pQ] #lleno los paramatro hasta el punto de quiebre (padre i-1)
            for pQ in range(pQuiebre,4):
                 aux_cruz[pQ]=aux[i,pQ] #lleno los parametro despues del punto de quiebre (padre i)
            aux_pasa=np.vstack((aux_pasa, aux_cruz)) # Guardo al segundo hijo           
            i=i-2
    return aux_pasa[1:,:]

def mutacion(oPob,pMuta,dMuta):
    #Funcion que recorre la poblacion futura y genera la mutacion en los individuos   
    aux = np.copy(oPob) #auxiliar para la poblacion
    cuenta=0
    max_muta=(dMuta/100)+1 #culculo de maxima mutacion hacia arriba dMuta=taza de mutacion
    min_muta=1-(dMuta/100) #culculo de maxima mutacion hacia abajo dMuta=taza de mutacion
    print('Max muta',max_muta, 'y Min Muta', min_muta)
    for total in range(len(oPob[:,0])):
        for param in range(len(oPob[0,:])):
            if pMuta > (random.randrange(0, 1000, 1))/10: #avanzo por todos los parametros y segun la probabilidad de muta se eligen
                cuenta=cuenta+1                
                if param == 0 :
                    aux[total,param]= round(random.uniform(aux[total,param]*min_muta,aux[total,param]*max_muta)) #muto el parametro entero
                else:
                    aux[total,param]= random.uniform(aux[total,param]*min_muta,aux[total,param]*max_muta) #muto el parametro no entero               
    print('Cantidad de parametros mutados', cuenta)
    return aux


















