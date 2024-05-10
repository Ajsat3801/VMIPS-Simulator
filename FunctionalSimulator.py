import os
import argparse

class IMEM_func(object):
    def __init__(self, iodir):
        self.size = pow(2, 16) # Can hold a maximum of 2^16 instructions.
        self.filepath = os.path.abspath(os.path.join(iodir, "Code.asm"))
        self.opfilepath = os.path.abspath(os.path.join(iodir, "trace.asm"))
        self.instructions = []
        self.unrolled_instructions = []

        try:
            with open(self.filepath, 'r') as insf:
                self.instructions = [ins.strip() for ins in insf.readlines()]
            print("IMEM - Instructions loaded from file:", self.filepath)
            # print("IMEM - Instructions:", self.instructions)
        except:
            print("IMEM - ERROR: Couldn't open file in path:", self.filepath)

    def removeComments(self,l):
        i = 0
        while i < len(l):
            if "#" in l[i]: break
            else: i+=1
        return l[:i]
    
    def Read(self, idx): # Use this to read from IMEM.
        if idx < self.size:
            #try:
            instr_list = self.instructions[idx].split()
            return self.removeComments(instr_list)
            #except: 
            #    print("Error at index:",idx)

        else:
            print("IMEM - ERROR: Invalid memory access at index: ", idx, " with memory size: ", self.size)

    def Dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(unroll_instr) + '\n' for unroll_instr in self.unrolled_instructions]
                opf.writelines(lines)
            print("Dumped unrolled instructions into output file in path:", self.opfilepath)
        except:
            print("ERROR: Couldn't dump unrolled instructions output file in path:", self.opfilepath)

class DMEM_func(object):
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

    def Read(self, idx): # Use this to read from DMEM.
        if idx>self.size:
            print("Index out of bounds")
            return
        return self.data[idx]
        #pass # Replace this line with your code here.

    def Write(self, idx, val): # Use this to write into DMEM.
        if idx > self.size:
            print("Index out of bounds")
            return
        self.data[idx] = val
        return
        
        pass # Replace this line with your code here.

    def dump(self):
        try:
            with open(self.opfilepath, 'w') as opf:
                lines = [str(data) + '\n' for data in self.data]
                opf.writelines(lines)
            print(self.name, "- Dumped data into output file in path:", self.opfilepath)
        except:
            print(self.name, "- ERROR: Couldn't open output file in path:", self.opfilepath)

class RegisterFile_func(object):
    def __init__(self, name, count, length = 1, size = 32):
        self.name       = name
        self.reg_count  = count         # Number of registers
        self.vec_length = length        # Number of 32 bit words in a vector.
        self.reg_bits   = size          # Number of bits in a register
        self.min_value  = -pow(2, self.reg_bits-1)
        self.max_value  = pow(2, self.reg_bits-1) - 1
        self.registers  = [[0x0 for e in range(self.vec_length)] for r in range(self.reg_count)] # list of lists of integers

    def Read(self, idx):
        """
        Function to read a value from a register
        Args    : integer : idx : index of register
        Returns : list    : vector of values
        """
        
        # will make easier to debug. Checks if accessing out of bounds
        if (idx >= len(self.registers)):
            print("Read Out of bounds")
            return -1

        item = self.registers[idx]
        
        return item
        # pass # Replace this line with your code.

    def Write(self, idx, val):

        """
        Function to write a value to a register
        Args: 
        1) integer                   : idx : index of register
        2) list of length vector_len : val : value to be added to the register

        """

        
        # will make easier to debug. Checks if accessing out of bounds
        if (idx >= len(self.registers)):
            print("Write Out of bounds")
            return -1
        
        # will make easier to debug. Checks if any element values greater than allowed
        """
        for element in val:
            if element > self.max_value or element < self.min_value:
                print("Value Out of Bounds at",idx )
                print(val)
                return -1
        """
        self.registers[idx] = val

        return 0
        
        # pass # Replace this line with your code.

    def dump(self, iodir):  # DONT TOUCH
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

class Core_func():
    def __init__(self, imem, sdmem, vdmem):
        self.IMEM = imem
        self.SDMEM = sdmem
        self.VDMEM = vdmem
        self.PC = 0

        self.RFs = {"SRF": RegisterFile_func("SRF", 8),      # 8 registers of 32 bit integers
                    "VRF": RegisterFile_func("VRF", 8, 64),  # 8 registers of 64 elements; each of 32 bits
                    "VMR": RegisterFile_func("VMR", 1, 64),
                    "VLR": RegisterFile_func("VLR", 1)
                }  
        
        # Your code here.returVV
        
    """
    EXECUTE OPERATIONS:
    Args: self, instruction in a list format; 
          0th element of list is the instruction name and subsequent elements  are operands
    Returns 0 if operation is successful, else returns -1
    """

    def execute_ADDVV(self,instr_list): 
        
        # Load Vector Registers into the functions
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(VLR): 
            if VMR[i] == 1: VR1[i] = VR2[i]+VR3[i]

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0

    def execute_SUBVV(self,instr_list):
        try:
            VR3 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR1 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(VLR):
            if VMR[i] == 1:  VR3[i] = VR1[i]-VR2[i]

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR3)
        
        return 0

    def execute_ADDVS(self,instr_list):
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(VLR): 
            if VMR[i] == 1: VR1[i] = VR2[i] + SR1
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0

    def execute_SUBVS(self,instr_list):
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(VLR): 
            if VMR[i] == 1: VR1[i] = VR2[i] - SR1
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0

    def execute_MULVV(self,instr_list):
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(VLR): 
            if VMR[i] == 1: VR1[i] = VR2[i] * VR3[i]
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0

    def execute_DIVVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1

        for i in range(VLR): 
            if VMR[i] == 1: 
                try:
                    VR1[i] = int(VR2[i] / VR3[i])
                except ZeroDivisionError as e: 
                    VR1[i] = 0

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        return 0
    
    def execute_MULVS(self,instr_list):
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
 
        for i in range(VLR): 
            if VMR[i] == 1: VR1[i] = VR2[i] * SR1
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0
    
    def execute_DIVVS(self,instr_list):
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        try:
            for i in range(VLR): 
                if VMR[i] == 1: VR1[i] = int(VR2[i] / SR1)
        except ZeroDivisionError as e: 
            print("Divide by Zero error")
            return -1
 
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0

    # Vector Mask Register Operations
    
    def execute_SEQVV(self,instr_list):  
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] == VR2[i]: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SNEVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] != VR2[i]: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0) 
                mask_str = mask_str + "0,"
        
        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SGTVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1  

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] > VR2[i]: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0," 

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SLTVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] < VR2[i]:
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SGEVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] >= VR2[i]: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)

        return 0

    def execute_SLEVV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2])
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] <= VR2[i]:
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0," 

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVV"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SEQVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] == SR1: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SNEVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] != SR1:
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)

        return 0

    def execute_SGTVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] > SR1: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_SLTVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] < SR1: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)

        return 0

    def execute_SGEVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] >= SR1: 
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0
    
    def execute_SLEVS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
        except: 
            print("Error while loading values from register")
            return -1

        mask = []
        mask_str = " ("

        for i in range(VLR):
            if VR1[i] <= SR1:
                mask.append(1)
                mask_str = mask_str + "1,"
            else: 
                mask.append(0)
                mask_str = mask_str + "0,"

        pad_len = self.RFs["VMR"].vec_length - VLR
        mask = mask + [1]*pad_len
        self.RFs["VMR"].Write(0, mask)

        mask_str = mask_str + "1,"*pad_len
        mask_str = mask_str[:-1]+")"
        self.IMEM.unrolled_instructions.append("SVS"+" "+instr_list[1]+" "+instr_list[2]+mask_str)
        
        return 0

    def execute_CVM(self): 
        try:
            self.RFs["VMR"].Write(0, [1] * 64)
            self.IMEM.unrolled_instructions.append("CVM")
            return 0
        except: return -1
    
    def execute_POP(self,instr_list): 
        try:
            SR1 = 0
            VMR = self.RFs["VMR"].Read(0)
            for i in range(len(VMR)):
                if VMR[i] == 1: SR1 += 1
            
            self.RFs["SRF"].Write(int(instr_list[1][2:]), [SR1])
            self.IMEM.unrolled_instructions.append("POP"+instr_list[1])
            
            return 0
        except: return -1

    # Vector Length Register Operations

    def execute_MTCL(self,instr_list):  
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
        except: return -1
        if SR1<=0:
            print("VLR cannot be negative or zero")
            print("SR1:",SR1)
            return -1
        
        if SR1>64:
            print("VLR cannot be greater than 64")
            print(SR1)
            return -1
        
        self.RFs["VLR"].Write(0, [SR1])
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1] + " ("+str(SR1)+")")
        return 0
    
    def execute_MFCL(self,instr_list): 
        try:
            VLR = self.RFs["VLR"].Read(0)[0]
            self.RFs["SRF"].Write(int(instr_list[1][2:]),[VLR])
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1] + " ("+str(VLR)+")")
        except: return -1

    # Memory Access Operations

    def execute_LV(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1
        op_str = "("
        for i in range(VLR): 
            if VMR[i] == 1: 
                VR1[i] = self.VDMEM.Read(SR1+i)
                op_str += str(SR1+i)
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"
        
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str)
        return 0

    def execute_SV(self,instr_list): 

        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1
        
        op_str = "("       
        for i in range(VLR):
            if VMR[i] == 1: 
                self.VDMEM.Write(SR1 + i, VR1[i])
                op_str += str(SR1+i)
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str) 
        return 0

    def execute_LVI(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1
        
        op_str = "("
        for i in range(VLR):
            if VMR[i] == 1:
                VR1[i] = self.VDMEM.Read(SR1 + VR2[i])
                op_str += str(SR1 + VR2[i])
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"
        
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str) 
        
        return 0

    def execute_SVI(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1
        
        op_str = "("
        for i in range(VLR): 
            if VMR[i] == 1: 
                self.VDMEM.Write(SR1 + VR2[i], VR1[i])
                op_str += str(SR1 + VR2[i])
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"

        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str) 
        return 0

    def execute_LVWS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1
        
        op_str = "("
        for i in range(VLR):
            if VMR[i] == 1:
                VR1[i] = self.VDMEM.Read(SR1 + (SR2 * i))
                op_str += str(SR1 + (SR2 * i))
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"
        
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str) 
        
        return 0

    def execute_SVWS(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            VLR = self.RFs["VLR"].Read(0)[0]
            VMR = self.RFs["VMR"].Read(0)
        except:
            print("Error while loading values from register")
            return -1

        op_str = "("
        for i in range(VLR): 
            if VMR[i] == 1:
                self.VDMEM.Write(SR1 + (SR2 * i), VR1[i])
                op_str += str(SR1 + (SR2 * i))
                op_str +=","
            else: op_str+="-1,"
        op_str= op_str[:-1] + ")"
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+op_str) 
        return 0

    def execute_LS(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except:
            print("Error while loading values from register")
            return -1
        
        SR2 = self.SDMEM.Read(SR1+IMM)
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" ("+str(SR1+IMM)+")")
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR2])
        return 0

    def execute_SS(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            IMM = int(instr_list[3])
        except:
            print("Error while loading values from register")
            return -1

        self.SDMEM.Write(SR1 + IMM, SR2)
        self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" ("+str(SR1+IMM)+")")
        return

    # Scalar Operations

    def execute_ADD(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        SR3 = SR1 + SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])
        
        return 0

    def execute_SUB(self,instr_list):
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        SR3 = SR1 - SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])

        return 0

    def execute_AND(self,instr_list):
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        SR3 = SR1 & SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])

        return 0
    
    def execute_OR(self,instr_list):
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        SR3 = SR1 | SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])

        return 0

    def execute_XOR(self,instr_list):
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        SR3 = SR1 ^ SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])

        return 0

    def execute_SLL(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if SR2 <0:
            print("invalid input for shifting")
            return -1
        
        SR3 = SR1 << SR2        
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])
        return 0
    
    def execute_SRL(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if SR2 <0:
            print("invalid input for shifting")
            return -1
        
        SR3 = (SR1 % 0x100000000) >> SR2

        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])
        return 0

    def execute_SRA(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[3][2:]))[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if SR2 <0:
            print("invalid input for shifting")
            return -1
        
        SR3 = SR1 >> SR2
        self.RFs["SRF"].Write(int(instr_list[1][2:]),[SR3])

        return 0

    def execute_BEQ(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 == SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0

    def execute_BNE(self,instr_list):
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 != SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0
        
    def execute_BGT(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 > SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0
        
    def execute_BLT(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 < SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0
        
    def execute_BGE(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 >= SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0
        
    def execute_BLE(self,instr_list): 
        try:
            SR1 = self.RFs["SRF"].Read(int(instr_list[1][2:]))[0]
            SR2 = self.RFs["SRF"].Read(int(instr_list[2][2:]))[0]
            IMM = int(instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        if IMM > pow(2, 20) or IMM < -pow(2, 20):
            print("Invalid Immediate value")
            return -1
        
        if SR1 <= SR2:
            self.PC += IMM -1
        
        self.IMEM.unrolled_instructions.append("B ("+str(self.PC + 1)+")")
        return 0

    # Register - Register shuffle

    def execute_UNPACKLO(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1

        for i in range(0,VLR,2 ):
            VR1[i] = VR2[int(i/2)]
            VR1[i+1] = VR3[int(i/2)]

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0
    
    def execute_UNPACKHI(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1

        for i in range(0,VLR,2 ):
            VR1[i] = VR2[int(VLR/2 + i/2)]
            VR1[i+1] = VR3[int(VLR/2 + i/2)]

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        
        return 0
    
    def execute_PACKLO(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1
        
        for i in range(0,VLR,2 ):
            VR1[int(i/2)] = VR2[i]
            VR1[int(VLR/2+i/2)] = VR3[i]

        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        return 0

    def execute_PACKHI(self,instr_list): 
        try:
            VR1 = self.RFs["VRF"].Read(int(instr_list[1][2:]))
            VR2 = self.RFs["VRF"].Read(int(instr_list[2][2:]))
            VR3 = self.RFs["VRF"].Read(int(instr_list[3][2:]))
            VLR = self.RFs["VLR"].Read(0)[0]
            self.IMEM.unrolled_instructions.append(instr_list[0]+" "+instr_list[1]+" "+instr_list[2]+" "+instr_list[3])
        except: 
            print("Error while loading values from register")
            return -1

        for i in range(0,VLR,2 ):
            VR1[int(i/2)] = VR2[i+1]
            VR1[int(VLR/2+i/2)] = VR3[i+1]
        self.RFs["VRF"].Write(int(instr_list[1][2:]),VR1)
        return 0


    def instruction_decode(self,instr_list):
        """
        Function to decode the instruction and pass to subsequent execute function
        Inputs: instr_list : instruction in a list format
        """
        instr_type = instr_list[0]
        ex_status = 0

        if  instr_type == "ADDVV" : ex_status = self.execute_ADDVV(instr_list)
        elif  instr_type == "SUBVV" : ex_status = self.execute_SUBVV(instr_list)
        elif  instr_type == "ADDVS" : ex_status = self.execute_ADDVS(instr_list)
        elif  instr_type == "SUBVS" : ex_status = self.execute_SUBVS(instr_list)
        elif  instr_type == "MULVV" : ex_status = self.execute_MULVV(instr_list)
        elif  instr_type == "DIVVV" : ex_status = self.execute_DIVVV(instr_list)
        elif  instr_type == "MULVS" : ex_status = self.execute_MULVS(instr_list)
        elif  instr_type == "DIVVS" : ex_status = self.execute_DIVVS(instr_list)

        elif  instr_type == "SEQVV" : ex_status = self.execute_SEQVV(instr_list)
        elif  instr_type == "SNEVV" : ex_status = self.execute_SNEVV(instr_list)
        elif  instr_type == "SGTVV" : ex_status = self.execute_SGTVV(instr_list)
        elif  instr_type == "SLTVV" : ex_status = self.execute_SLTVV(instr_list)
        elif  instr_type == "SGEVV" : ex_status = self.execute_SGEVV(instr_list)
        elif  instr_type == "SLEVV" : ex_status = self.execute_SLEVV(instr_list)

        elif  instr_type == "SEQVS" : ex_status = self.execute_SEQVS(instr_list)
        elif  instr_type == "SNEVS" : ex_status = self.execute_SNEVS(instr_list)
        elif  instr_type == "SGTVS" : ex_status = self.execute_SGTVS(instr_list)
        elif  instr_type == "SLTVS" : ex_status = self.execute_SLTVS(instr_list)
        elif  instr_type == "SGEVS" : ex_status = self.execute_SGEVS(instr_list)
        elif  instr_type == "SLEVS" : ex_status = self.execute_SLEVS(instr_list)

        elif  instr_type == "CVM" : ex_status = self.execute_CVM()
        elif  instr_type == "POP" : ex_status = self.execute_POP(instr_list)

        elif  instr_type == "MTCL" : ex_status = self.execute_MTCL(instr_list)
        elif  instr_type == "MFCL" : ex_status = self.execute_MFCL(instr_list)

        elif  instr_type == "LV" : ex_status = self.execute_LV(instr_list)
        elif  instr_type == "SV" : ex_status = self.execute_SV(instr_list)
        elif  instr_type == "LVI" : ex_status = self.execute_LVI(instr_list)
        elif  instr_type == "SVI" : ex_status = self.execute_SVI(instr_list)
        elif  instr_type == "LVWS" : ex_status = self.execute_LVWS(instr_list)
        elif  instr_type == "SVWS" : ex_status = self.execute_SVWS(instr_list)
        elif  instr_type == "LS" : ex_status = self.execute_LS(instr_list)
        elif  instr_type == "SS" : ex_status = self.execute_SS(instr_list)

        elif  instr_type == "ADD" : ex_status = self.execute_ADD(instr_list)
        elif  instr_type == "SUB" : ex_status = self.execute_SUB(instr_list)
        elif  instr_type == "AND" : ex_status = self.execute_AND(instr_list)
        elif  instr_type == "OR" : ex_status = self.execute_OR(instr_list)
        elif  instr_type == "XOR" : ex_status = self.execute_XOR(instr_list)
        elif  instr_type == "SLL" : ex_status = self.execute_SLL(instr_list)
        elif  instr_type == "SRL" : ex_status = self.execute_SRL(instr_list)
        elif  instr_type == "SRA" : ex_status = self.execute_SRA(instr_list)

        elif  instr_type == "BEQ" : ex_status = self.execute_BEQ(instr_list)
        elif  instr_type == "BNE" : ex_status = self.execute_BNE(instr_list)
        elif  instr_type == "BGT" : ex_status = self.execute_BGT(instr_list)
        elif  instr_type == "BLT" : ex_status = self.execute_BLT(instr_list)
        elif  instr_type == "BGE" : ex_status = self.execute_BGE(instr_list)
        elif  instr_type == "BLE" : ex_status = self.execute_BLE(instr_list)

        elif  instr_type == "UNPACKLO" : ex_status = self.execute_UNPACKLO(instr_list)
        elif  instr_type == "UNPACKHI" : ex_status = self.execute_UNPACKHI(instr_list)
        elif  instr_type == "PACKLO" : ex_status = self.execute_PACKLO(instr_list)
        elif  instr_type == "PACKHI" : ex_status = self.execute_PACKHI(instr_list)


        if ex_status == -1:
            print("instruction:",instr_list)
            print("Error in executing statement")
            return -1

        return 0
     
    def run(self): # THIS IS OUR MAIN FUNCTION
        self.PC = 0
        ex_status = 0
        while(True):
            # break # Replace this line with your code.
            #read
            instr_list = self.IMEM.Read(self.PC)

            if instr_list:
                if instr_list[0] == "HALT": 
                    self.IMEM.unrolled_instructions.append("HALT")
                    break
                else: 
                    ex_status = self.instruction_decode(instr_list)
                    if ex_status == -1: 
                        print("Failed Execution")
                        break

            self.PC = self.PC + 1
            

    def dumpregs(self, iodir):
        for rf in self.RFs.values():
            rf.dump(iodir)

    
    ## one method for each function

if __name__ == "__main__":
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='Vector Core Performance Model')
    parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
    args = parser.parse_args()

    iodir = os.path.abspath(args.iodir)
    print("IO Directory:", iodir)

    # Parse IMEM
    imem = IMEM_func(iodir)  
    # Parse SMEM
    sdmem = DMEM_func("SDMEM", iodir, 13) # 32 KB is 2^15 bytes = 2^13 K 32-bit words.
    # Parse VMEM
    vdmem = DMEM_func("VDMEM", iodir, 17) # 512 KB is 2^19 bytes = 2^17 K 32-bit words. 

    # Create Vector Core
    vcore = Core_func(imem, sdmem, vdmem)

    # Run Core
    vcore.run()   
    vcore.dumpregs(iodir)
    
    imem.Dump()
    sdmem.dump()
    vdmem.dump()

    # THE END