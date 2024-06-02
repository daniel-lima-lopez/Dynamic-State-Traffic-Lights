from __future__ import absolute_import
from __future__ import print_function

import NNControls as nnc
import pandas as pd

import os
import sys
import optparse
import random
import numpy as np

from sumolib import checkBinary  # noqa
import traci  # noqa
import tensorflow as tf

class Traffic_light:
    def __init__(self, id, edge1,edge2,edge3,edge4, dt=5):
        #self.dt = dt

        #self.dtrans = int(0.2*dt)
        self.ID = id # ide del semaforo
        self.edges = [edge1, edge2, edge3, edge4] # ids de las edges
        self.edge_id = {edge1:0, edge2:2, edge3:4, edge4:6}
        self.phase = self.get_phase() # fase actual del semaforo
        
    def get_num_car(self,edge):
        return traci.edge.getLastStepVehicleNumber(edge)
        
    def getwait(self,edge_id):
        return traci.edge.getWaitingTime(edge_id)
        
    def get_phase_time(self):
        return traci.trafficlight.getPhaseDuration(self.ID)
        
    def get_phase(self):
        return traci.trafficlight.getPhase(self.ID)
        
    def evalu(self,step):
        if step%40==0:
            self.set_phase(self.phase+1)
        elif (self.phase%2)-1==0:
            self.set_phase(self.phase+1)
            
    def set_phase(self,num):
        if num>7:
            self.phase = 0
        else:
            self.phase = num
        traci.trafficlight.setPhase(self.ID,self.phase)
def run(gui=False):
    """execute the TraCI control loop"""
    if gui:
         sumoBinary = checkBinary('sumo-gui')
    else:
         sumoBinary = checkBinary('sumo')
    traci.start([sumoBinary, "-c", "osm.sumocfg",
                     "--no-warnings"])
    ei = 0 # estado inicial
    steps = 0
    dy = 2 # delta amarillo
    dg = 10 # delta verde
    auxt = 0
    isGreen = True
    i = 1
    t0=Traffic_light("S1","E1","-E3","E5","-E4")
    A=[]
    B=[]
    id_pred=0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        if steps%5==0:
            t0.evalu(steps)
        #    t0.set_phase(random.randint(0,8))
        steps+=1
                
    print(f'tiempo {steps} \n')
    #np.savetxt('wait.csv', A, fmt="%d", delimiter=",")
    #np.savetxt('numcar.csv', B, fmt="%d", delimiter=",")
    traci.close()
    sys.stdout.flush()
class SimStateRandom:
    def __init__(self, seed, steps=1000, gui=False, verbose=False,act_rou=True):
        # crea rutas aleatorias con la seed
        if act_rou:
            os.system(f'python "%SUMO_HOME%\\tools\\randomTrips.py" -n osm.net.xml  -o osm.passenger.trips.xml -r osm.passenger.rou.xml -e {steps} -s {seed}  --lanes --validate --period 0.7 --binomial 4')
        
        # bandera para mostrar info
        self.verbose = verbose

        # importamos librearias y herramientas de SUMO
        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        # verificamos si la simulacion se ejecutara con o sin gui
        if gui:
            sumoBinary = checkBinary('sumo-gui')
        else:
            sumoBinary = checkBinary('sumo')
        
        # instanciamos el traci con la configuracion del gui, el .sumocfg (este contiene el .net y .trips)
        traci.start([sumoBinary, "-c", "osm.sumocfg"])

        # instanciamos un semaforo para la simulacion
        self.TL = Traffic_light("S1","E1","-E3","E5","-E4")

    def control(self):
        pred = random.choice(self.TL.edges)
        id = self.TL.edge_id[pred]
        if self.verbose:
            print(f'\n Prediccion: {pred}  id: {id}')
        return id
    
    def fitness(self, cfg='f0'):
        if cfg == 'f0':
            return self.steps
        elif cfg == 'f1':
            return self.f1
        elif cfg == 'f2':
            return self.f2

    def run(self):
        ei = 0 # estado inicial (semaforo 0 verde)
        self.steps = 0 # numero de steps trasncurridos
        dy = 2 # delta amarillo
        dg = 20 # delta verde
        auxt = 0 # auxiliar para control de semaforos
        isGreen = True # estado verde o amarillo
    
        #t0 = Traffic_light("S1","E1","-E3","E5","-E4")
        #A=[]
        #B=[]
        self.f1 = 0 # fitness unos 
        self.f2 = 0 # fitnes dos
        id_pred = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep() # avanza un step en la simulacion
            
            # si se alcanzo dg y algun semaforo esta en verde
            if auxt == dg and isGreen: 
                id_pred = self.control() # se realiza una prediccion del siguiente estado con el control
                auxt = 0 # reinicia contador auxiliar
                cs = np.array([self.TL.get_num_car(id) for id in self.TL.edges])
                ts = np.array([self.TL.getwait(id) for id in self.TL.edges])
                self.f1 += np.sum(cs)
                self.f2 += np.sum(ts)
                if self.TL.get_phase()==id_pred: # si la fase predicha es identica a la actual
                    pass
                else: # si la prediccion es distinto al estado actual
                    isGreen = False
                    self.TL.set_phase(self.TL.get_phase()+1) # fase amarilla del estado actual
                    ei = ei+1
            
            # si se alcanzo dy y algun semaforo esta en amarillo
            elif auxt==dy and not isGreen:
                self.TL.set_phase(id_pred) # cambia a la fase predicha por el control
                ei = id_pred
                isGreen = True
                auxt = 0
            auxt += 1
            self.steps += 1 # actualiza el contador de steps
        
        # cerramos el traci
        traci.close()
        sys.stdout.flush()


class SimStateNN:
    def __init__(self, seed, gen, steps=1000, gui=False, verbose=False, worst=4000, act_rou=True):
        # maximo numero de steps considerados en la simulacion
        self.worst = worst

        # crea rutas aleatorias con la seed
        if act_rou:
            os.system(f'python "%SUMO_HOME%\\tools\\randomTrips.py" -n osm.net.xml  -o osm.passenger.trips.xml -r osm.passenger.rou.xml -e {steps} -s {seed}  --lanes --validate  --binomial 1')

        # crea una red neuronal con la configuracion de gen
        tf.keras.backend.clear_session() # limpia memoria
        cs = 4 # tamano del vector de entrada evaluado por la red
        es = 4 # numero de configuraciones del semaforo

        self.NN = nnc.ControlState(cs=4, opts=es)
        self.NN.predict(np.array([[0. for i in range(cs)]]), verbose=False) ## llamada auxiliar para construir el nodo de la red

        # configura la arquitectura con la configuracion de gen
        self.NN.set_phen(gen)
        
        # bandera para mostrar info
        self.verbose = verbose

        # importamos librearias y herramientas de SUMO
        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        # verificamos si la simulacion se ejecutara con o sin gui
        if gui:
            sumoBinary = checkBinary('sumo-gui')
        else:
            sumoBinary = checkBinary('sumo')
        
        # instanciamos el traci con la configuracion del gui, el .sumocfg (este contiene el .net y .trips)
        #traci.start([sumoBinary, "-c", "osm.sumocfg"])
        traci.start([sumoBinary, "-c", "osm.sumocfg",
                     "--no-warnings"])

        # instanciamos un semaforo para la simulacion
        self.TL = Traffic_light("S1","E1","-E3","E5","-E4")

    def control(self, cs):
        outs = self.NN.predict(np.expand_dims(cs, axis=0), verbose=0)[0]
        pred = self.TL.edges[np.argmax(outs)] # elige el estado de maxima probabilidad de softmax
        id = self.TL.edge_id[pred]
        
        if self.verbose:
            print(f'\n Prediccion: {pred}  id: {id}')
        return id
    
    def fitness(self, cfg='f0'):
        if cfg == 'f0':
            return self.steps
        elif cfg == 'f1':
            return self.f1
        elif cfg == 'f2':
            return self.f2

    def run(self):
        ei = 0 # estado inicial (semaforo 0 verde)
        self.steps = 0 # numero de steps trasncurridos
        dy = 2 # delta amarillo
        dg = 20 # delta verde
        auxt = 0 # auxiliar para control de semaforos
        isGreen = True # estado verde o amarillo
    
        #t0 = Traffic_light("S1","E1","-E3","E5","-E4")
        #A=[]
        #B=[]
        self.f1 = 0 # fitness unos 
        self.f2 = 0 # fitnes dos
        id_pred = 0
        while traci.simulation.getMinExpectedNumber() > 0 and self.steps<self.worst:
            traci.simulationStep() # avanza un step en la simulacion
            
            # si se alcanzo dg y algun semaforo esta en verde
            if auxt == dg and isGreen: 
                auxt = 0 # reinicia contador auxiliar
                cs = np.array([self.TL.get_num_car(id) for id in self.TL.edges], dtype=np.float32)
                ts = np.array([self.TL.getwait(id) for id in self.TL.edges])
                id_pred = self.control(cs) # se realiza una prediccion del siguiente estado con el control
                self.f1 += np.sum(cs)
                self.f2 += np.sum(ts)
                if self.TL.get_phase()==id_pred: # si la fase predicha es identica a la actual
                    pass
                else: # si la prediccion es distinto al estado actual
                    isGreen = False
                    self.TL.set_phase(self.TL.get_phase()+1) # fase amarilla del estado actual
                    ei = ei+1
            
            # si se alcanzo dy y algun semaforo esta en amarillo
            elif auxt==dy and not isGreen:
                self.TL.set_phase(id_pred) # cambia a la fase predicha por el control
                ei = id_pred
                isGreen = True
                auxt = 0
            auxt += 1
            self.steps += 1 # actualiza el contador de steps
        
        # cerramos el traci
        traci.close()
        sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("--version", type="int",default=0, help="run the commandline version of sumo")    
    options, args = optParser.parse_args()
    return options

if __name__ == '__main__':
 # ejemplo semaforos random
    random.seed(0) # semilla de semaforos
    options = get_options()
    if options.nogui:
        nog=False
    else:
        nog=True
    if options.version==0:
    # instanciamos la simulacion
        test = SimStateRandom(seed=78, gui=nog, verbose=False,act_rou=False)
	
    # se corre la simulacion aleatoria
        test.run()
        print(f"\nSteps totales: {test.fitness('f0')}")
        print(f"f1: {test.fitness('f1')}")
        print(f"f2: {test.fitness('f2')}\n")
    elif options.version==1:
	#se corre la simulacion normal
        run(nog)
    else:
    # se imprime el fitness
    # ejemplo red neuronal
        max_steps = 4000 # maximo de steps en la simulacion antes de forzar el cierre
    
    # lectura del genotipo
        gen = pd.read_csv('optimo.txt', header=None).values[:,0]
        print(gen.shape, gen.dtype)
    
    # instanciamos la simulacion
        test = SimStateNN(gen=gen, seed=78, gui=nog, verbose=False, worst=max_steps,act_rou=False)

    # se corre la simulacion
        test.run()



    # se imprime el fitness
        print(f"\nSteps totales: {test.fitness('f0')}")
        print(f"f1: {test.fitness('f1')}")
        print(f"f2: {test.fitness('f2')}\n")
