import numpy as np
from scipy.optimize import minimize, Bounds, NonlinearConstraint, BFGS

import hydraulicSim

if __name__ == '__main__':

    # Number of times the pump turns on
    n_duty_cycles = 3

    # Initial guesses
    x0_Min = [0.1, 7.352, 14.925] + [4, 4.077, 2.073]
    x0_Max = [0.1, 7.352, 14.925] + [4, 4.077, 2.073]

    FD_dx = 1.E-4
    
    # Objective function
    def f_Max(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Max)
        return cumulative_cost_values[-1]
    
    def f_Min(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Min)
        return cumulative_cost_values[-1]


    # Constraint function: x[i] - x[i-1] - x[i-1 + n] > 0  for i in 1..n-1
    # This makes sure the vector x makes sense in the context of the problem
    def fun_constraint_x(x):
        return np.array([x[i + 1] - x[i] - x[i + n_duty_cycles] for i in range(0, n_duty_cycles - 1)])
    nonlin_constraint_x = NonlinearConstraint(fun_constraint_x, lb=0, ub=np.inf)


    # Water level constraint
    def fun_water_level_constraint_Max(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Max)
        
        return z_values
    
    def fun_water_level_constraint_Min(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Min)
        
        return z_values

    water_level_constraint_Max = NonlinearConstraint(fun_water_level_constraint_Max, lb=hydraulicSim.z_abslim[0], ub=hydraulicSim.z_abslim[1], jac='2-point', hess=BFGS(), keep_feasible=False, finite_diff_rel_step = FD_dx)
    water_level_constraint_Min = NonlinearConstraint(fun_water_level_constraint_Min, lb=hydraulicSim.z_abslim[0], ub=hydraulicSim.z_abslim[1], jac='2-point', hess=BFGS(), keep_feasible=False, finite_diff_rel_step = FD_dx)
 

    def fun_constr_2(x):
        constr2 = []
        for i in range(n_duty_cycles-1):
            constr2.append(x[i]+x[i+n_duty_cycles] - x[i+1])
        constr2.append(x[n_duty_cycles-1]+x[2*n_duty_cycles-1] - 24)
        return constr2
    c2 = NonlinearConstraint(lambda x: fun_constr_2(x), -np.inf, 0.0, jac='2-point', hess=BFGS(), keep_feasible=True, finite_diff_rel_step = FD_dx)

    bounds = Bounds(0, 24)
    
    # Run the optimization
    result_Max = minimize(f_Max, x0_Max, constraints=[nonlin_constraint_x, c2, water_level_constraint_Max], bounds=bounds, method='SLSQP', jac='2-point', options={'ftol':0.01,'maxiter':20,'eps':FD_dx,'finite_diff_rel_step': FD_dx,'iprint': 3, 'disp': True})
    result_Min = minimize(f_Min, x0_Min, constraints=[nonlin_constraint_x, c2, water_level_constraint_Min], bounds=bounds, method='SLSQP', jac='2-point', options={'ftol':0.01,'maxiter':20,'eps':FD_dx,'finite_diff_rel_step': FD_dx,'iprint': 3, 'disp': True})
    
    print("Para Q_VC_Min:")
    print(result_Min)
    print("Para Q_VC_Max:")
    print(result_Max)

    x_Min = result_Min.x
    x_Max = result_Max.x
    t_values = np.linspace(0, 24, 30000)

    Q_P_values_Min, z_values_Min, power_values_Min, cumulative_energy_values_Min, cumulative_cost_values_Min = hydraulicSim.simul(x_Min, t_values, hydraulicSim.Q_VC_Min)

    Q_P_values_Max, z_values_Max, power_values_Max, cumulative_energy_values_Max, cumulative_cost_values_Max = hydraulicSim.simul(x_Max, t_values, hydraulicSim.Q_VC_Max)
    
    print("Para Q_VC_Min:")
    print(f"Cost: {cumulative_cost_values_Min[-1]:.2f} EUR")
    print(f"Total electrical energy: {cumulative_energy_values_Min[-1]:.1f} kWh")

    print("Para Q_VC_Max:")
    print(f"Cost: {cumulative_cost_values_Max[-1]:.2f} EUR")
    print(f"Total electrical energy: {cumulative_energy_values_Max[-1]:.1f} kWh")
    
    import matplotlib.pyplot as plt

    cumulative_energy_values_Min = np.array(cumulative_energy_values_Min) / 10
    cumulative_energy_values_Max = np.array(cumulative_energy_values_Max) / 10
    
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(t_values, Q_P_values_Min, label="Q_P (m^3 h^-1)")
    plt.plot(t_values, z_values_Min, label="z (m)")
    plt.plot(t_values, power_values_Min, label="Power (kW)")
    plt.plot(t_values, cumulative_energy_values_Min, label="Cumulative Energy (x10^4 W)")
    plt.plot(t_values, cumulative_cost_values_Min, label="Cumulative Cost (€)")
    plt.axhline(y=hydraulicSim.z_abslim[0], color='purple', linestyle=':', linewidth=2)
    plt.fill_between(t_values, hydraulicSim.z_lim[0], hydraulicSim.z_abslim[0], where=None, color='orange', alpha=0.3)
    plt.axhline(y=hydraulicSim.z_abslim[1], color='purple', linestyle=':', linewidth=2)
    plt.fill_between(t_values, hydraulicSim.z_abslim[1], hydraulicSim.z_lim[1], where=None, color='orange', alpha=0.3)
    plt.xlim(0, 24)
    plt.ylim(0)
    plt.xlabel("t (h)")
    plt.ylabel("")
    plt.title("Resultados da Otimização para Q_VC_Min")
    plt.grid(True)
    plt.legend()
    
    plt.figure()
    plt.plot(t_values, Q_P_values_Max, label="Q_P (m^3 h^-1)")
    plt.plot(t_values, z_values_Max, label="z (m)")
    plt.plot(t_values, power_values_Max, label="Power (kW)")
    plt.plot(t_values, cumulative_energy_values_Max, label="Cumulative Energy (x10^4 W)")
    plt.plot(t_values, cumulative_cost_values_Max, label="Cumulative Cost (€)")
    plt.axhline(y=hydraulicSim.z_abslim[0], color='purple', linestyle=':', linewidth=2)
    plt.fill_between(t_values, hydraulicSim.z_lim[0], hydraulicSim.z_abslim[0], where=None, color='orange', alpha=0.3)
    plt.axhline(y=hydraulicSim.z_abslim[1], color='purple', linestyle=':', linewidth=2)
    plt.fill_between(t_values, hydraulicSim.z_abslim[1], hydraulicSim.z_lim[1], where=None, color='orange', alpha=0.3)
    plt.xlim(0, 24)
    plt.ylim(0)
    plt.xlabel("t (h)")
    plt.title("Resultados da Otimização para Q_VC_Max")
    plt.grid(True)
    plt.legend()
    
    plt.show()