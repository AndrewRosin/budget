# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
