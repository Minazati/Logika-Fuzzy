# ==========================================================
# PROJEK LENGKAP: SISTEM INFERENSI FUZZY PENILAIAN BANJIR
# Metode: Sugeno Orde-0 / Weighted Average dengan Operator AND = MIN
# ==========================================================

# 1. FUNGSI KEANGGOTAAN (FUZZIFICATION)
# Fungsi Keanggotaan Kurva Segitiga (Trapezoidal/Triangular sederhana)

def fuzzify_curah_hujan(x):
    # x dalam satuan mm/jam (Rentang: 0 - 100)
    mu = {}
    # Rendah: [0, 0, 30]
    if x <= 0: mu['Rendah'] = 1.0
    elif x >= 30: mu['Rendah'] = 0.0
    else: mu['Rendah'] = (30 - x) / 30.0

    # Sedang: [10, 40, 70]
    if x <= 10 or x >= 70: mu['Sedang'] = 0.0
    elif 10 < x <= 40: mu['Sedang'] = (x - 10) / 30.0
    else: mu['Sedang'] = (70 - x) / 30.0

    # Tinggi: [50, 100, 100]
    if x <= 50: mu['Tinggi'] = 0.0
    elif x >= 100: mu['Tinggi'] = 1.0
    else: mu['Tinggi'] = (x - 50) / 50.0
    return mu

def fuzzify_tinggi_air(y):
    # y dalam satuan cm (Rentang: 0 - 200)
    mu = {}
    # Rendah: [0, 0, 60]
    if y <= 0: mu['Rendah'] = 1.0
    elif y >= 60: mu['Rendah'] = 0.0
    else: mu['Rendah'] = (60 - y) / 60.0

    # Sedang: [40, 100, 160]
    if y <= 40 or y >= 160: mu['Sedang'] = 0.0
    elif 40 < y <= 100: mu['Sedang'] = (y - 40) / 60.0
    else: mu['Sedang'] = (160 - y) / 60.0

    # Tinggi: [120, 200, 200]
    if y <= 120: mu['Tinggi'] = 0.0
    elif y >= 200: mu['Tinggi'] = 1.0
    else: mu['Tinggi'] = (y - 120) / 80.0
    return mu

# --- INPUT TEGAS (CRISP INPUT) DARI SENSOR ---
input_curah_hujan = 55.0  # mm/jam
input_tinggi_air = 130.0  # cm

print(f"=== INPUT SENSOR ===")
print(f"Curah Hujan : {input_curah_hujan} mm/jam")
print(f"Tinggi Air  : {input_tinggi_air} cm\n")

# Proses Fuzzifikasi Input
mu_ch = fuzzify_curah_hujan(input_curah_hujan)
mu_ta = fuzzify_tinggi_air(input_tinggi_air)

# 2. BASIS PENGETAHUAN & EVALUASI ATURAN (RULE BASE 3x3 DENGAN OPERATOR AND = MIN)
# Nilai konsekuen (z) untuk tingkat keparahan banjir (Skala 0 - 100)
rules_definition = [
    {"kode": "R1", "ch": "Rendah", "ta": "Rendah", "z": 25},
    {"kode": "R2", "ch": "Rendah", "ta": "Sedang", "z": 35},
    {"kode": "R3", "ch": "Rendah", "ta": "Tinggi", "z": 50},
    {"kode": "R4", "ch": "Sedang", "ta": "Rendah", "z": 40},
    {"kode": "R5", "ch": "Sedang", "ta": "Sedang", "z": 50},
    {"kode": "R6", "ch": "Sedang", "ta": "Tinggi", "z": 75},
    {"kode": "R7", "ch": "Tinggi", "ta": "Rendah", "z": 50},
    {"kode": "R8", "ch": "Tinggi", "ta": "Sedang", "z": 75},
    {"kode": "R9", "ch": "Tinggi", "ta": "Tinggi", "z": 100},
]

evaluated_rules = []

print("=== EVALUASI ATURAN (OPERATOR AND = MIN) ===")
for r in rules_definition:
    # Operator AND menggunakan fungsi MIN antara anteseden Curah Hujan dan Tinggi Air
    alpha = min(mu_ch[r["ch"]], mu_ta[r["ta"]])
    status = "Aktif" if alpha > 0.0 else "Tidak aktif"
    
    evaluated_rules.append({
        "kode": r["kode"],
        "input": f"{r['ch']} - {r['ta']}",
        "alpha": alpha,
        "z": r["z"],
        "status": status
    })
    
    print(f"Aturan {r['kode']} ({r['ch']} - {r['ta']}) -> Alpha: {alpha:.2f} | Status: {status}")

print("-" * 55)

# 3. FILTER ATURAN AKTIF
active_rules = [r for r in evaluated_rules if r["alpha"] > 0.0]
print(f"\nJumlah Aturan Aktif: {len(active_rules)}")

# 4. PROSES DEFUZZIFIKASI (METODE WEIGHTED AVERAGE)
total_numerator = sum(r["alpha"] * r["z"] for r in active_rules)
total_denominator = sum(r["alpha"] for r in active_rules)

if total_denominator > 0:
    crisp_output = total_numerator / total_denominator
else:
    crisp_output = 0.0

# 5. PENENTUAN STATUS / KATEGORI BANJIR
if crisp_output <= 40:
    kategori = "Rendah / Aman"
elif crisp_output <= 70:
    kategori = "Sedang / Waspada"
else:
    kategori = "Tinggi / Siaga"

# 6. MENAMPILKAN HASIL AKHIR
print("\n=== HASIL PERHITUNGAN DEFUZZIFIKASI ===")
print(f"Total Pembilang (Sum Alpha * Z) : {total_numerator:.2f}")
print(f"Total Penyebut (Sum Alpha)     : {total_denominator:.2f}")
print(f"Hasil Akhir (Crisp Output)     : {crisp_output:.2f}")
print(f"Status / Tingkat Banjir        : {kategori}")
