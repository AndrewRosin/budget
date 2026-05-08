
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Set time periods
T           = 150
T_stabilize = 25

years = np.arange(2026, 2026 + T, dtype = float)

###Budget###
#Set initial debt, intial deficit, interest rate, and growth rate of effective labor
d_0           = 0.0  
pd_exogenous  = 0.06
r             = 0.02
g             = 0.01

#Initialize arrays for debt and primary deficit
d                  = np.zeros(T)
primary_deficit    = np.zeros(T)
d[0]               = d_0

#Speed at which debt stabilizes
v = 0.1

for t in range(T):
    if t < T_stabilize:
        primary_deficit[t] = pd_exogenous
    else:
        target             = -d[t]*(r-g)
        primary_deficit[t] = primary_deficit[t-1] + v*(target-primary_deficit[t-1])

    if t < T - 1:
        d[t+1] = (d[t]*(1+r) + primary_deficit[t]) / (1+g)

###Macro###
#Initialize TFP, capital share, and depreciation rate
A      = 1.0
alpha  = 0.33
delta  = 0.06

#Introduce MPC
MPC = [0.25, 0.5, 0.75]

c_results             = {}
k_results             = {}
anmp_results          = {}
income_results        = {}

for i in MPC:

    #Allocate arrays
    f             = np.zeros(T) #output
    fp            = np.zeros(T) #MPK
    c             = np.zeros(T) #consumption
    s             = np.zeros(T) #interest rate
    w             = np.zeros(T) #wages
    k             = np.zeros(T) #capital stock
    anmp          = np.zeros(T) #average net marginal product
    income        = np.zeros(T) #net of depreciation income

    #Initialize capital stock
    k[0] = 10

    # Baseline steady-state values 
    f_b    = A * k[0]**alpha
    fp_b   = A * alpha * k[0]**(alpha - 1)
    c_b    = f_b - k[0]*(delta + g)

    for t in range(T):

        #output
        f[t]  = A * k[t]**alpha
        fp[t] = A * alpha * k[t] **(alpha - 1)

        #ANMP
        anmp[t] = ((fp[t] + fp_b) / 2) - delta

        #consumption
        c[t] = c_b + i*(primary_deficit[t] + (r - anmp[t]) * d[t])

        #capital
        if t < T - 1:
            k[t+1] = k[0] + (k[t] - k[0]) * (1 + anmp[t]) / (1 + g) - (c[t] - c_b) / (1 + g)
        
        #income
        #income[t] = f[t] - delta * k[t] + d[t] * r + primary_deficit[t]
        income[t] = f_b - delta * k[0] - anmp[t] *(k[0] - k[t]) + d[t] * r + primary_deficit[t]


    c_results[i]             = c.copy()
    k_results[i]             = k.copy()   
    anmp_results[i]          = anmp.copy()
    income_results[i]        = income.copy()


#Create datasets and print results

df_constant    = pd.DataFrame({
    "year": years,
    "primary deficit": primary_deficit,
    "debt": d
})

names   = ['consumption', 'capital', 'ANMP', 'income']
results = [c_results, k_results, anmp_results, income_results]

df_variable = None

for name, result in zip(names, results):
    df_temp = (pd.DataFrame.from_dict(result)
                    .reset_index()
                    .melt(id_vars='index', var_name='MPC', value_name=name))

    df_variable = df_temp if df_variable is None else df_variable.merge(df_temp, on = ['index', 'MPC'])


df_full = df_constant.reset_index() \
                     .merge(df_variable, how = "right", on = "index") \
                     .sort_values(by=["MPC", "index"])

income_b = f_b - delta * k[0]

df_full['capital_chg']        = df_full['capital'] - 10
df_full['debt_chg']           = df_full['debt']
df_full['consumption_chg']    = df_full['consumption'] - c_b
df_full['income_chg']         = df_full['income'] - income_b
df_full['wage_chg']           = (1 - alpha) * (df_full['ANMP'] + delta) * df_full['capital_chg']
df_full['cap_income_chg']     = (alpha * (df_full['ANMP'] + delta) - delta) * df_full['capital_chg'] + df_full['debt'] * r + df_full['primary deficit']

df_full.to_csv('df_closed.csv', index=False)


#Plot output
fig, ax = plt.subplots()

colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: "#a4c7f2"}

for mpc, group in df_full.groupby('MPC'):
    ax.plot(group['year'], group['capital_chg'], label=f'Capital (MPC={mpc})', color = colors[mpc])

debt = df_full[df_full['MPC'] == MPC[0]]
ax.plot(debt['year'], debt['debt_chg'], label='Debt', color='black')

ax.axvline(x = 2051, ymin = 0, ymax = 3.5, linestyle = 'dashed', color = 'black')

ax.set_title('Capital and Debt, Closed Economy')
ax.set_xlabel('Year')
ax.set_ylabel('Change (Trillions of Dollars)')
ax.legend()

#Plot consumption
fig, ax2 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax2.plot(group['year'], group['consumption_chg'], label=f'MPC={mpc}', color=colors[mpc])

ax2.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax2.set_title('Consumption, Closed Economy')
ax2.set_xlabel('Year')
ax2.set_ylabel('Change (Trillions of Dollars)')
ax2.legend()

#Plot income
fig, ax3 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax3.plot(group['year'], group['income_chg'], label=f'MPC={mpc}', color=colors[mpc])

ax3.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax3.set_title('Income, Closed Economy')
ax3.set_xlabel('Year')
ax3.set_ylabel('Change (Trillions of Dollars)')
ax3.legend()

#Plot labor and capital income for MPC = 0.5
fig, ax_wk = plt.subplots()

mpc_05 = df_full[df_full['MPC'] == 0.5]

ax_wk.plot(mpc_05['year'], mpc_05['wage_chg'],       label='Labor Income',   color='#053769')
ax_wk.plot(mpc_05['year'], mpc_05['cap_income_chg'], label='Capital Income', color='#ff5e1a')
ax_wk.plot(mpc_05['year'], mpc_05['income_chg'],     label='Total Income',   color='#a4c7f2')

ax_wk.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax_wk.set_title('Labor and Capital Income, Closed Economy (MPC=0.5)')
ax_wk.set_xlabel('Year')
ax_wk.set_ylabel('Change (Trillions of Dollars)')
ax_wk.legend()

###Heterogeneous agents: workers and capitalists###
MPC_w = 0.75  # workers save 25%
MPC_c = 0.25  # capitalists save 75%

k_het    = np.zeros(T)
k_het[0] = 10

for t in range(T):
    fp_t   = A * alpha * k_het[t] ** (alpha - 1)
    anmp_t = (fp_t + fp_b) / 2 - delta

    cap_chg_t        = k_het[t] - k_het[0]
    wage_chg_t       = (1 - alpha) * (anmp_t + delta) * cap_chg_t
    cap_income_chg_t = (alpha * (anmp_t + delta) - delta) * cap_chg_t + d[t] * r

    theta_t = MPC_w * (0.5 * primary_deficit[t] + wage_chg_t) + \
              MPC_c * (0.5 * primary_deficit[t] + cap_income_chg_t)

    if t < T - 1:
        k_het[t+1] = k_het[0] + cap_chg_t * (1 + anmp_t) / (1 + g) - theta_t / (1 + g)

fig, ax_het = plt.subplots()

k_rep = df_full[df_full['MPC'] == 0.5]['capital_chg'].values

ax_het.plot(years, k_het - 10, label='Capital (heterogeneous)',     color='#053769')
ax_het.plot(years, k_rep,      label='Capital (representative, MPC=0.5)', color='#ff5e1a')
ax_het.plot(years, d,          label='Debt',                        color='black')

ax_het.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax_het.set_title('Capital and Debt, Heterogeneous Agents')
ax_het.set_xlabel('Year')
ax_het.set_ylabel('Change (Trillions of Dollars)')
ax_het.legend()

###Income by crowd-out fraction###
fraction = [0, 1]

income_fraction_results = {}

for f in fraction:
    income_f = np.zeros(T)

    for t in range(T):
        k_f   = k[0] - f * d[t]
        fp_f  = A * alpha * k_f ** (alpha - 1)
        anmp_f      = (fp_f + fp_b) / 2 - delta
        income_f[t] = d[t] * (r - f * anmp_f) + primary_deficit[t]

    income_fraction_results[f] = income_f.copy()

df_income_fraction = pd.DataFrame(income_fraction_results)
df_income_fraction['year'] = years

df_income_fraction.to_csv('df_closed_corollary.csv', index=False)

fig, ax4 = plt.subplots()

colors_fraction = {0: '#053769', 1: '#ff5e1a'}

for f in fraction:
    ax4.plot(df_income_fraction['year'], df_income_fraction[f],
             label=f'Fraction={f}', color=colors_fraction[f])

ax4.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax4.set_title('Change in Net Income by Crowd-Out Fraction, Closed Economy')
ax4.set_xlabel('Year')
ax4.set_ylabel('Change (Trillions of Dollars)')
ax4.legend()

plt.show()