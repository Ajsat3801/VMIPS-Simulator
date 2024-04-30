import os
import argparse

class Config(object):
    def __init__(self, iodir):
        self.filepath = os.path.abspath(os.path.join(iodir, "Config.txt"))
        self.parameters = {} # dictionary of parameter name: value as strings.

        try:
            with open(self.filepath, 'r') as conf:
                self.parameters = {line.split('=')[0].strip(): int(line.split('=')[1].split('#')[0].strip()) for line in conf.readlines() if not (line.startswith('#') or line.strip() == '')}
            print("Config - Parameters loaded from file:", self.filepath)
            print("Config parameters:", self.parameters)
        except:
            print("Config - ERROR: Couldn't open file in path:", self.filepath)
            raise

class IMEM(object):
    def __init__(self, iodir):
        #self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "trace.asm"))
        self.instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.split('#')[0].strip() for ins in insf.readlines() if not (ins.startswith('#') or ins.strip() == '')]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)
            raise

    def Read(self, idx): # Use this to read from IMEM.
        #if idx < self.size:
            return self.instructions[idx].split()
        #else:
            #print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)
            #return -1

class DMEM(object):
    # Word addressible - each address contains 32 bits.
    def __init__(self, name, iodir, addressLen):
        self.name = name
        self.size = pow(2, addressLen)
        self.min_value  = -pow(2, 31)
        self.max_value  = pow(2, 31) - 1
        self.ipfilepath = os.path.abspath(os.path.join(iodir, name + ".txt"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, name + "OP.txt"))
        self.data = []

        try:
            with open(self.ipfilepath, 'r') as ipf:
                self.data = [int(line.strip()) for line in ipf.readlines()]
            print(self.name, "- Data loaded from file:", self.ipfilepath)
            # print(self.name, "- Data:", self.data)
            self.data.extend([0x0 for i in range(self.size - len(self.data))])
        except:
            print(self.name, "- ERROR: Couldn't open input file in path:", self.ipfilepath)
            raise

    def Read(self, idx): # Use this to read from DMEM.
        pass # Replace this line with your code here.

    def Write(self, idx, val): # Use this to write into DMEM.
        pass # Replace this line with your code here.

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)
            raise

class RegisterFile(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count
        self.vec_length = length # Number of 32 bit words in a register.
        self.reg_bits   = size
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        pass # Replace this line with your code.

    def Write(self, idx, val):
        pass # Replace this line with your code.

    def dump(self, iodir):
        opfilepath = os.path.abspath(os.path.join(iodir, self.name + ".txt"))
        try:
            with open(opfilepath, 'w') as opf:
                row_format = "{:<13}"*self.vec_length
                lines = [row_format.format(*[str(i) for i in range(self.vec_length)]) + "\n", '-'*(self.vec_length*13) + "\n"]
                lines += [row_format.format(*[str(val) for val in data]) + "\n" for data in self.registers]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", opfilepath)
            raise

class instruction():
    def __init__(self,instr_name,instr_queue,src_regs,dst_regs,smem_ad,vmem_ad,
                 instr_cycleCount,vectorLength,vectorMask,computeResource):
       # Each instruction after decoding will contain the following metadata
        self.instr_name = instr_name
        self.instr_queue = instr_queue              # number indicating which queue to enter
                                                    # 0: VectorCompute Queue; 1: VectorData Queue; 2: ScalarOps Queue
        self.src_regs = src_regs                    # list of all scalar registers used
        self.dst_regs = dst_regs                    # likewise for vector registers
        self.smem_ad = smem_ad                      # list of all scalar memory addresses used
        self.vmem_ad = vmem_ad                      # likewise for vector memory addresses
        self.instr_cycleCount = instr_cycleCount    # Number of cycles instruction takes
        self.vectorLength = vectorLength
        self.vectorMask = vectorMask
        self.computeResource = computeResource
    
    def __init__(self):
        # Constructor with default values
        self.instr_name = ""
        self.instr_queue = -1
        self.src_regs = {"Scalar":[],"Vector":[]}
        self.dst_regs = {"Scalar":[],"Vector":[]}
        self.smem_ad = []
        self.vmem_ad = []
        self.instr_cycleCount = 0
        self.vectorLength = 0
        self.vectorMask = [1]*64
        self.computeResource = ""

class Core():
    def __init__(self, imem, sdmem, vdmem, config):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        self.config = config
        self.PC = 0
        self.VLR = 0
        self.VMR = [1]*64

        self.RFs = {"SRF": RegisterFile("SRF", 8),      # 8 registers of 32 bit integers
                    "VRF": RegisterFile("VRF", 8, 64),  # 8 registers of 64 elements; each of 32 bits
                    "VMR": RegisterFile("VMR", 1, 64),
                    "VLR": RegisterFile("VLR", 1)
                }
        
        self.busyBoard = {"scalar": [False]*8,"vector": [False]*8}
        print(self.config.parameters)

        self.queues = {"vectorCompute":[],
                       "vectorData":[],
                       "scalarOps":[]
                       }
        
        self.fetched_instr_current = []
        self.fetched_instr_prev = []
        
        self.instrToBeQueued = instruction()
        self.instrToBeCompute = instruction()
        self.decode_input = []
        self.instrToBeExecuted = [None, None, None]
        self.resources_busy = {"Adder":[False,0],"Multiplier":[False,0],
                               "Divider":[False,0],"Shuffle":[False,0],
                               "Memory":[False,0],
                               "Scalar": [False, 0]
                              }
        self.banks_busy = [[False,0]]*config.parameters["vdmNumBanks"]
        
        self.nop = {"Fetch":False,
                      "Decode":True,
                      "SendToCompute":True}
                
        # Your code here.

        # Execute functions here

        # Decode functions here 
    
    def decode(self,instr_list):
        """
        Function to convert the instruction in a list format and creates an 
        instruction object with the relavent properties.

        Input   : instruction in list format
        Output  : Object of instruction class
        """
        # convert instuction list to instruction format
        # creating instruction object and loading default values

        # TODO: Incorporate VLR in the instruction

        ins = instruction()
        ins.instr_name = instr_list[0]
        

        if(ins.instr_name in ["ADDVV","SUBVV"]):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[2][2:]),int(instr_list[3][2:])]
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Adder"

        elif(ins.instr_name in ["ADDVS","SUBVS"]):
            ins.instr_queue = 0
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.src_regs["Vector"] = [int(instr_list[2][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[3][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Adder"

        elif(ins.instr_name == "MULVV"):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[2][2:]),int(instr_list[3][2:])]
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Multiplier"

        elif(ins.instr_name == "MULVS"):
            ins.instr_queue = 0
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.src_regs["Vector"] = [int(instr_list[2][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[3][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Multiplier"

        elif(ins.instr_name == "DIVVV"):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[2][2:]),int(instr_list[3][2:])]
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Divider"

        elif(ins.instr_name == "DIVVS"):
            ins.instr_queue = 0
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.src_regs["Vector"] = [int(instr_list[2][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[3][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Divider"

        elif(ins.instr_name =="SVV"):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[1][2:]),int(instr_list[2][2:])]
            ins.vectorLength = self.VLR
            self.VMR = instr_list[3][1:-1].split(",")
            ins.computeResource = "Adder"

        elif(ins.instr_name == "SVS"):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[1][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[2][2:])]
            self.VMR = instr_list[3][1:-1].split(",")
            ins.computeResource = "Adder"

        elif(ins.instr_name in ["CVM"]):
            ins.instr_queue = 0
            self.VMR=[1]*64
            ins.computeResource = "Adder"
            
        elif(ins.instr_name in ["POP","MFCL"]):
            ins.instr_queue = 2
            ins.s_regs = [int(instr_list[1][2:])]
            
        elif(ins.instr_name in ["MTCL"]):
            ins.instr_queue = 2
            ins.s_regs = [int(instr_list[1][2:])]
            self.VLR = int(instr_list[2][1:-1])
            ins.vectorLength = self.VLR

        elif(ins.instr_name in ["LV","LVI","LVWS",]):
            ins.instr_queue = 1
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vmem_ad = instr_list[2][1:-1].split(",")
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR

        elif(ins.instr_name in ['SV','SVI','SVWS']):
            ins.instr_queue = 1
            ins.src_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vmem_ad = instr_list[2][1:-1].split(",")
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR

        elif(ins.instr_name in ["LS"]):
            ins.instr_queue = 2
            ins.dst_regs["Scalar"] = [int(instr_list[1][2:])]
            ins.smem_ad = instr_list[2][1:-1].split(",")

        elif(ins.instr_name in ["SS"]):
            ins.instr_queue = 2
            ins.src_regs["Scalar"] = [int(instr_list[1][2:])]
            ins.smem_ad = instr_list[2][1:-1].split(",")        

        elif(ins.instr_name in ["ADD","SUB","AND","OR","XOR","SLL","SRL","SRA"]):
            ins.instr_queue = 2
            ins.dst_regs["Scalar"] = [int(instr_list[1][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[2][2:]),int(instr_list[3][2:])]
        
        elif(ins.instr_name == "B"):
            ins.instr_queue = 2 # again confirm if correct

        elif(ins.instr_name in ["UNPACKLO","UNPACKHI","PACKLO","PACKHI"]):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[2][2:]),int(instr_list[3][2:])]
            ins.dst_regs["Vector"] = [int(instr_list[1][2:])]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR
            ins.computeResource = "Shuffle"

        else: 
            print("UNKNOWN INSTRUCTION",instr_list)
            return -1
        
        return ins
    
    def CheckQueue(self,ins):
        # checking if queues are full (saves busyboard lookup)
        if(ins.instr_queue == 0):
            if(len(self.queues["vectorCompute"])>self.config.parameters["computeQueueDepth"]):
                print("Compute Queue depth exceeded")
            if(len(self.queues["vectorCompute"])>=self.config.parameters["computeQueueDepth"]):
                return False
        elif(ins.instr_queue == 1):
            if(len(self.queues["vectorData"])>self.config.parameters["dataQueueDepth"]):
                print("Vector Data Queue depth exceeded")
            if(len(self.queues["vectorData"])>=self.config.parameters["dataQueueDepth"]):
                return False
        elif(ins.instr_queue == 2):
            if(len(self.queues["scalarOps"])>self.config.parameters["computeQueueDepth"]):
                print("Scalar Queue depth exceeded")
            if(len(self.queues["scalarOps"])>=self.config.parameters["computeQueueDepth"]):
                return False

        # checking busyboard
        for reg in ins.src_regs["Scalar"]:
            if self.busyBoard["scalar"][reg]: return False
        for reg in ins.src_regs["Vector"]:
            if self.busyBoard["vector"][reg]: return False

        for reg in ins.dst_regs["Scalar"]:
            if self.busyBoard["scalar"][reg]: return False
        for reg in ins.dst_regs["Vector"]:
            if self.busyBoard["vector"][reg]: return False
        
        return True
    
    def sendToQueue(self,ins):
        """
        Function appends the instruction to the appropriate queue
        Also sets the busyboard to high for the registers used by the instruction
        input   : instruction object
        output  : status of appending to the queue
        """
        if(ins.instr_queue == 0):
            if(len(self.queues["vectorCompute"])<self.config.parameters["computeQueueDepth"]):
                self.queues["vectorCompute"].append(ins)
                for reg in ins.src_regs["Vector"]: self.busyBoard["vector"][reg] = True
                for reg in ins.dst_regs["Vector"]: self.busyBoard["vector"][reg] = True
            else: return -1
        elif(ins.instr_queue == 1):
            if(len(self.queues["vectorData"])<self.config.parameters["dataQueueDepth"]):
                self.queues["vectorData"].append(ins)
                for reg in ins.src_regs["Vector"]:self.busyBoard["vector"][reg] = True
                for reg in ins.dst_regs["Vector"]:self.busyBoard["vector"][reg] = True
            else: return -1
        elif(ins.instr_queue == 2):
            if(len(self.queues["scalarOps"])<self.config.parameters["computeQueueDepth"]):
                self.queues["scalarOps"].append(ins)
                for reg in ins.src_regs["Scalar"]: self.busyBoard["scalar"][reg] = True
                for reg in ins.dst_regs["Scalar"]: self.busyBoard["scalar"][reg] = True
            else: return -1
        return 0
    
    def checkResources(self):
        """
        Function to check whether the compute resource is available or not
        Returns a list of 3 booleans
        """
        res_list = [False,False,False]
        if len(self.queues["vectorCompute"]) > 0:
            instr = self.queues["vectorCompute"][0]
            if(self.resources_busy[instr.computeResource][0] == False): res_list[0] = True
        if len(self.queues["vectorData"]) > 0:
            if(self.resources_busy["Memory"][0] == False): res_list[1] = True
        if len(self.queues["scalarOps"]) > 0:  res_list[2] = True

        return res_list
    
    def sendToResources(self,condition_list): 
        
        returned_inst_list = [None,None,None]

        if len(self.queues["vectorCompute"])>0 and condition_list[0]==True:
            returned_inst_list[0] = self.queues["vectorCompute"].pop(0)

        if len(self.queues["vectorData"])>0 and condition_list[1]==True:
            returned_inst_list[1] = self.queues["vectorData"].pop(0)

        if len(self.queues["scalarOps"])>0 and condition_list[2]==True:
            returned_inst_list[2] = self.queues["scalarOps"].pop(0)
        
        return returned_inst_list
    
    def calculateNoComputeCycles(self,instr):
        # Requires Discussion
        lanes = [0]*config.parameters["numLanes"]
        for i in range(instr.vectorLength):
            lanes[i%config.parameters["numLanes"]] += instr.vectorMask[i]

        if instr.computeResource == "Adder":
            cycleCount = config.parameters["pipelineDepthAdd"] + max(lanes) - 1 
        elif instr.computeResource == "Multiplier":
            cycleCount = config.parameters["pipelineDepthMul"] + max(lanes) - 1 
        elif instr.computeResource == "Divider":
            cycleCount = config.parameters["pipelineDepthDiv"] + max(lanes) - 1 
        elif instr.computeResource == "Shuffle":
            cycleCount = config.parameters["pipelineDepthShuffle"] + max(lanes) - 1 

        return cycleCount
    
    def compute(self,instr):
        # decrement all counters if not zero
        keys = list(self.resources_busy.keys())
        for resource in keys[:-2]:
            if self.resources_busy[resource][0]:
                if self.resources_busy[resource][1] > 0:
                    self.resources_busy[resource][1] -= 1
                else:
                    self.resources_busy[resource][0] = False
                    self.resources_busy[resource][1] = 0
            
        if not self.resources_busy[instr.computeResource][0]:
            self.resources_busy[instr.computeResource][0] = True
            self.resources_busy[instr.computeResource][1] = self.calculateNoComputeCycles(instr)
            
            for reg in instr.src_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.src_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
            for reg in instr.dst_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.dst_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
        
        return
    
    def calculateNoMemoryCycles(self,instr):
        # Requires Discussion
        # calculate number of cycles to be taken in memory by simulating it

        # creating the queues for each lane:
        vls_pipelines = [[]] * config.parameters["numLanes"]
        # assigning each memory access to a queue
        for i in range(instr.vectorLength):
            if instr.vmem_ad[i] == -1:
                continue
            else:
                vls_pipelines[i % config.parameters["numLanes"]].append(instr.vmem_ad[i])
        
        # now we simulate all the memory accesses, and calculate the number of cycles to execute this instruction
        # to calculate which bank it should access, we mod the address by the number of banks

        cycleCount = 0
        while True:

            # setting checks for if we have finished processing all memory addresses:
            all_lanes_free = True
            all_banks_free = True
            
            # Let's check all banks
            # if bank is busy, check countdown. If it is zero, set to bank free. If nonzero, decrement by 1
            for each_bank in self.banks_busy:
                if each_bank[0] == True:
                    all_banks_free = False
                    if each_bank[1] == 0:
                        each_bank[0] = False
                    else:
                        each_bank[1] -= 1

            # checking each lane
            # now we will process each lane in order, automatically giving priority to the lower index
            for each_lane in vls_pipelines:
                if len(each_lane) > 0:
                    all_lanes_free = False

                    # let's look at the head of the queue and check which bank we should send the address to:
                    mem_addr = int(each_lane[0])
                    # print(type(mem_addr))
                    bank_idx = mem_addr % config.parameters["vdmNumBanks"]

                    # let's check that bank: if it isn't busy, we dispatch our request. else, do nothing.
                    if self.banks_busy[bank_idx][0] == False:
                        each_lane.pop(0)
                        self.banks_busy[bank_idx][0] = True
                        self.banks_busy[bank_idx][1] = config.parameters["vdmBankBusyTime"]

            # termination condition
            if all_lanes_free and all_banks_free:
                return cycleCount

            # incrementing cycle count
            cycleCount += 1
            
    def memory(self,instr):
        # decrement all counters if not zero

        #if(the resource ka value is not busy; 
        #   countdown is 0
        #   and there is an instruction dispatched to use it):
            # set countdown values
        #else: # decrement the countdown
        # update busyboard too 
        if self.resources_busy["Memory"][0] == True and self.resources_busy["Memory"][1] > 0:
            self.resources_busy["Memory"][1] -= 1
        elif self.resources_busy["Memory"][0] == True and self.resources_busy["Memory"][1] <= 0:
            self.resources_busy["Memory"][0] = False
            self.resources_busy["Memory"][1] = 0
        else:
            self.resources_busy["Memory"][0] = True
            self.resources_busy["Memory"][1] = self.calculateNoMemoryCycles(instr)
            for reg in instr.src_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.src_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
            for reg in instr.dst_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.dst_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
        
        return
    
    def scalar(self, instr):
        if self.resources_busy["Scalar"][0] == True and self.resources_busy["Scalar"][1] > 0:
            self.resources_busy["Scalar"][1] -= 1
        elif self.resources_busy["Scalar"][0] == True and self.resources_busy["Scalar"][1] <= 0:
            self.resources_busy["Scalar"][0] = False
            self.resources_busy["Scalar"][1] = 0
        else:
            self.resources_busy["Scalar"][0] = True
            self.resources_busy["Scalar"][1] = 1
            for reg in instr.src_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.src_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
            for reg in instr.dst_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = True
            for reg in instr.dst_regs["Vector"]:
                self.busyBoard["vector"][reg] = True
        
        return

        
    def run(self):
        self.PC = 0
        self.CycleCount = 0

        while(True):

            #Compute stage; decrement compute counter
            if self.instrToBeExecuted[0] is not None: self.compute(self.instrToBeExecuted[0])
            if self.instrToBeExecuted[1] is not None: self.memory(self.instrToBeExecuted[1])
            if self.instrToBeExecuted[2] is not None: self.scalar(self.instrToBeExecuted[2])
            # do for memory and scalar too

            # Send to Compute
            
            queue_status = self.checkResources() # Returns list of booleans
            self.instrToBeExecuted = self.sendToResources(queue_status)

            # Decode and SendToQueue
            print("length of decode input")
            print(len(self.decode_input))
            if len(self.decode_input)>0:
                print("Decoding...")
                self.instrToBeQueued = self.decode(self.decode_input)
                if self.instrToBeQueued == -1: break
                addToQueue = self.CheckQueue(self.instrToBeQueued) # checks busyboard and if queues are full
                print("addToQueue:",addToQueue)
                if addToQueue:
                    self.sendToQueue(self.instrToBeQueued)
                else: # set NOPS
                    self.nop["Fetch"] = True

            #print(self.queues)

            # Fetch
            print(self.PC, self.decode_input)
            if not self.nop["Fetch"]:
                print("fetching...")
                self.decode_input = self.IMEM.Read(self.PC)
                if self.decode_input == -1: break
                print(self.PC, self.decode_input)
                self.PC = self.PC + 1

            self.CycleCount+=1

            if self.CycleCount == 100:
                return self.CycleCount
            
            endCondition = True
            for resource in self.resources_busy:
                if self.resources_busy[resource][0]: endCondition = False
            for queue in self.queues:
                if len(self.queues[queue])>0: endCondition = False
            if len(self.decode_input) > 0: endCondition = False
            if endCondition == True: 
                print("ending")
                return self.CycleCount

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Functional Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)

    # Parse IMEM
    imem = IMEM(iodir)  
    # Parse SMEM
    sdmem = DMEM("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core(imem, sdmem, vdmem, config)

    # Run Core
    cycles = vcore.run()
    print(cycles)
    vcore.dumpregs(iodir)

    sdmem.dump()
    vdmem.dump()

    print("END")

    # THE END