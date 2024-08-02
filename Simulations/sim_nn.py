import Simulations as sim
import pandas as pd

seed = 0 # semilla 
gui_state = True # estado para mostrar o no la animacion

# experimento base
gen = pd.read_csv('optimo.txt', header=None).values[:,0]
test_nn = sim.SimStateNN(gen=gen, seed=seed, act_rou=False, gui=gui_state, verbose=False, steps=1000, worst=100000)
test_nn.run()
print(f'steps: {test_nn.fitness()}')