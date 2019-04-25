import random
import pyrtl
from pyrtl import *
#Instruction Memory _
#Wires are the input and ouptut interface

def rom_data_func(address):
    return 31-2 * address
rom_data_array = [rom_data_func(a) for a in range(16)]
rom1 = RomBlock(bitwidth=32,addrwidth= 32, romdata= rom_data_func, max_read_ports=10)
rom_add_1 = Input(32,"rom_in")
rom_out_1 = Output(32,"rom_out_1")
temp1 = rom1[rom_add_1]
rom_out_1<<= temp1

random.seed(4839483)

simvals = {
'rom_in':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1]}

sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for cycle in range(len(simvals['rom_in'])):
    sim.step({k: v[cycle] for k, v in simvals.items()})

sim_trace.render_trace()
