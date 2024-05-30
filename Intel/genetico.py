import numpy as np
import random
import os 
from pymoo.core.crossover import Crossover
from pymoo.operators.crossover.pntx import TwoPointCrossover
#from pymoo.core.problem import ElementwiseProblem
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.core.mutation import Mutation
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.util.display.column import Column
from pymoo.util.display.output import Output
from pymoo.algorithms.soo.nonconvex.ga import GA

from NNControls import *
from Simulations import *

class MyProblem(Problem):
	def __init__(self,waitcar,numcar, n_atri,num_o,num_est, l, u):
		self.Wait=waitcar
		self.Car=numcar
		self.n_atri=n_atri# tama\~no genotipo
		super().__init__(n_var=self.n_atri,
			n_obj=num_o,
			n_eq_constr=0,
			xl=l,
			xu=u)
        
	def _evaluate(self, x, out, *args, ** kwargs):
		# generar los trips
		f=[]
		se=np.random.randint(0,1000)
		max_steps = 4000
		print(se)
		print(x[0].shape)
		for i in range(x.shape[0]):
			# se actualiza la red con la configuracion del genotipo
			red=SimStateNN(gen=x[i], seed=se, gui=False, verbose=False, worst=max_steps)
			red.run()
			f.append(red.fitness("f0"))

		f=np.array(f)
		#f=f.reshape((100,1))
		out["F"]= f	
		#out["H"]=[phi]
                    

#samplig
class MySampling(Sampling):
	def _do(self, problem, n_samples, **kwargs):
		X= 2*np.random.random_sample((n_samples,problem.n_atri))-1
		print(X)
		return X

#mutacion
class MyMutation(Mutation):
	def __init__(self, prob):
		self.pro=prob
		self.pr=0
		super().__init__()

	def _do(self, problem,X,**kwargs):	
		self.pr=np.random.random()
		for i in range(X.shape[0]):
			for j in range(X.shape[1]):
				if(self.pr<self.pro):
					X[i,j]=random.choice(np.unique(problem.space[:,j]))
		return X

#

'''
class MyOutput(Output):
    def __init__(self):
        super().__init__()
        self.f1_mean = Column("mean F1",width=20)
        self.f2_mean = Column("mean F2",width=20)
        self.columns += [self.f1_mean, self.f2_mean]
    def update(self, algorithm):
        super().update(algorithm)
        # f son los fitnes de la poblacion actual
        self.f1_mean.set(np.mean(algorithm.pop.get("F")[:,0])) 
        self.f2_mean.set(np.mean(algorithm.pop.get("F")[:,1]))
'''

if __name__=="__main__":
	waitcar=np.loadtxt("wait.csv")
	waitcar=waitcar.reshape((waitcar.shape[0],1))
	numcar=np.loadtxt("numcar.csv")
	print(numcar.shape[0])
	numcar=numcar.reshape((numcar.shape[0],1))
	len_a=756;
	num_o=1;
	num_est=8;
	print(np.iinfo(np.int32).min)
	#l=np.array([np.iinfo(np.int32).min for i in range(len_a)])
	#u=np.array([np.iinfo(np.int32).max for i in range(len_a)])
	l=np.array([-1 for i in range(len_a)])
	u=np.array([1 for i in range(len_a)])

	prob=MyProblem(waitcar,numcar,len_a,num_o,num_est, l, u)
	algorithm= GA(
		pop_size=100,
		sampling=MySampling(),
		#crossover=TwoPointCrossover(prob=0.9),
		#mutation=BitflipMutation(1/len_a),
    eliminate_duplicates=True
		)
    
	term=get_termination("n_gen",100)
	
	#outS = MyOutput()
	res=minimize(
		prob,
		algorithm,
		termination=term,
		verbose=True,
		#output=outS
		)

	optimo = np.array(res.X)
	fen = np.array(res.F)
	print(pareto_op)
	print(pareto_fen)
	np.savetxt("optimo.txt", optimo, delimiter=" ", fmt="%0.3f")

