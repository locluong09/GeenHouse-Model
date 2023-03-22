from typing import NamedTuple

n_Dev  = 5

class StateVariables_Crop(NamedTuple):
	# TS_Can : float # The development rate of the plant is equal to the instantaneous temperature
	C_Buf : float # The evolution of the carbohydrates in the buffer
	# C_Fruit : [float for i in range(n_Dev)] # carbohydrates stored in the fruit development stage j:
	# N_Fruit : [int for i in range(n_Dev)] # The number of fruits in the fruit development stage i
	# C_Leaf : float # The carbohydrates stored in the leaves
	# C_Stem : float #The carbohydrates stored in the stem and roots
	# T_Can_24 : float # The 24h mean canopy temperature