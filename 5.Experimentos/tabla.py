import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

base = pd.read_csv('exp_base.txt', header=None, sep=' ').values[:,1]
gen = pd.read_csv('info.csv', sep=',').values[:,1]

plt.plot(range(50), base, label='Normal')
plt.plot(range(50), gen, label='Red Neuronal')

plt.ylabel('Steps')
plt.xlabel('Generacion')
plt.legend(loc='best')
plt.savefig('vsGen.png', bbox_inches='tight', dpi=300)

plt.show()