"""Regenerate the demo line and species tables in ``fastapi_slap2/data``.

The demo dataset is a small, hand-picked list of well-known atomic and
molecular lines. Values are representative (taken from NIST ASD / CDMS /
standard references and rounded); they are meant to exercise the protocol,
not to be used for science.

InChI / InChIKey / mass / formula values are computed with RDKit, which is
only needed to run this script, not to run the service:

    pip install rdkit
    python scripts/build_demo_data.py
"""

import csv
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

DATA_DIR = Path(__file__).resolve().parent.parent / "fastapi_slap2" / "data"

C_LIGHT = 299_792_458.0  # m / s
HC_J_CM = 1.98644586e-23  # J per cm^-1

NIST = ("10.18434/T4W30F", "https://physics.nist.gov/PhysRefData/ASD/lines_form.html")
CDMS = ("10.1016/j.molstruc.2005.01.027", "https://cdms.astro.uni-koeln.de/")
H2_REF = ("10.1051/0004-6361/201834636", "https://doi.org/10.1051/0004-6361/201834636")

# key: (species_name, SMILES, species_type)
SPECIES = {
    "H": ("H", "[H]", "atom"),
    "He": ("He", "[He]", "atom"),
    "He+": ("He", "[He+]", "atom"),
    "C+": ("C", "[C+]", "atom"),
    "C+3": ("C", "[C+3]", "atom"),
    "N+": ("N", "[N+]", "atom"),
    "O": ("O", "[O]", "atom"),
    "O+2": ("O", "[O+2]", "atom"),
    "Na": ("Na", "[Na]", "atom"),
    "Mg+": ("Mg", "[Mg+]", "atom"),
    "Ca+": ("Ca", "[Ca+]", "atom"),
    "Fe": ("Fe", "[Fe]", "atom"),
    "Fe+": ("Fe", "[Fe+]", "atom"),
    "CO": ("CO", "[C-]#[O+]", "molecule"),
    "13CO": ("13CO", "[13C-]#[O+]", "molecule"),
    "C18O": ("C18O", "[C-]#[18O+]", "molecule"),
    "H2": ("H2", "[H][H]", "molecule"),
    "H2O": ("H2O", "O", "molecule"),
    "OH": ("OH", "[OH]", "molecule"),
    "NH3": ("NH3", "N", "molecule"),
    "HCN": ("HCN", "C#N", "molecule"),
    "HCO+": ("HCO+", "[CH]#[O+]", "molecule"),
    "CS": ("CS", "[C-]#[S+]", "molecule"),
    "SiO": ("SiO", "[Si-]#[O+]", "molecule"),
    "CH3OH": ("CH3OH", "CO", "molecule"),
}

# Lines given by vacuum wavelength (m):
# (species key, wavelength, wavelength error, title, lower desc, upper desc, A (s^-1), E_lower (cm^-1), reference)
WL_LINES = [
    ("H", 1.2156701e-7, 1e-14, "H I Lyman alpha", "1s 2S 1/2", "2p 2P 3/2", 4.6986e8, 0.0, NIST),
    ("H", 1.0257223e-7, 1e-14, "H I Lyman beta", "1s 2S 1/2", "3p 2P 3/2", 5.5751e7, 0.0, NIST),
    ("H", 9.725368e-8, 1e-14, "H I Lyman gamma", "1s 2S 1/2", "4p 2P 3/2", 1.2785e7, 0.0, NIST),
    ("H", 6.56460e-7, 1e-13, "H I Balmer alpha", "n=2", "n=3", 4.4101e7, 82259.0, NIST),
    ("H", 4.862708e-7, 1e-13, "H I Balmer beta", "n=2", "n=4", 8.4193e6, 82259.0, NIST),
    ("H", 4.341692e-7, 1e-13, "H I Balmer gamma", "n=2", "n=5", 2.5304e6, 82259.0, NIST),
    ("H", 4.102892e-7, 1e-13, "H I Balmer delta", "n=2", "n=6", 9.7320e5, 82259.0, NIST),
    ("H", 1.875613e-6, 1e-12, "H I Paschen alpha", "n=3", "n=4", 8.9860e6, 97492.2, NIST),
    ("H", 0.21106114054, 1e-12, "H I 21 cm", "1s 2S 1/2 F=0", "1s 2S 1/2 F=1", 2.8843e-15, 0.0, NIST),
    ("He", 1.083330e-6, 1e-12, "He I 10833 A", "1s2s 3S 1", "1s2p 3P", 1.0216e7, 159855.97, NIST),
    ("He", 5.877250e-7, 1e-13, "He I 5877.25 A", "1s2p 3P", "1s3d 3D", 7.0703e7, 169086.8, NIST),
    ("He+", 1.640420e-7, 1e-13, "He II 1640.42 A", "n=2", "n=3", 1.0360e8, 329179.3, NIST),
    ("He+", 4.687020e-7, 1e-13, "He II 4687.02 A", "n=3", "n=4", None, 390140.8, NIST),
    ("C+", 1.334532e-7, 1e-13, "C II 1334.53 A", "2s2 2p 2P 1/2", "2s 2p2 2D 3/2", 2.41e8, 0.0, NIST),
    ("C+", 1.577409e-4, 1e-10, "[C II] 157.7 um", "2s2 2p 2P 1/2", "2s2 2p 2P 3/2", 2.29e-6, 0.0, NIST),
    ("C+3", 1.548187e-7, 1e-13, "C IV 1548.19 A", "1s2 2s 2S 1/2", "1s2 2p 2P 3/2", 2.65e8, 0.0, NIST),
    ("C+3", 1.550772e-7, 1e-13, "C IV 1550.77 A", "1s2 2s 2S 1/2", "1s2 2p 2P 1/2", 2.64e8, 0.0, NIST),
    ("N+", 6.549861e-7, 1e-13, "[N II] 6549.86 A", "2s2 2p2 3P 1", "2s2 2p2 1D 2", 9.84e-4, 48.7, NIST),
    ("N+", 6.585273e-7, 1e-13, "[N II] 6585.27 A", "2s2 2p2 3P 2", "2s2 2p2 1D 2", 2.92e-3, 130.8, NIST),
    ("O", 6.302046e-7, 1e-13, "[O I] 6302.05 A", "2s2 2p4 3P 2", "2s2 2p4 1D 2", 5.63e-3, 0.0, NIST),
    ("O", 6.3183705e-5, 1e-11, "[O I] 63.18 um", "2s2 2p4 3P 2", "2s2 2p4 3P 1", 8.91e-5, 0.0, NIST),
    ("O+2", 4.960295e-7, 1e-13, "[O III] 4960.30 A", "2s2 2p2 3P 1", "2s2 2p2 1D 2", 6.21e-3, 113.18, NIST),
    ("O+2", 5.008240e-7, 1e-13, "[O III] 5008.24 A", "2s2 2p2 3P 2", "2s2 2p2 1D 2", 1.81e-2, 306.17, NIST),
    ("Na", 5.891583e-7, 1e-14, "Na I D2", "3s 2S 1/2", "3p 2P 3/2", 6.16e7, 0.0, NIST),
    ("Na", 5.897558e-7, 1e-14, "Na I D1", "3s 2S 1/2", "3p 2P 1/2", 6.14e7, 0.0, NIST),
    ("Mg+", 2.796352e-7, 1e-14, "Mg II 2796.35 A", "3s 2S 1/2", "3p 2P 3/2", 2.60e8, 0.0, NIST),
    ("Mg+", 2.803531e-7, 1e-14, "Mg II 2803.53 A", "3s 2S 1/2", "3p 2P 1/2", 2.57e8, 0.0, NIST),
    ("Ca+", 3.934777e-7, 1e-14, "Ca II K", "4s 2S 1/2", "4p 2P 3/2", 1.47e8, 0.0, NIST),
    ("Ca+", 3.969591e-7, 1e-14, "Ca II H", "4s 2S 1/2", "4p 2P 1/2", 1.40e8, 0.0, NIST),
    ("Fe", 3.720993e-7, 1e-13, "Fe I 3720.99 A", "3d6 4s2 a5D 4", "3d6 4s 4p z5F 5", 1.62e7, 0.0, NIST),
    ("Fe", 3.861006e-7, 1e-13, "Fe I 3861.01 A", "3d6 4s2 a5D 4", "3d6 4s 4p z5D 4", 9.69e6, 0.0, NIST),
    ("Fe+", 2.382765e-7, 1e-13, "Fe II 2382.77 A", "3d6 4s a6D 9/2", "3d6 4p z6F 11/2", 3.13e8, 0.0, NIST),
    ("Fe+", 2.600173e-7, 1e-13, "Fe II 2600.17 A", "3d6 4s a6D 9/2", "3d6 4p z6D 9/2", 2.35e8, 0.0, NIST),
    ("H2", 2.82188e-5, 1e-10, "H2 0-0 S(0)", "v=0, J=0", "v=0, J=2", 2.94e-11, 0.0, H2_REF),
    ("H2", 1.70348e-5, 1e-10, "H2 0-0 S(1)", "v=0, J=1", "v=0, J=3", 4.76e-10, 118.5, H2_REF),
    ("H2", 1.22786e-5, 1e-10, "H2 0-0 S(2)", "v=0, J=2", "v=0, J=4", 2.75e-9, 354.4, H2_REF),
    ("H2", 2.121834e-6, 1e-11, "H2 1-0 S(1)", "v=0, J=1", "v=1, J=3", 3.47e-7, 118.5, H2_REF),
    ("H2", 2.223290e-6, 1e-11, "H2 1-0 S(0)", "v=0, J=0", "v=1, J=2", 2.53e-7, 0.0, H2_REF),
]

# Lines given by rest frequency (Hz), converted to vacuum wavelength:
# (species key, frequency, frequency error, title, lower desc, upper desc, A (s^-1), E_lower (cm^-1), reference)
FREQ_LINES = [
    ("CO", 115.2712018e9, 5e2, "CO 115.27 GHz", "v=0, J=0", "v=0, J=1", 7.203e-8, 0.0, CDMS),
    ("CO", 230.5380000e9, 5e2, "CO 230.54 GHz", "v=0, J=1", "v=0, J=2", 6.910e-7, 3.845, CDMS),
    ("CO", 345.7959899e9, 5e2, "CO 345.80 GHz", "v=0, J=2", "v=0, J=3", 2.497e-6, 11.535, CDMS),
    ("13CO", 110.2013543e9, 1e3, "13CO 110.20 GHz", "v=0, J=0", "v=0, J=1", 6.333e-8, 0.0, CDMS),
    ("13CO", 220.3986842e9, 1e3, "13CO 220.40 GHz", "v=0, J=1", "v=0, J=2", 6.038e-7, 3.676, CDMS),
    ("C18O", 109.7821734e9, 1e3, "C18O 109.78 GHz", "v=0, J=0", "v=0, J=1", 6.266e-8, 0.0, CDMS),
    ("C18O", 219.5603541e9, 1e3, "C18O 219.56 GHz", "v=0, J=1", "v=0, J=2", 6.011e-7, 3.662, CDMS),
    ("H2O", 22.235080e9, 1e3, "H2O 22.24 GHz", "6(1,6)", "5(2,3)", 1.99e-9, 446.5, CDMS),
    ("H2O", 183.310087e9, 1e3, "H2O 183.31 GHz", "2(2,0)", "3(1,3)", 3.63e-6, 136.16, CDMS),
    ("H2O", 556.9359877e9, 1e3, "H2O 556.94 GHz", "1(0,1)", "1(1,0)", 3.46e-3, 23.79, CDMS),
    ("OH", 1.6653590e9, 1e2, "OH 1665 MHz", "X2Pi3/2, J=3/2, F=1, +", "X2Pi3/2, J=3/2, F=1, -", 7.18e-11, None, CDMS),
    ("OH", 1.6673590e9, 1e2, "OH 1667 MHz", "X2Pi3/2, J=3/2, F=2, +", "X2Pi3/2, J=3/2, F=2, -", 7.78e-11, None, CDMS),
    ("NH3", 23.6944955e9, 1e2, "NH3 (1,1)", "J=1, K=1, a", "J=1, K=1, s", 1.67e-7, 16.17, CDMS),
    ("HCN", 88.6318470e9, 1e3, "HCN 1-0", "v=0, J=0", "v=0, J=1", 2.41e-5, 0.0, CDMS),
    ("HCO+", 89.1885247e9, 1e3, "HCO+ 1-0", "v=0, J=0", "v=0, J=1", 4.19e-5, 0.0, CDMS),
    ("CS", 97.9809533e9, 1e3, "CS 2-1", "v=0, J=1", "v=0, J=2", 1.68e-5, 1.634, CDMS),
    ("SiO", 86.8469985e9, 1e3, "SiO v=0 2-1", "v=0, J=1", "v=0, J=2", 2.93e-5, 1.448, CDMS),
    ("CH3OH", 96.741375e9, 1e3, "CH3OH 2(0)-1(0) A+", "1(0) A+", "2(0) A+", 3.41e-6, None, CDMS),
]

LINE_COLUMNS = [
    "vacuum_wavelength",
    "vacuum_wavelength_error",
    "line_title",
    "species_name",
    "species_mass",
    "inchikey",
    "inchi",
    "ion_charge",
    "lower_level_description",
    "upper_level_description",
    "einsteina",
    "lower_level_energy",
    "upper_level_energy",
    "reference_doi",
    "reference_uri",
]

SPECIES_COLUMNS = [
    "species_name",
    "ion_charge",
    "inchikey",
    "inchi",
    "stoichiometric_formula",
    "species_type",
    "number_of_atoms",
    "species_mass",
]


def hill_formula(mol) -> str:
    """Charge-free, isotope-free Hill formula (e.g. CO, H2O, CH4O)."""
    plain = Chem.Mol(mol)
    for atom in plain.GetAtoms():
        atom.SetIsotope(0)
        atom.SetFormalCharge(0)
    return rdMolDescriptors.CalcMolFormula(plain)


def species_record(key: str) -> dict:
    name, smiles, species_type = SPECIES[key]
    mol = Chem.MolFromSmiles(smiles)
    return {
        "species_name": name,
        "ion_charge": Chem.GetFormalCharge(mol),
        "inchikey": Chem.MolToInchiKey(mol),
        "inchi": Chem.MolToInchi(mol),
        "stoichiometric_formula": hill_formula(mol),
        "species_type": species_type,
        "number_of_atoms": Chem.AddHs(mol).GetNumAtoms(),
        "species_mass": f"{Descriptors.MolWt(mol):.4f}",
    }


def fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def line_record(key, wavelength, wavelength_err, title, lower, upper, einstein_a, e_lower_cm, ref) -> dict:
    species = species_record(key)
    if e_lower_cm is None:
        e_lower = e_upper = None
    else:
        e_lower = e_lower_cm * HC_J_CM
        e_upper = (e_lower_cm + 1.0 / (wavelength * 100.0)) * HC_J_CM
    return {
        "vacuum_wavelength": wavelength,
        "vacuum_wavelength_error": wavelength_err,
        "line_title": title,
        "species_name": species["species_name"],
        "species_mass": species["species_mass"],
        "inchikey": species["inchikey"],
        "inchi": species["inchi"],
        "ion_charge": species["ion_charge"],
        "lower_level_description": lower,
        "upper_level_description": upper,
        "einsteina": einstein_a,
        "lower_level_energy": e_lower,
        "upper_level_energy": e_upper,
        "reference_doi": ref[0],
        "reference_uri": ref[1],
    }


def main():
    lines = [line_record(*row) for row in WL_LINES]
    for key, freq, freq_err, *rest in FREQ_LINES:
        wavelength = C_LIGHT / freq
        lines.append(line_record(key, wavelength, wavelength * freq_err / freq, *rest))
    lines.sort(key=lambda r: r["vacuum_wavelength"])

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "lines.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LINE_COLUMNS)
        writer.writeheader()
        for row in lines:
            writer.writerow({k: fmt(v) for k, v in row.items()})

    with open(DATA_DIR / "species.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SPECIES_COLUMNS)
        writer.writeheader()
        for key in SPECIES:
            writer.writerow({k: fmt(v) for k, v in species_record(key).items()})

    print(f"Wrote {len(lines)} lines and {len(SPECIES)} species to {DATA_DIR}")


if __name__ == "__main__":
    main()
