# Graph Color Standards

All visualizations in this project use the following hex color palette. Every chart must use these exact codes.

## Color Palette

| Role | Hex | Preview | Usage |
|------|-----|---------|-------|
| Dark Blue | `#053769` | MPC = 0.25 / Assets (low sensitivity) |
| Orange | `#ff5e1a` | MPC = 0.5 / Debt (high sensitivity) |
| Light Blue | `#a4c7f2` | MPC = 0.75 / secondary scenario lines |
| Black | `#000000` | Debt reference lines, grid elements |

## Standard Color Dictionary

All multi-scenario line charts define colors with this pattern:

```python
colors = {0.25: '#053769', 0.5: '#ff5e1a', 0.75: '#a4c7f2'}
```

## Per-Series Color Assignments

For charts with individually specified series colors:

```python
# Assets / low-MPC series
color='#053769'

# Debt / high-MPC series
color='#ff5e1a'

# Reference / vertical lines
color='black'
```

## Files Using This Palette

- `equation_.py` — Closed economy capital and debt charts
- `equation_7.py` — Small open economy assets and debt charts (including non-constant MPC subplot)

Any new visualization added to this project must import colors from the palette above rather than defining new ones.
