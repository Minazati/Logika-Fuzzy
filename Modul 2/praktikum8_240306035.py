import numpy as np
import matplotlib.pyplot as plt

%matplotlib inline

# Kompatibilitas NumPy lama (<2.0) dan baru
trapz = getattr(np, "trapezoid", None) or np.trapz

# 1. FUNGSI KEANGGOTAAN
def trapesium(x, a, b, c, d):
    y = np.zeros_like(x, dtype=float)
    if a == b:
        y[x <= b] = 1
    else:
        idx = (x > a) & (x < b)
        y[idx] = (x[idx] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1
    if c == d:
        y[x >= c] = 1
    else:
        idx = (x > c) & (x < d)
        y[idx] = (d - x[idx]) / (d - c)
    return np.clip(y, 0, 1)

def segitiga(x, a, b, c):
    return trapesium(x, a, b, b, c)

# 2. VARIABEL OUTPUT RISIKO BANJIR
x = np.linspace(0, 100, 10001)
risiko_rendah = trapesium(x, 0, 0, 25, 45)
risiko_sedang = segitiga(x, 35, 55, 75)
risiko_tinggi = trapesium(x, 65, 85, 100, 100)

# 3. SIMULASI FIRING STRENGTH
alpha_rendah = 0.5
alpha_sedang = 0.8
alpha_tinggi = 0.2
print("FIRING STRENGTH")
print("Risiko Rendah :", alpha_rendah)
print("Risiko Sedang :", alpha_sedang)
print("Risiko Tinggi :", alpha_tinggi)

# 4. IMPLIKASI CLIPPING (MIN)
hasil_rendah = np.minimum(alpha_rendah, risiko_rendah)
hasil_sedang = np.minimum(alpha_sedang, risiko_sedang)
hasil_tinggi = np.minimum(alpha_tinggi, risiko_tinggi)

# 5. AGREGASI MAX
agregasi = np.maximum.reduce([hasil_rendah, hasil_sedang, hasil_tinggi])

# 6. METODE CENTROID
luas = trapz(agregasi, x)
if luas == 0:
    centroid = 0
else:
    centroid = trapz(x * agregasi, x) / luas

# 7. METODE BISECTOR
dx = np.diff(x)
luas_interval = ((agregasi[:-1] + agregasi[1:]) / 2) * dx
luas_kumulatif = np.concatenate([[0], np.cumsum(luas_interval)])
if luas == 0:
    bisector = 0
else:
    bisector = np.interp(luas / 2, luas_kumulatif, x)

# 8. METODE MOM, SOM, DAN LOM
nilai_maksimum = np.max(agregasi)
daerah_maksimum = x[np.isclose(agregasi, nilai_maksimum)]
if len(daerah_maksimum) == 0 or nilai_maksimum == 0:
    MOM = SOM = LOM = 0
else:
    SOM = np.min(daerah_maksimum)
    LOM = np.max(daerah_maksimum)
    MOM = np.mean(daerah_maksimum)

# 9. MENAMPILKAN HASIL DEFUZZIFIKASI
hasil = {"Centroid": centroid, "Bisector": bisector,
         "MOM": MOM, "SOM": SOM, "LOM": LOM}
print("\nHASIL DEFUZZIFIKASI")
print("=" * 45)
for metode, nilai in hasil.items():
    print(f"{metode:12s} = {nilai:.2f}")

# 10. MENENTUKAN KATEGORI RISIKO
def keputusan(nilai):
    if nilai < 45:
        return "Risiko Rendah"
    elif nilai < 65:
        return "Risiko Sedang"
    else:
        return "Risiko Tinggi"

print("\nTABEL PERBANDINGAN")
print("=" * 55)
print(f"{'Metode':15s} {'Nilai':12s} {'Kategori'}")
for metode, nilai in hasil.items():
    print(f"{metode:15s} {nilai:10.2f} {keputusan(nilai)}")

# 11. GRAFIK FUNGSI KEANGGOTAAN
plt.figure(figsize=(10, 5))
plt.plot(x, risiko_rendah, label="Risiko Rendah")
plt.plot(x, risiko_sedang, label="Risiko Sedang")
plt.plot(x, risiko_tinggi, label="Risiko Tinggi")
plt.title("Fungsi Keanggotaan Tingkat Risiko Banjir")
plt.xlabel("Tingkat Risiko Banjir")
plt.ylabel("Derajat Keanggotaan")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig("grafik_keanggotaan_banjir.png", dpi=200)
plt.show()

# 12. GRAFIK AGREGASI DAN DEFUZZIFIKASI
plt.figure(figsize=(11, 6))
plt.fill_between(x, agregasi, alpha=0.25, label="Daerah Agregasi")
plt.plot(x, agregasi, label="Kurva Agregasi")
for metode, nilai in hasil.items():
    plt.axvline(nilai, linestyle="--", label=f"{metode} = {nilai:.2f}")
plt.title("Perbandingan Lima Metode Defuzzifikasi")
plt.xlabel("Tingkat Risiko Banjir")
plt.ylabel("Derajat Keanggotaan")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig("grafik_defuzzifikasi_banjir.png", dpi=200)
plt.show()

# 13. GRAFIK PERBANDINGAN NILAI
plt.figure(figsize=(9, 5))
plt.bar(list(hasil.keys()), list(hasil.values()))
plt.title("Perbandingan Hasil Lima Metode")
plt.xlabel("Metode Defuzzifikasi")
plt.ylabel("Tingkat Risiko Banjir")
plt.ylim(0, 100)
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("grafik_perbandingan_banjir.png", dpi=200)
plt.show()

