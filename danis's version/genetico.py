import numpy as np
import random
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.core.mutation import Mutation
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.operators.crossover.sbx import SBX
from pymoo.util.display.column import Column
from pymoo.util.display.output import Output
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation

from NNControls import *
from Simulations import *
import pandas as pd

class MyOutput(Output):
    def __init__(self):
        super().__init__()
        self.meanf = Column("Mean F",width=20)
        self.minf = Column("Min F",width=20)
        
        self.columns += [self.meanf, self.minf]
        self.metrics = []

    def update(self, algorithm):
        super().update(algorithm)

        # f son los fitnes de la poblacion actual
        self.meanf.set(np.mean(algorithm.pop.get("F"))) 
        self.minf.set(np.mean(algorithm.pop.get("F")))

        self.metrics.append([np.mean(algorithm.pop.get("F")), np.mean(algorithm.pop.get("F"))])

class MyProblem(Problem):
	def __init__(self, n_atri, num_o, l, u):
		self.n_atri = n_atri# tamano genotipo
		self.gen = 0 # generacion actual
		
		# inicializa el problema
		super().__init__(n_var=self.n_atri,
			n_obj=num_o,
			n_eq_constr=0,
			xl=l, # limite inferior
			xu=u) # limite superior
        
	def _evaluate(self, x, out, *args, ** kwargs):
		# generar los trips
		f=[]
		se = np.random.randint(0,1000)
		max_steps = 4000

		for i in range(x.shape[0]):
			# se actualiza la red con la configuracion del genotipo
			if i == 0:
				red = SimStateNN(gen=x[i], seed=self.gen, act_rou=True, gui=False, verbose=False, worst=max_steps)
			else:
				red = SimStateNN(gen=x[i], seed=self.gen, gui=False, verbose=False, worst=max_steps, act_rou=False)
			red.run()
			f.append(red.fitness("f0"))
		self.gen += 1
		f=np.array(f)
		#f=f.reshape((100,1))
		out["F"]= f	
		#out["H"]=[phi]
                    

#samplig
class MySampling(Sampling):
	def _do(self, problem, n_samples, **kwargs):
		X= 2*np.random.random_sample((n_samples,problem.n_atri))-1
		return X


if __name__=="__main__":
	len_a = 756 # longitud del genotipo
	num_o = 1 # numero de objetivos
	
	# limites de cada atributo (-1 a 1 para todos)
	l = np.array([-1 for i in range(len_a)])
	u = np.array([1 for i in range(len_a)])

	# definimos el problema
	prob=MyProblem(len_a, num_o, l, u)
	
	# instanciamos al algoritmo
	algorithm= GA(
		pop_size=100,
		sampling=MySampling(),
		crossover=SBX(prob=0.9),
		mutation=PolynomialMutation(prob=0.9),
    eliminate_duplicates=True
		)
    
	# condicion determino
	term=get_termination("n_gen",50)
	
	# estadisticos
	outS = MyOutput()

	# se minimiza el problema con el algoritmo
	res=minimize(
		prob,
		algorithm,
		termination = term,
		verbose = True,
		output = outS
		)
	
	# se recupera informacion de las generaciones
	info = np.array(outS.metrics)
	data = pd.DataFrame({'means': info[:,0],
					     'mins': info[:,1]})
	data.to_csv('info_09.csv', index=False)
	
	# se recupera el genotipo de la mejor configuracion	
	optimo = np.array(res.X)
	np.savetxt("optimo_09.txt", optimo, delimiter=" ", fmt="%0.3f")