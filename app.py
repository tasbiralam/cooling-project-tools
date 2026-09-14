import streamlit as st
import math
from pathlib import Path

st.set_page_config(page_title="Exhaust Fan Aerodynamics Calculator", page_icon="🌀", layout="centered")

st.title("🌀 Exhaust Fan Aerodynamics Calculator")
st.write(
    "An aerodynamic performance estimator for a 5-blade exhaust fan, based on "
    "real dimensions extracted from my CAD model. Built as part of a CAD + "
    "CFD design project."
)

img_path = Path(__file__).parent / "fan_render.png"
if img_path.exists():
    st.image(str(img_path), caption="Fan impeller — 5-blade design (rendered from CAD model)", width=350)

st.header("Geometry (extracted from CAD)")

g1, g2, g3 = st.columns(3)
g1.metric("Blade tip diameter", "115.7 mm")
g2.metric("Hub diameter", "36.5 mm")
g3.metric("Blade count", "5")

st.caption("These geometry values were measured directly from the CAD model. You can still adjust them below to explore other scenarios.")

st.header("Input Parameters")

col1, col2 = st.columns(2)

with col1:
    rpm = st.slider("RPM (rotation speed)", min_value=100, max_value=5000, value=1500, step=50)
    blade_radius_mm = st.slider("Blade tip radius (mm)", min_value=10, max_value=120, value=58, step=1,
                                 help="Default (58mm) matches the actual CAD model's blade tip radius.")
    num_blades = st.slider("Number of blades", min_value=2, max_value=10, value=5, step=1,
                            help="Default (5) matches the actual CAD model.")

with col2:
    air_density = st.number_input("Air density (kg/m³)", value=1.225, format="%.3f")
    air_viscosity = st.number_input("Air dynamic viscosity (Pa·s)", value=1.81e-5, format="%.2e")
    efficiency_factor = st.slider("Rough flow efficiency factor", min_value=0.1, max_value=1.0, value=0.5, step=0.05,
                                   help="Accounts for the fact that not all swept area moves air at full tip speed.")

# ---- Calculations ----
blade_radius = blade_radius_mm / 1000  # convert to meters
omega = (2 * math.pi * rpm) / 60
tip_speed = omega * blade_radius
frontal_area = math.pi * (blade_radius ** 2)
flow_rate = frontal_area * tip_speed * efficiency_factor
reynolds_number = (air_density * tip_speed * blade_radius) / air_viscosity

if reynolds_number > 4000:
    flow_regime = "Turbulent"
elif reynolds_number < 2300:
    flow_regime = "Laminar"
else:
    flow_regime = "Transitional"

# ---- Output ----
st.header("Results")

r1, r2, r3 = st.columns(3)
r1.metric("Blade Tip Speed", f"{tip_speed:.2f} m/s")
r2.metric("Estimated Flow Rate", f"{flow_rate:.4f} m³/s")
r3.metric("Reynolds Number", f"{reynolds_number:,.0f}")

st.info(f"Flow regime: **{flow_regime}**")

with st.expander("See calculation details"):
    st.latex(r"\omega = \frac{2\pi \cdot RPM}{60}")
    st.write(f"ω = {omega:.2f} rad/s")
    st.latex(r"v_{tip} = \omega \cdot r")
    st.write(f"v_tip = {tip_speed:.2f} m/s")
    st.latex(r"Q \approx A \cdot v_{tip} \cdot \eta")
    st.write(f"Q ≈ {flow_rate:.5f} m³/s (A = {frontal_area:.5f} m², η = {efficiency_factor})")
    st.latex(r"Re = \frac{\rho \cdot v_{tip} \cdot r}{\mu}")
    st.write(f"Re = {reynolds_number:,.0f}")

st.caption(
    "Note: These are simplified theoretical estimates for benchmarking against "
    "CFD simulation results, not a replacement for full CFD analysis."
)
