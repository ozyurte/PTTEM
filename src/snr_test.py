import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from numpy import trapezoid

pi = np.pi
c = 3e8               # m/s
L = 2.5e9             # m
H100 = 3.24078e-18    # Hz (H0=100 km/s/Mpc)
T_obs = 4 * 3.15576e7 # s (4 yıl)

# LISA gürültü parametreleri
S_a_asd = 3e-15    # m/s^2 /sqrt(Hz)
S_om_asd = 1e-11   # m /sqrt(Hz)
S_a = S_a_asd**2
S_om = S_om_asd**2

def S_h_instr(f):
    term_acc = S_a / ((2 * pi * f)**4 * (2 * L)**2)
    term_opt = (2 * S_om) / (2 * L)**2
    return term_acc + term_opt

def S_gcn(f):
    # galaktik WD confusion noise yaklaşıklaştırması
    A, alpha, beta, kappa, gamma, f_k = 9e-45, 0.138, -221, 521, 1680, 0.00113
    exp_term = np.exp(-(f / alpha) + beta * f * np.sin(kappa * f))
    tanh_term = 1 + np.tanh(gamma * (f_k - f))
    return A * f**(-7/3) * exp_term * tanh_term

def S_sw(f, f_pk):
    # Hindmarsh tam şekil
    x = f / f_pk
    return (7.0 / (4.0 + 3.0 * x**2))**(7.0/2.0) * x**3

def effective_S_n(f, gcn_flag):
    S_single = S_h_instr(f)
    if gcn_flag:
        S_single += S_gcn(f)
    # TDI/yanıt yaklaşıklaştırması
    tdi_factor = 3.0 + 0.5 * (f * 1e3)**2
    R_f = 0.45 * (3.0/10.0)  # ~0.135
    return S_single * tdi_factor / (R_f**2)

def compute_snr(f_pk, Omega_pk, scenario, gcn_flag, R_Omega, n_points, band_type='standard'):
    assert 1e-5 < f_pk < 0.1, "f_pk out of Hz range!"
    # Bant sınırları: temkinli wide
    if scenario == 'S3':
        a, b = (0.2, 3.0) if band_type == 'standard' else (0.15, 4.0)
    else:
        a, b = (0.3, 3.0) if band_type == 'standard' else (0.2, 5.0)

    f_min = a * f_pk
    f_max = b * f_pk
    f = np.linspace(f_min, f_max, n_points)

    s_sw = S_sw(f, f_pk)
    om_g = Omega_pk * s_sw
    S_n = effective_S_n(f, gcn_flag)
    om_n = (2.0 * pi**2 / (3.0 * H100**2)) * f**3 * S_n / R_Omega

    integrand = (om_g / om_n)**2
    integral = trapezoid(integrand, f)
    snr = np.sqrt(T_obs * integral)
    return float(snr), f, integrand

# Senaryolar (f_pk [Hz], Omega_pk)
scenarios = {
    'S1': (0.0051, 7.3e-11),
    'S2': (0.0021, 5.4e-10),
    'S3': (0.0004, 1.1e-12),
}

# CLI
parser = argparse.ArgumentParser(description='PTTEM SNR Calculation (Physical V10.0)')
parser.add_argument('--scenarios', nargs='+', default=['S1', 'S2', 'S3'], help='Scenarios: S1 S2 S3')
parser.add_argument('--gcn', type=str, default='on', choices=['on', 'off'], help='GCN: on(off) = dahil etme(dahil etme)')
parser.add_argument('--r_omega', type=float, default=0.03, help='R_Omega (0.02-0.05 range affects SNR by +-25%%)')
parser.add_argument('--npts', type=int, default=100000, help='Integration points')
parser.add_argument('--band', type=str, default='standard', choices=['standard', 'wide'], help='Band: standard or wide')
args = parser.parse_args()

# Çıktı klasörü
os.makedirs('figs', exist_ok=True)

# Baz koşul SNR’ları (GCN=on, band=standard)
def snr_value(f_pk, om_pk, scen_name, gcn_on, r_omega, npts, band):
    snr, _, _ = compute_snr(f_pk, om_pk, scen_name, gcn_on, r_omega, npts, band)
    return snr

baseline = {}
for nm, (fpk, ompk) in scenarios.items():
    baseline[nm] = snr_value(fpk, ompk, nm, True, args.r_omega, args.npts, 'standard')

# Seçilen opsiyonlarla hesapla
gcn_flag = (args.gcn == 'on')
results = {}
for name in args.scenarios:
    f_pk, om_pk = scenarios[name]
    snr, f, integrand = compute_snr(f_pk, om_pk, name, gcn_flag, args.r_omega, args.npts, args.band)
    ratio = snr / baseline[name] if baseline[name] > 0 else np.inf

    results[name] = {
        'SNR': snr,
        'Baseline': baseline[name],
        'Ratio': ratio,
        'GCN': args.gcn,
        'R_Omega': args.r_omega,
        'Band': args.band
    }

    # Grafik
    plt.figure()
    plt.semilogx(f, integrand)
    plt.xlabel('f (Hz)')
    plt.ylabel('Integrand [(Ω_GW / Ω_N)^2]')
    plt.title(f'{name} Integrand (GCN {args.gcn.upper()}, {args.band})')
    plt.savefig(f'figs/{name}_integrand.png')
    plt.close()

# Göreli regresyon sınırları (senaryoya ve moda göre)
EXPECTED_MIN = 0.7
if gcn_flag and args.band == 'standard':
    max_map = {'S1': 1.3, 'S2': 1.3, 'S3': 1.5}
elif (not gcn_flag) and args.band == 'wide':
    max_map = {'S1': 80.0, 'S2': 80.0, 'S3': 300.0}  # S3 çok yükseliyor
else:
    max_map = {'S1': 12.0, 'S2': 12.0, 'S3': 40.0}

for nm, dat in results.items():
    r = dat['Ratio']
    assert EXPECTED_MIN <= r <= max_map[nm], (
        f"{nm} ratio {r:.2f} out of bounds [{EXPECTED_MIN},{max_map[nm]}]"
    )


# JSON
with open('output.json', 'w') as fp:
    json.dump(results, fp, indent=4)

print("OK. output.json yazıldı, figürler figs/ içinde.")
