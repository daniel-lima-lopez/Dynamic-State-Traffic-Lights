
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
        if num>7:
            self.phase=0
        else:
            self.phase=num
        traci.trafficlight.setPhase(self.ID,self.phase)

    
        
        
def control(cs):
    #print(cs)
    return random.choice([0, 2, 4, 6])   
        
def run(control=control):
    """execute the TraCI control loop"""
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
    f1=0
    f2=0
    id_pred=0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        if auxt==dg and isGreen:
            id_pred=control(1)
            auxt=0
            ns = np.array([t0.get_num_car(id) for id in ["E1","-E3","E5","-E4"]])
            ts = np.array([t0.getwait(id) for id in ["E1","-E3","E5","-E4"]])
            f1 += np.sum(ns)
            f2 += np.sum(ts)
            if t0.get_phase()==id_pred:
                pass
            else:
                isGreen=False
                t0.set_phase(t0.get_phase()+1)
                ei=ei+1
                
        elif auxt==dy and not isGreen :
            t0.set_phase(id_pred)
            ei=id_pred
            isGreen=True
            auxt=0
        auxt+=1
        steps+=1


        '''i += 1
        if ultimo coche llego a su destino:
            break'''
            


    print(steps)
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
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    # first, generate the route file for this simulation

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "osm.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
