# 16 Bit Adder Implementation
import random
import pyrtl
from pyrtl import *

def one_bit_add(a,b,carry_in):
    assert len(a)==len(b)==1
    sum = a^b^carry_in
    carry_out = a&b | a&carry_in |b & carry_in
    return sum,carry_out

def ripple_add(a,b,carry_in=0):
    a,b =pyrtl.match_bitwidth(a,b)
    if len(a) == 1:
        sumbits,carry_out = one_bit_add(a,b,carry_in)
    else:
        lsbit,ripplecarry = one_bit_add(a[0],b[0],carry_in)
        msbits,carry_out = ripple_add(a[1:],b[1:], ripplecarry)
        sumbits =pyrtl.concat(msbits,lsbit)
    return sumbits,carry_out

def my_adder(cpc):
    cpc = Input(bitwidth=32, name = 'cpc') #current pc value
    const_val = pyrtl.Const("32'b1")
    sumadder,carry_out = ripple_add(cpc, const_val, 0)
    cpc_out = Output(32, name='cpc_out')
    cpc_out <<= sumadder






sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for cycle in range(32):
    sim.step({
        'cpc': random.choice([0, 1])
        })
print('---32 Bit Adder Simulation ---')
sim_trace.render_trace(symbol_len=5, segment_size=5)
