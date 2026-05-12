
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Set time periods
T           = 150
T_stabilize = 25
years       = np.arange(2026, 2026 + T, dtype=float)

#Parameters
pd_exogenous = 0.06
g            = 0.01
v            = 0.1

MPC = [0.25, 0.5, 0.75]

###Closed Economy###
A     = 1.0
alpha = 0.33
delta = 0.06
k_b   = 10.0

f_b        = A * k_b ** alpha
fp_b       = A * alpha * k_b ** (alpha - 1)
c_b_closed = f_b - k_b * (delta + g)

capital_chg        = {}
consumption_closed = {}
anmp_results       = {}
d_closed           = {}
pd_closed          = {}
r_results          = {}

for mpc in MPC:
    k               = np.zeros(T)
    c               = np.zeros(T)
    anmp            = np.zeros(T)
    d               = np.zeros(T)
    primary_deficit = np.zeros(T)
    r               = np.zeros(T)
   
    k[0] = k_b
    d[0] = 0.0

    for t in range(T):
        fp      = A * alpha * k[t] ** (alpha - 1)
        r_t     = fp - delta
        r[t]    = r_t
        anmp[t] = (fp + fp_b) / 2 - delta

        if t < T_stabilize:
            primary_deficit[t] = pd_exogenous
        else:
            target             = -d[t] * (r_t - g)
            primary_deficit[t] = primary_deficit[t-1] + v * (target - primary_deficit[t-1])

        c[t] = c_b_closed + mpc * (primary_deficit[t] + (r_t - anmp[t]) * d[t])

        if t < T - 1:
            k[t+1] = k_b + (k[t] - k_b) * (1 + anmp[t]) / (1 + g) - (c[t] - c_b_closed) / (1 + g)
            d[t+1] = (d[t] * (1 + r_t) + primary_deficit[t]) / (1 + g)

    capital_chg[mpc]        = k - k_b
    consumption_closed[mpc] = c
    anmp_results[mpc]       = anmp
    d_closed[mpc]           = d
    pd_closed[mpc]          = primary_deficit
    r_results[mpc]          = r

###Small Open Economy###
r      = fp_b - delta
k      = 10.0
w      = (1 - alpha) * A * k ** alpha
a_b    = (c_b_closed - w) / (r - g) #calibrated such that baseline consumption is equal in closed and open economies
c_b_open = w + a_b * (r - g)

###Budget###
d_open               = np.zeros(T)
primary_deficit_open = np.zeros(T)
d_open[0]            = 0.0

for t in range(T):
    if t < T_stabilize:
        primary_deficit_open[t] = pd_exogenous
    else:
        target                  = -d_open[t] * (r - g)
        primary_deficit_open[t] = primary_deficit_open[t-1] + v * (target - primary_deficit_open[t-1])
    if t < T - 1:
        d_open[t+1] = (d_open[t] * (1 + r) + primary_deficit_open[t]) / (1 + g)

assets_chg       = {}
consumption_open = {}

for mpc in MPC:
    a    = np.zeros(T)
    c    = np.zeros(T)
    a[0] = a_b

    for t in range(T):
        c[t] = c_b_open + mpc * primary_deficit_open[t]
        if t < T - 1:
            a[t+1] = (a[t] * (1 + r) + w - c[t]) / (1 + g)

    assets_chg[mpc]       = a - a_b
    consumption_open[mpc] = c

###DataFrame###
df = pd.DataFrame({
    'year':                   years,
    'debt_closed':            d_closed[0.5],
    'debt_open':              d_open,
    'primary_deficit_closed': pd_closed[0.5],
    'primary_deficit_open':   primary_deficit_open,
    'capital':                k_b + capital_chg[0.5],
    'assets':                 a_b + assets_chg[0.5],
    'consumption_closed':     consumption_closed[0.5],
    'consumption_open':       consumption_open[0.5],
    'consumption_chg_closed': consumption_closed[0.5] - c_b_closed,
    'consumption_chg_open':   consumption_open[0.5]   - c_b_open,
    'anmp':                   anmp_results[0.5],
    'r' :                     r_results[0.5]
})

df.to_csv('df_compare.csv', index=False)

###Plot###
colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: '#a4c7f2'}

fig, ax = plt.subplots()

ax.plot(years, capital_chg[0.5],  color=colors[0.25], linestyle='solid',
        linewidth=1.5, label='Capital, Closed Economy')
ax.plot(years, assets_chg[0.5],   color=colors[0.25], linestyle='dashed',
        linewidth=1.5, label='Assets, Small Open Economy')
ax.plot(years, d_closed[0.5],     color=colors[0.5],  linestyle='solid',  label='Debt, Closed Economy')
ax.plot(years, d_open,            color=colors[0.5],  linestyle='dashed', label='Debt, Small Open Economy')

ax.axvline(x=2051, linestyle='dashed', color='black')
ax.set_title('Capital vs. Assets by Economy Type')
ax.set_xlabel('Year')
ax.set_ylabel('Change (Trillions of Dollars)')
ax.set_ylim(-2.5, 2.5)
ax.legend(fontsize=8)

plt.tight_layout()

fig2, ax2 = plt.subplots()

ax2.plot(years, consumption_closed[0.5] - c_b_closed, color='#053769', label='Consumption, Closed Economy')
ax2.plot(years, consumption_open[0.5]   - c_b_open,   color='#ff5e1a', label='Consumption, Small Open Economy')

ax2.axvline(x=2051, linestyle='dashed', color='black')
ax2.set_title('Consumption by Economy Type')
ax2.set_xlabel('Year')
ax2.set_xlim(2026, None)
ax2.set_ylabel('Change in Consumption (Trillions of Dollars)')
ax2.set_ylim(-0.02,0.04)
ax2.legend()

plt.tight_layout()

fig.savefig('graphs/capital_vs_assets.png', dpi=150, bbox_inches='tight')
fig2.savefig('graphs/consumption_by_economy.png', dpi=150, bbox_inches='tight')

plt.show()
