from typing import List, NamedTuple


class Coefficients(object):
	class Construction(NamedTuple):
		Ratio_Glob_Air = 0.1  # The ratio of the global radiation which is absorbed by the greenhouse construction elements
		Psi = 22  # Mean greenhouse cover slope
		A_Cov = 9.0E4  # Surface of the cover including side-walls
		A_Flr = 1.4E4  # Surface of the greenhouse floor
		C_HECin = 1.86  # Convective heat exchange parameter between cover and outdoor air that depends on the greenhouse shape
		C_HECout_1 = 2.8  # Convective heat exchange variables between cover and outdoor air which depend on the greenhouse shape
		C_HECout_2 = 1.2  # Convective heat exchange variables between cover and outdoor air which depend on the greenhouse shape
		C_HECout_3 = 1  # Convective heat exchange variables between cover and outdoor air which depend on the greenhouse shape
		Height_Air = 4.7  # Height of the greenhouse compartment below the thermal screen
		Height_Elevation = 1470  # The altitude of the greenhouse
		Height_Gh = 5.1  # Mean height of the greenhouse
	class Ventilation(NamedTuple):
		Eta_ShScrC_d = 0.5 # Parameter that determines the effect of the movable shading screen on the discharge coefficient
		Eta_ShScrC_w = 0.5 # Parameter that determines the effect of the movable shading screen on the global wind pressure coefficient
		Zeta_InsScr = 1  # The porosity of the insect screens
		A_Roof_A_Flr = 0.1  # The specific roof ventilation area
		A_Side_A_Flr = 0.09  # The side ventilation area
		C_Gh_d = 0.75  # Ventilation discharge coefficient depends on greenhouse shape
		C_Leakage = 1E-4  # Greenhouse leakage_coef coefficient
		C_Gh_w = 0.09  # Ventilation global wind pressure coefficient depends on greenhouse shape
		H_Side_Roof = 0# side_wall_roof_vent_distance The vertical distance between mid-points of side wall and roof ventilation openings
		H_Vent = 0.68  # The vertical dimension of a single ventilation opening

	class Roof(NamedTuple):
		FIR_emission = 0.85  # The FIR emission coefficient of the roof
		density = 2.6E3  # Density of the roof layer
		NIR_reflection= 0.13  # The NIR reflection coefficient of the roof
		PAR_reflection = 0.13  # The PAR reflection coefficient of the roof
		FIR_reflection = 0.15  # The FIR reflection coefficient of the roof
		NIR_transmission = 0.85  # The NIR transmission coefficient of the roof
		PAR_transmission = 0.85  # The PAR transmission coefficient of the roof
		FIR_transmission = 0  # The FIR transmission coefficient of the roof
		Heat_Conductivity = 1.05  # Thermal heat conductivity of the roof
		CP = 0.84E3  # The specific heat capacity of the roof layer
		h = 4E-3  # Thickness of the roof layer

	class Whitewash(NamedTuple):
		FIR_emission = 0.9 # FIR emission coefficient of the whitewash
		density = 1e3 # Density of the semi permanent shading screen
		NIR_reflection = 0.3 # NIR reflection coefficient of the whitewash
		PAR_reflection = 0.3 # PAR reflection coefficient of the whitewash
		FIR_reflection = 0 # FIR reflection coefficient of the whitewash
		NIR_transmission = 0.6 # NIR transmission coefficient of the whitewash
		PAR_transmission = 0.6 # PAR transmission coefficient of the whitewash
		FIR_transmission = 0.1 # FIR transmission coefficient of the whitewash
		Heat_Conductivity = 100000000000 # Thermal heat conductivity of the whitewash
		CP = 4.18*1e3 # Specific heat capacity of the whitewash
		h = 0.2*1e-3 # Thickness of the whitewash


	class Shadingscreen(NamedTuple):
		FIR_emission = 0.9 # FIR emission coefficient of the shadowscreen
		density = 1e3 # Density of the shadowscreen
		NIR_reflection = 0.3 # NIR reflection coefficient of the shadowscreen
		PAR_reflection = 0.3 # PAR reflection coefficient of the shadowscreen
		FIR_reflection = 0 # FIR reflection coefficient of the shadowscreen
		NIR_transmission = 0.6 # NIR transmission coefficient of the shadowscreen
		PAR_transmission = 0.6 # PAR transmission coefficient of the shadowscreen
		FIR_transmission = 0.1 # FIR transmission coefficient of the shadowscreen
		Heat_Conductivity = 100000000000 # Thermal heat conductivity of the shadowscreen
		CP = 4.18*1e3 # Specific heat capacity of the shadowscreen
		h = 0.2*1e-3 # Thickness of the shadowscreen

	class Thermalscreen(NamedTuple):
		FIR_emission = 0.44  # The FIR emission coefficient of the thermal screen
		density = 0.2E3  # Density of the thermal screen
		NIR_reflection = 0.7  # The NIR reflection coefficient of the thermal screen
		PAR_reflection = 0.7  # The PAR reflection coefficient of the thermal screen
		FIR_reflection = 0.45  # The FIR reflection coefficient of the thermal screen
		NIR_transmission = 0.25  # The NIR transmission coefficient of the thermal screen
		PAR_transmission = 0.25  # The PAR transmission coefficient of the thermal screen
		FIR_transmission = 0.11  # FIR transmission coefficient of the thermal screen
		CP = 1.8E3  # Specific heat capacity of the thermal screen
		h = 0.35E-3  # Thickness of the thermal screen
		K_ThScr = 0.05E-3  # The thermal screen flux coefficient
	class Floor(NamedTuple):
		FIR_emission = 1  # FIR emission coefficient of the floor
		density = 2300  # Density of the floor
		NIR_reflection = 0.5  # NIR reflection coefficient of the floor
		PAR_reflection = 0.65  # PAR reflection coefficient of the floor
		Heat_Conductivity = 1.7  # Thermal heat conductivity of the floor
		CP = 0.88E3  # Specific heat capacity of the floor
		h = 0.02  # Thickness of the greenhouse floor
	class Soil(NamedTuple):
		H_So = [0.04, 0.08, 0.16, 0.32, 0.64] # Thickness of the soil layers
		CP_So = 1.73E6  # The volumetric heat capacity of the soil
		Heat_Conductivity = 0.85  # Thermal heat conductivity of the soil layers.
	class HeatingSystem(NamedTuple):
		FIR_emission = 0.88  # FIR emission coefficient of the heating pipes
		D_ex = 51E-3  # External diameter of the heating pipe
		D_in = 47E-3  # Internal diameter of the heating pipe
		length = 1.25  # Length of the heating pipes per square meter greenhouse
	class ActiveClimateControl(NamedTuple):
		Eta_Pad = 0.8 # Efficiency of the pad and fan system
		Cap_Fog = 0# Capacity of the fogging system
		Cap_Pad = 0.8# Capacity of the air flux through the pad and fan system
		Phi_VentForced = 0.4 # Air flow capacity of the forced ventilation system
		Cap_ExtCO2 = 7.2E4  # Capacity of the external CO2 source
		Coeff_MechCool = 0 # Coefficient of performance of the mechanical cooling system
		HEC_PasAir =0  # The convective heat exchange coefficient between the passive heat storage facility and the greenhouse air temperature
		Heat_cap_Blow = 0 # Heat capacity of the heat blowers
		Heat_cap_Boil = 0 # Thermal heat capacity of the boiler
		Heat_cap_Geo = 0# Heat capacity of the geothermal heat source
		Heat_cap_Ind = 0# Heat capacity of the industrial heat source
		Heat_cap_MechCool= 0 # Electrical capacity of the mechanical cooling system

