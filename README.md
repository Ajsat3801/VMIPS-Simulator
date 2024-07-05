# Vector Functional and Timing Simulator

# Dependencies
No third party libraries used. Code developed and tested on python 3.9.7

# Architecture

### ISA Specifications
A vector has max length of 64 and each element is a 32-bit integer. There are 2 register files, the first having 8 scalar registers and a second having 8 vector registers. Additionally there is a vector mask register and a vector length register.

* **Vector Operations:** `ADDVV`, `SUBVV`, `MULVV`, `DIVVV`, `ADDVS`, `SUBVS`, `MULVS`, `DIVVS`
* **Vector Mask Register Operations:**  `SEQVV`, `SNEVV`, `SGTVV`, `SLTVV`, `SGEVV`, `SLEVV`, `SEQVS`, `SNEVS`, `SGTVS`, `SLTVS`, `SGEVS`, `SLEVS`, `CVM`, `POP`
* **Vector Length Register Operations:** `MTCL`, `MFCL`
* **Memory Access Operations:** `LV`, 'SV', `LVWS`, `SVWS`, `LVI`, 'SVI', `LS`, `SS`
* **Scalar Operations:** `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLL`, `SRL`, `SRA`
* **Control Operations:** `BEQ`,`BNE`,`BGT`,`BLT`,`BGE`,`BLE`
* **Register-Register Shuffle Operations:** `UNPACKLO`,`UNPACKHI`,`PACKLO`,`PACKHI`
* **Halt:** `HALT`

# Test Programs
### Found in the input directory
1. **Dot Product:**  Sum of the products of the corresponding entries of the two sequences of numbers. `MULVV`, `PACKLO`, `PACKHI` and `ADDVV` operations are used.
2. **Fully Connected Layer:** Multiplication of two matrices. Loading the matrices piece by piece, `MULVV` to multiply the columns and rows with each-other, `ADDVV` to add the bias, and `PACKHI` & `PACKLO` are used to accumulate the products
3. **Convolution:** Treated as a series of dot products across each row of the kernel and the window of the feature map using a series of `LVI`operations 
4. **Fast Fourier Transform:** Scatter-gather operations are used to load the elements of the vector in the order of the leaf node of a recursive tree. The algorithm is then simplified into a sequence of `MULVV`, `SUBVV`, `ADDVV`, `UNPACKLO`, `PACKLO` and `PACKHI` operations.

# How to run

To perform the timing simulation, run driver.py file to generate the result.  
To perform the design space analysis, run designSpaceAnalysis.py to generate the result.

**Note: SDMEM.txt, VDMEM.txt, Code.asm, functionalSimulator.py and timingSimulator.py must be in the same directory as the driver.py file.**

The instruction files and sample inputs for dot product, fully connected, convolution and fast fourier transforms are also given in the inputs directory. 
To run the functions, the respective input files must be copied to the main directory.
