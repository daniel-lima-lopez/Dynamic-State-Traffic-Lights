import numpy as np
import random
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
from pymoo.util.display.column import Column
from pymoo.util.display.output import Output
from pymoo.algorithms.soo.nonconvex.ga import GA

from test_RNN

class MyProblem(Problem):
	def __init__(self,waitcar,numcar, n_atri,num_o, l, u):
		self.Wait=waitcar
		self.Car=numcar
		self.n_atri=n_atri
		super().__init__(n_var=self.n_atri,
			n_obj=num_o,
			n_eq_constr=0,
			xl=l,
			xu=u)
        
	def _evaluate(self, x, out, *args, ** kwargs):
		out["F"]= [f1,f2]	
		out["H"]=[phi]
                    

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
	numcar=np.loadtxt("numcar.csv")
	len_a=790;
	num_o=1;
	print(np.iinfo(np.int32).min)
	#l=np.array([np.iinfo(np.int32).min for i in range(len_a)])
	#u=np.array([np.iinfo(np.int32).max for i in range(len_a)])
	l=np.array([-1 for i in range(len_a)])
	u=np.array([1 for i in range(len_a)])

	prob=MyProblem(waitcar,numcar,len_a,num_o, l, u)
	algorithm= NSGA2(
		pop_size=100,
		sampling=MySampling(),
		crossover=TwoPointCrossover(prob=0.9),
		mutation=MyMutation(1/4),
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

	pareto_op = np.array(res.X)
	pareto_fen = np.array(res.F)
	print(pareto_op)
	print(pareto_fen)
	np.savetxt("testores.txt", pareto_op, delimiter=" ", fmt="%0.3f")

