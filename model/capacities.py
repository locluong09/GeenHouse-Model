import math
from typing import List

from constants import *
from utils import air_density, heat_cap_helper, heat_cap_VP


def CAP_Canopy(LAI):
	return CAP_LEAF*LAI

def CAP_ExternalInternal(lumped_cover_heat_cap):
	return 0.1*lumped_cover_heat_cap

def CAP_Pipe(length_Pipe, D_ex, D_in):
	return 0.25*math.pi*length_Pipe*\
			((D_ex**2-D_in**2)*STEEL_DENSITY*CP_STEEL + D_in**2*WATER_DENSITY*CP_WATER)

def greenhouse_capacity(
	H_Elevation : float, # elevation height of greenhouse
	T_Air : float, # temperature
	H_Gh : float ,# height of green house
	H_Air : float, # hight from floor to thermal screen
	CP_Air : float, # specific heat capacity of air
	density_Flr : float, # Density of floar
	h_Flr : float, # thickness of floor
	CP_Flr : float, # specific heat capacity of floor
	CP_So : float, # specific heat capacity of soil
	H_So : List[float], # thickness of soil layer
	density_ThScr : float, # density of thermal screen
	h_ThScr : float, # thickness of thermal screen
	CP_ThScr : float #specific heat capacity of thermal screen
	):

	rho_air = air_density(H_Elevation, T_Air)

	CAP_Gh = heat_cap_helper(rho_air, H_Gh, CP_AIR)
	CAP_Flr = heat_cap_helper(density_Flr, h_Flr, CP_Flr)
	CAP_So = [i*CP_So for i in H_So]
	CAP_ThScr = heat_cap_helper(density_ThScr, h_ThScr, CP_ThScr)

	CAP_Air = H_Air/H_Gh*CAP_Gh
	CAP_Top = (H_Gh - H_Air)/H_Gh*CAP_Gh

	return (CAP_Air, CAP_Top, CAP_Flr, CAP_So, CAP_ThScr,)

def VP_Air_capacity(
	H_Air : float, # height from floor to thermal screen
	T_Air : float, # temperature of air compartment
	H_Gh : float, # height of green house
	):

	CAP_VP_Air = heat_cap_VP(H_Air, T_Air)
	CAP_VP_Top = heat_cap_VP(H_Gh - H_Air,T_Air)

	return (CAP_VP_Air, CAP_VP_Top)







