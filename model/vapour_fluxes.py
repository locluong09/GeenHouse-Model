import math
import numpy as np
from constants import *
from utils import saturated_vapour_pressure as svp

def MV_AirThScr(T_Air, T_ThScr, U_ThScr, VP_Air):
	VP_ThScr = svp(T_ThScr)
	HEC = 1.7*U_ThScr*(abs(T_Air - T_ThScr))**0.33
	if VP_Air <= VP_ThScr:
		return 0
	else:
		return 6.4*1E-9*HEC*(VP_Air - VP_ThScr)

def MV_TopCov_in(T_Top, T_Cov_in, C_HECin, A_Cov, A_Flr, VP_Top):
	HEC = C_HECin*(T_Top - T_Cov_in)**0.33*A_Cov/A_Flr
	# VP_Top = svp(T_Top)
	VP_Cov_in = svp(T_Cov_in)
	if VP_Top <= VP_Cov_in:
		return 0
	else:
		return 6.4*1E-9*HEC*(VP_Top - VP_Cov_in)

def MV_AirTop(T_Air, T_Top, f_ThScr, VP_Air, VP_Top):
	# print("abc",VP_Air/(T_Air + 273.15) - VP_Top/(T_Top+273.15))
	return WATER_MOLAR/GAS_MOLAR*f_ThScr*(VP_Air/(T_Air + 273.15) - VP_Top/(T_Top+273.15))

def MV_AirOut(T_Air, T_Out, f_VentSide, f_VentForced, VP_Air, VP_Out):
	# VP_Out = svp(T_Out)
	return WATER_MOLAR/GAS_MOLAR*(f_VentSide+f_VentForced)*(VP_Air/(T_Air + 273.15) - VP_Out/(T_Out+273.15))

def MV_TopOut(T_Top, T_Out, f_VentRoof, VP_Top, VP_Out):
	# VP_Out = svp(T_Out)
	# print((VP_Top/(T_Top + 273.15) - VP_Out/(T_Out+273.15)))
	return WATER_MOLAR/GAS_MOLAR*f_VentRoof*(VP_Top/(T_Top + 273.15) - VP_Out/(T_Out+273.15))


def MV_FogAir(U_Fog, Cap_Fog, A_Flr):
	return U_Fog*Cap_Fog/A_Flr

def MV_PadAir(rho_air, f_Pad, eta_Pad, x_Pad, x_Out):
	return rho_air*f_Pad*(eta_Pad*(x_Pad-x_Out)+ x_Out)

def MV_AirOutPad(f_Pad, VP_Air, T_Air):
	return f_Pad*WATER_MOLAR/GAS_MOLAR*VP_Air/(T_Air+273.15)

def MV_AirMech(U_Mech, COP_Mech, P_Mech, A_Flr, T_Air, T_Mech, VP_Air):
	VP_Mech = saturated_vapour_pressure(T_Mech)
	return (U_Mech*COP_Mech*P_Mech/A_Flr)/(T_Air - T_Mech + 6.4e-9*LATENT_EVAPORATION*(VP_Air-VP_Mech))*6.4E-9*(VP_Air - VP_Mech)


def MV_CanAir(T_Can, VP_Air,
	rho_air, LAI, R_Can, CO2_Air
	):
	'''
	Caculate the evaporation of the foliage
	:param VEC_can_air: Caculate from VEC_can_air funtion
	:param VP_can: 		Canopy vapour pressure
	:param VP_air:		Air vapour pressure 
	'''

	VP_Can = svp(T_Can)
	return VEC_can_air(rho_air, LAI, R_Can, CO2_Air, T_Can, VP_Air)*(VP_Can-VP_Air)

def VEC_can_air(rho_air, LAI, R_Can, CO2_Air, T_Can, VP_Air):
	'''
	Caculate vapour exchange coefficient
	:param rho_air: The density of greenhouse air
	:param c_p_air: Heat capacity of air
	:param LAI:		The leaf area index
	:param delta_h: Latent heat of evaporation
	:param gamma:		Psychrometric constant
	:param r_b:		Boundary layer resistance of the canopy for vapour transport
	:param r_s:		The canopy resistance for transpiration
	'''
	return (2*rho_air*CP_AIR*LAI)/(LATENT_EVAPORATION*GAMMA*(R_B+r_s(R_Can, CO2_Air, T_Can, VP_Air)))

def r_s(R_Can, CO2_Air, T_Can, VP_Air):
	'''
	Caculate the transpiration resistance
	:param r_s_min:    Minimum canopy resistance 
	'''
    # return 82
	return R_S_MIN*rf_R_can(R_Can)*rf_CO2(CO2_Air, R_Can)*rf_VP(T_Can, VP_Air, R_Can)

def rf_R_can(R_Can):
	'''
	Caculate the canopy resistance factor
	:param R_can:       Radiation above the canopy
	:param c_evap1: 	Observed param 1
	:param c_evap2:		Observed param 1 
	'''
	return ((R_Can+C_EVAP1)/(R_Can+C_EVAP2))

def rf_CO2(CO2_Air, R_Can):
	'''
	Caculate the resistance factor of Co2 in the lower compartment
	:param c_evap3: 	Observed param 3
	:param CO2_air:		CO2 amount in the lower compartment 
	'''
	temp = 1+c_evap3(R_Can)*(CO2_Air-200)**2
	return temp
	if temp <= 1.5:
		return temp
	return 1.5

def rf_VP(T_Can, VP_Air, R_Can):
	'''
	Caculate the resistance factor of vapour pressire in the lower compartment
	:param c_evap3: 	Observed param 4
	:param VP_air:		Vapour pressure in the lower compartment 
	:param VP_can:		Vapour pressure at the canopy 
	'''
	VP_Can = svp(T_Can)
	temp = 1+c_evap4(R_Can)*(VP_Can-VP_Air)**2
	return temp
	if temp <=5.8:
		return temp
	return 5.8

def S_rs(R_Can):
	'''
	Caculate the switch function
	:param s_r_s: 	    Slope of the function
	:param R_can:		Radiation above canopy 
	:param R_can_SP:	Radiation abobe canopy at night 
	'''
	return 1/(1+np.exp(S_R_S*(R_Can-RAD_CANOPY_SP)))

def c_evap3(R_Can):
	'''
	Caculate the resistance factor of vapour pressire in the lower compartment
	:param c_night_evap3: 	c_evap at night
	:param c_day_evap3:		c_evap at day
	'''
	return C_NIGHT_EVAP3*(1-S_rs(R_Can))+C_DAY_EVAP3*S_rs(R_Can)
def c_evap4(R_Can):
	'''
	Caculate the resistance factor of vapour pressire in the lower compartment
	:param c_night_evap4: 	c_evap at night
	:param c_day_evap4:		c_evap at day
	'''
	return C_NIGHT_EVAP4*(1-S_rs(R_Can))+C_DAY_EVAP4*S_rs(R_Can)



