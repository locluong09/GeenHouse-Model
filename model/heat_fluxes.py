import math
from constants import *
from utils import *

from lumped_cover_layers import trans_reflec_coeffs, two_layers_trans_reflec_coeffs


'''
PAR absorbed by canopy (R_PAR_SunCan)is the sum of the PAR transmitted 
by the greenhouse cover that is directly absorbed by the canopy ( R_PAR_SunCan↓ ),
and the PAR thatis first reflected by the greenhouse floor and then is absorbed 
by the canopy ( R_PAR_FlrCan)
'''

def PAR_absorbed_SunCanFlr(
	R_PAR_Gh,
	LAI, # the leaf area index
	PAR_reflection_Flr
	):
	R_PAR_SunCan = PAR_SunCan_absorbed_Can(R_PAR_Gh, LAI) + \
				PAR_SunCan_after_reflection_Floor(R_PAR_Gh, PAR_reflection_Flr, LAI)

	R_PAR_SunFlr = (1-PAR_reflection_Flr)*math.exp(-K1_PAR_CAN*LAI)*R_PAR_Gh

	return (R_PAR_SunCan, R_PAR_SunFlr)

def PAR_above_Can(Ratio_Glob_Air, PAR_trans_Cov, I_Glob):
	R_PAR_Gh = (1-Ratio_Glob_Air)*PAR_trans_Cov*RATIO_GLOB_PAR*I_Glob
	return R_PAR_Gh

def PAR_SunCan_absorbed_Can(
	R_PAR_Gh, # is the PAR above the canopy
	LAI # the leaf area index
	):
	PAR_Sun_absorbed_Can = R_PAR_Gh*(1-PAR_REFLECTION_CAN)*(1-math.exp(-K1_PAR_CAN*LAI))
	return PAR_Sun_absorbed_Can

def PAR_SunCan_after_reflection_Floor(
	R_PAR_Gh, # is the PAR above the canopy
	PAR_reflection_Flr, # PAR reflection coeff of the floor
	LAI):
	PAR_FlrCan = R_PAR_Gh*math.exp(-K1_PAR_CAN*LAI)*PAR_reflection_Flr*\
				(1-PAR_REFLECTION_CAN)*(1-math.exp(-K2_PAR_CAN*LAI))
	return PAR_FlrCan


'''
NIR absorbed by canopy and floor is determined by the lumped cover,
the canopy, and the floor as multiple layer model.

Global radiations absorbed by greenhouse and cover are alse determined by
using the lumped model.
'''

def virtual_NIR_transmission_Cov_Floor(
	NIR_reflec_Cov, 
	NIR_reflec_Flr
	):
	trans_CovNIR = 1 - NIR_reflec_Cov
	trans_FlrNIR = 1 - NIR_reflec_Flr
	return (trans_CovNIR, trans_FlrNIR)

def NIR_transmission_reflection_Can(LAI):
	trans = math.exp(-K_NIR_CAN*LAI)
	reflec = NIR_REFLECTION_CAN*(1-trans)
	return (trans, reflec)

def lumped_Cov_Can_Flr_coeffs(
	NIR_reflec_Cov, # lumped NIR reflection of cover
	NIR_reflec_Flr, # NIR reflection of Floor
	LAI, # leaf area index
	):
	(trans_CovNIR, trans_FlrNIR) = virtual_NIR_transmission_Cov_Floor(NIR_reflec_Cov,NIR_reflec_Flr)
	(trans_Can, reflec_Can) = NIR_transmission_reflection_Can(LAI)

	trans12, reflec12 = two_layers_trans_reflec_coeffs(1,1, trans_CovNIR, trans_FlrNIR, \
					NIR_reflec_Cov, NIR_reflec_Flr)

	lumped_trans, lumped_reflec = trans_reflec_coeffs(trans12, trans_Can, reflec12, reflec_Can)
	lumped_absortion = 1 - (lumped_trans + lumped_reflec)
	return (lumped_trans, lumped_reflec, lumped_absortion)


def NIR_Glob_absorbed_SunCanFlr(
	NIR_reflec_Cov,
	NIR_reflec_Flr,
	LAI,
	Ratio_Glob_Air,
	I_Glob,
	PAR_trans_Cov,
	NIR_absortion_Cov,
	PAR_absortion_Cov
	):

	(trans, reflec, absortion) = lumped_Cov_Can_Flr_coeffs(NIR_reflec_Cov, NIR_reflec_Flr, LAI)

	NIR_Can_absortion = absortion
	NIR_Flr_absortion = trans

	R_NIR_SunCan = (1-Ratio_Glob_Air)*NIR_Can_absortion*RATIO_GLOB_NIR*I_Glob
	R_NIR_SunFlr = (1-Ratio_Glob_Air)*NIR_Flr_absortion*RATIO_GLOB_NIR*I_Glob

	# global radiation absorbed by greenhouse construction elements
	R_Glob_SunAir = Ratio_Glob_Air*I_Glob*(PAR_trans_Cov*RATIO_GLOB_PAR+\
					(NIR_Can_absortion+NIR_Flr_absortion)*RATIO_GLOB_NIR)

	#global radiation absorbed by cover
	R_Glob_SunCov = (PAR_absortion_Cov*RATIO_GLOB_PAR+NIR_absortion_Cov*RATIO_GLOB_NIR)*I_Glob

	return (R_NIR_SunCan, R_NIR_SunFlr, R_Glob_SunAir, R_Glob_SunCov)


#========

def R_CanCov_in(
	LAI, 
	U_ThScr, 
	FIR_trans_ThScr, 
	FIR_emission_Cov, 
	T_Can, 
	T_Cov_in):
	# emission_Cov is lumped emission of cover which equation to lumped absortion of cover
	A_Can = 1 - math.exp(-K_FIR_CAN*LAI)
	F_CanCov_in = trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)
	return FIR_flux(A_Can, FIR_EMISSION_CAN, FIR_emission_Cov, F_CanCov_in, T_Can, T_Cov_in)

def R_CanSky(
	LAI,
	U_ThScr,
	FIR_trans_Cov,
	FIR_trans_ThScr,
	T_Can,
	T_Sky):
	#lumped_FIR_trans is the lumped FIR transmission of cover
	A_Can = 1 - math.exp(-K_FIR_CAN*LAI)
	F_CanSky = FIR_trans_Cov * trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)
	return FIR_flux(A_Can, FIR_EMISSION_CAN, FIR_EMISSION_SKY, F_CanSky, T_Can, T_Sky)

def R_CanThScr(
	LAI,
	U_ThScr,
	FIR_emission_ThScr,
	T_Can,
	T_ThScr
	):
	A_Can = 1 - math.exp(-K_FIR_CAN*LAI)
	F_CanThScr = U_ThScr
	return FIR_flux(A_Can, FIR_EMISSION_CAN, FIR_emission_ThScr, F_CanThScr, T_Can, T_ThScr)

def R_CanFlr(
	LAI,
	length_Pipe,
	D_ex,
	FIR_emission_Flr):
	A_Can = 1 - math.exp(-K_FIR_CAN*LAI)
	F_CanFlr = 1 - 0.49*math.pi*length_Pipe*D_ex
	return FIR_flux(A_Can, FIR_EMISSION_CAN, FIR_emission_Flr, F_CanFlr, T_Can, T_Flr)

def R_PipeCov_in(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_trans_ThScr,
	FIR_emission_Pipe,
	FIR_emission_Cov,
	T_Pipe,
	T_Cov_in):
	A_Pipe = math.pi*length_Pipe*D_ex
	F_PipeCov_in = trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)*0.49*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Pipe, FIR_emission_Pipe, emission_Cov, F_PipeCov_in, T_Pipe, T_Cov_in)

def R_PipeSky(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_trans_Cov,
	FIR_trans_ThScr,
	FIR_emission_Pipe,
	T_Pipe,
	T_Sky):
	A_Pipe = math.pi*length_Pipe*D_ex
	F_PipeSky = FIR_trans_Cov*trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)*0.49*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Pipe, FIR_emission_Pipe, FIR_EMISSION_SKY, F_PipeSky, T_Pipe, T_Sky)

def R_PipeThScr(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_emission_Pipe,
	FIR_emission_ThScr,
	T_Pipe,
	T_ThScr):
	A_Pipe = math.pi*length_Pipe*D_ex
	F_PipeThScr= U_ThScr*0.49*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Pipe, FIR_emission_Pipe, FIR_emission_ThScr, F_PipeThScr, T_Pipe, T_ThScr)

def R_PipeFlr(
	length_Pipe,
	D_ex,
	FIR_emission_Pipe,
	FIR_emission_Flr,
	T_Pipe,
	T_Flr):
	A_Pipe = math.pi*length_Pipe*D_ex
	F_PipeFlr = 0.49
	return FIR_flux(A_Pipe, FIR_emission_Pipe, FIR_emission_Floor, F_PipeFlr, T_Pipe, T_Flr)

def R_PipeCan(
	LAI,
	length_Pipe,
	D_ex,
	FIR_emission_Pipe,
	T_Pipe,
	T_Can):
	A_Pipe = math.pi*length_Pipe*D_ex
	F_PipeCan = 0.49*(1-math.exp(-K_FIR_CAN*LAI))
	return FIR_flux(A_Pipe, FIR_emission_Pipe, FIR_EMISSION_CAN, F_PipeCan, T_Pipe, T_Can)

def R_FlrCov_in(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_trans_ThScr,
	FIR_emission_Flr,
	FIR_emission_Cov,
	T_Flr,
	T_Cov_in):
	A_Flr = 1
	F_FlrCov_in = trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)*\
				(1- 0.49*math.pi*length_Pipe*D_ex)*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Flr, FIR_emission_Flr, FIR_emission_Cov, F_FlrCov_in, T_Flr, T_Cov_in)

def R_FlrSky(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_trans_Cov,
	FIR_trans_ThScr,
	FIR_emission_Flr,
	T_Flr,
	T_Sky):
	A_Flr = 1
	F_FlrSky = FIR_trans_Cov * trans_ThScrFIR_U(U_ThScr, FIR_trans_ThScr)*\
				(1- 0.49*math.pi*length_Pipe*D_ex)*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Flr, FIR_emission_Flr, FIR_EMISSION_SKY, F_FlrSky, T_Flr, T_Sky)

def R_FlrThScr(
	LAI,
	length_Pipe,
	D_ex,
	U_ThScr,
	FIR_emission_Flr,
	FIR_emission_ThScr,
	T_Flr,
	T_ThScr):
	A_Flr = 1
	F_FlrThScr= U_ThScr*(1- 0.49*math.pi*length_Pipe*D_ex)*math.exp(-K_FIR_CAN*LAI)
	return FIR_flux(A_Flr, FIR_emission_Flr, FIR_emission_ThScr, F_FlrThScr, T_Flr, T_ThScr)

def R_ThScrCov_in(
	U_ThScr,
	FIR_emission_ThScr,
	FIR_emission_Cov,
	T_ThScr,
	T_Cov_in):
	A_ThScr = 1
	F_ThScrCov_in = U_ThScr
	return FIR_flux(A_ThScr, FIR_emission_ThScr, FIR_emission_Cov, F_ThScrCov_in, T_ThScr, T_Cov_in)

def R_ThScrSky(
	U_ThScr,
	FIR_trans_Cov,
	FIR_emission_ThScr,
	T_ThScr,
	T_Sky):
	A_ThScr = 1
	F_ThScrSky = FIR_trans_Cov*U_ThScr
	return FIR_flux(A_ThScr, FIR_emission_ThScr, FIR_EMISSION_SKY, F_ThScrSky, T_ThScr, T_Sky)

def R_Cov_e_Sky(
	FIR_emission_Cov,
	T_Cov_e,
	T_Sky):
	A_Cov_e = 1
	F_Cov_e_Sky = 1
	return FIR_flux(A_Cov_e, FIR_emission_Cov, FIR_EMISSION_SKY, F_Cov_e_Sky, T_Cov_e, T_Sky)

#=====covection and conduction"

def H_CanAir(LAI, T_Can, T_Air):
	HEC = 2*CONVECTIVE_LEAF_AIR*LAI
	return convective_conductive_flux(HEC, T_Can, T_Air)

def H_AirFlr(T_Air, T_Flr):
	if T_Flr > T_Air:
		HEC = 1.7*(T_Flr - T_Air)**0.33
	elif T_Flr < T_Air:
		HEC = 1.3*(T_Air - T_Flr)**0.25
	else:
		HEC = 0
	return convective_conductive_flux(HEC, T_Air, T_Flr)

def H_AirThScr(T_Air, T_ThScr, U_ThScr):
	HEC = 1.7*U_ThScr*(abs(T_Air - T_ThScr))**0.33
	return convective_conductive_flux(HEC, T_Air, T_ThScr)

def H_AirOut(T_Air, T_Out, rho_air, f_VentSide, f_VentForced):
	HEC = rho_air*CP_AIR*(f_VentSide + f_VentForced)
	return convective_conductive_flux(HEC, T_Air, T_Out)

def H_AirTop(T_Air, T_Top, rho_air, f_ThScr,):
	HEC = rho_air*CP_AIR*f_ThScr
	return convective_conductive_flux(HEC, T_Air, T_Top)

def H_ThScrTop(T_ThScr, T_Top, U_ThScr,):
	HEC = 1.7*U_ThScr*(math.abs(T_ThScr - T_Top))**0.33
	return convective_conductive_flux(HEC, T_ThScr, T_Top)

def H_TopCov_in(T_Top, T_Cov_in, C_HECin, A_Cov, A_Flr):
	HEC = C_HECin*(T_Top - T_Cov_in)**0.33*A_Cov/A_Flr
	return convective_conductive_flux(HEC, T_Top, T_Cov_in)

def H_TopOut(T_Top, T_Out, rho_air, f_VentRoof):
	HEC = rho_air*CP_AIR*f_VentRoof
	return convective_conductive_flux(HEC, T_Top, T_Out)

def H_Cov_eOut(T_Cov_e, T_Out, A_Cov, A_Flr, C_HECout_1, C_HECout_2, C_HECout_3, V_Wind):
	HEC = A_Cov/A_Flr*(C_HECout_1 +C_HECout_2*V_Wind**C_HECout_3)
	return convective_conductive_flux(HEC, T_Cov_e, T_Out)

def H_PipeAir(T_Pipe, T_Air, length_Pipe, D_ex):
	HEC = 1.99*math.pi*D_ex*length_Pipe*(abs(T_Pipe - T_Air))**0.32
	return convective_conductive_flux(HEC, T_Pipe, T_Air)

def H_FlrSo1(T_Flr, T_So, H_So, h_Flr, lambda_Flr, lambda_So):
	HEC = 2/(h_Flr/lambda_Flr + H_So[0]/lambda_So)
	return convective_conductive_flux(HEC, T_Flr, T_So[0])

def H_SoiSoj(H_So, lambda_So):
	return [convective_conductive_flux(2*lambda_So/(H_So[i] + H_So[i+1])) for i in range(2, len(H_So)-1)]


'''
Passive heat storage
'''

def H_PasAir(HEC_PasAir, T_So, T_Air):
	#Passove heat storage
	return HEC_PasAir*(T_So[2] - T_Air)


'''
Sensible heat flux from the pad to the greenhouse air is described by
'''
def H_BlowAir(U_Blow, P_Blow, A_Flr):
	return U_Blow*P_Blow/A_Flr

def H_PadAir(f_Pad, rho_air, T_Out, eta_Pad, x_Pad, x_Out):
	return f_Pad*(rho_air*CP_AIR*T_Out-LATENT_EVAPORATION*rho_air*eta_Pad*(x_Pad-x_Out))

def H_AirOutPad(f_Pad, rho_air, T_Air):
	return f_Pad*rho_air*CP_AIR*T_Air

def H_MechAir(U_Mech, COP_Mech, P_Mech, A_Flr, T_Air, T_Mech, VP_Air):
	VP_Mech = saturated_vapour_pressure(T_Mech)
	return (U_Mech*COP_Mech*P_Mech/A_Flr)/(T_Air - T_Mech + 6.4e-9*LATENT_EVAPORATION*(VP_Air-VP_Mech))*(T_Mech - T_Air)
'''
Latent heat fluxes: is the amount of engergy needed to convert water to water vapour 
(canopy transpiration) or when water vapour becomes water (condensation).
'''
def L_CanAir(MV_CanAir):
	return LATENT_EVAPORATION*MV_CanAir

def LAirThScr(MV_AirThScr):
	return LATENT_EVAPORATION*MV_AirThScr

def L_TopCov_in(MV_TopCov_in):
	return LATENT_EVAPORATION*MV_TopCov_in

def L_AirFog(MV_FogAir):
	return LATENT_EVAPORATION*MV_FogAir
































