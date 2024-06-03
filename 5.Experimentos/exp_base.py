import Simulations as sim

steps = []
exps = 50
for i in range(0,exps):
    test = sim.SimBase(seed=i, gui=False, verbose=False)
    test.run()
    print(f'exp: {i}  steps: {test.fitness()}')
    steps.append(test.fitness())

with open('exp_base.txt', 'w') as f:
    for i in range(exps):
        f.write(f'{i} {steps[i]}\n')