import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ==============================================================================
# 1. INISIALISASI MODEL FUZZY MAMDANI
# ==============================================================================
def create_flood_decision_system():
    # Semesta Pembicaraan (Universe of Discourse)
    curah_hujan = ctrl.Antecedent(np.arange(0, 201, 1), 'curah_hujan')
    tinggi_air  = ctrl.Antecedent(np.arange(0, 251, 1), 'tinggi_air')
    peringatan  = ctrl.Consequent(np.arange(0, 101, 1), 'peringatan')

    # Fungsi Keanggotaan Input: Curah Hujan (mm/hari)
    curah_hujan['Rendah'] = fuzz.trapmf(curah_hujan.universe, [0, 0, 40, 80])
    curah_hujan['Sedang'] = fuzz.trimf(curah_hujan.universe, [50, 100, 150])
    curah_hujan['Tinggi'] = fuzz.trapmf(curah_hujan.universe, [120, 160, 200, 200])

    # Fungsi Keanggotaan Input: Tinggi Muka Air (cm)
    tinggi_air['Rendah'] = fuzz.trapmf(tinggi_air.universe, [0, 0, 60, 110])
    tinggi_air['Siaga']  = fuzz.trimf(tinggi_air.universe, [80, 130, 180])
    tinggi_air['Bahaya'] = fuzz.trapmf(tinggi_air.universe, [150, 190, 250, 250])

    # Fungsi Keanggotaan Output: Tingkat Peringatan (Indeks 0 - 100)
    peringatan['Aman']    = fuzz.trapmf(peringatan.universe, [0, 0, 25, 45])
    peringatan['Waspada'] = fuzz.trimf(peringatan.universe, [35, 55, 75])
    peringatan['Bahaya']  = fuzz.trapmf(peringatan.universe, [65, 80, 100, 100])

    # Basis Aturan (9 Aturan Mamdani)
    r1 = ctrl.Rule(curah_hujan['Rendah'] & tinggi_air['Rendah'], peringatan['Aman'])
    r2 = ctrl.Rule(curah_hujan['Rendah'] & tinggi_air['Siaga'],  peringatan['Aman'])
    r3 = ctrl.Rule(curah_hujan['Rendah'] & tinggi_air['Bahaya'], peringatan['Waspada'])
    r4 = ctrl.Rule(curah_hujan['Sedang'] & tinggi_air['Rendah'], peringatan['Aman'])
    r5 = ctrl.Rule(curah_hujan['Sedang'] & tinggi_air['Siaga'],  peringatan['Waspada'])
    r6 = ctrl.Rule(curah_hujan['Sedang'] & tinggi_air['Bahaya'], peringatan['Bahaya'])
    r7 = ctrl.Rule(curah_hujan['Tinggi'] & tinggi_air['Rendah'], peringatan['Waspada'])
    r8 = ctrl.Rule(curah_hujan['Tinggi'] & tinggi_air['Siaga'],  peringatan['Bahaya'])
    r9 = ctrl.Rule(curah_hujan['Tinggi'] & tinggi_air['Bahaya'], peringatan['Bahaya'])

    # Sistem Kontrol & Engine Simulasi
    flood_ctrl = ctrl.ControlSystem([r1, r2, r3, r4, r5, r6, r7, r8, r9])
    return ctrl.ControlSystemSimulation(flood_ctrl)

# ==============================================================================
# 2. FUNGSI KLASIFIKASI STATUS KEPUTUSAN
# ==============================================================================
def interpret_output(skor):
    if skor < 40.0:
        return "AMAN", "Kondisi normal. Pantau berkala sensor ketinggian air."
    elif skor <= 70.0:
        return "WASPADA", "Siaga potensi genangan/luapan air. Siapkan peralatan darurat."
    else:
        return "BAHAYA", "Darurat banjir! Aktifkan sirine dan lakukan evakuasi warga."

# ==============================================================================
# 3. PENGUJIAN 5 SKENARIO KASUS NYATA (OTOMATIS)
# ==============================================================================
def test_5_scenarios(simulasi):
    skenario_list = [
        ("Kondisi Normal / Kemarau", 20.0, 40.0),
        ("Anomali Air Kiriman Hulu", 25.0, 215.0),
        ("Musim Hujan Reguler (Transisi)", 95.0, 130.0),
        ("Hujan Lebat Baru Mulai", 175.0, 50.0),
        ("Bencana Cuaca Ekstrem", 185.0, 230.0)
    ]

    print("\n" + "=" * 80)
    print(" TABEL HASIL PENGUJIAN 5 SKENARIO KASUS NYATA")
    print("=" * 80)
    header = f"{'No':<3} | {'Nama Skenario':<30} | {'Hujan (mm)':<10} | {'Air (cm)':<8} | {'Indeks Crisp':<12} | {'Status':<10}"
    print(header)
    print("-" * 80)

    for idx, (nama, hujan, air) in enumerate(skenario_list, start=1):
        simulasi.input['curah_hujan'] = hujan
        simulasi.input['tinggi_air']  = air
        simulasi.compute()
        hasil = simulasi.output['peringatan']
        status, _ = interpret_output(hasil)
        print(f"{idx:<3} | {nama:<30} | {hujan:<10.1f} | {air:<8.1f} | {hasil:<12.2f} | {status:<10}")

    print("=" * 80 + "\n")

# ==============================================================================
# 4. VISUALISASI DECISION SURFACE PLOT 3D
# ==============================================================================
def plot_decision_surface(simulasi, titik_uji=None):
    print("Sedang merender Decision Surface Plot 3D...")
    x_vals = np.linspace(0, 200, 30)
    y_vals = np.linspace(0, 250, 30)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            simulasi.input['curah_hujan'] = X[i, j]
            simulasi.input['tinggi_air']  = Y[i, j]
            simulasi.compute()
            Z[i, j] = simulasi.output['peringatan']

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(X, Y, Z, cmap='coolwarm', edgecolor='k', linewidth=0.2, alpha=0.85)

    # Plot titik input pengguna jika ada
    if titik_uji:
        ux, uy, uz = titik_uji
        ax.scatter(ux, uy, uz, color='black', s=80, label=f'Input Uji ({ux:.1f}, {uy:.1f}, {uz:.1f})', zorder=5)
        ax.legend(loc='upper left')

    ax.set_title('Decision Surface Plot 3D - Sistem Penilaian Risiko Banjir (Mamdani)', fontsize=12, pad=15)
    ax.set_xlabel('Curah Hujan (mm)', fontsize=10, labelpad=10)
    ax.set_ylabel('Tinggi Muka Air (cm)', fontsize=10, labelpad=10)
    ax.set_zlabel('Indeks Peringatan Banjir (0-100)', fontsize=10, labelpad=10)
    ax.view_init(elev=28, azim=225)

    cbar = fig.colorbar(surf, ax=ax, shrink=0.55, aspect=8)
    cbar.set_label('Indeks Peringatan')
    plt.tight_layout()
    plt.show()

# ==============================================================================
# 5. PROGRAM UTAMA (MAIN EXECUTION)
# ==============================================================================
def main():
    simulasi = create_flood_decision_system()

    print("=" * 65)
    print(" SISTEM PENGAMBIL KEPUTUSAN PENILAIAN RISIKO BANJIR (MAMDANI)")
    print("=" * 65)

    # A. Input Nilai Crisp dari Pengguna
    try:
        val_hujan = float(input(">> Masukkan Curah Hujan (0 - 200 mm)    : "))
        val_air   = float(input(">> Masukkan Tinggi Muka Air (0 - 250 cm): "))
    except ValueError:
        print("\n[Error] Masukan harus berupa nilai angka numerik!")
        return

    # Batasi ke semesta pembicaraan (clamping)
    val_hujan_clamped = max(0.0, min(200.0, val_hujan))
    val_air_clamped   = max(0.0, min(250.0, val_air))

    # B. Proses Inferensi Mamdani & Defuzzifikasi Centroid
    simulasi.input['curah_hujan'] = val_hujan_clamped
    simulasi.input['tinggi_air']  = val_air_clamped
    simulasi.compute()
    skor_hasil = simulasi.output['peringatan']
    status, saran = interpret_output(skor_hasil)

    # C. Output Keputusan
    print("\n" + "-" * 50)
    print(" HASIL EVALUASI KEPUTUSAN FUZZY")
    print("-" * 50)
    print(f" Curah Hujan Input        : {val_hujan_clamped:.2f} mm")
    print(f" Tinggi Muka Air Input    : {val_air_clamped:.2f} cm")
    print(f" Nilai Crisp Output       : {skor_hasil:.2f} / 100")
    print(f" Status Keputusan         : {status}")
    print(f" Rekomendasi Lapangan     : {saran}")
    print("-" * 50)

    # D. Jalankan dan Tampilkan Pengujian 5 Skenario
    test_5_scenarios(simulasi)

    # E. Tampilkan Grafik 3D Permukaan Keputusan
    plot_decision_surface(simulasi, titik_uji=(val_hujan_clamped, val_air_clamped, skor_hasil))

if __name__ == "__main__":
    main()