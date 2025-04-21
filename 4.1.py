import numpy as np
from scipy.optimize import minimize, Bounds, NonlinearConstraint, LinearConstraint, BFGS

import hydraulicSim

if __name__ == '__main__':

    # Number of times the pump turns on
    # n_duty_cycles = 2

    # Initial guess
    # x0 = [2, 14, 2, 3]

    # Number of times the pump turns on
    n_duty_cycles = 6

    # Initial guess
    #x0 = np.concatenate([np.linspace(1, 23, n_duty_cycles), np.full(n_duty_cycles, 0.8)])
    #print(x0)

    x0 = [1.105, 5.4, 12.35, 17.6, 19.8, 23] + [4.2, 2.4, 2.35, 1.5, 0.5, 0.7]


    FD_dx = 1.E-4

    
    # Objective function
    def f(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Max)
        return cumulative_cost_values[-1]


    # Constraint function: x[i] - x[i-1] - x[i-1 + n] > 0  for i in 1..n-1
    # This makes sure the vector x makes sense in the context of the problem
    def fun_constraint_x(x):
        return np.array([x[i + 1] - x[i] - x[i + n_duty_cycles] for i in range(0, n_duty_cycles - 1)])
    nonlin_constraint_x = NonlinearConstraint(fun_constraint_x, lb=0, ub=np.inf)


    # Water level constraint
    def fun_water_level_constraint(x):
        t_values = np.linspace(0, 24, 30000)
        Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Max)
        
        return z_values

    water_level_constraint = NonlinearConstraint(fun_water_level_constraint, lb=hydraulicSim.z_lim[0], ub=hydraulicSim.z_lim[1], jac='2-point', hess=BFGS(), keep_feasible=False, finite_diff_rel_step = FD_dx)
 

    # --- Constraint 2: x[i] + x[i+n] <= 24  for i in 0..n-1
    # Build a linear constraint matrix
    #A = np.zeros((n_duty_cycles, 2*n_duty_cycles))
    #for i in range(n_duty_cycles):
    #    A[i, i] = 1      # x[i]
    #    A[i, i+n_duty_cycles] = 1    # x[i+n]
    #
    #lin_con = LinearConstraint(A, lb=-np.inf, ub=24, )

    def fun_constr_2(x):
        constr2 = []
        for i in range(n_duty_cycles-1):
            constr2.append(x[i]+x[i+n_duty_cycles] - x[i+1])
        constr2.append(x[n_duty_cycles-1]+x[2*n_duty_cycles-1] - 24)
        return constr2
    c2 = NonlinearConstraint(lambda x: fun_constr_2(x), -np.inf, 0.0, jac='2-point', hess=BFGS(), keep_feasible=True, finite_diff_rel_step = FD_dx)

    # --- Bounds: all x[i] >= 0
    bounds = Bounds(0, 24)

    
    # Run the optimization
    result = minimize(f, x0, constraints=[nonlin_constraint_x, c2, water_level_constraint], bounds=bounds, method='SLSQP', jac='2-point', options={'ftol':0.01,'maxiter':60,'eps':FD_dx,'finite_diff_rel_step': FD_dx,'iprint': 3, 'disp': True})

    print(result)

    x = result.x
    t_values = np.linspace(0, 24, 30000)

    # Get the results of the simulation when Q_VC = Q_VC_Max
    Q_P_values, z_values, power_values, cumulative_energy_values, cumulative_cost_values = hydraulicSim.simul(x, t_values, hydraulicSim.Q_VC_Max)

    print(f"Cost: {cumulative_cost_values[-1]:.2f} EUR")
    print(f"Total electrical energy: {cumulative_energy_values[-1]:.1f} kWh")
    
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(t_values, Q_P_values, label="Q_P_values")
    plt.plot(t_values, z_values, label="z_values")
    plt.plot(t_values, power_values, label="power_values")
    #plt.plot(t_values, cumulative_energy_values, label="cumulative_energy_values")
    #plt.plot(t_values, cumulative_cost_values, label="cumulative_cost_values")
    plt.axhline(y=hydraulicSim.z_lim[0], color='purple', linestyle=':', linewidth=2)
    plt.axhline(y=hydraulicSim.z_lim[1], color='purple', linestyle=':', linewidth=2)
    plt.xlim(0, 24)
    plt.ylim(140)
    plt.xlabel("t (h)")
    plt.ylabel("z (m) or Q_P (m^3 h^-1) or Electrical Power (kW)")
    plt.title("Result")
    plt.grid(True)
    plt.legend()
    plt.show()