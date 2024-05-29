#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2022 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

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





class Traffic_light:
    def __init__(self, id, edge1,edge2,edge3,edge4):
    
        self.ID=id
        self.edge1=edge1
        self.edge2=edge2
        self.edge3=edge3
        self.edge4=edge4
        self.phase=self.get_phase()
    def lastcar1(self):
        return traci.edge.getLastStepVehicleNumber(self.edge1)
    def lastcar2(self):
        return traci.edge.getLastStepVehicleNumber(self.edge2)
    def lastcar(self,edge):
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
        
        
                        
    def control(self,other,phase): 
       # print(traci.trafficlight.getPhaseDuration(self.ID))
        if(self.lastcar1()>self.lastcar2() and self.lastcar1()>10):
        #    print(self.getwait(self.edge2))
            if(self.getwait(self.edge2)<200):
                traci.trafficlight.setPhase(self.ID,phase[0])
        elif(self.lastcar1()<self.lastcar2() and self.lastcar2()>6):
            traci.trafficlight.setPhase(self.ID,phase[1])
            if(self.getwait(self.edge1)<200):
                traci.trafficlight.setPhase(self.ID,phase[1])
        elif(other.lastcar1()-self.lastcar1()>0 and self.lastcar2()<=5):
            traci.trafficlight.setPhase(self.ID,phase[0])
    
def metrics(edge,val):
    if val:
        return traci.edge.getWaitingTime(edge)
    else:
        return traci.edge.getLastStepVehicleNumber(edge)
def run():
    """execute the TraCI control loop"""
    step = 0
    t0=Traffic_light("S1","E1","-E3","E5","-E4")
    print(t0.get_phase_time(),t0.get_phase())
    A=[]
    B=[]
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if step%5==0:
            t0.evalu(step)
            A.append(metrics("E1",True))
            B.append(metrics("E1",False))
        if step>1000:
            break  
        step += 1
    np.savetxt('wait.csv', A, fmt="%d", delimiter=",")
    np.savetxt('numcar.csv', B, fmt="%d", delimiter=",")
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
