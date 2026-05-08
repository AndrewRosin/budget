
import numpy as np
import matplotlib.pyplot as plt

# --- Shared parameters ---
T           = 150
T_stabilize = 25
years       = np.arange(2026, 2026 + T, dtype=float)

d_0          = 0.0
pd_exogenous = 0.06
r            = 0.02
g            = 0.01
v            = 0.1

MPC_vals = [0.25, 0.5, 0.75]

# --- Budget block (identical for both economies) ---
d               = np.zeros(T)
primary_deficit = np.zeros(T)
d[0]            = d_0

for t in range(T):
    if t < T_stabilize:
        primary_deficit[t] = pd_exogenous
    else:
        target             = -d[t] * (r - g)
        primary_deficit[t] = primary_deficit[t-1] + v * (target - primary_deficit[t-1])
    if t < T - 1:
        d[t+1] = (d[t] * (1 + r) + primary_deficit[t]) / (1 + g)

# --- Closed economy ---
A     = 1.0
alpha = 0.33
delta = 0.06
k0    = 10.0

fp_b = A * alpha * k0 ** (alpha - 1)
f_b  = A * k0 ** alpha
c_b_closed = f_b - k0 * (delta + g)

capital_chg = {}

for mpc in MPC_vals:
    k    = np.zeros(T)
    k[0] = k0

    for t in range(T):
        fp_t    = A * alpha * k[t] ** (alpha - 1)
        anmp_t  = (fp_t + fp_b) / 2 - delta
        c_t     = c_b_closed + mpc * (primary_deficit[t] + (r - anmp_t) * d[t])
        if t < T - 1:
            k[t+1] = k0 + (k[t] - k0) * (1 + anmp_t) / (1 + g) - (c_t - c_b_closed) / (1 + g)

    capital_chg[mpc] = k - k0

# --- Small open economy ---
s_open = r
k_open = 10.0
A_open = 1.0
alpha_open = 0.33
a0   = 3.5
w    = (1 - alpha_open) * A_open * k_open ** alpha_open
c_b_open = w + a0 * (s_open - g)

assets_chg = {}

for mpc in MPC_vals:
    a    = np.zeros(T)
    a[0] = a0

    for t in range(T):
        c_t = c_b_open + mpc * primary_deficit[t]
        if t < T - 1:
            a[t+1] = (a[t] * (1 + s_open) + w - c_t) / (1 + g)

    assets_chg[mpc] = a - a0

# --- Plot ---
colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: '#a4c7f2'}

fig, ax = plt.subplots()

ax.plot(years, capital_chg[0.5], color=colors[0.5], linestyle='solid',
        linewidth=1.5, label='Capital, closed (MPC=0.5)')
ax.plot(years, assets_chg[0.5],  color=colors[0.5], linestyle='dashed',
        linewidth=2.5, label='Assets, open (MPC=0.5)')

ax.plot(years, d, color='black', label='Debt')
ax.axvline(x=2051, linestyle='dashed', color='black')

ax.set_title('Capital vs. Asset Change by Economy Type')
ax.set_xlabel('Year')
ax.set_ylabel('Change (Trillions of Dollars)')
ax.legend(fontsize=8)

plt.tight_layout()
plt.show()
