"""
SOIL H2 MODEL
Version 13

Inputs
- Field_data_log.csv: Field data log
- H2_Bind_All.csv: H2 binding data
- Model parameters: Model parameters

Outputs
- Modelled flux 

Units
- Concentrations: ppb
- Fluxes: micro mol H2 m-2 s-1
- Time: seconds
- Depth: metres
- Temperature: °C

Document structure
- Model parameters
- Model equations
- Model outputs
"""

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import linregress


# Read field data
field_data = pd.read_csv("Field_data_log.csv")

# Remove empty Excel columns
field_data = field_data.loc[:,~field_data.columns.str.contains("^Unnamed")]

# Convert date column
field_data["Date"] = pd.to_datetime(field_data["Date"], dayfirst=True)

# Read field flux data
flux_data = pd.read_csv("H2_Bind_All.csv")
flux_data = flux_data.loc[:, ~flux_data.columns.str.contains("^Unnamed")]
# Convert date column
flux_data["Date"] = pd.to_datetime(flux_data["Date"], dayfirst=True).dt.normalize()

# Prompt user for date and chamber number
date_input = input("Enter date (DD/MM/YYYY): ")
chamber_input = int(input("Enter chamber number: "))

# Convert date input to datetime object and normalize to remove time component
date_input = pd.to_datetime(date_input, dayfirst=True).normalize()
field_data["Date"] = pd.to_datetime(field_data["Date"], dayfirst=True).dt.normalize()

# Find matching field measurement
measurement = field_data[
    (field_data["Date"].dt.date == date_input.date()) &
    (field_data["Chamber"].astype(int) == chamber_input)
]

if measurement.empty:
    print("No matching chamber/date found")
    exit()


# Extract the first row for each chamber/date combination
# This assumes that there is only one match.
row = measurement.iloc[0]

# Find matching flux measurement
flux_measurement = flux_data[
    (flux_data["Date"] == date_input) &
    (flux_data["Chamber"].astype(int) == chamber_input)
]

if flux_measurement.empty:
    print("No matching field flux found.")
    field_flux = np.nan
    field_flux_min = np.nan
    field_flux_max = np.nan
else:
    flux_row = flux_measurement.iloc[0]
    field_flux = float(flux_row["H2_Flux"])
    field_flux_min = float(flux_row["H2_Min"])
    field_flux_max = float(flux_row["H2_Max"])

# Find the model parameters for the selected date and chamber

# Getting air temperature for the selected date 
air_measurement = field_data[
    (field_data["Date"].dt.date == date_input.date()) &
    (field_data["Chamber"].astype(int) == 1)
]
if air_measurement.empty:
    raise ValueError(
        "No air temperature found for the selected date."
    )

# Taking the measurements from the CSV file and converting them to float for calculations
air_temperature = float(air_measurement.iloc[0]["Air Temp"])
soil_temperature = float(row["T_ave"])
water_table_depth = float(row["Actual_WT"])

# Chamber height measurements
H1 = float(row["H1"])
H2 = float(row["H2"])
H3 = float(row["H3"])
H4 = float(row["H4"])

height_average = float(row["Height average"])
extension = float(row["Extension"])
Havg_cm = float(row["Havg_cm"])
chamber_volume = float(row["Chamber V"])

# Output the selected field measurement
print("\nSelected field measurement")
print("---------------------------")
print(f"Date : {date_input.date()}")
print(f"Chamber : {chamber_input}")
print(f"Air temperature : {air_temperature:.2f} °C")
print(f"Soil temperature : {soil_temperature:.2f} °C")
print(f"Water table : {water_table_depth:.2f} cm")
print(f"Chamber volume : {chamber_volume:.5f} m³")
print(f"Average height : {height_average:.2f} cm")

if not np.isnan(field_flux):
    print(f"Measured H₂ flux : {field_flux:.2f} nmol H₂ m⁻² s⁻¹")
    print(f"Flux range       : {field_flux_min:.2f} to {field_flux_max:.2f} nmol H₂ m⁻² s⁻¹")


# THE MODEL

# Time step and simulation time
# The user is given suggestions for both inputs
dt = float(input("Enter time step (seconds) - recommended 1.0: "))
simulation_time = float(input("Enter simulation time (seconds) - recommended 300: "))
time = np.arange(0, simulation_time + dt, dt) # Create time array from 0 to simulation_time with step dt

# Depth and layer thickness
# Values can be adjusted based on the soil profile
total_depth = 0.50      # metres
layer_thickness = 0.10  # metres
n_soil = int(total_depth / layer_thickness)
n_compartments = n_soil + 1 # Adding 1 for the chamber compartment

# Transport coefficients
## Values have been adjusted, but need more work

# Chamber to soil surface
k_chamber = 0.020

# Soil layer exchange
k_soil = 0.010

# Biological uptake
## Values have been adjusted, but need more work
km = 0.0007 # having this between 0.0005 and 0.0007 seems to be best.
print(f"km (maximum microbial H2 uptake rate): {km:.5f} ppb/s")

# Temperature response
# Based on graph from Bertagni et al. (2021)
# Could make finer resolution
temperature_points = np.array(
    [
        -20,
        -10,
        0,
        5,
        10,
        15,
        20,
        25,
        30,
        40,
        60,
        80,
        100
    ]
)

h_points = np.array(
    [
        0.00,
        0.05,
        0.30,
        0.50,
        0.70,
        0.90,
        0.98,
        1.00,
        1.00,
        0.95,
        0.50,
        0.10,
        0.00
    ]
)

temperature_history = np.full(
    len(time),
    soil_temperature
)

# Water table depth
# CSV value is cm below surface
water_table_depth = (water_table_depth / 100) # Convert to metres

print()
print(f"Water table depth used in model: {water_table_depth:.2f} m")


# Peat parameters 
# 3 cateogories of peat: fibric, hemic, sapric
# Based on Campbell equations and parameters from Letts et al. 2000
peat_parameters = [
    # Shallow peat
    {
        "top_depth": 0.00,
        "bottom_depth": 0.10,
        "peat_type": "Fibric",
        "b": 2.7,
        "theta_p": 0.93,
        # Suction at saturation, in cm of water
        "psi_s_cm": 1.03
    },

    # Middle peat
    {
        "top_depth": 0.10,
        "bottom_depth": 0.30,
        "peat_type": "Hemic",
        "b": 6.1,
        "theta_p": 0.88,
        # Suction at saturation, in cm of water
        "psi_s_cm": 1.02
    },

    # Deep peat
    {
        "top_depth": 0.30,
        "bottom_depth": 0.50,
        "peat_type": "Sapric",
        "b": 12.0,
        "theta_p": 0.83,
        # Suction at saturation, in cm of water
        "psi_s_cm": 1.01
    }
]

def get_peat_parameters(depth):
    """
    Get the peat parameters for a given depth.
    """
    for params in peat_parameters:

        if (params["top_depth"] <= depth < params["bottom_depth"]):
            return params
    return peat_parameters[-1]


# Print peat parameters for each layer

print("\nCampbell peat parameterisation")
print("-------------------------------")

for params in peat_parameters:
    print(
        f"{params['top_depth']:.2f}-"
        f"{params['bottom_depth']:.2f} m : "
        f"{params['peat_type']} peat, "
        f"b = {params['b']:.2f}, "
        f"theta_p = {params['theta_p']:.2f}, "
        f"psi_s = {params['psi_s_cm']:.2f} cm"
    )

# Saturation profile

def saturation_profile(depth):
    """
    Calculate the saturation at a given depth based on the water table depth and peat parameters.
    """
    # Distance from the water table
    height_above_wt = (water_table_depth - depth)

    # At or below the water table, saturation is 1.0
    if height_above_wt <= 0:
        return 1.0

    # Above the water table, use Campbell equation to calculate saturation
    params = get_peat_parameters(depth)
    b = params["b"]
    psi_s_cm = params["psi_s_cm"]

    # Convert height above water table (m) to suction in cm of water
    psi_cm = (height_above_wt * 100.0)

    # Campbell equation
    # s = (psi / psi_s)^(-1/b)
    s = (psi_cm / psi_s_cm) ** (-1.0 / b)

    # Take saturation values between 0 and 1
    s = np.clip(
        s,
        0.0,
        1.0
    )
    return s


# Calculate average saturation for each soil layer

# Set up an empty list to store the average saturation for each soil layer
soil_saturation = []

# Number of points used to average within each layer
n_points = 100

for i in range(n_soil):
    layer_top = (i * layer_thickness)

    layer_bottom = ((i + 1) * layer_thickness)

    depths = np.linspace(
        layer_top,
        layer_bottom,
        n_points
    )

    saturation_values = []

    for depth in depths:
        saturation_values.append(saturation_profile(depth))
    average_saturation = np.mean(saturation_values)
    soil_saturation.append(average_saturation)

# Moisture response function
s_ws = 0.20
s_opt = 0.80
s_up = 1.00

beta1 = 0.40
beta2 = beta1 * (1 - s_opt) / (s_opt - s_ws)

def raw_beta(s):
    """
    Calculate the raw beta function for a given saturation.
    """
    if s <= s_ws:
        return 0.0
    if s >= s_up:
        return 0.0
    return ((s - s_ws) ** beta1 * (s_up - s) ** beta2)

S = np.linspace(s_ws, s_up, 500)
N = max(raw_beta(x) for x in S)

def moisture_factor(s):
    """
    Calculate the moisture factor for a given saturation.
    """
    if s <= s_ws:
        return 0.0
    if s >= s_up:
        return 0.0
    return raw_beta(s) / N

soil_moisture_factor = []

for s in soil_saturation:
    soil_moisture_factor.append(moisture_factor(s))

# Print soil moisture profile

print("\nSoil moisture profile")
print("----------------------")

for i in range(n_soil):
    layer_midpoint = ((i + 0.5) * layer_thickness)

    params = get_peat_parameters(layer_midpoint)

    print(
        f"Layer {i+1}: "
        f"Depth = {layer_midpoint:.2f} m, "
        f"AverageSaturation = {soil_saturation[i]:.3f}, "
        f"Moisture factor = {soil_moisture_factor[i]:.3f}, "
        f"b = {params['b']:.2f}, "
        f"theta_p = {params['theta_p']:.2f}, "
        f"psi_s = {params['psi_s_cm']:.2f} cm"
    )

# Chamber dimensions
chamber_radius = 0.19 # m
chamber_area = (np.pi*chamber_radius**2) # m^2

# Print chamber dimensions
print()
print("Chamber dimensions")
print("---------------------------")

print(f"H1 : {H1:.2f} cm")
print(f"H2 : {H2:.2f} cm")
print(f"H3 : {H3:.2f} cm")
print(f"H4 : {H4:.2f} cm")
print(f"Extension : {extension:.2f} cm")
print(f"Area : {chamber_area:.4f} m²")
print(f"Volume : {chamber_volume:.5f} m³")

# Microbial distribution

# Fraction of each soil layer containing active microbes
# determined by water table depth
# 1 = fully above water table
# 0 = fully below water table

# Setting up an array to hold the microbial fraction for each compartment
microbial_fraction = np.zeros(n_compartments) 

for i in range(1, n_compartments):
    layer_top = ((i - 1)*layer_thickness)
    layer_bottom = (i*layer_thickness)

    # Layer entirely above water table
    if water_table_depth >= layer_bottom:
        microbial_fraction[i] = 1.0

    # Layer entirely below water table
    elif water_table_depth <= layer_top:

        microbial_fraction[i] = 0.0

    # Water table crosses layer
    else:
        microbial_fraction[i] = (water_table_depth - layer_top) / layer_thickness

print()
print("Microbial activity")
print("---------------------------")
for i in range(1, n_compartments):
    top = int((i-1)*layer_thickness*100)
    bottom = int(i*layer_thickness*100)
    print(f"{top:2d}-{bottom:2d} cm : {microbial_fraction[i]:.2f}")

# Inital surface H2 concentration
surface_H2 = float(
    input("Enter initial surface H2 concentration (ppb) (suggested input of 550): "))

# Setting the initial H2 concentration in all compartments to the surface H2 concentration
H2 = np.full(n_compartments, surface_H2)

# Storage for H2 concentrations over time
history = np.zeros((len(time), n_compartments))
history[0] = H2

# Setting up an array to hold the temperature response for each time step
temperature_response = np.zeros(len(time)) 
temperature_response[0] = np.interp(
    temperature_history[0],
    temperature_points,
    h_points
)

# Time loop for the model
for t in range(1, len(time)):

    new = H2.copy()
    # Chamber to surface exchange
    flux = (k_chamber*(H2[0]-H2[1])) * dt

    new[0] -= flux
    new[1] += flux

    # Soil layer exchange
    for i in range(1, n_compartments-1):
        flux = (k_soil*(H2[i]-H2[i+1])) * dt

        new[i] -= flux
        new[i+1] += flux

    # Biological uptake
    hT = np.interp(
        temperature_history[t],
        temperature_points,
        h_points
    )

    for i in range(1, n_compartments):
        fS = soil_moisture_factor[i-1]
        # Main uptake equation from Bertagni et al. (2021) with temperature and moisture factors applied
        loss = (hT * fS * km * microbial_fraction[i] * new[i] * dt)
        new[i] -= loss

    # Prevent negative concentrations
    new = np.maximum(
        new,
        0
    )
    H2 = new
    history[t] = H2
    temperature_response[t] = hT

# Flux calculation
rho_air = 1.2        # kg m-3
# Convert ppb to kg H2 per m3 air
H2_mass = (history[:,0]*1e-9*rho_air)

# Rate of concentration change
# Use first 5 minutes for chamber flux
fit_time = time[:]
fit_H2 = history[:,0]

slope, intercept, r, p, stderr = linregress(fit_time,fit_H2)

# ppb/s to kg/m3/s
dCdt = (slope*1e-9*rho_air)
flux = (dCdt*(chamber_volume/chamber_area))

# Convert kg H2 m-2 s-1 to nmol H2 m-2 s-1

flux_nmol = (flux / (2.016e-3) * 1e9)

print(
    f"H2 Flux: {flux_nmol:.2f} nmol H2 m-2 s-1"
)

print("\nFlux Comparison")
print("----------------")
print(f"Model flux : {flux_nmol:.2f} nmol H₂ m⁻² s⁻¹")

if not np.isnan(field_flux):
    print(f"Field flux : {field_flux:.2f} nmol H₂ m⁻² s⁻¹")
    difference = flux_nmol - field_flux
    print(f"Difference : {difference:.2f} nmol H₂ m⁻² s⁻¹")

# Output the final concentrations in each compartment
print()
print("Final concentrations")
print("---------------------------")

labels = ["Chamber"]

for i in range(n_soil):
    top = int(i * layer_thickness * 100)
    bottom = int((i+1) * layer_thickness * 100)
    labels.append(f"{top}-{bottom} cm")

for name,value in zip(labels,H2):
    print(f"{name:10s}: {value:.2f} ppb")

# Chamber observations
number_of_profiles = 6
sample_times = np.linspace(
    0,
    simulation_time,
    number_of_profiles,
    dtype=int
)

print()
print("Predicted chamber samples")
print("---------------------------")

for t in sample_times:
    print(f"{t/60:5.1f} min : {history[t,0]:.2f} ppb")

# PLOT 1
# CHAMBER CONCENTRATION

plt.figure(figsize=(8,5))
plt.plot(
    time/60,
    history[:,0],
    linewidth=2
)
plt.xlabel("Time (minutes)")
plt.ylabel("Chamber H₂ (ppb)")
plt.title("Predicted Chamber Concentration")
plt.grid(True)
plt.show()

# PLOT 2
# SOIL PROFILES

depth = np.arange(
    layer_thickness/2,
    total_depth,
    layer_thickness
)

plt.figure(
    figsize=(6,6))


for t in sample_times:
    plt.plot(
        history[t,1:],
        depth,
        marker="o",
        label=f"{t/60:.1f} min"
    )
plt.gca().invert_yaxis()
plt.xlabel(
    "Soil H₂ (ppb)")
plt.ylabel(
    "Depth (m)")
plt.title(
    "Soil H₂ Profiles")
plt.grid(True)
plt.legend()
plt.show()


# Saving the data
output_file = "Model_Field_Comparison.csv"

results = {
    "Site": row["Site"],
    "Date": date_input.strftime("%d/%m/%Y"),
    "Chamber": chamber_input,
    "Air Temp": air_temperature,
    "Soil Temp": soil_temperature,
    "Water Table": water_table_depth,
    "Model Flux": flux_nmol,
    "Field Flux": field_flux,
    "Difference": flux_nmol - field_flux,
    "Abs Error": abs(flux_nmol - field_flux),
    "Percent Error": abs(flux_nmol - field_flux) / abs(field_flux) * 100,
    "Ratio": abs(flux_nmol) / abs(field_flux),
    "Initial Surface H2": surface_H2
}

new_row = pd.DataFrame([results])

if os.path.exists(output_file):

    # Read existing results
    existing = pd.read_csv(output_file)

    print(existing.columns.tolist())

    # Remove spaces from headers
    existing.columns = existing.columns.str.strip()
    # Remove any existing row with the same date and chamber
    existing = existing[
        ~(
            (existing["Date"] == results["Date"]) &
            (existing["Chamber"] == results["Chamber"])
        )
    ]

    # Add the new result
    updated = pd.concat([existing, new_row], ignore_index=True)

else:

    updated = new_row

# Sort by date then chamber
updated["Date"] = pd.to_datetime(updated["Date"], dayfirst=True)

updated = updated.sort_values(
    ["Date", "Chamber"]
)

updated["Date"] = updated["Date"].dt.strftime("%d/%m/%Y")

# Round numerical columns
updated = updated.round({
    "Air Temp": 2,
    "Soil Temp": 2,
    "Water Table": 2,
    "Model Flux": 2,
    "Field Flux": 2,
    "Difference": 2,
    "Abs Error": 2,
    "Percent Error": 2,
    "Ratio": 2
})

# Save
updated.to_csv(
    output_file,
    index=False
)

print(f"\nResults saved to {output_file}")