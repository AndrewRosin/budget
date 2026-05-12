import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Set time periods
T           = 150
T_stabilize = 25

years = np.arange(2026, 2026 + T, dtype = float)

###Parameters###
pd_exogenous  = 0.06
g             = 0.01
v             = 0.1

A      = 1.0
alpha  = 0.33
delta  = 0.06

#Baseline steady-state values
k_b   = 10.0
f_b   = A * k_b**alpha
fp_b  = A * alpha * k_b**(alpha - 1)
c_b   = f_b - k_b * (delta + g)
income_b = f_b - delta * k_b

###Macro and Budget###
MPC = [0.25, 0.5, 0.75]

c_results      = {}
k_results      = {}
anmp_results   = {}
income_results = {}
d_results      = {}
pd_results     = {}
r_results      = {}

for i in MPC:

    #Allocate arrays
    f               = np.zeros(T)
    fp              = np.zeros(T)
    c               = np.zeros(T)
    k               = np.zeros(T)
    anmp            = np.zeros(T)
    income          = np.zeros(T)
    d               = np.zeros(T)
    primary_deficit = np.zeros(T)
    r_t             = np.zeros(T)

    k[0] = k_b
    d[0] = 0.0

    for t in range(T):

        #Output and MPK
        f[t]  = A * k[t]**alpha
        fp[t] = A * alpha * k[t]**(alpha - 1)

        #Interest rate equals current net MPK
        r      = fp[t] - delta
        r_t[t] = r

        #ANMP
        anmp[t] = (fp[t] + fp_b) / 2 - delta

        #Primary deficit
        if t < T_stabilize:
            primary_deficit[t] = pd_exogenous
        else:
            target             = -d[t] * (r - g)
            primary_deficit[t] = primary_deficit[t-1] + v * (target - primary_deficit[t-1])

        #Consumption
        c[t] = c_b + i * (primary_deficit[t] + (r - anmp[t]) * d[t]) #change in consumption that makes the change in the capital stock a fixed fraction of the debt

        #Income
        income[t] = f_b - delta * k_b - anmp[t] * (k_b - k[t]) + d[t] * r + primary_deficit[t] 

        if t < T - 1:
            #Capital accumulation
            k[t+1] = k_b + (k[t] - k_b) * (1 + anmp[t]) / (1 + g) - (c[t] - c_b) / (1 + g) #capital in time 't' + change in output - change in consumption
            #Debt accumulation
            d[t+1] = (d[t] * (1 + r) + primary_deficit[t]) / (1 + g)

    c_results[i]      = c.copy()
    k_results[i]      = k.copy()
    anmp_results[i]   = anmp.copy()
    income_results[i] = income.copy()
    d_results[i]      = d.copy()
    pd_results[i]     = primary_deficit.copy()
    r_results[i]      = r_t.copy()


#Build dataset
names   = ['primary deficit', 'debt', 'consumption', 'capital', 'r', 'ANMP', 'income']
results = [pd_results, d_results, c_results, k_results, r_results, anmp_results, income_results]

df_full = None

for name, result in zip(names, results):
    df_temp = (pd.DataFrame.from_dict(result)
                    .reset_index()
                    .melt(id_vars='index', var_name='MPC', value_name=name))
    df_full = df_temp if df_full is None else df_full.merge(df_temp, on=['index', 'MPC'])

df_full['year'] = years[df_full['index'].values]
df_full = df_full.sort_values(by=['MPC', 'index'])

df_full['debt_chg']        = df_full['debt']
df_full['consumption_chg'] = df_full['consumption'] - c_b
df_full['capital_chg']     = df_full['capital'] - k_b
df_full['income_chg']      = df_full['income'] - income_b
df_full['wage_chg']        = (1 - alpha) * (df_full['ANMP'] + delta) * df_full['capital_chg']
df_full['cap_income_chg']  = (alpha * (df_full['ANMP'] + delta) - delta) * df_full['capital_chg'] + df_full['debt'] * df_full['r'] + df_full['primary deficit']

df_full.to_csv('df_closed.csv', index=False)


#Plot capital and debt
fig, ax = plt.subplots()

colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: '#a4c7f2'}

for mpc, group in df_full.groupby('MPC'):
    ax.plot(group['year'], group['capital_chg'], label=f'Capital (MPC={mpc})', color=colors[mpc])

for mpc, group in df_full.groupby('MPC'):
    ax.plot(group['year'], group['debt_chg'], label=f'Debt (MPC = {mpc})', color=colors[mpc], linestyle='dashed')

ax.axvline(x=2051, ymin=0, ymax=3.5, linestyle='dashed', color='black')
ax.set_ylim(-2.5, 2.5)
ax.set_title('Capital and Debt, Closed Economy')
ax.set_xlabel('Year')
ax.set_ylabel('Change (Trillions of Dollars)')
ax.legend()
fig.savefig('graphs/capital_debt.png')

#Plot consumption
fig, ax2 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax2.plot(group['year'], group['consumption_chg'], label=f'MPC={mpc}', color=colors[mpc])

ax2.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax2.set_xlim(2026, None)
ax2.set_title('Consumption, Closed Economy')
ax2.set_xlabel('Year')
ax2.set_ylabel('Change (Trillions of Dollars)')
ax2.legend()
fig.savefig('graphs/consumption_closed.png')

#Plot income
fig, ax3 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax3.plot(group['year'], group['income_chg'], label=f'MPC={mpc}', color=colors[mpc])

ax3.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax3.set_xlim(2026, None)
ax3.set_ylim(-0.02, 0.08)
ax3.set_title('Private Income, Closed Economy')
ax3.set_xlabel('Year')
ax3.set_ylabel('Change (Trillions of Dollars)')
ax3.legend()
fig.savefig('graphs/private_income.png')

#Plot labor and capital income (for MPC = 0.5)
fig, ax_wk = plt.subplots()

mpc_05 = df_full[df_full['MPC'] == 0.5]

ax_wk.plot(mpc_05['year'], mpc_05['wage_chg'],       label='Labor Income',   color='#053769')
ax_wk.plot(mpc_05['year'], mpc_05['cap_income_chg'], label='Capital Income', color='#ff5e1a')
ax_wk.plot(mpc_05['year'], mpc_05['income_chg'],     label='Total Income',   color='#a4c7f2')

ax_wk.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax_wk.set_xlim(2026, None)
ax_wk.set_ylim(None, 0.12)
ax_wk.set_title('Labor and Capital Income, Closed Economy')
ax_wk.set_xlabel('Year')
ax_wk.set_ylabel('Change (Trillions of Dollars)')
ax_wk.legend()
fig.savefig('graphs/labor_capital_income.png')

###Heterogeneous agents: workers and capitalists
MPC_w = 0.75
MPC_c = 0.25

k_het  = np.zeros(T)
d_het  = np.zeros(T)
pd_het = np.zeros(T)

k_het[0] = k_b
d_het[0] = 0.0

for t in range(T):
    fp_t   = A * alpha * k_het[t] ** (alpha - 1)
    r    = fp_t - delta
    anmp_t = (fp_t + fp_b) / 2 - delta

    if t < T_stabilize:
        pd_het[t] = pd_exogenous
    else:
        target    = -d_het[t] * (r - g)
        pd_het[t] = pd_het[t-1] + v * (target - pd_het[t-1])

    lab_income_chg_t = (1 - alpha) * (anmp_t + delta) * (k_het[t] - k_b)
    cap_income_chg_t = (alpha * (anmp_t + delta) - delta) * (k_het[t] - k_b) + d_het[t] * r

    theta = MPC_w * ((1 - alpha) * pd_het[t] + lab_income_chg_t) + \
            MPC_c * (alpha * pd_het[t] + cap_income_chg_t)

    if t < T - 1:
        k_het[t+1] = k_b + (k_het[t] - k_b) * (1 + anmp_t) / (1 + g) - theta / (1 + g)
        d_het[t+1] = (d_het[t] * (1 + r) + pd_het[t]) / (1 + g)

fig, ax_het = plt.subplots()

k_rep = df_full[df_full['MPC'] == 0.5]['capital_chg'].values
d_rep = df_full[df_full['MPC'] == 0.5]['debt'].values

ax_het.plot(years, k_het - k_b, label='Capital (heterogeneous)', color='#053769')
ax_het.plot(years, k_rep,       label='Capital (representative)', color='#ff5e1a')
ax_het.plot(years, d_het,       label='Debt (hetereogeneous)', color='#053769', linestyle='dashed')
ax_het.plot(years, d_rep,       label='Debt (representative)', color='#ff5e1a', linestyle='dashed')
 
ax_het.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax_het.set_ylim(-2.5, 2.5)
ax_het.set_title('Capital and Debt, Closed Economy\nWage Earners and Capitalists vs. Representative Household', fontsize=11)
ax_het.set_xlabel('Year')
ax_het.set_ylabel('Change (Trillions of Dollars)')
ax_het.legend()
fig.savefig('graphs/heterogeneous_agents.png')

###Income by crowd-out fraction
fraction = [0, 1]

income_fraction_results = {}
d_fraction_results      = {}
k_fraction_results      = {}

for frac in fraction:
    income_f = np.zeros(T)
    d_f      = np.zeros(T)
    pd_f     = np.zeros(T)
    k_f_t    = np.zeros(T)
    d_f[0]   = 0.0

    for t in range(T):
        k_f         = k_b - frac * d_f[t]
        k_f_t[t]    = k_f
        fp_f        = A * alpha * k_f ** (alpha - 1)
        r_f         = fp_f - delta
        anmp_f      = (fp_f + fp_b) / 2 - delta

        if t < T_stabilize:
            pd_f[t] = pd_exogenous
        else:
            target  = -d_f[t] * (r_f - g)
            pd_f[t] = pd_f[t-1] + v * (target - pd_f[t-1])

        income_f[t] = d_f[t] * (r_f - frac * anmp_f) + pd_f[t]

        if t < T - 1:
            d_f[t+1] = (d_f[t] * (1 + r_f) + pd_f[t]) / (1 + g)

    income_fraction_results[frac] = income_f.copy()
    d_fraction_results[frac]      = d_f.copy()
    k_fraction_results[frac]      = k_f_t.copy()

frac_names   = ['debt', 'capital', 'income']
frac_results = [d_fraction_results, k_fraction_results, income_fraction_results,]

df_income_fraction = None

for name, result in zip(frac_names, frac_results):
    df_temp = (pd.DataFrame.from_dict(result)
                    .reset_index()
                    .melt(id_vars='index', var_name='fraction', value_name=name))
    df_income_fraction = df_temp if df_income_fraction is None else df_income_fraction.merge(df_temp, on=['index', 'fraction'])

df_income_fraction['year'] = years[df_income_fraction['index'].values]
df_income_fraction = df_income_fraction.sort_values(by=['fraction', 'index'])

df_income_fraction.to_csv('df_closed_corollary.csv', index=False)

fig, ax4 = plt.subplots()

colors_fraction = {0: '#053769', 1: '#ff5e1a'}

for frac, group in df_income_fraction.groupby('fraction'):
    ax4.plot(group['year'], group['income'],
             label=f'Fraction={frac}', color=colors_fraction[frac])

ax4.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax4.set_xlim(2026, None)
ax4.set_ylim(-0.02, 0.08)
ax4.set_title('Private Income by Crowd-Out Fraction, Closed Economy')
ax4.set_xlabel('Year')
ax4.set_ylabel('Change (Trillions of Dollars)')
ax4.legend()
fig.savefig('graphs/crowd_out_fraction.png')

plt.show()
