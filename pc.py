import pyrtl
from pyrtl import *
import random



def pc():
    npc = Input(32, 'npc')
    pcvalue = Register(32, 'pcvalue')
    pc_output =Output(32,'pc_output')
    #pcvalue <<=wire_pcvalue
    #set the initial program count as 0
    pcvalue.next <<= npc
    pc_output <<= pcvalue
    sim_trace = SimulationTrace()#
    sim= Simulation(tracer = sim_trace)
    for cycle in range(15):
        sim.step({'npc': random.choice([0, 1])
        })
    sim_trace.render_trace(symbol_len=5, segment_size=5)

pc()


# # def pc():
# #     npc = Input(32, 'npc')
# #     pcvalue = Register(32, 'pcvalue')
# #     pc_output =Output(32,'pc_output')
# #     #pcvalue <<=wire_pcvalue
# #      #set the initial program count as 0
# #     pcvalue.next <<= npc
# #     pc_output <<= pcvalue
# INSTRUCTION_WIDTH = 32
# IMEM_ADDR_SIZE = 12
#
# IMem = MemBlock(bitwidth= INSTRUCTION_WIDTH, addrwidth=IMEM_ADDR_SIZE)
# pc = Register(IMEM_ADDR_SIZE)
# pc.incr = WireVector(1, "pcincr")
# with conditional_assignment:
#     with pc.incr:
#         pc.next |= pc +1
# pc.incr <<= 1
# instr=IMem[pc]
#
#

sim = SimulationTrace()#
sim= Simulation(tracer = sim_trace)
for cycle in range(15):
    sim.step({
    'pc_output':pc("00000000000011110")
    })

sim_trace.render_trace



# with pyrtl.conditional_assignment:
#     with reset ==1:
#             pcresult <<= "16b'1"
#     with pcwrite ==1:
#             pcresult <<= pcnext
#     return pcresult
