import math
from constants import *
from utils import *



def MC_MV_BlowAir(U_Blow, P_Blow, A_Flr):
	'''
	Calculate the flow of CO2 from blower to the greenhouse air
	:param eta_heatCO2: Amount of CO2 generated when 1J of sensible heat is generated
	by the direct air heater
	:param U_blow: The control valve of the direct air heater
	:param P_blow: The heat capacity of the direct air heater
	:param A_flr: Greenhouse floor area
	'''
	MC_BlowAir = (ETA_HEAT_CO2*U_Blow*P_Blow)/A_Flr
	MV_BlowAir = (ETA_HEAT_VAP*U_Blow*P_Blow)/A_Flr
	return (MC_BlowAir, MV_BlowAir)



def MC_ExtAir(U_ExtCO2, Cap_ExtCO2, A_Flr):
	'''
	Calculate the CO2 supply rate (from the provider)
	:param U_extCO2: The control valve of the external CO2 source
	:param phi_extCO2: The capacity of the external CO2 source
	:param A_flr: Greenhouse floor area
	'''
	MC_ExtAir  = (U_ExtCO2*Cap_ExtCO2)/A_Flr
	return MC_ExtAir


def MC_PadAir(U_Pad, Cap_Pad, A_Flr, CO2_Out, CO2_Air):
	'''
	Calculate the flow of CO2 from the pad and fan system to greenhouse air
	==============================
		U_Pad: Pad and fan control
		phi_pad: Capacity of the air flux through the pad and fan system
		CO2_out: Outdoor CO2 concentration
		CO2_air: CO2-concentration of the greenhouse air
	'''
	return ((U_Pad*Cap_Pad)/A_Flr)*(CO2_Out - CO2_Air)


def MC_MV_BoilPipe(U_Boil, P_Boil, A_Flr):
	H_BoilPipe = U_Boil*P_Boil/A_Flr
	MC_BoilPipe = ETA_HEAT_CO2*H_BoilPipe
	MV_BoilPiPe = ETA_HEAT_VAP*H_BoilPipe
	return (MC_BoilPipe, MV_BoilPiPe)

def MC_MV_IndPipe(U_HeadInd, P_Ind, A_Flr):
	H_IndPiPe = U_HeadInd*P_Ind/A_Flr
	MC_IndPiPe = ETA_HEAT_CO2*H_IndPiPe
	MV_IndPiPe = ETA_HEAT_VAP*H_IndPiPe
	return (MC_IndPiPe, MV_IndPiPe)

def MC_MV_GeoPipe(U_HeadGeo, P_Geo, A_Flr):
	H_GeoPiPe = U_HeadGeo*P_Geo/A_Flr
	MC_GeoPiPe = ETA_HEAT_CO2*H_GeoPiPe
	MV_GeoPiPe = ETA_HEAT_VAP*H_GeoPiPe
	return (MC_GeoPiPe, MV_GeoPiPe)






