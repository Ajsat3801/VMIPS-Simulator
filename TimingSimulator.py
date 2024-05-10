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
            #print("Config parameters:", self.parameters)
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
        self.vectorLength = 64
        self.vectorMask = [1 for i in range(64)]
        self.computeResource = ""

class Core():
    def __init__(self, imem, config):
        self.IMEM = imem
        self.config = config
        self.PC = 0
        self.VLR = 64
        self.VMR = [1 for i in range(64)]
       
        self.busyBoard = {"scalar": [False for i in range(8)],"vector": [False for i in range(8)]}

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
        self.resources_busy = {"Adder":[None,0],"Multiplier":[None,0],
                               "Divider":[None,0],"Shuffle":[None,0],
                               "Memory":[None,0],
                               "Scalar": [None, 0]
                              }
        self.banks_busy = [[False,0] for i in range(self.config.parameters["vdmNumBanks"])]
        
        self.nop = {"Fetch":False,"Decode":True,"SendToCompute":True}
                
        
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
            self.VMR = [int(ele) for ele in instr_list[3][1:-1].split(",")]
            ins.computeResource = "Adder"

        elif(ins.instr_name == "SVS"):
            ins.instr_queue = 0
            ins.src_regs["Vector"] = [int(instr_list[1][2:])]
            ins.src_regs["Scalar"] = [int(instr_list[2][2:])]
            self.VMR = [int(ele) for ele in instr_list[3][1:-1].split(",")]
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
            #ins.vmem_ad = instr_list[2][1:-1].split(",")
            ins.vmem_ad = [int(ele) for ele in instr_list[2][1:-1].split(",")]
            ins.vectorLength = self.VLR
            ins.vectorMask = self.VMR

        elif(ins.instr_name in ['SV','SVI','SVWS']):
            ins.instr_queue = 1
            ins.src_regs["Vector"] = [int(instr_list[1][2:])]
            #ins.vmem_ad = instr_list[2][1:-1].split(",")
            ins.vmem_ad = [int(ele) for ele in instr_list[2][1:-1].split(",")]
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
        
        elif (ins.instr_name =="HALT"): self.nop["Fetch"] = True
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
        elif(ins.instr_name == "HALT"): return False

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
            if(self.resources_busy[instr.computeResource][0] is None): res_list[0] = True
        if len(self.queues["vectorData"]) > 0:
            if(self.resources_busy["Memory"][0] is None): res_list[1] = True
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
        lanes = [0]*self.config.parameters["numLanes"]
        for i in range(instr.vectorLength):
            lanes[i%self.config.parameters["numLanes"]] += instr.vectorMask[i]

        if instr.computeResource == "Adder":
            cycleCount = self.config.parameters["pipelineDepthAdd"] + max(lanes) - 1 
        elif instr.computeResource == "Multiplier":
            cycleCount = self.config.parameters["pipelineDepthMul"] + max(lanes) - 1 
        elif instr.computeResource == "Divider":
            cycleCount = self.config.parameters["pipelineDepthDiv"] + max(lanes) - 1 
        elif instr.computeResource == "Shuffle":
            cycleCount = self.config.parameters["pipelineDepthShuffle"] + max(lanes) - 1 

        return cycleCount
    
    def compute(self):
    
        # decrement all counters if not zero
        keys = list(self.resources_busy.keys())
        for resource in keys[:-2]:
            if self.resources_busy[resource][0] is not None:
                if self.resources_busy[resource][1] > 0:
                    self.resources_busy[resource][1] -= 1
                    #print(self.resources_busy[resource][1])
                else:
                    for reg in self.resources_busy[resource][0].src_regs["Scalar"]:
                        self.busyBoard["scalar"][reg] = False
                    for reg in self.resources_busy[resource][0].src_regs["Vector"]:
                        self.busyBoard["vector"][reg] = False
                    for reg in self.resources_busy[resource][0].dst_regs["Scalar"]:
                        self.busyBoard["scalar"][reg] = False
                    for reg in self.resources_busy[resource][0].dst_regs["Vector"]:
                        self.busyBoard["vector"][reg] = False

                    self.resources_busy[resource][0] = None
                    self.resources_busy[resource][1] = 0
            
        if self.instrToBeExecuted[0] is not None:
            instr = self.instrToBeExecuted[0]
            self.resources_busy[instr.computeResource][0] = instr
            self.resources_busy[instr.computeResource][1] = self.calculateNoComputeCycles(instr) -1
            #print(self.resources_busy[instr.computeResource][1])
        
        return
    
    def calculateNoMemoryCycles(self,instr):
        
        # calculate number of cycles to be taken in memory by simulating it
        # creating the queues for each lane:
        
        vls_pipelines = [[] for i in range(self.config.parameters["numLanes"])]
        # assigning each memory access to a queue

        for i in range(instr.vectorLength):
            if instr.vmem_ad[i] == -1: continue
            else: 
                index = instr.vmem_ad[i] % self.config.parameters["numLanes"]
                vls_pipelines[index].append(instr.vmem_ad[i])
        
        # now we simulate all the memory accesses, and calculate the number of cycles to execute this instruction
        # to calculate which bank it should access, we mod the address by the number of banks

        cycleCount = self.config.parameters["vlsPipelineDepth"] - 1
        while True:

            # setting checks for if we have finished processing all memory addresses:
            all_lanes_free = True
            all_banks_free = True
            
            # checking banks; if bank is busy, check countdown. If it is zero, set to bank free. If nonzero, decrement by 1
            for each_bank in self.banks_busy:
                if each_bank[0] == True:
                    all_banks_free = False
                    if each_bank[1] == 0: each_bank[0] = False
                    else: each_bank[1] -= 1

            # checking each lane; now we will process each lane in order, automatically giving priority to the lower index
            for each_lane in vls_pipelines:
                if len(each_lane) > 0:
                    all_lanes_free = False

                    mem_addr = int(each_lane[0]) # let's look at the head of the queue and check which bank we should send the address to:
                    bank_idx = mem_addr % self.config.parameters["vdmNumBanks"]

                    # let's check that bank: if it isn't busy, we dispatch our request. else, do nothing.
                    if self.banks_busy[bank_idx][0] == False:
                        each_lane.pop(0)
                        self.banks_busy[bank_idx][0] = True
                        self.banks_busy[bank_idx][1] = self.config.parameters["vdmBankBusyTime"]

            if all_lanes_free and all_banks_free: return cycleCount # termination condition

            # incrementing cycle count
            cycleCount += 1
            
    def memory(self):
        # decrement all counters if not zero

        #if(the resource ka value is not busy; 
        #   countdown is 0
        #   and there is an instruction dispatched to use it):
            # set countdown values
        #else: # decrement the countdown
        # update busyboard too 
        
        if self.resources_busy["Memory"][0] is not None and self.resources_busy["Memory"][1] > 0:
            self.resources_busy["Memory"][1] -= 1
        elif self.resources_busy["Memory"][0] is not None and self.resources_busy["Memory"][1] <= 0:
            
            for reg in self.resources_busy["Memory"][0].src_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = False
            for reg in self.resources_busy["Memory"][0].src_regs["Vector"]:
                self.busyBoard["vector"][reg] = False
            for reg in self.resources_busy["Memory"][0].dst_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = False
            for reg in self.resources_busy["Memory"][0].dst_regs["Vector"]:
                self.busyBoard["vector"][reg] = False
            
            
            self.resources_busy["Memory"][0] = None
            self.resources_busy["Memory"][1] = 0
        else:
            if self.instrToBeExecuted[1] is not None:
                instr = self.instrToBeExecuted[1]
                self.resources_busy["Memory"][0] = instr
                self.resources_busy["Memory"][1] = self.calculateNoMemoryCycles(instr) -1 # -1 to prevent a 2 cycle lag
                
                for reg in instr.src_regs["Scalar"]:
                    self.busyBoard["scalar"][reg] = True
                for reg in instr.src_regs["Vector"]:
                    self.busyBoard["vector"][reg] = True
                for reg in instr.dst_regs["Scalar"]:
                    self.busyBoard["scalar"][reg] = True
                for reg in instr.dst_regs["Vector"]:
                    self.busyBoard["vector"][reg] = True
        
        return
    
    def scalar(self):

        if self.instrToBeExecuted[2] is not None:
            instr = self.instrToBeExecuted[2]

            for reg in instr.src_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = False
            for reg in instr.src_regs["Vector"]:
                self.busyBoard["vector"][reg] = False
            for reg in instr.dst_regs["Scalar"]:
                self.busyBoard["scalar"][reg] = False
            for reg in instr.dst_regs["Vector"]:
                self.busyBoard["vector"][reg] = False
        
        return

        
    def run(self):
        self.PC = 0
        self.CycleCount = 0

        while(True):
            
            # These functions run every cycle, decrementing the cycle countdown of instructions 
            # are still executing, and updating the busyboard/freeing the resources once they are done computing
            self.compute()
            self.memory()
            self.scalar()
            
            # This function checks which resources are available to dispatch instructions to
            queue_status = self.checkResources() # Returns list of booleans
            # This instructions dispatches those instructions to their respective resources
            self.instrToBeExecuted = self.sendToResources(queue_status)

            # Decode and SendToQueue
            if len(self.decode_input)>0:
                self.instrToBeQueued = self.decode(self.decode_input)
                if self.instrToBeQueued == -1: break
                addToQueue = self.CheckQueue(self.instrToBeQueued) # checks busyboard and if queues are full
                # This bool check allows us to stall the fetch and decode if the 
                # queues are full or there is a data dependency
                if addToQueue:
                    self.sendToQueue(self.instrToBeQueued)
                    self.nop["Fetch"] = False
                else: # set NOPS
                    self.nop["Fetch"] = True

            # Fetch: we stall if decode needs to stall
            if not self.nop["Fetch"]:
                self.decode_input = self.IMEM.Read(self.PC)
                if self.decode_input == -1: break
                self.PC = self.PC + 1

            self.CycleCount+=1

            endCondition = True
            for resource in self.resources_busy:
                if self.resources_busy[resource][0] is not None: endCondition = False
            for queue in self.queues:
                if len(self.queues[queue])>0: endCondition = False
            if len(self.decode_input) > 0 and self.decode_input != ["HALT"]: endCondition = False
            for elem in self.busyBoard["scalar"]: 
                if elem == True: endCondition = False
            for elem in self.busyBoard["vector"]: 
                if elem == True: endCondition = False
            if endCondition == True: return self.CycleCount

if __name__ == "__main__": 
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Timing Simulator')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse Config
    config = Config(iodir)

    # Parse IMEM
    imem = IMEM(iodir)  

    # Create Vector Core
    vcore = Core(imem, config)

    # Run Core
    cycles = vcore.run()
    print(cycles)
    print("END")

    # THE END