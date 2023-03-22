from typing import NamedTuple, List

class ControlVariables(object):
	def __init__(self, U_Blow, U_Boil, U_HeadInd, U_HeadGeo, U_Pad, U_MechCool, U_Fog, U_Roof,
					U_Side, U_VentForced, U_ExtCO2, U_ShScr, U_ShScrPer, U_ThScr):
		self.U_Blow = U_Blow  # Heat blower control
		self.U_Boil = U_Boil  # Boiler control
		self.U_HeadInd =U_HeadInd # Control of the head input from industry
		self.U_HeadGeo =  U_HeadGeo # Control of the head input from geothermal source
		self.U_Pad = U_Pad # Pad and fan control
		self.U_MechCool = U_MechCool  # Control of mechanical cooling
		self.U_Fog = U_Fog # Control of fogging system
		self.U_Roof = U_Roof# Control of roof ventilators
		self.U_Side =  U_Side # Control of side ventilators
		self.U_VentForced = U_VentForced  # Control of forced ventilators
		self.U_ExtCO2 = U_ExtCO2 # Control of the CO2 input from external source
		self.U_ShScr  = U_ShScr# Control of external shading screen
		self.U_ShScrPer = U_ShScrPer  # Control of semi-permanent shading screen
		self.U_ThScr  =  U_ThScr# Control of thermal screen

class StateVariables(object):
	def __init__(self, T_Can, T_Air, T_Flr, T_So, T_ThScr, T_Top, T_Cov_in, T_Cov_e, T_Pipe,
						VP_Air, VP_Top, CO2_Air, CO2_Top):
		self.T_Can    = T_Can# canopy temperature
		self.T_Air    = T_Air# greenhouse air temperature
		self.T_Flr    = T_Flr# floor layer (first layer of the greenhouse underground) temperature
		self.T_So    = T_So #soil layer temperatures
		self.T_ThScr  = T_ThScr # thermal screen temperature
		self.T_Top   = T_Top #top compartment above the thermal screen temperature
		self.T_Cov_in = T_Cov_in  # internal cover temperature
		self.T_Cov_e  = T_Cov_e # external cover temperature
		self.T_Pipe   = T_Pipe# pipe temperature
		self.VP_Air   = VP_Air# vapour pressure of greenhouse air
		self.VP_Top   = VP_Top# vapour pressure of top compartment
		self.CO2_Air  = CO2_Air # CO2 concentration of greenhouse air
		self.CO2_Top  = CO2_Top # CO2 concentration of top compartment

class ExternalClimateInputs(object):
	def __init__(self, CO2_Out, I_Glob, T_Out, T_Sky, T_SoOut, VP_Out, V_Wind):
		self.CO2_Out = CO2_Out  # outdoor CO2 concentration
		self.I_Glob  = I_Glob # the outside global radiation
		self.T_Out   = T_Out# outdoor temperature
		self.T_Sky   = T_Sky# sky temperature
		self.T_SoOut = T_SoOut  # soil temperature of outer soil layer
		self.VP_Out  = VP_Out # outdoor vapour pressure
		self.V_Wind  = V_Wind # outdoor wind velocity

class AuxiliaryInputs(object):
	def __init__(self, LAI, MC_AirCan, T_MechCool, P_Blow):
		self.LAI   = LAI# the leaf area index
		self.MC_AirCan = MC_AirCan  # the net CO2 flux from the air to canopy
		self.T_MechCool = T_MechCool  # the temperature of the cool surface of the mechanical cooling system
		self.P_Blow = P_Blow

