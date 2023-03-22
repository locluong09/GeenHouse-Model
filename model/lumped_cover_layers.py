import math
from constants import *


'''
	In the lumped cover layers model, there are 4 layers:
		1. movable outdoor shading screen ()
		2. semi-permanent shading screen
		3. greenhouse roof
		4. movable indoor thermal screen
	To simplify the model, individual properties of the four layers are lumped together
	into a lumped model (cover layers).
	First, we define two helper function 
		- trans_reflec_cooeff
		- two_layers_trans_reflec_coeffs
	Then, use them to calcualate the lumped properties of the model

'''

def trans_reflec_coeffs(trans1, trans2, reflec1, reflec2):
	'''
	Calculate transmission and reflection coefficient of a double layer
		Layer 1: transmission coeff 1, reflection coeff 1
		Layer 2: transmission coeff 2, reflection coeff 2
	'''
	trans12 = trans1*trans2/(1-reflec1*reflec2)
	reflec12 = reflec1+ trans1**2*reflec2/(1-reflec1*reflec2)

	return (trans12, reflec12)

def two_layers_trans_reflec_coeffs(U1, U2, trans1, trans2, reflec1, reflec2):
	'''
	Calculate the transmission and reflection coefficient of the movable shading screen
	and the semi-perminent shading screen:
		U1 (U_ShScr) : control of the layer 1
		U2 (U_ShScrPer) : control of the layer 2
		trans1, trans2 : PAR transmission coeffs of layers 1 and 2, respectively
		reflec1, reflec2 : reflection coeffs of layers 1 and 2, respectively
	'''
	trans12 =  (1 - U1*(1-trans1))*(1-U2*(1-trans2))/(1-U1*reflec1*U2*reflec2)
	reflec12 =  trans1*reflec1 + (1 - U1*(1-trans1))**2*trans2*reflec2/(1-U1*reflec1*U2*reflec2)

	return (trans12, reflec12)


def PAR_lumped_model(
	U_ShScr : float, # control of shading screen
	U_ShScrPer : float, # control of semi-permanent shading screen
	PAR_transmission1 : float,
	PAR_transmission2 : float,
	PAR_reflection1 : float,
	PAR_reflection2 : float,

	U_Roof : float, # control of roof
	U_ThScr : float, # control of thermal screen
	PAR_transmission3 : float,
	PAR_transmission4 : float,
	PAR_reflection3 : float,
	PAR_reflection4 : float
	):

	(trans12, reflec12) = two_layers_trans_reflec_coeffs(U_ShScr, U_ShScrPer,
											PAR_transmission1,
											PAR_transmission2,
											PAR_reflection1,
											PAR_reflection2)

	(trans34, reflec34) = two_layers_trans_reflec_coeffs(U_Roof, U_ThScr,
											PAR_transmission3,
											PAR_transmission4,
											PAR_reflection3,
											PAR_reflection4)
	lumped_trans, lumped_reflec =  trans_reflec_coeffs(trans12, trans34, reflec12, reflec34)
	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
	return (lumped_trans, lumped_reflec, lumped_absortion)


def NIR_lumped_model(
	U_ShScr : float, # control of shading screen
	U_ShScrPer : float, # control of semi-permanent shading screen
	NIR_transmission1 : float,
	NIR_transmission2 : float,
	NIR_reflection1 : float,
	NIR_reflection2 : float,

	U_Roof : float, # control of roof
	U_ThScr : float, # control of thermal screen
	NIR_transmission3 : float,
	NIR_transmission4 : float,
	NIR_reflection3 : float,
	NIR_reflection4 : float
	):

	(trans12, reflec12) = two_layers_trans_reflec_coeffs(U_ShScr, U_ShScrPer,
											NIR_transmission1,
											NIR_transmission2,
											NIR_reflection1,
											NIR_reflection2)

	(trans34, reflec34) = two_layers_trans_reflec_coeffs(U_Roof, U_ThScr,
											NIR_transmission3,
											NIR_transmission4,
											NIR_reflection3,
											NIR_reflection4)
	lumped_trans, lumped_reflec =  trans_reflec_coeffs(trans12, trans34, reflec12, reflec34)
	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
	return (lumped_trans, lumped_reflec, lumped_absortion)

def FIR_lumped_model(
	U_ShScr : float, # control of shading screen
	U_ShScrPer : float, # control of semi-permanent shading screen
	FIR_transmisson1 : float,
	FIR_transmission2 : float,
	FIR_reflection1 : float,
	FIIR_reflection2 : float,

	U_Roof : float, # control of roof
	U_ThScr : float, # control of thermal screen
	FIR_transmission3 : float,
	FIR_transmission4 : float,
	FIR_reflection3 : float,
	FIR_reflection4 : float
	):

	(trans12, reflec12) = two_layers_trans_reflec_coeffs(U_ShScr, U_ShSrcPer,
											FIR_transmission1,
											FIR_transmission2,
											FIR_reflection1,
											FIR_reflection2)

	(trans34, reflec34) = two_layers_trans_reflec_coeffs(U_Roof, U_ThScr,
											FIR_transmission3,
											FIR_transmission3,
											FIR_reflection4,
											FIR_reflection4)
	lumped_trans, lumped_reflec =  trans_reflec_coeffs(trans12, trans34, reflec12, reflec34)
	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
	return (lumped_trans, lumped_reflec, lumped_absortion)

# def NIR_lumped_model():
# 	(trans12, reflec12) = two_layers_trans_reflec_coeffs(CV.U_ShScr, CV.U_ShSrcPer,
# 											coef.Shadowscreen.NIR_transmission,
# 											coef.Whitewash.NIR_transmission,
# 											coef.Shadowscreen.NIR_reflection,
# 											coef.Whitewash.NIR_reflection)

# 	(trans34, reflec34) = two_layers_trans_reflec_coeffs(CV.U_Roof, CV.U_ThScr,
# 											coef.Roof.NIR_transmission,
# 											coef.Thermalscreen.NIR_transmission,
# 											coef.Roof.NIR_reflection,
# 											coef.Thermalscreen.NIR_reflection)
# 	lumped_trans, lumped_reflec =  trans_reflec_coeffs(tran12, trans34, reflec12, reflec34)
# 	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
# 	return (lumped_trans, lumped_reflec, lumped_absortion)
	

# def FIR_lumped_model():
# 	(trans12, reflec12) = two_layers_trans_reflec_coeffs(CV.U_ShScr, CV.U_ShSrcPer,
# 											coef.Shadowscreen.FIR_transmission,
# 											coef.Whitewash.FIR_transmission,
# 											coef.Shadowscreen.FIR_reflection,
# 											coef.Whitewash.FIR_reflection)

# 	(trans34, reflec34) = two_layers_trans_reflec_coeffs(CV.U_Roof, CV.U_ThScr,
# 											coef.Roof.FIR_transmission,
# 											coef.Thermalscreen.FIR_transmission,
# 											coef.Roof.FIR_reflection,
# 											coef.Thermalscreen.FIR_reflection)
# 	lumped_trans, lumped_reflec =  trans_reflec_coeffs(tran12, trans34, reflec12, reflec34)
# 	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
# 	lumped_emission = lumped_absortion
# 	return (lumped_trans, lumped_reflec, lumped_absortion, lumped_emission)


def CAP_lumped_model(
	Psi : float, # mean green house cover slope 
	U_ShSrcPer,  #control of semi-permanent shading screen
	h_ShSrcPer, # thickness
	rho_ShSrcPer, # density
	CP_ShSrcPer, # specific capacity
	h_Rf, # thickness of roof
	rho_Rf, # density of roof
	CP_Rf): # speicific capacity of roof

	CAP_cov = math.cos(Psi)*(U_ShSrcPer*h_ShSrcPer*rho_ShSrcPer*CP_ShSrcPer +\
	 				h_Rf*rho_Rf*CP_Rf)

	return CAP_Cov


def HEC_lumped_model(
	h_Rf : float, # roof thickness 
	lambda_Rf : float, # heat conductivity of semi-perminent shading screen
	U_ShSrcPer : float, # control of semi-perminent shading screen
	h_ShSrcPer : float, # thichkness
	lambda_ShSrcPer : float # conductivity of semi-perminent shading sceen
	):

	HEC_lumped = 1/(h_Rf/lambda_Rf + U_ShSrcPer*h_ShSrcPer/lambda_ShSrcPer)
	return HCE_lumped











