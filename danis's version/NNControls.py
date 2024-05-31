import tensorflow as tf
import numpy as np

class StateTime(tf.keras.layers.Layer):
    def __init__(self, opts, t0=5, tf=15):
        super().__init__()
        self.opts = opts # numero de casos de semaforos considerados
        self.t0 = t0 # rango inferior de la ventana de tiempo
        self.tf = tf # rango superior de la ventana de tiempo
    
    def get_config(self):
        return {'opts': self.opts}

    def build(self, input_shape): # (batch, units)
        self.Wopt = self.add_weight(shape=(input_shape[-1], self.opts)) # matriz de pesos para opciones de control
        self.bopt = self.add_weight(shape=(self.opts,)) # bias para opciones de control

        self.Wt = self.add_weight(shape=(input_shape[-1],1)) # matriz de pesos para opciones de control
        self.bt = self.add_weight(shape=(1,)) # bias para opciones de control

    
    def call(self, Xs):
        yopt = tf.keras.activations.softmax(tf.matmul(Xs, self.Wopt) + self.bopt)
        yt = (self.tf-self.t0)*tf.keras.activations.sigmoid(tf.matmul(Xs, self.Wt) + self.bt) + self.t0

        ys = tf.concat([yopt, yt], axis=-1)
        
        return ys


class ControlStateTime(tf.keras.Model):
    def __init__(self, cs, u1=16, u2=32, opts=4):
        super().__init__()

        self.cs = cs
        self.u1 = u1
        self.u2 = u2
        self.opts = opts

        self.d1 = tf.keras.layers.Dense(units=self.u1, activation='relu', input_dim=self.cs)
        self.d2 = tf.keras.layers.Dense(units=self.u2, activation='relu')
        self.trafic = StateTime(opts=self.opts)

    def call(self, Xs):
        ys = self.d1(Xs)
        ys = self.d2(ys)
        ys = self.trafic(ys)

        return ys
    
    def get_gen(self):
        gen = []
        for layer in [self.d1, self.d2, self.trafic]:
            Ws = layer.get_weights()
            for wi in Ws:
                wi = np.array(wi)
                wi = wi.flatten(order='C')
                gen += list(wi)
        return np.array(gen)
    
    def set_phen(self, gen):
        aux = 0 # limite inferior para saber que variables tomar
        for layer in [self.d1, self.d2, self.trafic]:
            Ws = layer.get_weights()
            new_ws = []
            for wi in Ws:
                inc = np.prod(wi.shape)
                auxW = gen[aux:aux+inc]
                auxW = np.reshape(auxW, newshape=wi.shape)
                new_ws.append(auxW)
                aux += inc
            layer.set_weights(new_ws)


class ControlState(tf.keras.Model):
    def __init__(self, cs=4, u1=16, u2=32, opts=4):
        super().__init__()

        self.cs = cs # tamano del vector de entrada de la red
        self.u1 = u1
        self.u2 = u2
        self.opts = opts
        
        self.d1 = tf.keras.layers.Dense(units=u1, activation='relu')
        self.d2 = tf.keras.layers.Dense(units=u2, activation='relu')
        self.trafic = tf.keras.layers.Dense(units=opts, activation='softmax')
    
    def call(self, Xs):
        ys = self.d1(Xs)
        ys = self.d2(ys)
        ys = self.trafic(ys)

        return ys
    
    def get_gen(self):
        gen = []
        for layer in [self.d1, self.d2, self.trafic]:
            Ws = layer.get_weights()
            for wi in Ws:
                wi = np.array(wi)
                wi = wi.flatten(order='C')
                gen += list(wi)
        return np.array(gen)
    
    def set_phen(self, gen):
        aux = 0 # limite inferior para saber que variables tomar
        for layer in [self.d1, self.d2, self.trafic]:
            Ws = layer.get_weights()
            new_ws = []
            for wi in Ws:
                inc = np.prod(wi.shape)
                auxW = gen[aux:aux+inc]
                auxW = np.reshape(auxW, newshape=wi.shape)
                new_ws.append(auxW)
                aux += inc
            layer.set_weights(new_ws)