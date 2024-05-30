
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import numpy as np
# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

#controla semaforo aleatorio
random.seed(42)


class Traffic_light:
    def __init__(self, id, edge1,edge2,edge3,edge4, dt=5):
        self.dt = dt

        self.dtrans = int(0.2*dt)

    
        self.ID=id
        self.edge1=edge1
        self.edge2=edge2
        self.edge3=edge3
        self.edge4=edge4
        self.phase=self.get_phase()
        
    def get_num_car(self,edge):
        return traci.edge.getLastStepVehicleNumber(edge)
        
    def getwait(self,edge_id):
        return traci.edge.getWaitingTime(edge_id)
        
    def get_phase_time(self):
        return traci.trafficlight.getPhaseDuration(self.ID)
        
    def get_phase(self):
        return traci.trafficlight.getPhase(self.ID)
        
    def evalu(self,step):
        print(self.get_phase_time(),self.get_phase())
        if step%40==0:
            self.set_phase(self.phase+1)
        elif (self.phase%2)-1==0:
            self.set_phase(self.phase+1)
            
    def set_phase(self,num):
        

        '''
        e0: semaforo 0 en verde
        e2: semaforo 2 en verde
        e4: semaforo 4 en verde
        e6: semaforo 6 en verde

        e0 -> e1 -> e6
        e0
        get_phase()+1
        e1
        set_phase(epredi)
        5s

        
        
        David5
        caso diferente
        set_phase(epred_current)(5s) -> set_pahese(epred_current+1) -> set_phase(epred_next)
         
        caso igual
        set_phase(epred_current)(5s) -> setphase(epred_next)
        
        if step%5==0:
            id_phase=Control()
            if (get_phase==id_phase):
                pass
            else:
                set_phase(get_phase+1)
                
                
        
        



        e0: semaforo 0 en verde
        e2: semaforo 2 en verde
        e4: semaforo 4 en verde
        e6: semaforo 6 en verde

        e1: semaforo 0 en amarillo
        e3: semaforo 2 en amarillo
        e5: semaforo 4 en amarillo
        e7: semaforo 6 en amarillo 
            


        #KAMIGOD    
        e6  e7  e0
        e0  e1  e6
        ei = 0 # estado inicial
        steps = 0
        while not finish:
            simulationStep()
            if steps%2==0:
                if getphase%2-1==0 #e1 impar
                    setphase(id_phase) #e6
            if steps % 5 == 0:
                get_phase #e0
                id_phase = control() 
                id_phase #e6
                if id==ini:
                    pass
                else:
                    set_phase(get_phase+1) #e1
            
            steps += 1


        # DANIEL ei -> ei+1 -> epred
        ei = 0 # estado inicial
        steps = 0
        dy = 2 # delta amarillo
        dg = 10 # delta verde
        auxt = 0
        isGreen = True
        i = 1
        while not finish:
            simulationStep()
            
            if isGreen and auxt==dg: # si estamos con semaforo verde y se alcanzo dg
                id_pred = Control()
                auxt = 0
                if ei = id_pred: # si se predice el mismo estado al actual
                    pass
                else: # si el estado predicho es distinto
                    isGreen = False
                    set_phase(ei+1) # estado siguiente al actual (amarillo)
                    ei = ei+1 # se actualiza el estado
            else:
                if auxt==dy: # si se alcanzo dy
                    set_phase(id_pred)
                    ei = id_pred # actualiza el estado
                    isGreen = True
                    auxt = 0
                
            auxt += 1
            steps += 1
            
        

        ...
        '''
        if num>7:
            self.phase=0
        else:
            self.phase=num
        traci.trafficlight.setPhase(self.ID,self.phase)

    
        
        
def control(cs):
    #print(cs)
    return random.randint(0,8)          
        
def run(control=control):
    """execute the TraCI control loop"""
    step = 0
    t0=Traffic_light("S1","E1","-E3","E5","-E4")
    #print(t0.get_phase_time(),t0.get_phase())
    
    A=[]
    B=[]

    f1 = 0
    f2 = 0
    
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        if step%t0.dt==0:
            
            # calcular fi
            ns = np.array([t0.get_num_car(ei) for ei in ["E1","-E3","E5","-E4"]])
            ts = np.array([t0.getwait(ei) for ei in ["E1","-E3","E5","-E4"]])

            id_phase = control(ns) # devuelve el id de la siguiente fase

            if id_phase==t0.get_phase():
                pass
            else:
                t0.set_phase(id_phase+1)
                if state = 'transicion':
                    t0.set_trans(id_phase)
                id state = 'new':
                    t0.set_phase(id_phase)

            
            #t0.evalu(step)
            t0.set_phase(id_phase)
            
            
            f1 += np.sum(ns)
            f2 += np.sum(ts)

        '''i += 1
        if ultimo coche llego a su destino:
            break'''
            


        step += 1
    print(step)
    print('TERMINO')
    print(f1,f2,'\n')

    traci.close()
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run

    sumoBinary = checkBinary('sumo')
    # first, generate the route file for this simulation

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "osm.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
