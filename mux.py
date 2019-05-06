import pyrtl
from pyrtl import *

#def multiplexer():
a0 = Input(32,"a0")#  pc value from memory
a1 = Input(32,"a1")# pc value calculated in execute stage
npc = Output(32, "npc")
#value from execute stage
sel = Input(1)
npc <<= select(sel=0,truecase = a1,falsecase=a0)

#return npc or nex


sim = FastSimulation()# need to find out how to pass values into Inputs and Outputs
sim.step({sel:0,a1:1,a0:0})
print(sim.inspect(a0))
sim.tracer.print_trace(compact=True)
