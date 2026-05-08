# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Source Paper

Sheiner, Louise. "Comparing the Macroeconomic and Budgetary Costs of Debt." Hutchins Center Working Paper #101, Brookings Institution, February 2025.
https://www.brookings.edu/wp-content/uploads/2025/02/WP101-Sheiner.pdf

All variables are per unit of effective labor. Effective labor grows at rate `g`.

### Budget Block (both economies)

Debt evolves as: `d[t+1] = (d[t]*(1+r) + pd[t]) / (1+g)`

Debt-stabilizing primary deficit (Equation 2): `pd_stabilize = -d[t]*(r - g)`

### Closed Economy Model

**ANMP** (average net marginal product, between baseline and time t):
`ANMP_t = (f'(k_t) + f'(k_b)) / 2 - delta`

Output approximation used throughout:
`f(k_t) ≈ f(k_b) + (ANMP_t + delta) * (k_t - k_b)`

**Baseline steady-state consumption** (Equation 8):
`c_b = f(k_b) - k_b*(g + delta)`

**Consumption boost from deficits** (Box 6) — theta is the MPC-scaled income effect:
`theta_t = MPC * (pd_t + (r - ANMP_t) * d_t)`

So: `c_t = c_b + theta_t`

The two terms in theta: `pd_t` is the direct fiscal transfer; `(r - ANMP_t)*d_t` is the net return on bonds versus displaced capital (negative when capital is productive, i.e., the crowding-out income loss).

**Capital accumulation** (Box 3, applying the output approximation to the resource constraint):
`k[t+1] = k_b + (k_t - k_b)*(1 + ANMP_t)/(1+g) - theta_t/(1+g)`

**Key result** (Box 6): when `theta_t = MPC*(pd_t + (r - ANMP_t)*d_t)`, crowd-out is proportional to debt at every period: `k_b - k_t = MPC * d_t`.

**Long-run consumption cost** (Equation 10):
`c_newsteadystate - c_b ≈ (k_T - k_b)*(ANMP_T - g)`

### Small Open Economy Model

Interest rate `s` is exogenous; households hold assets `a` rather than capital.

**Assets** (Equation 4): `a_T = a_b - SUM[ theta_i * (1+s)^{T-1-i} / (1+g)^{T-i} ]`

With constant MPC: `a_b - a_T = MPC * d_T` (Equation 7)

**Consumption boost**: `theta_t = MPC * pd_t` (no ANMP term — wages and returns are fixed)

**Long-run consumption cost** (Equation 6): `c_new - c_b = -(a_b - a_T)*(s - g)`

## Running Scripts

Each script is self-contained and runs directly:

```
python equation_.py
python equation_1_2.py
python equation_7.py
```

Dependencies: `numpy`, `pandas`, `matplotlib`.

## Architecture

This project models the macroeconomic and budgetary costs of government debt accumulation across two economy types. All scripts share the same budget block and differ in how the macro side is modeled.

### Shared Budget Block

All scripts simulate debt dynamics over `T` periods with two phases:
- **Accumulation phase** (`t < T_stabilize`): primary deficit held at `pd_exogenous`
- **Stabilization phase** (`t >= T_stabilize`): primary deficit adjusts toward the debt-stabilizing level `-(r-g)*d[t]`, with speed parameter `v`

Debt evolves as: `d[t+1] = (d[t]*(1+r) + primary_deficit[t]) / (1+g)`

### Script Roles

- **`equation_1_2.py`** — Budget block only. Outputs a table of debt and primary deficit trajectories. No macro model, no charts.

- **`equation_.py`** — Closed economy model. Capital stock `k` evolves endogenously; consumption responds to deficits via MPC. The average net marginal product (ANMP) links the interest rate to the capital stock. Plots capital and debt over time for three MPC scenarios (0.25, 0.5, 0.75).

- **`equation_7.py`** — Small open economy model. Capital stock is fixed; households hold assets `a` rather than capital. The interest rate `s` is exogenous. Plots assets and debt for three constant MPC scenarios, plus a second chart for a non-constant MPC (high during accumulation, low during stabilization).

### Key Parameters (shared defaults)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `r` | 0.02 | Interest rate |
| `g` | 0.01 | Growth rate of effective labor |
| `pd_exogenous` | 0.06 | Primary deficit during accumulation |
| `T_stabilize` | 25 | Period when stabilization begins |
| `T` | 50 | Total periods |
| `alpha` | 0.33 | Capital share (closed economy) |
| `delta` | 0.06 | Depreciation rate (closed economy) |

## Graph Colors

See `.claude/SKILLS.md` for the required hex palette. All charts must use those codes — do not introduce new colors.
