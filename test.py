import simpy
import numpy as np

class HaulTruck():
    def __init__(self,env,id):
        self.id = id
        self.name = f'rd{id:03d}'
        self.DieselLevel = 50.0
        self.env = env

        env.process(self.usefuel())
    def usefuel(self):
        tUsed = np.random.normal(10.0,1.0)
        yield env.timeout(tUsed)
        self.DieselLevel = self.DieselLevel - 0.5 * tUsed
        env.process(self.usefuel())
        print(f'{self.env.now:0.2f} {self.name} DieselLevel {self.DieselLevel:0.2f}')

env = simpy.Environment()

HaulTruck(env,0)
HaulTruck(env,1)
HaulTruck(env,2)


env.run(until=100)