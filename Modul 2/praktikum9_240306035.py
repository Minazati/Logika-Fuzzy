import matplotlib.pyplot as plt

# ---------- Grafik 1: Fungsi keanggotaan input ----------
xh = np.linspace(0, 200, 400)
xt = np.linspace(0, 350, 400)

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(xh, [ramp_down(x, 50, 150) for x in xh], label="Rendah")
ax[0].plot(xh, [ramp_up(x, 50, 150) for x in xh], label="Tinggi")
ax[0].set(title="Keanggotaan Curah Hujan", xlabel="mm/hari", ylabel="μ")
ax[1].plot(xt, [ramp_down(x, 100, 250) for x in xt], label="Rendah")
ax[1].plot(xt, [ramp_up(x, 100, 250) for x in xt], label="Tinggi")
ax[1].set(title="Keanggotaan Tinggi Muka Air (TMA)", xlabel="cm", ylabel="μ")
for a in ax:
    a.legend(); a.grid(alpha=0.3)
plt.tight_layout(); plt.show()

# ---------- Grafik 2: Perbandingan Sugeno vs Tsukamoto ----------
nama = [d[0] for d in data]
hasil_s = [sugeno0(h, t) for _, h, t in data]
hasil_k = [tsukamoto(h, t) for _, h, t in data]

x = np.arange(len(data)); w = 0.38
fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, hasil_s, w, label="Sugeno Orde 0")
b2 = ax.bar(x + w/2, hasil_k, w, label="Tsukamoto")
ax.bar_label(b1, fmt="%.1f", padding=2)
ax.bar_label(b2, fmt="%.1f", padding=2)
ax.axhline(35, ls="--", c="gray", lw=0.8)   # batas Rendah/Sedang
ax.axhline(65, ls="--", c="gray", lw=0.8)   # batas Sedang/Tinggi
ax.set_xticks(x)
ax.set_xticklabels([f"{n}\n(H={h}, TMA={t})" for n, h, t in data])
ax.set(ylabel="Tingkat risiko banjir", ylim=(0, 105),
       title="Perbandingan Output Sugeno vs Tsukamoto")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.show()

# ---------- Grafik 3: Permukaan output (heatmap) ----------
H = np.linspace(0, 200, 60)
T = np.linspace(0, 350, 60)
Zs = np.array([[sugeno0(h, t) for h in H] for t in T])
Zk = np.array([[tsukamoto(h, t) for h in H] for t in T])

fig, ax = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for a, Z, judul in zip(ax, [Zs, Zk], ["Sugeno Orde 0", "Tsukamoto"]):
    im = a.contourf(H, T, Z, levels=20, cmap="RdYlGn_r", vmin=0, vmax=100)
    a.set(title=f"Permukaan Output {judul}", xlabel="Curah hujan (mm/hari)")
    # tandai 5 titik uji
    for n, h, t in data:
        a.plot(h, t, "ko", ms=4)
        a.annotate(n[-1], (h, t), textcoords="offset points", xytext=(5, 5))
ax[0].set_ylabel("TMA (cm)")
fig.colorbar(im, ax=ax, label="Risiko banjir")
plt.show()
