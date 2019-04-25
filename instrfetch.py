import pyrtl
from pyrtl import *

def instrfetch.py():
    NPCin,instin = Input(32,'NPCin'), Input(32,'instin')
    NPCout,instout = Output(32,'NPCout'), Output(32,'instout')
    #pass new values to the next stage of the circuit

    NPCout <<= NPCin
    instout <<= instin

    sim = FastSimulation()# need to find out how to pass values into Inputs and Outputs
    sim.step({NPCin: 1,instin: 5})
    print(sim.inspect(NPCin))
    sim.tracer.print_trace(compact=True)
