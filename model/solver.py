import numpy as np
import math


def Runge_Kutta4_1(dx, x0, h):
	K1x = dx(x0)
	K1x = h * K1x
	K2x= dx(x0 + K1x/2)
	K2x = h * K2x
	K3x= dx(x0 + K2x/2)
	K3x = h * K3x
	K4x = dx(x0 + K3x)
	K4x = h * K4x
	Kx = (1 / 6) * (K1x + 2 * K2x + 2 * K3x + K4x)
	# print(Kx)
	x0 = x0 + Kx
	return x0

def Runge_Kutta4_2(dx, x0, y0, h):
	K1x, K1y = dx(x0, y0)
	K1x = h * K1x
	K1y = h * K1y
	K2x, K2y = dx(x0 + K1x/2, y0 + K1y/2)
	K2x = h * K2x
	K2y = h * K2y
	K3x, K3y = dx(x0 + K2x/2, y0 + K2y/2)
	K3x = h * K3x
	K3y = h * K3y
	K4x, K4y = dx(x0 + K3x, y0 + K3y)
	K4x = h * K4x
	K4y = h * K4y
	Kx = (1 / 6) * (K1x + 2 * K2x + 2 * K3x + K4x)
	x0 = x0 + Kx
	Ky = (1 / 6) * (K1y + 2 * K2y + 2 * K3y + K4y)
	y0 = y0 + Ky
	return x0, y0