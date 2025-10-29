# Grand Tack Code Corrections

## Summary
Revised the Grand Tack simulation based on **Walsh et al. (2011) Nature 475, 206-209** - the original Grand Tack paper.

## Key Corrections Made

### 1. Migration Timescale
**Before:** `MIGRATION_TIMESCALE_0 = 50,000 years`  
**After:** `MIGRATION_TIMESCALE_0 = 100,000 years`  
**Reason:** Walsh et al. (2011) states migration occurs on ~100,000 year timescale

### 2. Type II Migration Formula
**Before:** `da/dt = -a / (2 * t_mig)`  
**After:** `da/dt = -2a / t_mig`  
**Reason:** Standard Type II migration prescription (Morbidelli & Crida 2007)
- The factor of 2 comes from the proper normalization
- Inward migration: da/dt = -2a/t_mig (negative)
- Outward migration: da/dt = +2a/t_mig (positive, after resonance)

### 3. Mass-Dependent Migration
**Before:** `mass_factor = (M_Jup/M_Sat)^0.5` (square root dependence)  
**After:** `t_mig,Saturn = t_mig,Jupiter / (M_Jup/M_Sat)` (inverse linear)  
**Reason:** Type II migration timescale inversely proportional to planet mass
- Lower mass → faster migration
- Saturn (0.3 M_Jup initially) migrates ~3x faster than Jupiter
- This allows Saturn to catch up and establish resonance

### 4. Eccentricity Damping
**Before:** `ECCENTRICITY_DAMPING_FACTOR = 100`  
**After:** `ECCENTRICITY_DAMPING_FACTOR = 10`  
**Reason:** More conservative/realistic damping timescale
- Literature suggests t_damp ~ 10-100 orbital periods
- Used factor of 10 as conservative estimate
- Prevents over-damping while maintaining near-circular orbits

### 5. Saturn Growth Timescale
**Before:** `SATURN_GROWTH_TIME = 200,000 years`  
**After:** `SATURN_GROWTH_TIME = 100,000 years`  
**Reason:** Faster growth allows resonance capture during inward migration phase
- Saturn needs to reach sufficient mass to lock in resonance
- 100 kyr aligns with inward migration timescale

### 6. Total Simulation Time
**Before:** `TOTAL_SIMULATION_TIME = 600,000 years`  
**After:** `TOTAL_SIMULATION_TIME = 700,000 years`  
**Reason:** Extended for safety margin
- Ensures outward migration phase is fully captured
- Disk dissipation occurs over 1-3 Myr (plenty of time)

## Physics Background

### Type II Migration
When a giant planet opens a gap in the protoplanetary disk:

```
da/dt = -2a / t_mig
```

Where `t_mig` depends on:
- Disk surface density: Σ
- Disk viscosity: ν
- Planet mass: M_planet

For Type II: `t_mig ∝ 1/M_planet` (inversely proportional)

### Resonance Capture Mechanism
1. **Initial state:** Jupiter at 3.5 AU, Saturn at 4.5 AU
2. **Both migrate inward:** Saturn faster due to lower mass
3. **Approach resonance:** Period ratio P_Sat/P_Jup → 1.5
4. **Capture:** Resonant torques lock configuration
5. **Outward migration:** Locked pair migrates outward together

### Why Jupiter "Tacks"?
- Inward migration until resonance capture at ~1.5 AU
- Resonance locks the system
- Combined resonant torques drive outward migration
- Creates characteristic "tack" shape in semi-major axis vs time

## Expected Results

After running corrected simulation:

| Parameter | Initial | Tack Point | Final |
|-----------|---------|------------|-------|
| **Jupiter SMA** | 3.5 AU | ~1.5 AU | ~5.2 AU |
| **Saturn SMA** | 4.5 AU | ~2.3 AU | ~9.5 AU |
| **Period Ratio** | ~1.65 | ~1.50 | ~1.50 |
| **Time** | 0 kyr | ~100 kyr | ~700 kyr |

## Key Diagnostic Plots

1. **Semi-major axis evolution** - Shows the "tack" at 1.5 AU
2. **Period ratio** - Locks at 1.5 (3:2 resonance)
3. **Eccentricities** - Remain low (~0.01-0.05) due to damping
4. **Saturn mass** - Grows from 0.3 to 0.95 M_Jup
5. **Migration rates** - Changes sign at resonance capture
6. **Phase space** - Trajectory in (a_Jup, a_Sat) plane

## References

**Primary:**
- Walsh, K. J., Morbidelli, A., Raymond, S. N., O'Brien, D. P., & Mandell, A. M. (2011). "A low mass for Mars from Jupiter's early gas-driven migration." *Nature*, 475(7355), 206-209.

**Supporting:**
- Morbidelli, A., & Crida, A. (2007). "The dynamics of Jupiter and Saturn in the gaseous protoplanetary disk." *Icarus*, 191(1), 158-171.

- Raymond, S. N., & Morbidelli, A. (2014). "The Grand Tack model: a critical review." In *Protostars and Planets VI*.

## Next Steps

1. **Run simulation** with corrected parameters
2. **Verify tack point** occurs at ~1.5 AU around t=100 kyr
3. **Check resonance** capture mechanism
4. **Validate final orbits** match Jupiter/Saturn today
5. **Compare** with Walsh et al. (2011) Figure 1

## Notes

- Original code was close but had small errors in normalization
- Main issue was migration timescale (50 vs 100 kyr)
- Type II formula factor of 2 is critical for correct migration rate
- Mass dependence ensures Saturn catches Jupiter
- These corrections align simulation with published literature
