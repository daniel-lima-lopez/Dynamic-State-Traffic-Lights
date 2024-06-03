import Simulations as sim
import pandas as pd
import numpy as np

steps_base = []
steps_nn = []
exps = 10
for i in range(0,exps):
    # experimento base
    test_base = sim.SimBase(seed=i*100, gui=False, verbose=False, steps=1000)
    test_base.run()
    steps_base.append(test_base.fitness())

    # experimento NN
    gen = pd.read_csv('optimo_david2.txt', header=None).values[:,0]
    test_nn = sim.SimStateNN(gen=gen, seed=i*100, act_rou=False, gui=False, verbose=False, steps=1000, worst=100000)
    test_nn.run()
    steps_nn.append(test_nn.fitness('f0'))

    print(f'exp: {i}  base: {test_base.fitness()}  NN: {test_nn.fitness("f0")}')

print(f'MEAN  base: {np.mean(steps_base)}  NN: {np.mean(steps_nn)}')

with open('vsModels.csv', 'w') as f:
    f.write('Exp, Base, NN\n')
    for i in range(exps):
        f.write(f'{i},{steps_base[i]},{steps_nn[i]}\n')
    f.write(f'MEAN  base: {np.mean(steps_base)}  NN: {np.mean(steps_nn)}')