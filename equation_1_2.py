import pandas as pd
import numpy as np

#Set time periods
T           = 75
T_stabilize = 30

#Set initial debt, intial deficit, interest rate, and growth rate of effective labor
d_0           = 0.0
pd_exogenous  = 0.06
r             = 0.02
g             = 0.01

#Initialize arrays for debt and primary deficit
d                 = np.zeros(T)
primary_deficit   = np.zeros(T)
d[0]              = d_0

for t in range (T - 1):
    if t < T_stabilize:
        primary_deficit[t] = pd_exogenous
    else:
        primary_deficit[t] = -d[t]*(r-g)

    d[t+1] = (d[t]*(1+r) + primary_deficit[t]) / (1+g)


#Write results to table
df = pd.DataFrame({
    "year"              : np.arange(T),
    "debt"              : d,
    "primary_deficit"   : primary_deficit
})

print(df)