import random
import pyrtl
from pyrtl import *
#Instruction Memory _
#Wires are the input and ouptut interface



class InstructionMem():
    def rom_data_func(self,address):
        self.address = address
        return 31-2 * address

    def readMemory(self):
        rom_data_array = [self.rom_data_func(a) for a in range(16)]
        rom1 = RomBlock(bitwidth=32,addrwidth= 32, romdata= rom_data_array, max_read_ports=5)
        rom_add_1 = Input(32,"self.rom_in")
        rom_add_2 = Input(32,"self.rom_in_2")
        rom_add_3 = Input(32,"self.rom_in_3")
        rom_add_4 = Input(32,"self.rom_in_4")
        temp1 = rom1[rom_add_1]
        temp2 = rom1[rom_add_2]
        temp3 = rom1[rom_add_3]
        temp4 = rom1[rom_add_4]
        global rom_out_1,rom_out_2,rom_out_3,rom_out_4
        rom_out_1 = Register(32,"rom_out_1")
        rom_out_2 = Register(32,"rom_out_2")
        rom_out_3 = Register(32,"rom_out_3")
        rom_out_4 = Register(32,"rom_out_4")
        rom_out_1.next <<= temp1[0:7]
        rom_out_2.next <<= temp2[3:10]
        rom_out_3.next <<= temp3[2:16]
        rom_out_4.next <<= temp4[4:20]
        return rom_out_1,rom_out_2,rom_out_3,rom_out_4



    def simul(self):
        random.seed(4839483)

        simvals = {
        'self.rom_in':[11],
        'self.rom_in_2':[13],
        'self.rom_in_3':[15],
        'self.rom_in_4':[5]
        }

        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.FastSimulation(tracer=sim_trace)
        for cycle in range(len(simvals['self.rom_in'])):
            sim.step({k: v[cycle] for k, v in simvals.items()})

        sim_trace.render_trace()

class SimplePipeline(object):
    def __init__(self):
        self._pipeline_register_map = {}
        self._current_stage_num = 0
        stage_list = [method for method in dir(self) if method.startswith('stage')]
        for stage in sorted(stage_list):
            stage_method = getattr(self, stage)
            stage_method()
            self._current_stage_num += 1

    def __getattr__(self, name):
        try:
            return self._pipeline_register_map[self._current_stage_num][name]
        except KeyError:
            raise pyrtl.PyrtlError(
                'error, no pipeline register "%s" defined for stage %d'
                % (name, self._current_stage_num))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # do not do anything tricky with variables starting with '_'
            object.__setattr__(self, name, value)
        else:
            next_stage = self._current_stage_num + 1
            instructionreg_id  = str(self._current_stage_num) + 'to' + str(next_stage)
            rname = 'pipeinstruction_' + instructionreg_id + '_' + name
            new_pipereg = pyrtl.Register(bitwidth=len(value), name=rname)
            if next_stage not in self._pipeline_register_map:
                self._pipeline_register_map[next_stage] = {}
            self._pipeline_register_map[next_stage][name] = new_pipereg
            new_pipereg.next <<= value

class SimplePipelineExample(SimplePipeline):

    def __init__(self):
        self._loopback = pyrtl.WireVector(1, 'loopback')
        self._rom_out_1 = rom_out_1
        self._rom_out_2 = rom_out_2
        self._rom_out_3 = rom_out_3
        self._rom_out_4 = rom_out_4
        super(SimplePipelineExample, self).__init__()

    def stage0(self):
        self.n = self._rom_out_1

    def stage1(self):
        self.n = self._rom_out_2

    def stage2(self):
        self.n = self._rom_out_3

    def stage3(self):
        self.n = self._rom_out_4

    def stage4(self):
        self._loopback<<= self.n

    def simul2(self):
        simvals = {
        'self.rom_in':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
        'self.rom_in_2':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
        'self.rom_in_3':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1],
        'self.rom_in_4':[1, 11, 4, 2, 7, 8, 2, 4, 5, 13, 15, 3, 4, 4, 4, 8, 12, 13, 2, 1]
        }
        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.FastSimulation(tracer=sim_trace)
        for cycle in range(len(simvals['self.rom_in'])):
            sim.step({k: v[cycle] for k, v in simvals.items()})
        sim_trace.render_trace()



if __name__ == '__main__':
    abc = InstructionMem()
    abc.rom_data_func(16)
    abc.readMemory()
    abc.simul()
    simplepipeline = SimplePipelineExample()
