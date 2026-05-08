
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Set time periods
T           = 150
T_stabilize = 25

years = np.arange(2026, 2026 + T, dtype=float)

###Budget###
#Set initial debt, intial deficit, interest rate, and growth rate of effective labor
d_0           = 0
pd_exogenous  = 0.06
r             = 0.02
g             = 0.01

#Initialize arrays for debt and primary deficit
d                 = np.zeros(T)
primary_deficit   = np.zeros(T)
d[0]              = d_0

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
#Initialize TFP, capital share, interest rate, and capital stock
A      = 1.0
alpha  = 0.33
s      = r #Risk-adjusted return to capital
k      = 10


#Introduce MPC
MPC = [0.25, 0.5, 0.75]

# Baseline steady-state values
f    = A * k**alpha
w    = (1-alpha) * f
c_b  = w + 3.5*(s - g)

c_results = {}
a_results = {}

for i in MPC:

    #Allocate arrays
    c       = np.zeros(T) #consumption
    a       = np.zeros(T) #assets

    #Initialize assets
    a[0] = 3.5

    for t in range(T):

        #Consumption and asset accumulation
        c[t] = c_b + i * primary_deficit[t]

        if t < T - 1:
            a[t+1] = (a[t]*(1+s) + w - c[t]) / (1+g)

    c_results[i] = c.copy()
    a_results[i] = a.copy()   


#Create datasets and print results

df_constant    = pd.DataFrame({
    "year": years,
    "primary deficit": primary_deficit,
    "debt": d
})

df_consumption = (pd.DataFrame.from_dict(c_results)
                    .reset_index()
                    .melt(id_vars='index', var_name='MPC', value_name='consumption'))

df_assets      = (pd.DataFrame.from_dict(a_results)
                    .reset_index()
                    .melt(id_vars='index', var_name='MPC', value_name='assets'))

df_variable    = df_consumption.merge(df_assets, on=['index', 'MPC'])

df_full = df_constant.reset_index() \
                     .merge(df_variable, how = "right", on = "index") \
                     .sort_values(by=["MPC", "index"])

df_full['assets_chg']         = df_full['assets'] - 3.5
df_full['debt_chg']           = df_full['debt']
df_full['foreign_capital']    = k - df_full['assets'] - 6.5
df_full['income']             = w + df_full['assets'] * s
df_full['savings_rate']       = (df_full['income'] - df_full['consumption']) / df_full['income']

df_full.to_csv('df_open_full.csv', index=False)

# print(df_full.head(50))
# print(df_full.tail(50))


#Plot output
fig, ax = plt.subplots()

colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: "#a4c7f2"}

for mpc, group in df_full.groupby('MPC'):
    ax.plot(group['year'], group['assets_chg'], label=f'Assets (MPC={mpc})', color = colors[mpc])

debt = df_full[df_full['MPC'] == MPC[0]]
ax.plot(debt['year'], debt['debt_chg'], label='Debt', color='black')

ax.axvline(x = 2051, ymin = 0, ymax = 3.5, linestyle = 'dashed', color = 'black')

ax.set_title('Assets and Debt, Small Open Economy')
ax.set_xlabel('Year')
ax.set_ylabel('Change (Trillions of Dollars)')
ax.set_ylim(-3, 3)
ax.legend()

#Plot consumption by MPC
fig, ax2 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax2.plot(group['year'], group['consumption'], label=f'MPC={mpc}', color=colors[mpc])

ax2.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax2.set_title('Consumption by MPC, Small Open Economy')
ax2.set_xlabel('Year')
ax2.set_ylabel('Consumption (Trillions of Dollars)')
ax2.set_ylim(1.4, 1.6)
ax2.legend()

#Plot foreign-owned capital by MPC
fig, ax3 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax3.plot(group['year'], group['foreign_capital'], label=f'MPC={mpc}', color=colors[mpc])

ax3.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax3.set_title('Foreign-Owned Capital by MPC, Small Open Economy')
ax3.set_xlabel('Year')
ax3.set_ylabel('Foreign-Owned Capital (Trillions of Dollars)')
ax3.set_ylim(0, 2)
ax3.legend()


#Plot savings rate by MPC
fig, ax5 = plt.subplots()

for mpc, group in df_full.groupby('MPC'):
    ax5.plot(group['year'], group['savings_rate'], label=f'MPC={mpc}', color=colors[mpc])

ax5.axvline(x=2051, ymin=0, ymax=1, linestyle='dashed', color='black')
ax5.set_title('Savings Rate by MPC, Small Open Economy')
ax5.set_xlabel('Year')
ax5.set_ylabel('Savings Rate')
ax5.legend()

###Different MPCs###
#Introduce MPC
MPC_accumulation  = 1
MPC_stabilization = 0

#Allocate arrays
c       = np.zeros(T) #consumption
a       = np.zeros(T) #assets

#Initialize assets
a[0] = 3.5

for t in range(T):

    #Consumption and asset accumulation
    if t < T_stabilize:
        c[t] = c_b + MPC_accumulation*primary_deficit[t]
    else:
        c[t] = c_b + MPC_stabilization*primary_deficit[t]

    if t < T - 1:
        a[t+1] = (a[t]*(1+s) + w - c[t]) / (1+g)




#Create datasets and print results

df_corollary  = pd.DataFrame({
    "year": years,
    "consumption": c,
    "assets": a,
    "primary deficit": primary_deficit,
    "debt": d
})

df_corollary.to_csv('df_open_corollary.csv', index=False)

# print(df_corollary.head(5))
# print(df_corollary.tail(5))


#Plot output
fig, ax1 = plt.subplots()

a_chg = a - 3.5
d_chg = d

ax1.plot(years, a_chg, label = 'Assets', color = '#053769')
ax1.plot(years, d_chg, label = 'Debt', color = '#ff5e1a')

ax1.axvline(x = 2051, ymin = 0, ymax = 3.5, linestyle = 'dashed', color = 'black')

plt.suptitle('        Assets and Debt, Small Open Economy', ha = 'center')
ax1.set_title('Non-Constant MPC', fontsize = 11, ha = 'center')
ax1.set_xlabel('Year')
ax1.set_ylabel('Change (Trillions of Dollars)')
ax1.set_ylim(-6,6)
ax1.legend()

plt.tight_layout()
plt.show()