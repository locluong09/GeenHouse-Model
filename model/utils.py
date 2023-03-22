import math
import numpy as np
from constants import *


def ppm_to_mgm3(ppm):
    return ppm/0.554

def mgm3_to_ppm(mgm3):
    return mgm3*0.554

def air_density(h_ele, T):
	return AIR_DENSITY * math.exp(GRAVITY * AIR_MOLAR * h_ele / ((T+273.15) * GAS_MOLAR))

def heat_cap_helper(height, density, specific_cap):
	return height*density*specific_cap

def heat_cap_VP(h, temp):
	return WATER_MOLAR*h/GAS_MOLAR/(temp + 273.15)

def FIR_flux(Ai, ei, ej, Fij, Ti, Tj):
	return Ai*ei*ej*Fij*BOLTZMANN_CONST*Fij*((Ti+273.15)**4 - (Tj+273.15)**4)

def trans_ThScrFIR_U(CV, trans_ThScr_FIR):
	return 1 - CV*(1-trans_ThScr_FIR)

def convective_conductive_flux(HEC, T1, T2):
	return HEC*(T1-T2)


def saturated_vapour_pressure(Temp):
	'''
	Formula is extracted from H.F. De Zwart. “Analyzing energy-saving options 
	in greenhouse cultivation using a simulation model”. 
	English. WU thesis 2071 Proefschrift Wageningen. PhD thesis. 1996.
	'''
	return -274.36+877.52*math.exp(0.0545*Temp)
	# return 610.78 * np.exp( Temp / ( Temp + 238.3 ) * 17.2694 )

def f_Pad_estimate(U_Pad, Cap_Pad, A_Flr):
	return U_Pad*Cap_Pad/A_Flr


def f_ThScr_estimate(U, K, T1, T2, rho_mean, rho1, rho2):
	return U*K*(abs(T1-T2))**0.66+(1-U)/rho_mean*(0.5*rho_mean*\
		(1-U)*GRAVITY*abs(rho1 - rho2))**0.5
	#todo it rho_in rho_out

def eta_Roof_estimate(U_Roof, U_Side, A_Roof, A_Side):
	if (A_Roof*U_Roof + A_Side*U_Side == 0):
		return 0
	else:
		return (A_Roof*U_Roof)/(A_Roof*U_Roof + A_Side*U_Side)

def eta_Side_estimate(U_Roof, U_Side, A_Roof, A_Side):
	if (A_Roof*U_Roof + A_Side*U_Side == 0):
		return 0
	else:
		return (A_Side*U_Side)/(A_Roof*U_Roof + A_Side*U_Side)

def f_Leakage_estimate(C_Leakge, V_Wind):
	return 0.25*C_Leakge if V_Wind < 0.25 else C_Leakge*V_Wind

def f_VentSide_estimate(eta_InsScr, f2_VentSide, f_Leakage, U_ThScr, f2_VentRoofSide,
			eta_Side, eta_Roof, eta_Roof_Thr):
	if eta_Roof < eta_Roof_Thr:
		return eta_InsScr*(U_ThScr*f2_VentSide + (1-U_ThScr)*f2_VentRoofSide*eta_Side)+0.5*f_Leakage
	else:
		return eta_InsScr*f2_VentSide+ 0.5*f_Leakage

def C_d_estimate(C_d_Gh, eta_shscrCd, U_ShScr):
	return C_d_Gh*(1-eta_shscrCd*U_ShScr)

def C_w_estimate(C_w_Gh, eta_shscrCw, U_ShScr):
	return C_w_Gh*(1-eta_shscrCw*U_ShScr)

def f2_VentSide_estimate(C_d, U_Side, A_Side, V_Wind, A_Flr, C_w):
	return ((C_d*U_Side*A_Side*V_Wind)/(2*A_Flr))*np.sqrt(C_w)

def f2_VentRoofSide_estimate(C_d, A_Flr, U_Roof, U_Side, A_Roof, A_Side, H_Side_Roof,
        T_Air, T_Out, T_mean_air, C_w, V_Wind):

	if (U_Side*A_Side == 0 and U_Roof*A_Roof == 0):
		return 0
	else:
		return (C_d/A_Flr)*(((U_Roof**2)*(U_Side**2)*(A_Roof**2)*(A_Side**2)) /\
			((U_Roof**2)*(A_Roof**2)+(U_Side**2)*(A_Side**2)) \
			* (2*GRAVITY*H_Side_Roof*(T_Air - T_Out)) / (T_mean_air + 273.15) \
			+ (((U_Roof*A_Roof + U_Side*A_Side)/2)**2) * C_w * V_Wind ** 2)**(1/2)


def f_VentRoof_estimate(eta_InsScr, f2_VentRoof, f_Leakage, U_ThScr, f2_VentRoofSide,
        eta_Roof, eta_Roof_Thr):
	if eta_Roof < eta_Roof_Thr:
		return eta_InsScr*(U_ThScr*f2_VentRoof + (1-U_ThScr)*f2_VentRoofSide*eta_Roof)+0.5*f_Leakage
	else:
		return eta_InsScr*f2_VentRoof + 0.5*f_Leakage

def f2_VentRoof_estimate(U_Roof, A_Roof, C_d, A_Flr, H_Vent, T_Air, T_Out, T_Mean, C_w, V_Wind):
	# print(T_Air)
	return U_Roof*A_Roof*C_d/2/A_Flr*np.sqrt(GRAVITY*H_Vent/2*(T_Air-T_Out)/(T_Mean+273.15)+C_w*V_Wind**2)


def f_VentForced_estimate(eta_InsScr, U_VentForced, phi_VentForced, A_Flr):
	return (eta_InsScr*U_VentForced*phi_VentForced)/A_Flr


def CO2_flux(f12, CO2_1, CO2_2):
	'''
	f12 is the CO2 flux from 1 to 2.
	'''
	return f12*(CO2_1 - CO2_2)

def MC_AirBuf(CH2O_MOLAR,h_C_Buf, P, R):
	return CH2O_MOLAR*h_C_Buf*(P-R)

def h_C_Buf_MC_Air(C_Buf, C_BUF_MAX):
	return 0 if C_Buf > C_BUF_MAX else 1

def photosynthesis_Rate(J, CO2_Stom, Gamma):
	P = J*(CO2_Stom - Gamma)/4/(CO2_Stom + 2*Gamma)
	return P

def photorespiration_Rate(P, Gamma, CO2_Stom):
	R = P*Gamma/CO2_Stom
	return R

def electron_transport_Rate(J_POT, alpha, PAR_Can, Theta):
	J = (J_POT + alpha*PAR_Can - \
			np.sqrt( (J_POT + alpha*PAR_Can)**2 - 4*Theta*J_POT \
			*alpha*PAR_Can ))/ (2*Theta)
	return J


def J_POT_estimate(J_Max_25can, Ej, T_Can, T_25, S, H ):
	return J_Max_25can*np.exp(Ej*( (T_Can + 273.15) -T_25)/(GAS_MOLAR*(10**-3)* (T_Can + 273.15) *T_25)) \
			* (1 + np.exp((S*T_25 - H)/(GAS_MOLAR*(10**-3)*T_25))) \
			/(1 + np.exp((S* (T_Can + 273.15) - H)/(GAS_MOLAR*(10**-3)* (T_Can + 273.15) )))

def J_MAX_25CAN_estimate(LAI, J_Max_25leaf):
	return LAI*J_Max_25leaf

def CO2_Stom_estimate(eta_CO2_Air_Stom, CO2_Air):
	return eta_CO2_Air_Stom*CO2_Air

def Gamma_estimate(J_Max_25can, J_Max_25leaf, c_Gamma, T_Can):
	return (J_Max_25leaf /J_Max_25can)*c_Gamma*(T_Can + 273.15) \
		+ 20*c_Gamma*(1 - (J_Max_25leaf/J_Max_25can))






















