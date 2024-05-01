CVM  

LS SR1 SR0 1 	# = 1; used for incrementing by 1
LS SR2 SR0 2	#  = 64; used to increment base address of A; also for setting VRL in packhi-packlo
LS SR3 SR0 3	# = 256 * 64;  used to increment addresses while loading slices of columns
LS SR4 SR0 0	# Counter for current column number – initial value 0
LS SR5 SR0 4	# Base address of slice of A – initial value 0
LS SR6 SR0 7	# Base address of slice of column of W – initial value 0
LS SR7 SR0 4    # = 256;  used for stride in LVWS for columns
# Start of Loop
LS SR2 SR0 2
MTCL SR2 				# Set VRL as 64
# ---------------START OF CALCULATIONS----------------
LS SR5 SR0 4
LV VR1 SR5              # Load slice of A; start 256
ADDVV VR4 VR0 VR0
LVWS VR2 SR6 SR7

MULVV  VR3 VR1 VR2
ADDVV VR4 VR4 VR3

ADD SR5 SR5 SR2
ADD SR6 SR6 SR3
# --------- END OF FIRST 64 ELEMENTS -------------------
LV VR1 SR5
LVWS VR2 SR6 SR7

MULVV  VR3 VR1 VR2
ADDVV VR4 VR4 VR3

ADD SR5 SR5 SR2
ADD SR6 SR6 SR3
# --------- END OF SECOND 64 ELEMENTS -------------------
LV VR1 SR5
LVWS VR2 SR6 SR7

MULVV  VR3 VR1 VR2
ADDVV VR4 VR4 VR3

ADD SR5 SR5 SR2
ADD SR6 SR6 SR3
# --------- END OF THIRD 64 ELEMENTS -------------------
LV VR1 SR5
LVWS VR2 SR6 SR7

MULVV  VR3 VR1 VR2
ADDVV VR4 VR4 VR3

# --------- END OF LAST 64 ELEMENTS -------------------

# VR4 Contains the aggregate dot product that needs to be summed
# Now VR1 and VR2 will store PACKLO and PACKHI intermediate values
# Now VR3 will store sum of PACKLO PACKHI as well as the final result of that column
# SR2 is now used to determine VRL length
ADDVV VR1 VR0 VR0
ADDVV VR2 VR0 VR0
PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 32
MTCL SR2			    # Use newly halved value into the VRL
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 16
MTCL SR2			    # Use newly halved value into the VRL
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 8
MTCL SR2			    # Use newly halved value into the VRL
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 4
MTCL SR2			    # Use newly halved value into the VRL 
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 2
MTCL SR2			    # Use newly halved value into the VRL
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

PACKLO VR1 VR4 VR0		# store even elements of result into first half of VR1
PACKHI VR2 VR4 VR0		# store odd elements of result into first half of VR2
SRL SR2 SR2 SR1 		# Use right shift to halve the value of SR2 – to 1
MTCL SR2			    # Use newly halved value into the VRL
ADDVV VR4 VR1 VR2		# Sum the two halves of the result

# Now SR2 + column number is used to determine the VDMEM address for the calculated element
LS SR2 SR0 0
ADD SR2 SR2 SR4
SV VR4 SR2
ADD SR4 SR4 SR1 		# increment column number; memory address as well 
LS SR6 SR0 7
ADD SR6 SR4 SR6 		# SR_Base = column number 

BNE SR7 SR4 -92         # – JUMP TO START OF LOOP

LS SR2 SR0 2            # Set SR2 to 64
MTCL SR2                # Set VLR to 64
LS SR3 SR0 5            # Set SR3 to 512
LS SR6 SR0 0            # Set SR6 to 0

LV VR1 SR3              # – this will load vector B from the input VDMEM
LV VR2 SR6              # – this will load the result vector of a * W from the VDMEM
ADDVV VR3 VR1 VR2
SV VR3 SR6              # – storing the final results

ADD SR3 SR3 SR2
ADD SR6 SR6 SR2
LV VR1 SR3              # – this will load vector B from the input VDMEM
LV VR2 SR6              # – this will load the result vector of a * W from the VDMEM
ADDVV VR3 VR1 VR2
SV VR3 SR6              # – storing the final results

ADD SR3 SR3 SR2
ADD SR6 SR6 SR2
LV VR1 SR3              # – this will load vector B from the input VDMEM
LV VR2 SR6              # – this will load the result vector of a * W from the VDMEM
ADDVV VR3 VR1 VR2
SV VR3 SR6              # – storing the final results

ADD SR3 SR3 SR2
ADD SR6 SR6 SR2
LV VR1 SR3              # – this will load vector B from the input VDMEM
LV VR2 SR6              # – this will load the result vector of a * W from the VDMEM
ADDVV VR3 VR1 VR2
SV VR3 SR6              # – storing the final results


HALT