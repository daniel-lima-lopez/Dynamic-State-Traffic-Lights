# Dynamic-State-Traffic-Lights
This project presents a proposal to implement a dynamic state traffic light system, which adapts to conditions in real time to optimize the trafic flow.

The following video shows a comparison between our trained model and a conventional traffic light system:

## Instalation
In order to try our model, a basic installation of SUMO is needed (see SUMO oficial installation). Moreover, the Traffic Control Interface and SUMO python libraries must be installed to. You can install these libraries using pip:
```bash
pip install traci
```
```bash
pip install sumolib
```

## Method description
The proposed method consists of a traffic light system whose states are controlled by a neural network, which receives as input the number of cars in each lane.

Regarding the neural network training, genetic algorithms are used to optimize the weights configuration. In this approach, the genetic algorithm seeks to minimize the time needed to handle a defined traffic flow. In this way, the algorithm optimizes the neural network configuration to control traffic appropriately.

## Training








Ejemplo del funcionamiento del proyecto considerando la misma configuracion de rutas:
https://youtu.be/caAPAvuc0jY
[![](https://markdown-videos.deta.dev/youtube/caAPAvuc0jY)](https://youtu.be/caAPAvuc0jY)
