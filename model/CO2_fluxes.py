import numpy as np
import math

from constants import *

def MC_AirTop(f_ThScr, CO2_Air, CO2_Top):
    '''
    Return : Calculate the flow of CO2 from the greenhouse air to the top compartment air
    
    Args:
        f_ThScr: Air flux rate through the thermal screen
        CO2_Air: CO2-concentration of the greenhouse air
        CO2_Top: CO2-concentration of the top compartment air
    '''
    return f_ThScr*(CO2_Air - CO2_Top)



def MC_AirOut(f_VentSide, f_VentForced, CO2_Air, CO2_Out):
    '''
    Return : Calculate the flow of CO2 from the greenhouse air to the outdoor

    Args:
        f_VentSide: Natural ventilation rate for side window
        f_VentForced : Forced ventilation rate for side window
        CO2_Air: CO2-concentration rate of the greenhouse air
        CO2_Osut: CO2-concentration rate of the outdoor
    '''
    return (f_VentSide + f_VentForced)*(CO2_Air - CO2_Out)







def MC_TopOut(f_VentRoof, CO2_Top, CO2_Out):
    '''
    Return: Calculate the CO2 exchange between the top compartment air and the outside air
    
    Args:
        f_VenRoof: The ventilation rate through roof openings
        CO2_Top: CO2-concentration of the top compartment air
        CO2_Out: CO2-concentration of the outside air
    '''
    return f_VentRoof*(CO2_Top - CO2_Out)


def MC_AirCan(h_Cbuf, P, R_P):
    '''
    Return: Calculate the CO2 flux from the air to the canopy   
    Args:
        M_CH2O: The molar mass of CH2O
        h_Cbuf: The inhibition of the photosynthesis rate by saturation of the leaves
            with carbonhydrates
        P: The photonsynthesis rate
        R: The photorespiration during the photosynthesis process
    '''
    return CH2O_MOLAR*h_Cbuf*(P - R_P)


