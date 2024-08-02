import Simulations as sim

seed = 0 # semilla 
gui_state = True # estado para mostrar o no la animacion

# experimento base
test_base = sim.SimBase(seed=seed, gui=gui_state, verbose=False, steps=1000)
test_base.run()
print(f'steps: {test_base.fitness()}')