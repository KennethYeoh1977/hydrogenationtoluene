import streamlit as st
import matplotlib.pyplot as plt
import math

# Function to calculate temperature factor using the Arrhenius equation
def temperature_factor(T):
    """Arrhenius equation for temperature sensitivity."""
    A = 1e5  # Arbitrary pre-exponential factor
    Ea = 70000  # Activation energy in J/mol (example value 70000 J for hydrogenation)
    R = 8.314  # Gas constant in J/(mol·K)
    T_k = T + 273.15  # Convert °C to Kelvin
    return A * math.exp(-Ea / (R * T_k))

# Function to calculate pressure factor based on equilibrium constant
def pressure_factor(P):
    """Pressure sensitivity based on equilibrium constant."""
    P_standard = 1  # Standard pressure in bar
    return P / P_standard if P > 0 else 1  # Favor higher pressures

# Streamlit App Title
st.title("Toluene to MCH Hydrogenation Simulation")

# User Inputs with constraints and type consistency
target_mch_yield = st.number_input("Enter the target cumulative yield of MCH in kg", value=95000.0, min_value=1.0)  # Target cumulative yield of MCH in kg
toluene_flow_rate = st.number_input("Enter the increment of toluene added each hour in kg", value=60000.0, min_value=1.0)  # Increment of toluene added each hour in kg
temperature = st.number_input("Enter the temperature in °C for the catalyst", value=200.0, min_value=10.0, max_value=900.0)  # Set reaction temperature in °C
pressure = st.number_input("Enter the pressure, barg (assumed constant)", value=10.0, min_value=0.1)  # Assume constant pressure for simplicity

# Define 'max_yield_ratio' if it is missing
try:
    max_yield_ratio
except NameError:
    max_yield_ratio = 1.0  # Example default value

# Selectivity, Conversion Rates, and Recycling Rate
selectivity = st.number_input("Enter the selectivity rate (0-1)", value=0.95, min_value=0.0, max_value=1.0)  # Selectivity rate (95%)
conversion_rate = st.number_input("Enter the conversion rate (0-1)", value=0.9, min_value=0.0, max_value=1.0)  # Conversion rate (90%)

# Option for Recycling Toggle
recycling_enabled = st.radio("Enable Recycling?", options=["Yes", "No"], index=0)
recycling_rate = st.number_input("Enter the recycling rate (0-1)", value=0.85, min_value=0.0, max_value=1.0) if recycling_enabled == "Yes" else 0

# Hydrogen-to-Toluene Ratio Input
hydrogen_to_toluene_ratio = st.number_input("Enter the hydrogen-to-toluene ratio (3:1 to 5:1)", value=4.0, min_value=3.0, max_value=5.0)

# Yield factors and constants for cumulative yield function
a = hydrogen_to_toluene_ratio * max_yield_ratio * selectivity * conversion_rate  # Yield factor
b = 0.0  # Constant for initial yield or inefficiencies

# Initialize variables
cumulative_mch_yield = 0  # Cumulative yield of MCH
total_toluene_used = 0  # Total toluene used in kg
remaining_toluene = toluene_flow_rate * (1 - recycling_rate) if recycling_enabled == "Yes" else 0
iterations = 0  # Count of iterations

# Lists for storing iteration data
toluene_usage = []
mch_yields = []
remaining_toluene_list = []
efficiency_list = []

# Define the MCH yield function with temperature, pressure, and hydrogen-to-toluene ratio effects
def simulate_yield_with_hydrogen(toluene_used, T, P, hydrogen_ratio):
    """Simulate yield considering temperature, pressure, and hydrogen-to-toluene ratio."""
    temp_effect = temperature_factor(T)
    pressure_effect = pressure_factor(P)
    # Hydrogen effect: Ensure hydrogen ratio is sufficient for complete conversion
    hydrogen_effect = 8.0 if 3.0 <= hydrogen_ratio <= 5.0 else 0.8  # Penalize if outside typical range
    yield_with_factors = a * toluene_used * temp_effect * pressure_effect * hydrogen_effect + b
    return yield_with_factors

# Iterative loop to reach target cumulative MCH yield
while cumulative_mch_yield < target_mch_yield:
    iterations += 1
    
    # Calculate current total toluene used
    total_toluene_used += toluene_flow_rate
    
    # Calculate MCH yield based on the defined relationship
    mch_yield_current = simulate_yield_with_hydrogen(total_toluene_used, temperature, pressure, hydrogen_to_toluene_ratio)
    
    # Update cumulative MCH yield considering conversion and selectivity
    effective_conversion_rate = selectivity * conversion_rate
    mch_yield_current *= effective_conversion_rate
    
    # Update cumulative values and remaining toluene after recycling (if enabled)
    cumulative_mch_yield += mch_yield_current
    
    if recycling_enabled == "Yes":
        remaining_toluene += toluene_flow_rate * (1 - recycling_rate)
    
    # Calculate efficiency for this iteration
    efficiency_current = mch_yield_current / (toluene_flow_rate * max_yield_ratio) if toluene_flow_rate > 0 else 0
    
    # Append data for plotting and tracking
    toluene_usage.append(total_toluene_used)
    mch_yields.append(cumulative_mch_yield)
    
    if recycling_enabled == "Yes":
        remaining_toluene_list.append(remaining_toluene)
    
    efficiency_list.append(efficiency_current)

# Plotting results using Matplotlib and displaying them in Streamlit using `st.pyplot`
plt.figure(figsize=(12, 8))

# Cumulative MCH Yield Plot
plt.subplot(3, 1, 1)
plt.plot(toluene_usage, mch_yields, marker="o", color="blue", label="Cumulative MCH Yield")
plt.axhline(y=target_mch_yield, color="red", linestyle="--", label="Target MCH Yield")
plt.xlabel("Total Toluene Used (kg)")
plt.ylabel("Cumulative MCH Yield (kg)")
plt.title(f"Cumulative MCH Yield vs. Total Toluene Usage ({'With Recycling' if recycling_enabled == 'Yes' else 'No Recycling'})")
plt.legend()
plt.grid(True)

# Remaining Toluene Plot
plt.subplot(3, 1, 2)
if recycling_enabled == "Yes":
    plt.plot(toluene_usage, remaining_toluene_list, marker="o", color="green", label="Remaining Toluene")
    plt.xlabel("Total Toluene Used (kg)")
    plt.ylabel("Remaining Toluene (kg)")
    plt.title("Remaining Toluene vs. Total Toluene Usage")
    plt.legend()
    plt.grid(True)
else:
    plt.text(0.5, 0.5, "No Recycling Enabled", horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
    plt.axis('off')

# Efficiency Plot
plt.subplot(3, 1, 3)
plt.plot(toluene_usage, efficiency_list, marker="o", color="orange", label="Yield Efficiency")
plt.xlabel("Total Toluene Used (kg)")
plt.ylabel("Yield Efficiency (kg MCH/kg Toluene)")
plt.title(f"Yield Efficiency vs. Total Toluene Usage ({'With Recycling' if recycling_enabled == 'Yes' else 'No Recycling'})")
plt.legend()
plt.grid(True)

plt.tight_layout()

# Display the plots in Streamlit using Matplotlib's `pyplot` interface.
st.pyplot(plt)
