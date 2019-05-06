import pyrtl
from pyrtl import *
import io
import random
from pyrtl.analysis import area_estimation, TimingAnalysis
reset_working_block()


#SIMPLE FETCH UNIT

# Program Counter with an initialized Value
def pc():
    first_state= Input(1,'fs')
    next_state = Input(1,'ns')
    global npc
    global newvalue_pc
    npc = Input(32,'npc')
    global pcvalue
    pcvalue = Register(32, 'pcvalue')
    #value = Output(32,'pc_out')
    try:
        with pyrtl.conditional_assignment:
            with first_state:  # signal of highest precedence
                pcvalue.next |= npc
            with next_state:  # if token received, advance state in counter sequence
                pcvalue.next |= newvalue_pc
    except NameError as e:
        pass
    else:
        pcvalue.next |= npc

pc()


# 32 Bit Adder  updates the value of Program Counter
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


current_pc = npc #current pc value
const_val = pyrtl.Const("32'b1")
global sumadder
sumadder,carry_out = ripple_add(current_pc, const_val, 0)


#Multiplexer takes in the PC Value of from my_adder
def multiplex():
    a0 = sumadder#  pc value from adder
    a1 = pyrtl.Const("32'b1")# pc value calculated in execute stage
    next_pc = Output(32,"next_pc")
    #value from execute stage
    sel = Input(1, "sel")
    newvalue_pc = select(sel=1,truecase = a1,falsecase = a0)  # next_pc is the new value for program counter
    next_pc <<= newvalue_pc
multiplex()

#Instruction Memory

def rom_data_func(address):
    return 31-2 * address


rom_data_array = [rom_data_func(a) for a in range(16)]
rom1 = RomBlock(bitwidth=32,addrwidth= 32, romdata= rom_data_array,asynchronous= False, max_read_ports=5)
rom_add_1 = Input(32,"rom_in")
a1 = rom_add_1
temp1 = rom1[rom_add_1]
rom_out_1 = WireVector(32,"rom_out_1")
rom_out_1 <<= temp1[0:7]



#Instruction Fetch Register
def InstrReg():
    NPCin,instin = sumadder, temp1 # Input is the PC Value from Adder and Instruction from Memory
    NPCout,instout = Output(32,'NPCout'), Output(32,'instout')#Output is the PC Value from Adder and Instruction from Memory
    #pass new values to the next stage of the circuit
    NPCout <<= NPCin
    instout <<= instin
    return NPCin,instin
InstrReg()


# Define Hardware
simvals = {'rom_in':[1, 11, 4, 2, 7, 8, 2, 15],
'npc':[random.randint(0,1) for i in range(9)],
'sel':[random.randint(0,1) for i in range(9)],
'fs':[random.randint(0,1) for i in range(9)],
'ns':[random.randint(0,1) for i in range(9)]}
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.Simulation(tracer=sim_trace)
for cycle in range(len(simvals['rom_in'])):
    sim.step({k: v[cycle] for k, v in simvals.items()})

print('---FETCH UNIT ---')
sim_trace.render_trace()

def run_synth():
    print("logic = {:2f} mm^2, mem={:2f} mm^2".format(*area_estimation()))
    t = TimingAnalysis()
    print("Max freq = {} MHz".format(t.max_freq()))
    print("")
    print("Running synthesis...")
    synthesize()
    print("logic = {:2f} mm^2, mem={:2f} mm^2".format(*area_estimation()))
    t = TimingAnalysis()
    print("Max freq = {} MHz".format(t.max_freq()))
    print("")
    print("Running optimizations...")
    optimize()
    total = 0
    for gate in working_block():
        if gate.op in ('s', 'c'):
            pass
        total += 1
    print("Gate total: " + str(total))
    print("logic = {:2f} mm^2, mem={:2f} mm^2".format(*area_estimation()))
    t = TimingAnalysis()
    print("Max freq = {} MHz".format(t.max_freq()))
run_synth()
