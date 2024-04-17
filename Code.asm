# Remember to initialise VDMEM and SDMEM
CVM
LS SR1 SR0 1                            # Load value 9 needed to set MTCL
LS SR2 SR0 2                            # Load memAddress for VR1

MTCL SR1                                # Set VLR to 9
LV VR1 SR2                              # Load vector (offset elements for LVI matrix window)

LS SR2 SR0 3                            # Load memAddress of Kernel
LS SR3 SR0 4                            # Load value 16 needed to set MTCL

MTCL SR3                                # Set VLR to 16
MULVV VR2 VR2 VR0                       # Ensure VR2 is fresh till 16 elements
MTCL SR1                                # Set VLR to 9

LV VR2 SR2                              # Load kernel unrolled (9 elements)

LS SR2 SR0 5                            # Load Outer Loop base address (row) of matrix starting point
LS SR7 SR0 6                            # Load value 127 to outer loop counter
LS SR3 SR0 0                            # Load base address of result (initialised to 0)


# Start of Outer loop (moves downward): (moves down the column till last 2 rows left)
LS SR1 SR0 6                            # Load value 127 to inner loop counter
LS SR5 SR0 7                            # Load value 1 to perform SRL divide and increment (is in the loop to reuse the register)
ADD SR6 SR2 SR0                         # Initialise Inner Loop base address (column) to current row

# Start of Inner Loop (moves rightward): (moves across row till last 2 columns left)
LS SR4 SR0 4                            # Load value 16 to divide and update VLR
MTCL SR4                                # Set VLR to 16
MULVV VR3 VR3 VR0                       # Ensure VR3 is fresh till 16 elements
SRL SR4 SR4 SR5                         # Half value of SR4 to 8
ADD SR4 SR4 SR5                         # Add 1 to value of SR4 to get 9
MTCL SR4                                # Set VLR to 9
LVI VR3 SR6 VR1                         # Load 9 element slice of current column
SUB SR4 SR4 SR5                         # Subtract 1 to value of SR4 to get 8
SLL SR4 SR4 SR5                         # Double value of SR4 to get 16 again
MTCL SR4                                # Set VLR to 16
# Start of Dot Product phase
MULVV VR4 VR2 VR3                       # Elementwise multiplication of kernel and window
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 16 to 8
MTCL SR4                                # Set VLR 8
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 8 to 4
MTCL SR4                                # Set VLR 4
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 4 to 2
MTCL SR4                                # Set VLR 2
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 2 to 1
MTCL SR4                                # Set VLR 1
ADDVV VR4 VR5 VR6                       # Accumulate final result
# End of Dot Product phase
SV VR4 SR3                              # Store convolution result in VDMEM
ADD SR3 SR3 SR5                         # Increment VDMEM base address of result by 1 for next element
ADD SR6 SR6 SR5                         # Increment current column counter by 1
ADD SR6 SR6 SR5                         # Increment current column counter by 1 more (jump 2 columns rightward)
SUB SR1 SR1 SR5                         # Decrement inner loop counter by 1
BNE SR1 SR0 -39                         # If counter != 0 jump back to start of inner loop
# End of Inner Loop

# Processing last 2 columns of the current row
# We mask the LVI operation to load only the first two elements per row of the window, effectively zero padding

CVM                                     # Clear Mask Register

LS SR4 SR0 4                            # Load value 16 to divide and update VLR
MTCL SR4                                # Set VLR to 16
MULVV VR3 VR3 VR0                       # Ensure VR3 is fresh till 16 elements
SRL SR4 SR4 SR5                         # Half value of SR4 to 8
ADD SR4 SR4 SR5                         # Add 1 to value of SR4 to get 9
MTCL SR4                                # Set VLR to 9

# Setting the mask for the LVI
LS SR5 SR0 8                            # Load memAddress for VR7 which will be used to set Mask Register
LV VR7 SR5                              # Load vector to set Mask Register
LS SR5 SR0 7                            # Reset SR5 value 1 to perform SRL divide and increment 
SNEVV VR0 VR7                           # Set Mask to 1 where VR7 is set to 1

LVI VR3 SR6 VR1                         # Load 9 element slice of current column (masked)

CVM                                     # Clear Mask Register

SUB SR4 SR4 SR5                         # Subtract 1 to value of SR4 to get 8
SLL SR4 SR4 SR5                         # Double value of SR4 to get 16 again
MTCL SR4                                # Set VLR to 16
# Start of Dot Product phase
MULVV VR4 VR2 VR3                       # Elementwise multiplication of kernel and window
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 16 to 8
MTCL SR4                                # Set VLR 8
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 8 to 4
MTCL SR4                                # Set VLR 4
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 4 to 2
MTCL SR4                                # Set VLR 2
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 2 to 1
MTCL SR4                                # Set VLR 1
ADDVV VR4 VR5 VR6                       # Accumulate final result
# End of Dot Product phase
SV VR4 SR3                              # Store convolution result in VDMEM
ADD SR3 SR3 SR5                         # Increment VDMEM base address of result by 1 for next element

SUB SR7 SR7 SR5                         # Decrement outer loop counter by 1
LS SR5 SR0 9                            # Load value 512 to increment outer base address (row) (should be reassigned back to 1 at head of loop)
ADD SR2 SR2 SR5                         # Increment row by 512 (jump two rows downward)
BNE SR7 SR0 -101                        # If counter != 0 jump back to start of outer loop
# End of Outer Loop

# Processing the last 2 rows of the matrix
LS SR1 SR0 6                            # Reload value 127 to inner loop counter

LS SR5 SR0 7                            # Load value 1 to perform SRL divide and increment (since this was done at head of outer loop)
ADD SR6 SR2 SR0                         # Initialise Inner Loop base address (column) to current row


# We mask the LVI operation to load only the first two rows of the window, effectively zero padding the last row
Start of Last Inner Loop(moves rightward): (goes till last 2 columns of last 2 rows left)
CVM                                     # Clear Mask Register

LS SR4 SR0 4                            # Load value 16 to divide and update VLR
MTCL SR4                                # Set VLR to 16
MULVV VR3 VR3 VR0                       # Ensure VR3 is fresh till 16 elements
SRL SR4 SR4 SR5                         # Half value of SR4 to 8
ADD SR4 SR4 SR5                         # Add 1 to value of SR4 to get 9
MTCL SR4                                # Set VLR to 9

# Setting the mask for the LVI
LS SR5 SR0 10                           # Load memAddress for VR7 which will be used to set Mask Register
LV VR7 SR5                              # Load vector to set Mask Register
LS SR5 SR0 7                            # Reset SR5 value 1 to perform SRL divide and increment 
SNEVV VR0 VR7                           # Set Mask to 1 where VR7 is set to 1

LVI VR3 SR6 VR1                         # Load 9 element slice of current column (masked)

CVM                                     # Clear Mask Register

SUB SR4 SR4 SR5                         # Subtract 1 to value of SR4 to get 8
SLL SR4 SR4 SR5                         # Double value of SR4 to get 16 again
MTCL SR4                                # Set VLR to 16
# Start of Dot Product phase
MULVV VR4 VR2 VR3                       # Elementwise multiplication of kernel and window
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 16 to 8
MTCL SR4                                # Set VLR 8
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 8 to 4
MTCL SR4                                # Set VLR 4
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 4 to 2
MTCL SR4                                # Set VLR 2
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 2 to 1
MTCL SR4                                # Set VLR 1
ADDVV VR4 VR5 VR6                       # Accumulate final result
# End of Dot Product phase
SV VR4 SR3                              # Store convolution result in VDMEM
ADD SR3 SR3 SR5                         # Increment VDMEM base address of result by 1 for next element
ADD SR6 SR6 SR5                         # Increment current column counter by 1
ADD SR6 SR6 SR5                         # Increment current column counter by 1 more (jump 2 columns rightward)
SUB SR1 SR1 SR5                         # Decrement inner loop counter by 1
BNE SR1 SR0 -51                         # If counter != 0 jump back to start of inner loop
# End of Last Inner Loop

# Processing last 2 columns of the last two rows (just one convolution)
# We mask the LVI operation to load only the first two elements of the first two rows of the window, effectively zero padding

CVM                                     # Clear Mask Register

LS SR4 SR0 4                            # Load value 16 to divide and update VLR
MTCL SR4                                # Set VLR to 16
MULVV VR3 VR3 VR0                       # Ensure VR3 is fresh till 16 elements
SRL SR4 SR4 SR5                         # Half value of SR4 to 8
ADD SR4 SR4 SR5                         # Add 1 to value of SR4 to get 9
MTCL SR4                                # Set VLR to 9

# Setting the mask for the LVI
LS SR5 SR0 11                           # Load memAddress for VR7 which will be used to set Mask Register
LV VR7 SR5                              # Load vector to set Mask Register
LS SR5 SR0 7                            # Reset SR5 value 1 to perform SRL divide and increment 
SNEVV VR0 VR7                           # Set Mask to 1 where VR7 is set to 1

LVI VR3 SR6 VR1                         # Load 9 element slice of current column (masked)

CVM                                     # Clear Mask Register

SUB SR4 SR4 SR5                         # Subtract 1 to value of SR4 to get 8
SLL SR4 SR4 SR5                         # Double value of SR4 to get 16 again
MTCL SR4                                # Set VLR to 16
# Start of Dot Product phase
MULVV VR4 VR2 VR3                       # Elementwise multiplication of kernel and window
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 16 to 8
MTCL SR4                                # Set VLR 8
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 8 to 4
MTCL SR4                                # Set VLR 4
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 4 to 2
MTCL SR4                                # Set VLR 2
ADDVV VR4 VR5 VR6                       # Accumulate halves to be summed again
PACKLO VR5 VR4 VR0                      # Even half of vector to be summed
PACKHI VR6 VR4 VR0                      # Odd half of vector to be summed
SRL SR4 SR4 SR5                         # Change value from 2 to 1
MTCL SR4                                # Set VLR 1
ADDVV VR4 VR5 VR6                       # Accumulate final result
# End of Dot Product phase
SV VR4 SR3                              # Store convolution result in VDMEM

HALT