import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Inputs (from COMSOL run, 1000 RPM placeholder, extra coarse mesh)
Q = (0.038302 + 0.039027) / 2   # m^3/s, mean of the two boundary integrals
rho, cp = 1.2, 1005.0           # air density [kg/m^3], specific heat [J/(kg K)]

P = np.linspace(0, 500, 200)    # heat load [W]
dT = P / (rho * cp * Q)         # ideal air temperature rise [K]

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(P, dT, color="tab:blue", lw=2)
ax.axhline(10, color="gray", ls="--", lw=1)
P10 = 10 * rho * cp * Q
ax.plot([P10], [10], "o", color="tab:red")
ax.annotate(f"{P10:.0f} W at 10 K rise", (P10, 10),
            textcoords="offset points", xytext=(-110, 12))
ax.set_xlabel("Heat load P [W]")
ax.set_ylabel("Air temperature rise ΔT [K]")
ax.set_title(f"Ideal heat removal, Q = {Q*1000:.1f} L/s ({Q*2118.88:.0f} CFM)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("/mnt/user-data/outputs/heat_removal_plot.png", dpi=200)
print(f"Q = {Q:.5f} m3/s, rho*cp*Q = {rho*cp*Q:.1f} W/K, P at 10 K = {P10:.0f} W")
