import pyrtl
from pyrtl import *
import io
import random
from pyrtl.analysis import area_estimation, TimingAnalysis
import logging
import threading
import time


# Fetch Unit With Multithreading(SIMD)
# Program Counter with an initialized Value
class PC():
    first_state= Input(1,'fs')
    next_state = Input(1,'ns')
    #global npc
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

#Define 4 program counters
pc1 = PC()
pc2 = PC()
pc3 = PC()
pc4 = PC()


# 32 BIT ADDER updates the value of Program Counter
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


current_pc1 = pc1.npc #current pc value
current_pc2 = pc2.npc
current_pc3 = pc3.npc
current_pc4 = pc4.npc
const_val = pyrtl.Const("32'b1")
global sumadder1,sumadder2,sumadder3,sumadder4
sumadder1,carry_out = ripple_add(current_pc1, const_val, 0)
sumadder2,carry_out = ripple_add(current_pc2, const_val, 0)
sumadder3,carry_out = ripple_add(current_pc3, const_val, 0)
sumadder4,carry_out = ripple_add(current_pc4, const_val, 0)


#Multiplexer takes in the PC Value of from my_adder
def multiplex():
    global a1,a2,a3,a4
    a1 = sumadder1#  pc value from adder
    a2= sumadder2
    a3= sumadder3
    a4 = sumadder4
    wv1= Input(1,'wv1')
    wv2 = Input(1,'wv2')
    wv3 =Input(1,'wv3')
    wv4 =Input(1,'wv4')
    state = pyrtl.Register(32, 'state1')
    #consta_val = pyrtl.Const("32'b1")# pc value calculated in execute stage,redundant here
    next_pc1 = Output(32,"next_pc1")
    next_pc2 = Output(32,"next_pc2")
    next_pc3 = Output(32,"next_pc3")
    next_pc4 = Output(32,"next_pc4")
    #value from execute stage
    # sel = Input(1, "sel")
    # newvalue_pc = select(sel=1,truecase = a1,falsecase = a0)  # next_pc is the new value for program counter
    with pyrtl.conditional_assignment:
        with wv1:
            state.next |= a1
        with wv2:
            state.next |= a2
        with wv3:
            state.next |= a3
        with wv4:
            state.next |= a4
            with pyrtl.otherwise:  # token received but in state where we can't handle it
                pass
    next_pc1 <<= a1
    next_pc2 <<= a2
    next_pc3 <<= a3
    next_pc4 <<= a4

multiplex()

#Instruction Memory
class InstructionMem():
    global temp1,temp2,temp3,temp4
    def rom_data_func(self,address):
        self.address = address
        return 31-2 * address

    def readMemory(self):
        rom_data_array = [self.rom_data_func(a) for a in range(16)]
        rom1 = RomBlock(bitwidth=32,addrwidth= 32, romdata= rom_data_array, max_read_ports=5)
        rom_add_1 = Input(32,"rom_in")
        rom_add_2 = Input(32,"rom_in_2")
        rom_add_3 = Input(32,"rom_in_3")
        rom_add_4 = Input(32,"rom_in_4")
        a1 = rom_add_1
        a2 = rom_add_2
        a3 = rom_add_3
        a4 = rom_add_4
        global temp1,temp2,temp3,temp4
        temp1 = rom1[rom_add_1]
        temp2 = rom1[rom_add_2]
        temp3 = rom1[rom_add_3]
        temp4 = rom1[rom_add_4]
        global rom_out_1,rom_out_2,rom_out_3,rom_out_4

        def stage0():
            rom_out_1 = WireVector(32,"rom_out_1")
            rom_out_1 <<= temp1[0:7]
        def stage1():
            rom_out_2 = WireVector(32,"rom_out_2")
            rom_out_2 <<= temp2[3:10]
        def stage2():
            rom_out_3 = WireVector(32,"rom_out_3")
            rom_out_3 <<= temp3[2:16]
        def stage3():
            rom_out_4 = WireVector(32,"rom_out_4")
            rom_out_4 <<= temp4[4:20]
        t = threading.Thread(target = stage0) # Multithreading for different instructions
        t.start()
        t2 = threading.Thread(target =stage1)
        t2.start()
        t3 = threading.Thread(target = stage2)
        # helpful if you want it to die automatically
        t3.start()
        t4 = threading.Thread(target =stage3)
        t4.start()
        t.join()
        t2.join()
        t3.join()
        t4.join()
     # return rom_out_1,rom_out_2,rom_out_3,rom_out_4,temp1,temp2,temp3,temp4









# #Instruction Fetch Register
# def InstrReg():
#     NPCin,instin = sumadder, temp1 # Input is the PC Value from Adder and Instruction from Memory
#     NPCout,instout = Output(32,'NPCout'), Output(32,'instout')#Output is the PC Value from Adder and Instruction from Memory
#     #pass new values to the next stage of the circuit
#     NPCout <<= NPCin
#     instout <<= instin
#     return NPCin,instin
# InstrReg()

#Test Hardware using Simulation Class
def simul():
    random.seed(4839483)

    simvals = {
    'rom_in':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
    'rom_in_2':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
    'rom_in_3':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
    'rom_in_4':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
    'wv1': [random.randint(0,1) for i in range(20)],
    'wv2': [random.randint(0,1) for i in range(20)],
    'wv3': [random.randint(0,1) for i in range(20)],
    'wv4': [random.randint(0,1) for i in range(20)],
    'npc':[random.randint(0,1) for i in range(20)],
    'fs': [random.randint(0,1) for i in range(20)],
    'ns': [random.randint(0,1) for i in range(20)]
    }



    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace)
    # for cycle in range(15):
    #     sim.step({'wv1': random.choice([0, 1]),
    #     'wv2': random.choice([0, 1]),
    #     'wv3': random.choice([0, 1]),
    #     'wv4': random.choice([0, 1]),
    #     'npc':random.choice([0, 1]),
    #     'fs': random.choice([0, 1]),
    #     'ns': random.choice([0, 1])})
    for cycle in range(len(simvals['rom_in'])):
        sim.step({k: v[cycle] for k, v in simvals.items()})

    print('---FETCH UNIT ---')
    sim_trace.render_trace()

print(pyrtl.working_block())
print()

def run_synth():# Run Optimization and Synthesis
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



if __name__ == '__main__':
    abc = InstructionMem()
    abc.rom_data_func(16)
    abc.readMemory()
    simul()
    run_synth()
