# Main file

import numpy as np
import simpy
#import simpy.rt

REALTIME = 0
SEED = 42
TOTALHAULTRUCKS = 5
GOLINETIMEVAR = 15
TOTALSIMTIME = 12*60
MEANDEPARTTIME = 30
VARDEPARTTIME = 10
LASTLOADTIME = TOTALSIMTIME-60 #After this time, default response after dumping is to return to go-line
MEANLOADTIME = 3

GOLINETODIGGER = 1.2 #Km goline to digger
EX1HAULROUTEDIST = 1.9 #Km

class HaulTruck():
    def __init__(self,env,id):
        # Self defines
        self.id = id
        self.name = f'rd{id:03d}'
        self.GasLevel = np.random.uniform(10.0,100.0)
        self.DieselLevel = np.random.uniform(10.0,100.0)
        self.PreStartTime = np.random.normal(30,5)
        self.Loaded = False
        self.CurrentLocation = 1
        self.env = env

        env.process(self.source())

    def source(self):
        yield env.timeout(self.PreStartTime)
        env.process(self.HaulRoad())

    def LoadingAtDigger(self):
        queueEnterTime = env.now
        print(f'{env.now:0.2f} {self.name}: Queuing for EX1')
        with digger.request() as req:
            yield req
            self.Loaded = True
            self.CurrentLocation = 2
            loadStartTime = env.now
            queueTime = env.now - queueEnterTime
            print(f'{env.now:0.2f} {self.name}: Loading at EX1, queue time was {queueTime:7.2}')
            loadtime = np.random.normal(MEANLOADTIME, 1)
            yield env.timeout(loadtime)
            env.process(self.HaulRoad())

    def HaulRoad(self):
        if not self.Loaded:
            if env.now > 690:
                print(f'{env.now:0.2f} {self.name}: Returning to Go-Line')
                speed = np.random.normal(40, 2)
                time = GOLINETODIGGER * 60 / speed
                yield env.timeout(time)
                print(f'{env.now:0.2f} {self.name}: Parked at Go-Line')
            else:
                print(f'{env.now:0.2f} {self.name}: Moving to Excavator')
                speed = np.random.normal(40, 2)
                time = EX1HAULROUTEDIST * 60 / speed
                yield env.timeout(time)
                env.process(self.LoadingAtDigger())
        else:
            print(f'{env.now:0.2f} {self.name}: Hauling to Tip')
            speed = np.random.normal(25, 2)
            time = EX1HAULROUTEDIST * 60 / speed
            yield env.timeout(time)
            env.process(self.TipPoint())

    def TipPoint(self):
        queueEnterTime = env.now
        with tippoint.request() as req:
            yield req
            self.Loaded = False
            self.CurrentLocation = 3
            tipStartTime = env.now
            queueTime = env.now - queueEnterTime
            print(f'{env.now:0.2f} {self.name}: Tipping Started, queue time was {queueTime:7.2f}')
            tipTime = np.clip(np.random.normal(MEANLOADTIME*0.33, 0.33),0)
            yield env.timeout(tipTime)
            env.process(self.HaulRoad())


if REALTIME == 1:
    env = simpy.rt.RealtimeEnvironment(factor=0.3)
else:
    env = simpy.Environment()

global digger
global tippoint
digger = simpy.Resource(env)
tippoint = simpy.Resource(env,3)

for i in range(TOTALHAULTRUCKS):
    HaulTruck(env, i)

env.run(until=720)