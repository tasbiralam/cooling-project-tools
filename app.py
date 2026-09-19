import streamlit as st
import math
from pathlib import Path

st.set_page_config(page_title="Exhaust Fan Aerodynamics Calculator", page_icon="🌀", layout="centered")

st.title("🌀 Exhaust Fan Aerodynamics Calculator")

# ---- Two fan images, side by side ----
img_path_1 = Path(__file__).parent / "fan_render.png"
img_path_2 = Path(__file__).parent / "fan_render_2.png"

img_col1, img_col2 = st.columns(2)
with img_col1:
    if img_path_1.exists():
        st.image(str(img_path_1), caption="Fan design — view 1", use_container_width=True)
with img_col2:
    if img_path_2.exists():
        st.image(str(img_path_2), caption="Fan design — view 2", use_container_width=True)

st.subheader("Project Objective")
st.markdown(
    "This project follows a **design → predict → verify** workflow:\n\n"
    "- **Design** — Modeled a 5-blade axial exhaust fan in CAD.\n"
    "- **Predict** — Estimated the expected airflow using standard fluid "
    "mechanics formulas.\n"
    "- **Verify** — Ran a CFD simulation (COMSOL Multiphysics) on the actual "
    "CAD geometry and compared it against the prediction.\n\n"
    "The result: the hand-calculated estimate and the CFD simulation agree "
    "within a reasonable margin, validating both the design and the analysis."
)

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

# ---- CFD Validation Section ----
st.header("🔬 CFD Validation (COMSOL)")
st.write(
    "The theoretical estimate above was benchmarked against a full CFD simulation "
    "(COMSOL Multiphysics, Turbulent Flow k-ε, Frozen Rotor approach) using the "
    "actual CAD geometry."
)

cfd_col1, cfd_col2 = st.columns(2)

with cfd_col1:
    st.subheader("CFD Simulation Inputs")
    cfd_inlet_flow = st.number_input(
        "CFD flow rate — Inlet boundary (m³/s)",
        value=0.038302, format="%.6f",
        help="Surface integral of velocity (w-component) over the inlet boundary in COMSOL."
    )
    cfd_outlet_flow = st.number_input(
        "CFD flow rate — Outlet boundary (m³/s)",
        value=0.039027, format="%.6f",
        help="Surface integral of velocity (w-component) over the outlet boundary in COMSOL."
    )

cfd_avg_flow = (abs(cfd_inlet_flow) + abs(cfd_outlet_flow)) / 2
mass_conservation_error = abs(abs(cfd_inlet_flow) - abs(cfd_outlet_flow)) / cfd_avg_flow * 100
percent_diff = abs(flow_rate - cfd_avg_flow) / flow_rate * 100

with cfd_col2:
    st.subheader("Validation Summary")
    st.metric("Avg. CFD Flow Rate", f"{cfd_avg_flow:.5f} m³/s")
    st.metric("Mass Conservation Check", f"{mass_conservation_error:.2f}% diff",
              help="Difference between inlet and outlet flow rates — should be small (a few %).")
    st.metric("Hand Calc vs CFD", f"{percent_diff:.1f}% diff",
              help="Difference between the theoretical estimate above and the CFD result.")

st.subheader("Comparison Table")
comparison_data = {
    "Method": ["Hand Calculation (theoretical)", "CFD — Inlet", "CFD — Outlet", "CFD — Average"],
    "Flow Rate (m³/s)": [
        f"{flow_rate:.5f}",
        f"{abs(cfd_inlet_flow):.5f}",
        f"{abs(cfd_outlet_flow):.5f}",
        f"{cfd_avg_flow:.5f}",
    ],
}
st.table(comparison_data)

st.markdown(f"**Hand calculation and CFD agree within {percent_diff:.1f}%.** The remaining gap is expected:")
st.markdown(
    "- The hand calculation uses a simplified flow-efficiency factor\n"
    "- It assumes uniform flow across the swept area\n"
    "- The CFD result accounts for actual blade geometry, turbulence, and boundary layer effects"
)

# ---- CFD Contour Images ----
import base64

velocity_img = Path(__file__).parent / "velocity_contour.png"
pressure_img = Path(__file__).parent / "pressure_contour.png"

def img_to_base64(path):
    return base64.b64encode(path.read_bytes()).decode()

if velocity_img.exists() or pressure_img.exists():
    st.subheader("CFD Result Visuals")
    vcol, pcol = st.columns(2)
    fixed_height = 320
    box_style = (
        f"height:{fixed_height}px; display:flex; align-items:center; "
        f"justify-content:center; border:1px solid #444; border-radius:6px; "
        f"overflow:hidden; background:white;"
    )
    img_style = "max-height:100%; max-width:100%; object-fit:contain;"

    if velocity_img.exists():
        with vcol:
            b64 = img_to_base64(velocity_img)
            st.markdown(
                f'<div style="{box_style}"><img src="data:image/png;base64,{b64}" style="{img_style}"></div>',
                unsafe_allow_html=True,
            )
            st.caption("Velocity magnitude (COMSOL)")
    if pressure_img.exists():
        with pcol:
            b64 = img_to_base64(pressure_img)
            st.markdown(
                f'<div style="{box_style}"><img src="data:image/png;base64,{b64}" style="{img_style}"></div>',
                unsafe_allow_html=True,
            )
            st.caption("Pressure distribution (COMSOL)")
else:
    st.caption(
        "Add `velocity_contour.png` and `pressure_contour.png` next to this app "
        "file (same GitHub folder) to display the CFD result visuals here."
    )

st.subheader("Interpreting the Results")

st.markdown("**Velocity — highest at the blade tip**")
st.markdown(
    "- Velocity scales directly with radius: v = ω × r\n"
    "- The tip (largest r) moves fastest → highest velocity in the contour\n"
    "- Near the hub (r ≈ 0) and outside the domain, velocity drops close to zero"
)

st.markdown("**Pressure — differs across each blade face**")
st.markdown(
    "- Pressure side (front face): pushes air → higher pressure\n"
    "- Suction side (trailing face): pulls air along → lower pressure\n"
    "- This pressure difference generates thrust — the same principle as lift on an airplane wing"
)

st.caption(
    "Note: the Inlet and Outlet boundaries were set to a fixed Pressure = 0 Pa "
    "condition (a modeling choice, not a measured result), so domain-average "
    "pressure isn't meaningful here. The local pressure difference across each "
    "blade, shown above, is what reflects the fan's actual aerodynamic loading."
)
