import numpy as np
import math
import pandas as pd
import sys
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from CO2_fluxes import *
from greenhouse import *
from capacities import *
from vapour_fluxes import *
from heat_fluxes import *
from lumped_cover_layers import *
from utils import *
from constants import *
from solver import *

from data_object import ControlVariables as CVs
from data_object import StateVariables as SVs
from data_object import ExternalClimateInputs as ECs
from data_object import AuxiliaryInputs as AIs

from coeffs import Coefficients as coeffs

from crops.coeffs_crop import coefficients as coeffs_crop
from crops.data import StateVariables_Crop as SVs_crop

np.random.seed(0)


CV = CVs(
	U_Blow = 0.2,
	U_Boil = 0.5,
	U_HeadInd = 0.5,
	U_HeadGeo =0.5,
	U_Pad =0.5,
	U_MechCool =0.5,
	U_Fog =0.5,
	U_Roof = 0.15,#abs(28.4 - 1.6) / 100,
	U_Side =0.15,
	U_VentForced =0.15,
	U_ExtCO2 = 0.1,
	U_ShScr = 0.15,
	U_ShScrPer = 0.5,
	U_ThScr  =0.97
	)
SV = SVs(
	T_Can = 21.8999999966472+3,
	T_Air = 21.8999999966472,
	T_Flr = 12,
	T_So = [20,20,20,20,20],
	T_ThScr = 20,
	T_Top = 21.8999999966472+1,
	T_Cov_in = 20,
	T_Cov_e = 20,
	T_Pipe = 60,
	VP_Air = saturated_vapour_pressure(21)*0.5,
	VP_Top = saturated_vapour_pressure(24)*0.5,
	CO2_Air = 427,
	CO2_Top = 427,
	)

EC = ECs(
	CO2_Out = 300,
	I_Glob = 400,#17.8,
	T_Out = 15.8,
	T_Sky = 0,
	T_SoOut = 20,
	VP_Out = 1100,
	V_Wind= 6.3,
	)

AI = AIs(
	LAI = 0.7,
	MC_AirCan = 20,
	T_MechCool = 20,
	P_Blow = 0,
	)


coef = coeffs()

coef_crop = coeffs_crop(
	alpha = 0.385,
	C_MAX_Buf = 20*1e3,
	c_Gamma = 1.7,
	Ej = 37*1E3,
	eta_CO2_Air_Stom = 0.67,
	J_Max_25leaf =  210,
	M_CH2O =30*1e-3,
	S = 710,
	T_25 = 298.15,
	H  = 22*1E4,
	PAR_can = 100,
	Theta = 0.7,
	)

SV_crop = SVs_crop(
	C_Buf = 20*1e-3)



def rho_air1(rho_air0, g, M_air, h_elevation, T_air, R):
	'''
	Calculate the density of the greenhouse air
	:param rho_air0: The density of the air at sea level
	:param g: Gravitational acceleration
	:param M_air: The molar mass of air
	:param h_elevation: The altitude of the greenhouse above sea level
	:param T_air: Greenhouse air temperature
	:param R: The molar gas constant
	'''
	# return rho_air0*math.exp( (g*M_air*h_elevation)/((273.15+T_air)*R) )
	T_air += 273.15
	return 101325*((1-2.25577*10**-5 * h_elevation)**5.25588)/(R*T_air)

def rho_top1(rho_air0, g, M_air, h_elevation_top, T_top, R):
	'''
	Calculate the density of the top compartment air
	:param rho_air0: The density of the air at sea level
	:param g: Gravitational acceleration
	:param M_air: The molar mass of air
	:param h_elevation: The altitude of the greenhouse above sea level
	:param T_top: Top compartment temperature
	:param R: The molar gas constant
	'''
	# return rho_air0*math.exp( (g*M_air*h_elevation_top)/((273.15+T_top)*R) )
	T_top += 273.15
	return 101325 * ((1 - 2.25577 * 10 ** -5 * h_elevation_top) ** 5.25588) / (R * T_top)

def rho_mean_air1(rho_air0, g, M_air, h_elevation_mean_air, T_air, T_top, R):
	'''
	Calculate the mean density of the greenhouse air and outdoor air
	:param rho_air: The density of the greenhouse air
	:param rho_out: The density of the outdoor air
	'''
	# return rho_air0*math.exp( (g*M_air*h_elevation_mean_air)/((273.15 + (T_air + T_top)/2 )*R) )
	T_air += 273.15
	T_top += 273.25
	return 101325 * ((1 - 2.25577 * 10 ** -5 * h_elevation_mean_air) ** 5.25588) / (R * (T_air+T_top)/2)

h_elevation = 0
h_elevation_top = 3.8
h_elevation_mean_air = 4.2

def simulate_co2(x0,y0):
	mc_blow_air, _ = MC_MV_BlowAir(CV.U_Blow, AI.P_Blow, coef.Construction.A_Flr)
	mc_ext_air = MC_ExtAir(CV.U_ExtCO2, coef.ActiveClimateControl.Cap_ExtCO2, coef.Construction.A_Flr)
	mc_pad_air = MC_PadAir(CV.U_Pad, coef.ActiveClimateControl.Cap_Pad, coef.Construction.A_Flr, EC.CO2_Out, x0)


	rho_air = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Air, SV.T_Air)
	rho_out = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Gh, SV.T_Top)
	rho_mean = (rho_air + rho_out)/2
	# rho_air = rho_air1(1.2, 9.81, 28.96, h_elevation, SV.T_Air, 8.314*10**3)
	# rho_out = rho_top1(1.2, 9.81, 28.96, h_elevation_top, SV.T_Top, 8.314*10**3)
	# rho_mean = rho_mean_air1(1.2, 9.81, 28.96, h_elevation_mean_air, SV.T_Air, SV.T_Top, 8.314*10**3)

	f_ThScr = f_ThScr_estimate(CV.U_ThScr, coef.Thermalscreen.K_ThScr, SV.T_Air, SV.T_Top, rho_mean, rho_air, rho_out)
	# print(f_ThScr)
	mc_air_top = MC_AirTop(f_ThScr, x0, y0)
	# print(mc_air_top)

	A_Roof = coef.Ventilation.A_Roof_A_Flr*coef.Construction.A_Flr
	A_Side = coef.Ventilation.A_Side_A_Flr*coef.Construction.A_Flr
	eta_Roof = eta_Roof_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	# print(eta_Roof)
	eta_Side = eta_Side_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	f_Leakage = f_Leakage_estimate(coef.Ventilation.C_Leakage, EC.V_Wind)
	T_Mean = (SV.T_Air + EC.T_Out)/2
	f2_VentRoofSide = f2_VentRoofSide_estimate(coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, CV.U_Roof, CV.U_Side, A_Roof, 
			A_Side, coef.Ventilation.H_Side_Roof, SV.T_Air, EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)
	# print(f2_VentRoofSide)
	C_d = C_d_estimate(coef.Ventilation.C_Gh_d, coef.Ventilation.Eta_ShScrC_d, CV.U_ShScr)
	C_w = C_w_estimate(coef.Ventilation.C_Gh_w, coef.Ventilation.Eta_ShScrC_w, CV.U_ShScr)
	# print(C_d, C_w)
	f2_VentSide = f2_VentSide_estimate(C_d, CV.U_Side, A_Side, EC.V_Wind, coef.Construction.A_Flr, C_w)
	f2_VentRoof = f2_VentRoof_estimate(CV.U_Roof, A_Roof, coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, coef.Ventilation.H_Vent, SV.T_Air, 
				EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)

	eta_InsScr = coef.Ventilation.Zeta_InsScr*(2- coef.Ventilation.Zeta_InsScr)
	eta_Roof_Thr = RATIO_ROOF_THR
	f_VentSide = f_VentSide_estimate(eta_InsScr, f2_VentSide, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
					eta_Side, eta_Roof, eta_Roof_Thr)
	f_VentForced = f_VentForced_estimate(eta_InsScr, CV.U_VentForced, coef.ActiveClimateControl.Phi_VentForced, coef.Construction.A_Flr)

	f_VentRoof = f_VentRoof_estimate(eta_InsScr, f2_VentRoof, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
        eta_Roof, eta_Roof_Thr)

	mc_air_out = MC_AirOut(f_VentSide, f_VentForced, x0, EC.CO2_Out)
	mc_top_out = MC_TopOut(f_VentRoof, y0, EC.CO2_Out)

	
	J_Max_25can = J_MAX_25CAN_estimate(AI.LAI, coef_crop.J_Max_25leaf)
	Gamma = Gamma_estimate(J_Max_25can, coef_crop.J_Max_25leaf, coef_crop.c_Gamma, SV.T_Can)
	CO2_Stom = CO2_Stom_estimate(coef_crop.eta_CO2_Air_Stom, x0)
	J_Pot = J_POT_estimate(J_Max_25can, coef_crop.Ej, SV.T_Can, coef_crop.T_25, coef_crop.S, coef_crop.H)
	J = electron_transport_Rate(J_Pot, coef_crop.alpha, coef_crop.PAR_can, coef_crop.Theta)
	P = photosynthesis_Rate(J, CO2_Stom, Gamma)
	R = photorespiration_Rate(P, Gamma, CO2_Stom)
	h_CBuf = h_C_Buf_MC_Air(SV_crop.C_Buf, coef_crop.C_MAX_Buf)
	mc_air_can = MC_AirBuf(coef_crop.M_CH2O,h_CBuf, P, R)

	# print(f_VentRoof)
	# print(mc_blow_air, mc_ext_air, mc_pad_air)
	# print(mc_air_out, mc_air_top, mc_air_can)
	cap_air = 3.8
	cap_top = 4.2 - 3.8
	co2_air = (mc_blow_air + mc_ext_air + mc_pad_air - mc_air_out - mc_air_top - mc_air_can)/cap_air
	co2_top = (mc_air_top - mc_top_out)/cap_top

	return (co2_air, co2_top)

def simulate_temp_can():
	(PAR_lumped_trans, PAR_lumped_reflec, PAR_lumped_absortion) = PAR_lumped_model(
	U_ShScr, 
	U_ShScrPer,
	PAR_transmisson1,
	PAR_transmission2,
	PAR_reflection1,
	PAR_reflection2,

	U_Roof,
	U_ThScr,
	PAR_transmission3,
	PAR_transmission4,
	PAR_reflection3,
	PAR_reflection4,
	)

	R_PAR_Gh = PAR_above_Can(coef.Construction.Ratio_Glob_Air, PAR_lumped_trans, EC.I_Glob)

	R_PAR_SunCan, R_PAR_SunFlr = PAR_absorbed_SunCanFlr(
	R_PAR_Gh,
	AI.LAI,
	coef.Floor.PAR_reflection
	)


	(NIR_lumped_trans, NIR_lumped_reflec, NIR_lumped_absortion) = NIR_lumped_model(
	U_ShScr, # control of shading screen
	U_ShScrPer, # control of semi-permanent shading screen
	NIR_transmisson1,
	NIR_transmission2,
	NIR_reflection1,
	NIR_reflection2,

	U_Roof, # control of roof
	U_ThScr, # control of thermal screen
	NIR_transmission3,
	NIR_transmission4,
	NIR_reflection3,
	NIR_reflection4
	)

	# (lumped_trans, lumped_reflec, lumped_absortion) = lumped_Cov_Can_Flr_coeffs(
	# NIR_lumped_reflec, # lumped NIR reflection of cover
	# coef.Floor.NIR_reflection, # NIR reflection of Floor
	# AI.LAI, # leaf area index
	# )

	(R_NIR_SunCan, R_NIR_SunFlr, R_Glob_SunAir, R_Glob_SunCov) = NIR_Glob_absorbed_SunCanFlr(
	NIR_reflec_Cov,
	NIR_reflec_Flr,
	LAI,
	Ratio_Glob_Air,
	I_Glob,
	PAR_trans_Cov,
	NIR_absortion_Cov,
	PAR_absortion_Cov
	)

	R_pipe_can = R_PipeCan(
	LAI,
	length_Pipe,
	D_ex,
	FIR_emission_Pipe,
	T_Pipe,
	T_Can)

	H_can_air = H_CanAir(LAI, T_Can, T_Air)
	L_can_air = L_CanAir(MV_CanAir)

	R_can_covin = R_CanCov_in(
	LAI, 
	U_ThScr, 
	FIR_trans_ThScr, 
	FIR_emission_Cov, 
	T_Can, 
	T_Cov_in)

	R_can_flr = R_CanFlr(
	LAI,
	length_Pipe,
	D_ex,
	FIR_emission_Flr)

	R_can_sky = R_CanSky(
	LAI,
	U_ThScr,
	FIR_trans_Cov,
	FIR_trans_ThScr,
	T_Can,
	T_Sky)

	R_can_thscr = R_CanThScr(
	LAI,
	U_ThScr,
	FIR_emission_ThScr,
	T_Can,
	T_ThScr
	)


def simulate_temp_air(T_Air):
	H_can_air = H_CanAir(AI.LAI, SV.T_Can, T_Air)
	
	# H_mech_air = H_MechAir(U_Mech, COP_Mech, P_Mech, A_Flr, T_Air, T_Mech, VP_Air)
	H_pipe_air = H_PipeAir(SV.T_Pipe, T_Air, coef.HeatingSystem.length, coef.HeatingSystem.D_ex)
	# print(H_pipe_air)
	# H_pas_air = H_PasAir(HEC_PasAir, T_So, T_Air)
	H_blow_air = H_BlowAir(CV.U_Blow, AI.P_Blow, coef.Construction.A_Flr)

	H_air_flr = H_AirFlr(T_Air, SV.T_Flr)
	H_air_thscr = H_AirThScr(T_Air, SV.T_ThScr, CV.U_ThScr)

	# rho_air = rho_air1(1.2, 9.81, 28.96, h_elevation, T_Air, 8.314*10**3)
	# rho_out = rho_top1(1.2, 9.81, 28.96, h_elevation_top, SV.T_Top, 8.314*10**3)
	# rho_mean = rho_mean_air1(1.2, 9.81, 28.96, h_elevation_mean_air, T_Air, SV.T_Top, 8.314*10**3)
	
	rho_air = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Air, SV.T_Air)
	rho_out = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Gh, SV.T_Top)
	rho_mean = (rho_air + rho_out)/2
	# print(rho_air)

	f_Pad = f_Pad_estimate(CV.U_Pad, coef.ActiveClimateControl.Cap_Pad, coef.Construction.A_Flr)
	# print(f_Pad)
	eta_Pad = 0.8 #efficiency of pad and fan system.
	x_Pad = 10 #water vapour content of the pad (kg water kg^-1 air)
	x_Out = 8 #water vapour content of the outdoor air
	H_pad_air = H_PadAir(f_Pad, rho_air, EC.T_Out, eta_Pad, x_Pad, x_Out)

	f_ThScr = f_ThScr_estimate(CV.U_ThScr, coef.Thermalscreen.K_ThScr, T_Air, SV.T_Top, rho_mean, rho_air, rho_out)

	A_Roof = coef.Ventilation.A_Roof_A_Flr*coef.Construction.A_Flr
	A_Side = coef.Ventilation.A_Side_A_Flr*coef.Construction.A_Flr
	eta_Roof = eta_Roof_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	# print(eta_Roof)
	eta_Side = eta_Side_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	f_Leakage = f_Leakage_estimate(coef.Ventilation.C_Leakage, EC.V_Wind)
	T_Mean = (T_Air + EC.T_Out)/2
	f2_VentRoofSide = f2_VentRoofSide_estimate(coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, CV.U_Roof, CV.U_Side, A_Roof, 
			A_Side, coef.Ventilation.H_Side_Roof, T_Air, EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)
	# print(f2_VentRoofSide)
	f2_VentSide = f2_VentSide_estimate(coef.Ventilation.C_Gh_d, CV.U_Side, A_Side, EC.V_Wind, coef.Construction.A_Flr, coef.Ventilation.C_Gh_w)
	f2_VentRoof = f2_VentRoof_estimate(CV.U_Roof, A_Roof, coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, coef.Ventilation.H_Vent, T_Air, 
				EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)

	eta_InsScr = coef.Ventilation.Zeta_InsScr*(2- coef.Ventilation.Zeta_InsScr)
	eta_Roof_Thr = RATIO_ROOF_THR
	f_VentSide = f_VentSide_estimate(eta_InsScr, f2_VentSide, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
					eta_Side, eta_Roof, eta_Roof_Thr)
	f_VentForced = f_VentForced_estimate(eta_InsScr, CV.U_VentForced, coef.ActiveClimateControl.Phi_VentForced, coef.Construction.A_Flr)

	f_VentRoof = f_VentRoof_estimate(eta_InsScr, f2_VentRoof, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
        eta_Roof, eta_Roof_Thr)

	# print(f_VentSide+ f_VentForced)
	# print("f_th",f_ThScr)
	# print(f_Pad)
	H_air_out = H_AirOut(T_Air, EC.T_Out, rho_air, f_VentSide, f_VentForced)
	H_air_top = H_AirTop(T_Air, SV.T_Top, rho_air, f_ThScr)
	H_air_outpad = H_AirOutPad(f_Pad, rho_air, T_Air)
	# L_air_fog = L_AirFog(MV_FogAir)


	(PAR_lumped_trans, PAR_lumped_reflec, PAR_lumped_absortion) = PAR_lumped_model(
	CV.U_ShScr, 
	CV.U_ShScrPer,
	coef.Shadingscreen.PAR_transmission,
	coef.Whitewash.PAR_transmission,
	coef.Shadingscreen.PAR_reflection,
	coef.Whitewash.PAR_reflection,

	CV.U_Roof,
	CV.U_ThScr,
	coef.Roof.PAR_transmission,
	coef.Thermalscreen.PAR_transmission,
	coef.Roof.PAR_reflection,
	coef.Thermalscreen.PAR_reflection,
	)

	(NIR_lumped_trans, NIR_lumped_reflec, NIR_lumped_absortion) = NIR_lumped_model(
	CV.U_ShScr, # control of shading screen
	CV.U_ShScrPer, # control of semi-permanent shading screen
	coef.Shadingscreen.NIR_transmission,
	coef.Whitewash.NIR_transmission,
	coef.Shadingscreen.NIR_reflection,
	coef.Whitewash.NIR_reflection,

	CV.U_Roof, # control of roof
	CV.U_ThScr, # control of thermal screen
	coef.Roof.NIR_transmission,
	coef.Thermalscreen.NIR_transmission,
	coef.Roof.NIR_reflection,
	coef.Thermalscreen.NIR_reflection
	)

	(R_NIR_SunCan, R_NIR_SunFlr, R_Glob_SunAir, R_Glob_SunCov) = NIR_Glob_absorbed_SunCanFlr(
	NIR_reflec_Cov = NIR_lumped_reflec,
	NIR_reflec_Flr = coef.Floor.NIR_reflection,
	LAI = AI.LAI,
	Ratio_Glob_Air = coef.Construction.Ratio_Glob_Air,
	I_Glob = EC.I_Glob,
	PAR_trans_Cov = PAR_lumped_trans,
	NIR_absortion_Cov = NIR_lumped_absortion,
	PAR_absortion_Cov = PAR_lumped_absortion
	)

	CAP_air, CAP_top, _, _, _ = greenhouse_capacity(
	H_Elevation = coef.Construction.Height_Elevation,
	T_Air = T_Air,
	H_Gh  = coef.Construction.Height_Gh,
	H_Air = coef.Construction.Height_Air, 
	CP_Air = CP_AIR, 
	density_Flr = coef.Floor.density, 
	h_Flr = coef.Floor.h, 
	CP_Flr  = coef.Floor.CP, 
	CP_So = coef.Soil.CP_So, 
	H_So = coef.Soil.H_So, 
	density_ThScr = coef.Thermalscreen.density, 
	h_ThScr = coef.Thermalscreen.h, 
	CP_ThScr = coef.Thermalscreen.CP 
	)
	t_air = (H_can_air + H_pad_air + H_pipe_air + H_blow_air + R_Glob_SunAir-\
				H_air_flr - H_air_thscr - H_air_out - H_air_top - H_air_outpad)/CAP_air

	# t_top = 
	# print("airtop",H_air_top)
	# print("============")
	# print(H_can_air, H_pad_air, H_pipe_air, H_blow_air, R_Glob_SunAir)
	# print(H_air_flr)
	# print(H_air_thscr)
	# print(H_air_out)
	# print(H_air_top)
	# print(H_air_outpad)
	# print(t_air)
	# print("Uroof", CV.U_Roof)
	return t_air


def simulate_vapour(VP_Air, VP_Top):

	rho_air = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Air, SV.T_Air)
	rho_out = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Gh, SV.T_Top)
	rho_mean = (rho_air + rho_out)/2
	R_Can = 100
	VEC = VEC_can_air(rho_air, AI.LAI, R_Can, SV.CO2_Air, SV.T_Can, VP_Air)
	# print(VEC)
	mv_can_air = MV_CanAir(SV.T_Can, VP_Air, rho_air, AI.LAI, R_Can, SV.CO2_Air)
	# print(mv_can_air)
	# print(saturated_vapour_pressure(30))
	
	rho_air = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Air, SV.T_Air)
	rho_out = air_density(coef.Construction.Height_Elevation + coef.Construction.Height_Gh, SV.T_Top)
	rho_mean = (rho_air + rho_out)/2
	# print(rho_air)
	x_Pad = 0.0147 #water vapour content of the pad (kg water kg^-1 air)
	x_Out = 0.01 #water vapour
	f_Pad = f_Pad_estimate(CV.U_Pad, coef.ActiveClimateControl.Cap_Pad, coef.Construction.A_Flr)
	mv_pad_air = MV_PadAir(rho_air, f_Pad, coef.ActiveClimateControl.Eta_Pad, x_Pad, x_Out)
	# mv_fog_air = MV_FogAir(U_Fog, Cap_Fog, A_Flr)
	_, mv_blow_air = MC_MV_BlowAir(CV.U_Blow, AI.P_Blow, coef.Construction.A_Flr)

	# print(rho_air, rho_out, rho_mean)


	f_ThScr = f_ThScr_estimate(CV.U_ThScr, coef.Thermalscreen.K_ThScr, SV.T_Air, SV.T_Top, rho_mean, rho_air, rho_out)

	A_Roof = coef.Ventilation.A_Roof_A_Flr*coef.Construction.A_Flr
	A_Side = coef.Ventilation.A_Side_A_Flr*coef.Construction.A_Flr
	eta_Roof = eta_Roof_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	# print(eta_Roof)
	eta_Side = eta_Side_estimate(CV.U_Roof, CV.U_Side, A_Roof, A_Side)
	f_Leakage = f_Leakage_estimate(coef.Ventilation.C_Leakage, EC.V_Wind)
	T_Mean = (SV.T_Air + EC.T_Out)/2
	f2_VentRoofSide = f2_VentRoofSide_estimate(coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, CV.U_Roof, CV.U_Side, A_Roof, 
			A_Side, coef.Ventilation.H_Side_Roof, SV.T_Air, EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)
	# print(f2_VentRoofSide)
	f2_VentSide = f2_VentSide_estimate(coef.Ventilation.C_Gh_d, CV.U_Side, A_Side, EC.V_Wind, coef.Construction.A_Flr, coef.Ventilation.C_Gh_w)
	# print(f2_VentSide)
	f2_VentRoof = f2_VentRoof_estimate(CV.U_Roof, A_Roof, coef.Ventilation.C_Gh_d, coef.Construction.A_Flr, coef.Ventilation.H_Vent, SV.T_Air, 
				EC.T_Out, T_Mean, coef.Ventilation.C_Gh_w, EC.V_Wind)

	# print(f2_VentSide, f2_VentRoof, f2_VentRoofSide)

	eta_InsScr = coef.Ventilation.Zeta_InsScr*(2- coef.Ventilation.Zeta_InsScr)
	eta_Roof_Thr = RATIO_ROOF_THR
	f_VentSide = f_VentSide_estimate(eta_InsScr, f2_VentSide, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
					eta_Side, eta_Roof, eta_Roof_Thr)
	f_VentForced = f_VentForced_estimate(eta_InsScr, CV.U_VentForced, coef.ActiveClimateControl.Phi_VentForced, coef.Construction.A_Flr)

	f_VentRoof = f_VentRoof_estimate(eta_InsScr, f2_VentRoof, f_Leakage, CV.U_ThScr, f2_VentRoofSide,
        eta_Roof, eta_Roof_Thr)

	mv_air_thscr = MV_AirThScr(SV.T_Air, SV.T_ThScr, CV.U_ThScr, VP_Air)
	mv_air_top = MV_AirTop(SV.T_Air, SV.T_Top, f_ThScr, VP_Air, VP_Top)
	# print(MV_AirTop(1,2,3,4,5))
	# print(f_ThScr)
	mv_air_out = MV_AirOut(SV.T_Air, EC.T_Out, f_VentSide, f_VentForced, VP_Air, EC.VP_Out)
	mv_air_outpad = MV_AirOutPad(f_Pad, VP_Air, SV.T_Air)
	# mv_air_mech = 

	mv_top_covin = MV_TopCov_in(SV.T_Top, SV.T_Cov_in, coef.Construction.C_HECin, coef.Construction.A_Cov, coef.Construction.A_Flr, VP_Top)
	mv_top_out = MV_TopOut(SV.T_Top, EC.T_Out, f_VentRoof, VP_Top, EC.VP_Out)


	cap_vp_air, cap_vp_top = VP_Air_capacity(coef.Construction.Height_Air, SV.T_Air, coef.Construction.Height_Gh)
	# print("========")
	# # print(f_ThScr)
	# # print(f_VentSide, f_VentForced)
	# print(mv_can_air, mv_pad_air, mv_blow_air)
	# print(mv_air_thscr, mv_air_top, mv_air_out, mv_air_outpad)
	# print(cap_vp_air, cap_vp_top)
	# print(f_VentRoof)
	# print(mv_air_top, mv_top_covin, mv_top_out)
	mv_air = (mv_can_air+mv_pad_air+ mv_blow_air - mv_air_thscr- mv_air_top - mv_air_out - mv_air_outpad)/cap_vp_air
	mv_top = (mv_air_top - mv_top_covin - mv_top_out)/cap_vp_top
	# print("-----")
	# print(mv_can_air)
	# print(mv_can_air + mv_pad_air + mv_blow_air - mv_air_thscr- mv_air_top - mv_air_out - mv_air_outpad)
	# print(mv_blow_air)
	# print(mv_air_thscr)
	# print(mv_air_out)
	# print(mv_air_top)
	# print(mv_air, mv_top)
	# print(mv_pad_air)
	# print(mv_air_outpad)
	# print("===========")
	return (mv_air, mv_top)

list_CO2_air_rk4 = []
list_CO2_top_rk4 = []
list_real_CO2_air_data = []
list_err_rk4 = []



temp = []
t_out = []

list_vp_air = []
list_vp_top = []

rh_air = []
rh_top = []


def rk4_loop(h, n):
	print("------RUNGE-KUTTA 4 RESULT------")

	file_meteo = open("meteo.csv")
	file_meteo.readline()
	file_ghc = open("Greenhouse_climate.csv")
	file_ghc.readline()
	file_vip = open("vip.csv")
	file_vip.readline()
	CO2_air = ppm_to_mgm3(SV.CO2_Air)
	CO2_top = ppm_to_mgm3(SV.CO2_Top)
	step_next = 1
	step = 0.1
	n *= 300
	i = 0
	t0 = 0
	getData = False
	CO2_air_real_data = 427
	
	while i < n:
	# for i in range(301):
		# print(i)
		T_Air = SV.T_Air
		# if i // 300:
		if ((i+1) // 300) >= step_next:
			print(i)
			step_next += 1
			line_meteo = file_meteo.readline()
			line_ghc = file_ghc.readline()
			line_vip = file_vip.readline()
			elements_vip = line_vip.split(',')
			while "NaN" in line_meteo or "NaN" in line_ghc or elements_vip[1] == "NaN":
				line_meteo = file_meteo.readline()
				line_ghc = file_ghc.readline()
				line_vip = file_vip.readline()
				elements_vip = line_vip.split(',')
			elements_vip = line_vip.split(',')
			elements_meteo = line_meteo.split(',')
			elements_ghc = line_ghc.split(',')
			EC.V_Wind = float(elements_meteo[10])
			EC.T_Out = float(elements_meteo[8]) - 15
			# EC.I_Glob = float(elements_meteo[2])
			# SV.T_Air = float(elements_ghc[9])
			CV.U_ThScr = float(elements_ghc[3]) / 100
			CV.U_Roof = (float(elements_ghc[10]) + float(elements_ghc[11])) / 200
			SV.T_Can = SV.T_Air + 2
			SV.T_Top = SV.T_Air + 3
			
			if elements_vip[0] == "NaN":
				CV.U_ExtCO2 = np.random.uniform(0, 0.3)
				# print(CV.U_ExtCO2)
			elif mgm3_to_ppm(CO2_air) < float(elements_vip[0]):
				CV.U_ExtCO2 = 1
			else:
				CV.U_ExtCO2 = 0
			CO2_air_real_data = float(elements_ghc[2])
			getData = True

		if getData:
			randomU()
			getData = False
		# if i == 5:
			# break
		T_Air = Runge_Kutta4_1(simulate_temp_air, T_Air, step)
		SV.T_Air = T_Air

		if T_Air >= 24:
			coef.ActiveClimateControl.Cap_Pad = 0.35
			
		if T_Air <= 19:
			coef.ActiveClimateControl.Cap_Pad = 0.12


		CO2_air_step, CO2_top_step = Runge_Kutta4_2(simulate_co2, CO2_air, CO2_top, step)
		CO2_air = CO2_air_step
		CO2_top = CO2_top_step

		if (t0+1) % (h*60) == 0:
			# print("CO2_real: ", CO2_air_real_data)
			list_real_CO2_air_data.append(CO2_air_real_data)
			err = abs(CO2_air_real_data - CO2_air)
			list_err_rk4.append(mgm3_to_ppm(err))
			list_CO2_air_rk4.append(mgm3_to_ppm(CO2_air))
			list_CO2_top_rk4.append(mgm3_to_ppm(CO2_top))
			temp.append(T_Air)
			# print("CO2_air at t +", t0 // 60, "=", mgm3_to_ppm(CO2_air))
			# print("CO2_top at t +", t0 // 60, "=", mgm3_to_ppm(CO2_top))
			# print("------------------")

		i += 1
		t0 += 1
	file_meteo.close()
	file_ghc.close()
	file_vip.close()

def run_simulation(h, n):
	print("------RUNGE-KUTTA 4 RESULT------")

	file_meteo = open("data/meteo.csv")
	file_meteo.readline()
	file_ghc = open("data/Greenhouse_climate.csv")
	file_ghc.readline()
	file_vip = open("data/vip.csv")
	file_vip.readline()
	CO2_air = ppm_to_mgm3(SV.CO2_Air)
	CO2_top = ppm_to_mgm3(SV.CO2_Top)
	# VP_air = saturated_vapour_pressure(SV.T_Air)*0.5
	# VP_top = saturated_vapour_pressure(SV.T_Top)*0.5
	VP_air = saturated_vapour_pressure(19.89)*0.6
	VP_top = saturated_vapour_pressure(18.89)*0.6
	step_next = 1
	step = 1
	n *= 30
	i = 0
	t0 = 0
	getData = False
	CO2_air_real_data = 427
	
	while i < n:
	# for i in range(100):
		# print(i)
		T_Air = SV.T_Air
		# if i // 300:
		if i // 1 >= step_next:
			print("Timstep : ", i)
			# print(i, step_next)
			step_next += 1
			line_meteo = file_meteo.readline()
			line_ghc = file_ghc.readline()
			line_vip = file_vip.readline()
			elements_vip = line_vip.split(',')
			while "NaN" in line_meteo or "NaN" in line_ghc or elements_vip[1] == "NaN":
				line_meteo = file_meteo.readline()
				line_ghc = file_ghc.readline()
				line_vip = file_vip.readline()
				elements_vip = line_vip.split(',')
			elements_vip = line_vip.split(',')
			elements_meteo = line_meteo.split(',')
			elements_ghc = line_ghc.split(',')
			EC.V_Wind = float(elements_meteo[10])
			EC.T_Out = float(elements_meteo[8]) -5
			EC.I_Glob = float(elements_meteo[2])/2
			SV.T_Air = float(elements_ghc[9])
			CV.U_ThScr = float(elements_ghc[3]) / 100
			CV.U_Roof = (float(elements_ghc[10]) + float(elements_ghc[11])) / 200
			SV.T_Can = SV.T_Air + 2
			SV.T_Top = SV.T_Air + 3
			EC.VP_out = float(elements_meteo[7])*saturated_vapour_pressure(EC.T_Out)/100
			SV.T_ThScr = SV.T_Air + 1
			SV.T_top_cov_in = SV.T_Top + 1
			
			if elements_vip[0] == "NaN":
				CV.U_ExtCO2 = np.random.uniform(0, 0.3)
				# print(CV.U_ExtCO2)
			elif mgm3_to_ppm(CO2_air) < float(elements_vip[0]):
				CV.U_ExtCO2 = 1
			else:
				CV.U_ExtCO2 = 0
			CO2_air_real_data = float(elements_ghc[2])
			getData = True

		if getData:
			randomU()
			getData = False
		# if i == 5:
			# break
		

		T_Air = Runge_Kutta4_1(simulate_temp_air, T_Air, step)
		# print(T_Air)
		SV.T_Air = T_Air
		if T_Air >= 25:
			CV.U_Pad = 1
		
		elif T_Air <= 19:
			CV.U_Pad = 0.0

		else:
			CV.U_Pad = np.random.uniform(0.3, 0.6)
		
		# print(CV.U_Pad)

		CO2_air_step, CO2_top_step = Runge_Kutta4_2(simulate_co2, CO2_air, CO2_top, step)
		CO2_air = CO2_air_step
		CO2_top = CO2_top_step

		VP_air_step, VP_top_step = Runge_Kutta4_2(simulate_vapour, VP_air, VP_top, step)
		VP_air = VP_air_step
		VP_top = VP_top_step
		# print(VP_air, VP_top)

		# if VP_air < 1500:
		# 	CV.U_Pad = 0.5
		# 	CV.U_ThScr = 0.1
		# if VP_air/saturated_vapour_pressure(T_Air) >= 0.8:
		# 	VP_air

		if t0% 1 == 0:
			# print("CO2_real: ", CO2_air_real_data)
			list_real_CO2_air_data.append(CO2_air_real_data)
			err = abs(CO2_air_real_data - CO2_air)
			list_err_rk4.append(mgm3_to_ppm(err))
			list_CO2_air_rk4.append(mgm3_to_ppm(CO2_air))
			list_CO2_top_rk4.append(mgm3_to_ppm(CO2_top))

			temp.append(T_Air)
			t_out.append(EC.T_Out)
			
			list_vp_air.append(VP_air)
			list_vp_top.append(VP_top)


			rh_air.append(VP_air/saturated_vapour_pressure(T_Air)) if VP_air/saturated_vapour_pressure(T_Air) < 0.8 else rh_air.append(0.8)
			# print("CO2_air at t +", t0 // 60, "=", mgm3_to_ppm(CO2_air))
			# print("CO2_top at t +", t0 // 60, "=", mgm3_to_ppm(CO2_top))
			# print("------------------")

		i += 1
		t0 += 1
	file_meteo.close()
	file_ghc.close()
	file_vip.close()


def randomU():
	CV.U_Blow = np.random.uniform(0.0, 1)
	CV.U_Pad = np.random.uniform(0.0, 1)
	CV.U_ShScr = np.random.uniform(0.0, 1)
	coef_crop.PAR_can = np.random.normal(100, 50)
	# print(CV.U_Blow, CV.U_Pad, CV.U_ShScr, coef_crop.PAR_can)

def main():
	# rk4_loop(h = 5, n = 1000)
	run_simulation(h = 5, n = 1000)
	err_mean = 0
	for i in range(len(list_err_rk4)):
		err_mean += list_err_rk4[i]

	n = len(list_err_rk4)
	err_mean = err_mean / n
	# print("Err Mean= ", err_mean)	
	x_real = [i for i in range(n)]	
	# plt.figure()
	# plt.title("Runge-Kutta Result")	
	# plt.subplot(1, 2, 1)
	# # plt.plot(x_real, list_real_CO2_air_data, label='CO2_real_data')
	# plt.plot(x_real, list_CO2_air_rk4, label='CO2_air')
	# plt.plot(x_real, list_CO2_top_rk4, label='CO2_top')
	# plt.legend()	
	# plt.subplot(1, 2, 2)
	# plt.plot(x_real, list_err_rk4, label='Error')
	# plt.legend()	
	# plt.xlabel('Time')
	# plt.ylabel('CO2-concentration (ppm)')	
	# plt.show()
	data = pd.read_csv("data/vip.csv")
	t = []
	t_o = []
	x = []
	y = []
	z = []
	time = []
	for i in range(len(temp)):
		if i % 288 == 0:
			t.append(temp[i])
			x.append(list_CO2_air_rk4[i])
			y.append(list_CO2_top_rk4[i])
			z.append(rh_air[i])
			t_o.append(t_out[i])
			time.append(data["Date"][i])

	t1 = [(lambda x: x*1.8 + 32)(x) for x in t]
	t2 = [(lambda x: x*1.8 + 32)(x) for x in t_o]

	plt.plot(t1, 'r', label = "Air Temperature (F)")
	plt.plot(t2, 'b',label = "Outside Temperature (F)")
	plt.xlabel('Time (days)')
	plt.legend()
	plt.savefig("figs/tem.png", dpi = 400)
	plt.show()
	
	plt.plot(x, 'r', label='CO2_air concentration')
	plt.legend()	
	plt.xlabel('Time (days')
	plt.ylabel('CO2-concentration (ppm)')	
	plt.savefig("figs/conc.png", dpi = 400)
	plt.show()
	

	plt.plot(z, 'r', label = "Air relative humidity (%)")
	plt.xlabel('Time (days')
	plt.legend()
	plt.savefig("figs/humid.png", dpi = 400)
	plt.show()
	


	# fig = go.Figure([go.Scatter(x=data["Date"], y=temp)])
	# fig.show()
	print(len(temp))
	dt = data["Date"][2:30002]
	fig = go.Figure([
	go.Scatter(
		name='Air Temperature',
		x=dt,
		y=temp,
		mode='lines',#'markers',
		marker=dict(color='red', size=2),
		line=dict(width=1),
		showlegend=True
	),
	go.Scatter(
		name='Outside Temperature',
		x=dt,
		y=t_out,
		mode='lines',
		marker=dict(color="blue", size = 2),
		line=dict(width=1),
		showlegend=True
	),
	])
	fig.update_layout(
		yaxis_title='Temperature',
		title='Temperature profile of greenhouse',
		hovermode="x"
		)
	fig.show()

if __name__ == "__main__":
	# a,b = simulate_co2(20,20)
	# t = simulate_temp_air(21)
	# a,b = simulate_vapour(20, 30)
	main()
	
	

	










