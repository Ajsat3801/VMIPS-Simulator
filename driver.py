import os
import argparse

from FunctionalSimulator import IMEM_func, DMEM_func, Core_func
from TimingSimulator import Config, Core, IMEM #DMEM

parser = argparse.ArgumentParser(description='Vector Core Performance Model')
parser.add_argument('--iodir', default="", type=str, help='Path to the folder containing the input files - instructions and data.')
args = parser.parse_args()

iodir = os.path.abspath(args.iodir)
print("IO Directory:", iodir)
print("------------------------------------------------")
print("Starting Functional Simulator")
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

print("\n Functional simulation complete; generated trace")

print("------------------------------------------")
print("Starting Timing Simulator")

# Parse Config
config = Config(iodir)
imem = IMEM(iodir)  


vcore = Core(imem, config)
cycles = vcore.run()
    

print("\nTiming Simulator complete")
print("Total Cycles taken:",cycles)
