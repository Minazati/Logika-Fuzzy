import numpy as np
import matplotlib.pyplot as plt

# =====================================
# 1. FUNGSI KEANGGOTAAN
# =====================================

def trapmf(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

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


def trimf(x, a, b, c):
    return trapmf(x, a, b, b, c)


# =====================================
# 2. KELAS FUZZY INFERENCE SYSTEM
# =====================================

class FuzzyInferenceSystem:

    def __init__(self):
        self.inputs = {}
        self.output = None
        self.rules = []
        self.last_rules = []
        self.last_aggregation = None

    # Menambahkan variabel input
    def add_input_variable(self, name, universe, mf_dict):
        self.inputs[name] = {
            "universe": universe,
            "mf": mf_dict
        }

    # Menambahkan variabel output
    def set_output_variable(self, name, universe, mf_dict):
        self.output = {
            "name": name,
            "universe": universe,
            "mf": mf_dict
        }

    # Menambahkan aturan fuzzy
    def add_rule(self, rule_tuple):
        self.rules.append(rule_tuple)

    # Menghitung hasil fuzzy
    def compute(self, input_values_dict):

        # A. FUZZIFIKASI
        fuzzifikasi = {}

        for name, value in input_values_dict.items():
            data = self.inputs[name]
            fuzzifikasi[name] = {}

            for label, mf in data["mf"].items():
                fuzzifikasi[name][label] = np.interp(
                    value, data["universe"], mf
                )

        # B. EVALUASI DAN AGREGASI
        u = self.output["universe"]
        agregasi = np.zeros_like(u)
        aturan_aktif = []

        for i, rule in enumerate(self.rules, start=1):

            var1, mf1, var2, mf2, hasil = rule

            nilai1 = fuzzifikasi[var1][mf1]
            nilai2 = fuzzifikasi[var2][mf2]

            # Firing strength menggunakan MIN
            alpha = min(nilai1, nilai2)

            if alpha > 0:
                aturan_aktif.append((i, mf1, mf2, hasil, alpha))

                # Implikasi Clipping MIN
                kurva = np.minimum(alpha, self.output["mf"][hasil])

                # Agregasi MAX
                agregasi = np.maximum(agregasi, kurva)

        # C. DEFUZZIFIKASI CENTROID
        pembilang = np.sum(u * agregasi)
        penyebut = np.sum(agregasi)

        if penyebut == 0:
            # Fallback: tidak ada aturan aktif, pakai titik tengah semesta
            crisp_output = (u[0] + u[-1]) / 2
        else:
            crisp_output = pembilang / penyebut

        self.last_rules = aturan_aktif
        self.last_aggregation = agregasi

        # Mengembalikan nilai crisp output
        return crisp_output


# =====================================
# 3. MEMBUAT VARIABEL INPUT
# =====================================

fis = FuzzyInferenceSystem()

# Curah hujan (mm/hari)
u_hujan = np.linspace(0, 300, 601)

fis.add_input_variable(
    "CurahHujan",
    u_hujan,
    {
        "Rendah": trapmf(u_hujan, 0, 0, 50, 100),
        "Sedang": trapmf(u_hujan, 50, 100, 150, 200),
        "Tinggi": trapmf(u_hujan, 150, 200, 300, 300)
    }
)

# Tinggi muka air sungai (cm)
u_air = np.linspace(0, 400, 801)

fis.add_input_variable(
    "TinggiAir",
    u_air,
    {
        "Normal": trapmf(u_air, 0, 0, 100, 200),
        "Waspada": trapmf(u_air, 100, 200, 250, 300),
        "Bahaya": trapmf(u_air, 250, 300, 400, 400)
    }
)


# =====================================
# 4. MEMBUAT VARIABEL OUTPUT
# =====================================

u_risiko = np.linspace(0, 100, 1001)

fis.set_output_variable(
    "Risiko",
    u_risiko,
    {
        "Rendah": trapmf(u_risiko, 0, 0, 25, 50),
        "Sedang": trimf(u_risiko, 25, 50, 75),
        "Tinggi": trapmf(u_risiko, 50, 75, 100, 100)
    }
)


# =====================================
# 5. MEMBUAT 9 ATURAN FUZZY
# =====================================

aturan = [
    ("CurahHujan", "Rendah", "TinggiAir", "Normal",  "Rendah"),
    ("CurahHujan", "Rendah", "TinggiAir", "Waspada", "Rendah"),
    ("CurahHujan", "Rendah", "TinggiAir", "Bahaya",  "Sedang"),

    ("CurahHujan", "Sedang", "TinggiAir", "Normal",  "Rendah"),
    ("CurahHujan", "Sedang", "TinggiAir", "Waspada", "Sedang"),
    ("CurahHujan", "Sedang", "TinggiAir", "Bahaya",  "Tinggi"),

    ("CurahHujan", "Tinggi", "TinggiAir", "Normal",  "Sedang"),
    ("CurahHujan", "Tinggi", "TinggiAir", "Waspada", "Tinggi"),
    ("CurahHujan", "Tinggi", "TinggiAir", "Bahaya",  "Tinggi")
]

for rule in aturan:
    fis.add_rule(rule)


# =====================================
# 6. PENGUJIAN 3 KASUS
# =====================================

kasus = [
    ("Kasus 1", 70, 120),
    ("Kasus 2", 120, 190),
    ("Kasus 3", 270, 340)
]

print("SISTEM PENILAIAN RISIKO BANJIR")

hasil_semua = []

for nama, hujan, air in kasus:

    print("\n================================")
    print(nama)
    print("Curah Hujan:", hujan, "mm/hari")
    print("Tinggi Muka Air:", air, "cm")

    hasil = fis.compute({"CurahHujan": hujan, "TinggiAir": air})

    print("\nATURAN YANG AKTIF:")
    for no, p, b, output, alpha in fis.last_rules:
        print(f"R{no}: {p} AND {b} THEN {output}")
        print(f"Firing Strength = {alpha:.2f}")

    print("\nHASIL DEFUZZIFIKASI:")
    print(f"Nilai Risiko = {hasil:.2f}")

    if hasil < 40:
        keputusan = "RISIKO RENDAH"
    elif hasil <= 60:
        keputusan = "RISIKO SEDANG"
    else:
        keputusan = "RISIKO TINGGI"

    print("Keputusan:", keputusan)
    hasil_semua.append((nama, hujan, air, hasil, keputusan))

    # Menampilkan grafik
    plt.figure(figsize=(8, 4))
    plt.plot(u_risiko, fis.last_aggregation, label="Hasil Agregasi")
    plt.axvline(hasil, linestyle="--", label=f"Centroid = {hasil:.2f}")
    plt.title("Grafik " + nama)
    plt.xlabel("Nilai Risiko Banjir")
    plt.ylabel("Derajat Keanggotaan")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(nama.replace(" ", "_") + ".png", dpi=300)
    plt.show()


# =====================================
# 7. RINGKASAN HASIL
# =====================================

print("\n================================")
print("RINGKASAN HASIL PENGUJIAN")

for nama, h, a, hasil, keputusan in hasil_semua:
    print(
        f"{nama}: Hujan={h} mm, Air={a} cm, "
        f"Output={hasil:.2f}, Keputusan={keputusan}"
    )
