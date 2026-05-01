
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Set time periods
T           = 50
T_stabilize = 25

years       = np.zeros(T)
years[0]    = 2026
for t in range(T-1):
    years[t+1] = years[t] + 1

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
v = 0.5

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
    k[0] = 3.5

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

print(df_full.head(50))
print(df_full.tail(50))


#Plot output
fig, ax = plt.subplots()

colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: "#a4c7f2"}

for mpc, group in df_full.groupby('MPC'):
    ax.plot(group['year'], group['capital'], label=f'Capital (MPC={mpc})', color = colors[mpc])

debt = df_full[df_full['MPC'] == MPC[0]]
ax.plot(debt['year'], debt['debt'], label='Debt', color='black')

ax.axvline(x = 2051, ymin = 0, ymax = 3.5, linestyle = 'dashed', color = 'black')

ax.set_title('Capital and Debt, Closed Economy')
ax.set_xlabel('Year')
ax.set_ylabel('Trillions of Dollars')
ax.legend()

# ###Private Income###
# #Introduce crowd out
# fraction = [0, 0.5, 1]

# c_results             = {}
# k_results             = {}
# anmp_results          = {}
# income_results        = {}

# for i in fraction:

#     #Allocate arrays
#     f             = np.zeros(T) #output
#     fp            = np.zeros(T) #MPK
#     fp_assumed    = np.zeros(T) #MPK with assumed capital level
#     c             = np.zeros(T) #consumption
#     w             = np.zeros(T) #wages
#     k             = np.zeros(T) #capital stock
#     k_assumed     = np.zeros(T) #capital stock with assumed capital level
#     anmp          = np.zeros(T) #average net marginal product
#     income        = np.zeros(T) #net of depreciation income

#     #Initialize capital stock
#     k[0] = 10

#     # Baseline steady-state values 
#     f_b    = A * k[0]**alpha
#     fp_b   = A * alpha * k[0]**(alpha - 1)
#     c_b    = f_b - k[0]*(delta + g)


#     for t in range(T):

#         #output
#         f[t]  = A * k[t]**alpha
#         fp[t] = A * alpha * k[t] **(alpha - 1)

#         #consumption
#         c[t] = c_b + i*primary_deficit[t]

#         #capital
#         if t < T - 1:
#             k[t+1] = (k[t]*(1 - delta) + f[t] - c[t]) / (1 + g)
        
#         #ANMP
#         k_assumed[t]  = k[0] - i*d[t]
#         fp_assumed[t] = A * alpha * k_assumed[t] ** (alpha - 1)
#         anmp[t]       = ((fp_assumed[t] + fp_b) / 2) - delta

#         #income
#         income[t] = f_b - delta * k[0] - anmp[t] *(i * d[t]) + d[t] * r + primary_deficit[t]


#     c_results[i]             = c.copy()
#     k_results[i]             = k.copy()   
#     anmp_results[i]          = anmp.copy()
#     income_results[i]        = income.copy()


# #Create datasets and print results

# df_constant    = pd.DataFrame({
#     "year": years,
#     "primary deficit": primary_deficit,
#     "debt": d
# })

# names   = ['consumption', 'capital', 'ANMP', 'income']
# results = [c_results, k_results, anmp_results, income_results]

# df_variable = None

# for name, result in zip(names, results):
#     df_temp = (pd.DataFrame.from_dict(result)
#                     .reset_index()
#                     .melt(id_vars='index', var_name='fraction', value_name=name))

#     df_variable = df_temp if df_variable is None else df_variable.merge(df_temp, on = ['index', 'fraction'])


# df_full = df_constant.reset_index() \
#                      .merge(df_variable, how = "right", on = "index") \
#                      .sort_values(by=["fraction", "index"])

# print(df_full.head(50))
# print(df_full.tail(50))


# #Plot output
# fig, ax = plt.subplots()

# colors = {0: '#053769', 0.5: '#ff5e1a', 1: "#a4c7f2"}

# for frac, group in df_full.groupby('fraction'):
#     ax.plot(group['year'], group['income'], label=f'Income (Fraction={frac})', color=colors[frac])

# debt = df_full[df_full['fraction'] == fraction[0]]
# # ax.plot(debt['year'], debt['debt'], label='Debt', color='black')

# ax.axvline(x = 2051, ymin = 0, ymax = 3.5, linestyle = 'dashed', color = 'black')

# ax.set_title('Private Income, Closed Economy')
# ax.set_xlabel('Year')
# #ax.set_ylabel('Trillions of Dollars')
# ax.set_yticklabels([])
# ax.set_yticks([])
# ax.legend()

plt.show()