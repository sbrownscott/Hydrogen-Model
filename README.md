# Peat Soil H2 Uptake Model 

The model represents a sealed chamber containing a air space above the ground and 5 soil layers. Hydrogen is transported between the chamber and soil layers and soil uptake is controlled by temperature and soil moisture. 

## Model Structure

The model has six compartments
- Chamber - height from the field inputs 
- Soil layers
    - layers 1 to 5 each set at 10 cm.

*Both number of layers and height of layers can be changed*

Hydrogen concentration is tracked through time in each compartment

**Modelling**
---
- Hydrogen transport between compartments 
- Temperature dependent uptake 
- Soil moisture dependent uptake 
- Water table dependence
- Flux calculation
- Comparison with field measurements
---

## Input Data
### Field_data_log.csv 
- Measured data from the field

Containing:
Date, Site, Chamber, Air temp, Soil temp, Water-table depth

### H2_Bind_All.csv
- H2 chamber measuresments from the field

Containing:
Date, Site, Cahmber, H2 Flux

---

## User Inputs
The model will ask for date of field measurement and the chamber number 

The model will then output the key data. It will also ask for a time step. 

## Outputs

The model produces a comparison between modelled and measured field flux.

The output file contains:

- Date
- Site
- Chamber
- Air temperature
- Soil temperature
- Water table
- Model flux
- Field flux
- Difference
- Absolute error
- Percentage error
- Ratio
- Initial surface H₂ concentration

## Current Model Performance

Using the current model version, comparison against the available field
measurements gives approximately:

- Mean bias: 2.06 μmol H₂ m⁻² s⁻¹
- MAE: 12.35 μmol H₂ m⁻² s⁻¹
- RMSE: 16.57 μmol H₂ m⁻² s⁻¹

## Files

Field_data_log.csv - Input file from Ruby 
H2_Bind_All.csv - Comparison file from Ruby
Hydrogen_Uptake_Model.py - Main model
flux_comparison.py - Plots the model error (diff between model and field) against some of the they variables

## References

Bertagni, M.B., Paulot, F. and Porporato, A., 2021. Moisture fluctuations modulate abiotic and biotic limitations of H2 soil uptake. Global Biogeochemical Cycles, 35(12), p.e2021GB006987.

Mezbahuddin, M., Grant, R.F. and Flanagan, L.B., 2016. Modeling hydrological controls on variations in peat water content, water table depth, and surface energy exchange of a boreal western Canadian fen peatland. Journal of Geophysical Research: Biogeosciences, 121(8), pp.2216-2242.

Letts, M.G., Roulet, N.T., Comer, N.T., Skarupa, M.R. and Verseghy, D.L. (2019). Parametrization of Peatland Hydraulic Properties for the Canadian Land Surface Scheme. Data, Models and Analysis, [online] pp.93–105. doi:10.4324/9781315170206-8.
