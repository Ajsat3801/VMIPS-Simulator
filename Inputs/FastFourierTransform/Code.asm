# 544 -> START OF REAL PART OF inputs
# 672 -> START OF VIRTUAL PART OF inputs
# 800 -> START OF REAL PART OF TWIDDLE factors
# 864 -> START OF VIRTUAL PARTS OF TWIDDLE FACTORS

# LOGIC
# The input vectors are loaded in the order of the leaf nodes in the recursion tree.
# The input has 2 vectors; 1 for the real part and 1 for complex part
# The iterations are unrolled and the result of each iteration can be simulated as follows:
#   The even elements: 
#       Real        : a_1 + a_2*c + b_2*d
#       Imaginary   : a_1 - a_2*d - b_2*c
#   The odd elements:
#       Real        : b_1 + a_2*d + b_2*c
#       Imaginary   : b_1 - a_2*d - b_2*c
 
# The above equations are applied when the even input is (a_1 + b_1 j), the odd input is (a_2 + b_2 j) and the twiddle factors are (c + d j)

CVM
LS SR1 SR0 1
LS SR2 SR0 12
LS SR3 SR0 3
LS SR4 SR0 4

MTCL SR4

LS SR5 SR0 10
LS SR6 SR0 6
LS SR7 SR0 11

LV VR4 SR5 # Load index vector for even elements
LVI VR7 SR6 VR4 # Use LVI to load even elements in order of leaf nodes of recursion tree

# Load VR3, VR4, VR5, VR6
PACKLO VR3 VR7 VR0      # a_1 is loaded to VR3
PACKHI VR5 VR7 VR0      # a_2 is loaded to VR5

ADD SR6 SR6 SR4
ADD SR6 SR6 SR4

LVI VR7 SR6 VR4
PACKLO VR4 VR7 VR0      # b_1 loaded to VR4
PACKHI VR6 VR7 VR0      # b_2 loaded to VR6

LS SR5 SR0 8
ADD SR6 SR5 SR4

ADDVV VR7 VR0 VR0

# ------------------ FIRST ITERATION (1/6) --------------------------
MTCL SR3

LV VR7 SR0              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1       # a_2*c
DIVVS VR5 VR5 SR2       # dividing due to offset 
MULVV VR6 VR6 VR2       # b_2*d
DIVVS VR6 VR6 SR2       # dividing due to offset

SUBVV VR7 VR3 VR5       # a_1 - a_2*c
SUBVV VR7 VR7 VR6       # a_1 - a_2*c - b_2*d (odd elements of the result)

ADDVV VR3 VR3 VR5       # a_1 + a_2*c
ADDVV VR3 VR3 VR6       # a_1 + a_2*c + b_2*d (even elements of the result)

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

# Reverting a_2*c and b_2*d due to register constraints
MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2       # a_2*d
MULVV VR6 VR6 VR1       # b_2*c
DIVVS VR5 VR5 SR2       # dividing due to offset 
DIVVS VR6 VR6 SR2       # dividing due to offset 

SUBVV VR7 VR4 VR5       # b1 - a_2*d
SUBVV VR7 VR7 VR6       # b1 - a_2*d - b_2*c (odd elements of the result)

ADDVV VR4 VR4 VR5       # b1 + a_2*d
ADDVV VR4 VR4 VR6       # b1 + a_2*d - b_2*c (even elements of the result)

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration
ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 2ND ITERATION (2/6) ------------------

MTCL SR3

LV VR7 SR7                # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 3RD ITERATION (3/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 4th ITERATION (4/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 5th ITERATION (5/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 6th ITERATION (6/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADD SR4 SR4 SR4

SV VR3 SR0 
SV VR4 SR4

SUB SR4 SR4 SR3
SUB SR4 SR4 SR3

LS SR7 SR0 11

# --------------- COMPUTATION COMPLETE FOR EVEN HALF OF INPUT

MTCL SR4

LV VR4 416 # Load index vector for even elements
LVI VR7 544 VR4 # Use LVI to load even elements in order of leaf nodes of recursion tree

# Load VR3, VR4, VR5, VR6
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

LS SR7 SR0 7

LVI VR7 SR7 VR4
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# ------------------ FIRST ITERATION (1/6) --------------------------
MTCL SR3

LV VR7 SR4                # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration
ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 2ND ITERATION (2/6) ------------------

MTCL SR3

LS SR7 SR0 11
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 3RD ITERATION (3/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 4th ITERATION (4/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 5th ITERATION (5/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# Load VR3, VR4, VR5, VR6 for next iteration

ADDVV VR7 VR3 VR0
PACKLO VR3 VR7 VR0
PACKHI VR5 VR7 VR0

ADDVV VR7 VR4 VR0
PACKLO VR4 VR7 VR0
PACKHI VR6 VR7 VR0

# -------------------- 6th ITERATION (6/6) ------------------

MTCL SR3

SUB SR7 SR7 SR3
LV VR7 SR7              # Load index for twiddle factor
LVI VR1 SR5 VR7         # Load real part of twiddle factors
LVI VR2 SR6 VR7         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

MTCL SR4
UNPACKLO VR3 VR3 VR7    # Result of the real part of this iteration
MTCL SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6

MTCL SR4
UNPACKLO VR4 VR4 VR7    # Result of the virtual part of this iteration

# --------------- COMPUTATION COMPLETE FOR ODD HALF OF INPUT

# VR3 -> REAL OF ODD HALF
# VR4 -> VIRTUAL OF ODD HALF

# VR1 -> REAL OF EVEN HALF
# VR2 -> VIRTUAL OF EVEN HALF

LV VR1 SR1
ADD SR4 SR4 SR4
LV VR2 SR4
SUB SR4 SR4 SR3
SUB SR4 SR4 SR3

ADDVV VR7 VR3 VR0
PACKLO VR3 VR1 VR7
PACKHI VR5 VR1 VR7 

ADDVV VR7 VR4 VR0
PACKLO VR4 VR2 VR7
PACKHI VR6 VR2 VR7

LV VR1 SR5         # Load real part of twiddle factors
LV VR2 SR6         # Load virtual parts of twiddle factors

MULVV VR5 VR5 VR1
DIVVS VR5 VR5 SR2
MULVV VR6 VR6 VR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR3 VR5
SUBVV VR7 VR7 VR6

ADDVV VR3 VR3 VR5
ADDVV VR3 VR3 VR6

SLL SR3 SR1 SR1

SVWS VR3 SR0 SR3    # The two stores result in the final output of real part 
SVWS VR7 SR1 SR3

MULVS VR5 VR5 SR2
MULVS VR6 VR6 SR2
DIVVV VR5 VR5 VR1
DIVVV VR6 VR6 VR2

MULVV VR5 VR5 VR2
MULVV VR6 VR6 VR1
DIVVS VR5 VR5 SR2
DIVVS VR6 VR6 SR2

SUBVV VR7 VR4 VR5
SUBVV VR7 VR7 VR6

ADDVV VR4 VR4 VR5
ADDVV VR4 VR4 VR6
SLL SR4 SR4 SR1
SVWS VR4 SR4 SR3    # The two stores result in the final output of virtual part 
ADD SR4 SR4 SR1
SVWS VR7 SR4 SR3

HALT