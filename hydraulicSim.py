from math import pi, floor
import numpy as np

# Units:
# Flow rates (Q) in m^3/h
# heights in meters
# time in hours

#
# Acceleration of Gravity
# in m/h^2
#
g = 9.81 * 3600**2

#
# Water's density
# in kg/m^3
#
rho = 1000

#
# Pump's Efficiency
#
efficiency = 0.65

#
# Pump Equation
#
# h_P = 260 - 0.002 Q^2
#
a1 = 260
a2 = - 0.002
def h_P(Q):
    return a1 + a2 * Q**2

#
# Consumption Curves
#
# Q_R = -0.004t^3 + 0.09t^2 + 0.1335t + 20
#
def Q_R(t):
    return -0.004 * t**3 + 0.09 * t**2 + 0.1335 * t + 20
#
# Q_VC_Max = -1.19333e-7 t^7 - 4.90754e-5 t^6 + 3.733e-3 t^5 - 0.09621t^4 + 1.03965t^3 - 3.8645t^2 - 1.0124t + 75.393
#
def Q_VC_Max(t):
    return - 1.19333e-7 * t**7 - 4.90754e-5 * t**6 + 3.733e-3 * t**5 - 0.09621 * t**4 + 1.03965 * t**3 - 3.8645 * t**2 - 1.0124 * t + 75.393
#
# Q_VC_Min = 1.19333e-7 t^7 - 6.54846e-5 t^6 + 4.1432e-3 t^5 - 0.100585t^4 + 1.05575t^3 - 3.85966t^2 - 1.32657t + 75.393
#
def Q_VC_Min(t):
    return 1.19333e-7 * t**7 - 6.54846e-5 * t**6 + 4.1432e-3 * t**5 - 0.100585 * t**4 + 1.05575 * t**3 - 3.85966 * t**2 - 1.32657 * t + 75.393

#
# Water Tank
#
z_i = 154               # Initial water level [m]
z_lim = [152, 157]      # Water level limits
z_abslim = [150, 159]   # Water level absolute limits
Area = 185              # Tank's Area [m^2]

#
# Inline Losses 
# h_L = ( 32fL / d^5 g pi^2 ) Q^2 = k Q^2
#
L1 = 2500
L2 = 5000
f = 0.02        # Fanning friction factor
d = 0.3
k1 = (32 * f * L1) / (d**5 * g * pi**2)
k2 = (32 * f * L2) / (d**5 * g * pi**2)


#
# This function calculates the flow rate of the pump, when it is enabled
#
def Pump_Enabled_Q(t, z, Q_VC):
    A = a2 - k1 - k2 - 1/ (2 * g * Area**2)
    B = 2 * k2 * Q_R(t) + (Q_R(t) + Q_VC(t)) / (g * Area**2)
    C = a1 - z - k2 * Q_R(t)**2 - (Q_R(t) + Q_VC(t))**2 / (2 * g * Area**2)
    roots = np.roots([A, B, C])
    return next(x for x in roots if x > 0 and np.isreal(x))     # Return the first positive real root (throw an error if none found)


#
# This function calculates the next water level of the tank
#
def z_next(Q_P, z, t, delta_t, Q_VC):
    dzdt = (Q_P - Q_R(t) - Q_VC(t)) / Area
    return z + dzdt * delta_t


#
# Cost of electricity, divided in 
# parcels of two hours, in EUR/kWh
#
Tarif = [0.0713, 0.0651, 0.0593, 0.0778, 0.0851, 0.0923, 0.0968, 0.10094, 0.10132, 0.10230, 0.10189, 0.10132]


def simul(x, t_values, Q_VC):
    delta_t = t_values[1] - t_values[0]
    z = z_i
    z_values = []
    Q_P_values = []
    power_values = []
    energy = 0
    cumulative_energy_values = []
    cost = 0
    cumulative_cost_values = []
    i = 0
    n_duty_cycles = len(x) // 2
    pump_enabled = False
    Tarif_i = Tarif[0]

    for t in t_values:

        if (i < n_duty_cycles):
            if (not pump_enabled and t >= x[i]):
                pump_enabled = True
            
            if (pump_enabled and t >= x[i] + x[i + n_duty_cycles]): 
                pump_enabled = False
                i += 1

        if (pump_enabled):
            Q_P = Pump_Enabled_Q(t, z, Q_VC)

            if (t < 24):    # To prevent float impercision above 24 (oob of the array)
                Tarif_i = Tarif[floor(abs(t)/2)]    # abs to prevent negative number from underflowing

            power = (rho * g / efficiency) * Q_P * h_P(Q_P) / (3600**3 * 1000) # in kW
            power_values.append(power) 
            energy += power * delta_t # in kWh
            cumulative_energy_values.append(energy)
            cost += power * delta_t * Tarif_i # in EUR
            cumulative_cost_values.append(cost)

        else:
            Q_P = 0
            power_values.append(0)
            cumulative_energy_values.append(energy)
            cumulative_cost_values.append(cost)

        Q_P_values.append(Q_P)
        z = z_next(Q_P, z, 0, delta_t, Q_VC)
        z_values.append(z)
    
    return Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values


#
# This function plots the givens curves of
# Q_R, Q_VC_Max, Q_VC_Min
# as well as the pump's equation h_P(Q)
#
def plot_given_curves():
    t_values = np.linspace(0, 24, 80)
    plt.figure()
    plt.plot(t_values, Q_R(t_values), label="Q_R")
    plt.plot(t_values, Q_VC_Max(t_values), label="Q_VC_Max", linestyle="--")
    plt.plot(t_values, Q_VC_Min(t_values), label="Q_VC_Min", linestyle="--")
    plt.fill_between(t_values, Q_VC_Min(t_values), Q_VC_Max(t_values), where=None, color='orange', alpha=0.3)
    plt.xlim(0, 24)
    plt.xlabel("t (h)") 
    plt.ylabel("Q (m^3 h^-1)")
    plt.title("Consumption Curves")
    plt.grid(True)
    plt.legend()

    Q_values = np.linspace(0, 400, 80)
    h_values = h_P(Q_values)
    plt.figure()
    plt.plot(Q_values[h_values > 0], h_values[h_values > 0], label="")
    plt.xlim(0)
    plt.ylim(0)
    plt.xlabel("Q (m^3 h^-1)")
    plt.ylabel("h_P (m)")
    plt.title("Pump Equation")
    plt.grid(True)
    plt.show(block=False)
    plt.pause(0.001)


#
# If this file is executed directly, 
# it will run from here
#
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    plot_given_curves()

    # Array of time positions. 40000 seems to be high enough so the results converge well
    t_values = np.linspace(0, 24, 40000)

    # Pump decision variable:
    x = [1, 5, 10, 16] + [2, 3, 3, 3]

    # Get the results of the simulation when Q_VC = Q_VC_Max
    Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = simul(x, t_values, Q_VC_Max)

    print(f"Cost: {cumulative_cost_values[-1]:.2f} EUR")
    print(f"Total electrical energy: {cumulative_energy_values[-1]:.1f} kWh")
    
    plt.figure()
    plt.plot(t_values, Q_P_values, label="Q_P_values")
    plt.plot(t_values, z_values, label="z_values")
    plt.plot(t_values, power_values, label="power_values")
    #plt.plot(t_values, cumulative_energy_values, label="cumulative_energy_values")
    #plt.plot(t_values, cumulative_cost_values, label="cumulative_cost_values")
    plt.axhline(y=z_lim[0], color='purple', linestyle=':', linewidth=2)
    plt.axhline(y=z_lim[1], color='purple', linestyle=':', linewidth=2)
    plt.xlim(0, 24)
    plt.ylim(140)
    plt.xlabel("t (h)")
    plt.ylabel("z (m) or Q_P (m^3 h^-1) or Electrical Power (kW)")
    plt.title("Result")
    plt.grid(True)
    plt.legend()
    plt.show()