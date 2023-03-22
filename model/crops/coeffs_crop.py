from typing import List, NamedTuple

class coefficients(object):
	def __init__(self, alpha, C_MAX_Buf, c_Gamma, Ej, eta_CO2_Air_Stom, J_Max_25leaf, M_CH2O, S, T_25,
					H, PAR_can, Theta):
		self.alpha = alpha
		self.C_MAX_Buf = C_MAX_Buf
		self.c_Gamma = c_Gamma
		self.Ej = Ej
		self.eta_CO2_Air_Stom = eta_CO2_Air_Stom
		self.J_Max_25leaf = J_Max_25leaf
		self.M_CH2O = M_CH2O
		self.S = S
		self.T_25 = T_25
		self.H = H
		self.PAR_can = PAR_can
		self.Theta = Theta
