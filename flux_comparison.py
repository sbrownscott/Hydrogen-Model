"""
Compare model predictions with field measurements.

Inputs:
- Model predictions
- Field measurements
Outputs:
- Scatter plot of model vs field measurements
- Scatter plot of model error vs water table depth
- Scatter plot of model error vs soil temperature
- Key data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

# Read comparison data
data = pd.read_csv("Model_Field_Comparison.csv")
# Remove leading/trailing spaces from column names
data.columns = data.columns.str.strip()
# Convert "Date" column to datetime
data["Date"] = pd.to_datetime(data["Date"], dayfirst=True)

# Split into positive and negative differences
# Split by site and model performance
# AC = Auchencorth Moss
ac_over = data[
    (data["Site"] == "AC") &
    (data["Difference"] > 0)
]

ac_under = data[
    (data["Site"] == "AC") &
    (data["Difference"] <= 0)
]

# WH = Whim Bog
wh_over = data[
    (data["Site"] == "WH") &
    (data["Difference"] > 0)
]

wh_under = data[
    (data["Site"] == "WH") &
    (data["Difference"] <= 0)
]

plt.figure(figsize=(6,6))

# AC
plt.scatter(
    ac_under["Field Flux"],
    ac_under["Model Flux"],
    color="navy",
    label="AC - Model predicts greater uptake",
    s=80
)

plt.scatter(
    ac_over["Field Flux"],
    ac_over["Model Flux"],
    color="skyblue",
    label="AC - Model predicts smaller uptake",
    s=80
)

# WH
plt.scatter(
    wh_under["Field Flux"],
    wh_under["Model Flux"],
    color="darkorange",
    label="WH - Model predicts greater uptake",
    s=80
)

plt.scatter(
    wh_over["Field Flux"],
    wh_over["Model Flux"],
    color="moccasin",
    label="WH - Model predicts smaller uptake",
    s=80
)

# 1:1 line
minimum = min(
    data["Field Flux"].min(),
    data["Model Flux"].min()
)

maximum = max(
    data["Field Flux"].max(),
    data["Model Flux"].max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum],
    "k--",
    label="1:1 line"
)

plt.xlabel("Measured H₂ flux (nmol H$_2$ m$^{-2}$ s$^{-1}$)")
plt.ylabel("Modelled H₂ flux (nmol H$_2$ m$^{-2}$ s$^{-1}$)")

plt.title("Model vs Field H$_2$ Flux")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.axis("equal")

plt.show()

# Difference vs Water Table Depth Plot
plt.figure(figsize=(6,6))
plt.scatter(
    ac_under["Water Table"],
    ac_under["Difference"],
    color="navy",
    s=80,
    label="AC - Greater uptake"
)

plt.scatter(
    ac_over["Water Table"],
    ac_over["Difference"],
    color="skyblue",
    s=80,
    label="AC - Smaller uptake"
)

plt.scatter(
    wh_under["Water Table"],
    wh_under["Difference"],
    color="darkorange",
    s=80,
    label="WH - Greater uptake"
)

plt.scatter(
    wh_over["Water Table"],
    wh_over["Difference"],
    color="moccasin",
    s=80,
    label="WH - Smaller uptake"
)

plt.legend()
plt.axhline(0, linestyle="--")
plt.xlabel("Water Table Depth (m)")
plt.ylabel("Model - Field flux")
plt.title("Model Error vs Water Table Depth")
plt.grid(True)
plt.show()

# Difference vs Soil Temperature Plot
plt.figure(figsize=(7,5))

plt.scatter(
    ac_under["Soil Temp"],
    ac_under["Difference"],
    color="navy",
    s=80,
    label="AC - Greater uptake"
)

plt.scatter(
    ac_over["Soil Temp"],
    ac_over["Difference"],
    color="skyblue",
    s=80,
    label="AC - Smaller uptake"
)

plt.scatter(
    wh_under["Soil Temp"],
    wh_under["Difference"],
    color="darkorange",
    s=80,
    label="WH - Greater uptake"
)

plt.scatter(
    wh_over["Soil Temp"],
    wh_over["Difference"],
    color="moccasin",
    s=80,
    label="WH - Smaller uptake"
)

plt.legend()

plt.axhline(
    0,
    linestyle="--")

plt.xlabel(
    "Soil Temperature (°C)")

plt.ylabel(
    "Model - Field Flux")

plt.title(
    "Model Error vs Soil Temperature")

plt.grid(True)

plt.show()


# Mean Bias Error (MBE), Mean Absolute Error (MAE), and Root Mean Square Error (RMSE)
mbe = data["Difference"].mean()
print(f"Mean bias: {mbe:.2f}")
mae = data["Abs Error"].mean()
print(f"MAE: {mae:.2f}")
rmse = np.sqrt(
    np.mean(data["Difference"]**2)
)
print(f"RMSE: {rmse:.2f}")