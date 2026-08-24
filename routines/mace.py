"""MACE-backed isolated-molecule preparation for the QCT notebook."""

from pathlib import Path
from typing import Optional

import numpy as np
from ase.atoms import Atoms
from ase.build import molecule
from ase.optimize import BFGS
from ase.vibrations import Vibrations


def build_mace_calculator(model_path: Path, *, device: str = "cpu",
                          default_dtype: str = "float64", head: Optional[str] = None,
                          dispersion: bool = False):
    """Load a local MACE model.

    ``head=None`` lets MACE use the model default and therefore works for
    single-head models.  Supply a head name only for a multi-head model when
    you deliberately want to choose a particular head.
    """
    try:
        from mace.calculators import mace_mp
    except ImportError as exc:
        raise ImportError("mace-torch is required; install the repository requirements.") from exc
    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"MACE model not found: {model_path}")
    kwargs = {
        "model": str(model_path.resolve()),
        "device": device,
        "default_dtype": default_dtype,
        "dispersion": dispersion,
    }
    if head is not None:
        kwargs["head"] = head
    return mace_mp(**kwargs)


def build_isolated_molecule(formula: str) -> Atoms:
    """Build ASE's standard gas-phase geometry for a molecule name/formula.

    For example, ``"SO2"``, ``"CO2"`` and ``"H2O"`` require no input file.
    ASE only has reference geometries for a finite set of molecules; for an
    unknown formula, use the ``file`` input mode with a user-provided geometry.
    """
    try:
        return molecule(str(formula))
    except (KeyError, ValueError) as exc:
        raise ValueError(
            f"ASE does not provide a built-in geometry for {formula!r}. "
            "Use MOLECULE_SOURCE['input_mode'] = 'file' and provide molecule_structure."
        ) from exc


def optimize_and_calculate_modes(atoms: Atoms, model_path: Path, *,
                                 fmax_eV_A: float = 1.0e-3, max_steps: int = 500,
                                 delta_A: float = 0.01, device: str = "cpu",
                                 default_dtype: str = "float64", head: Optional[str] = None,
                                 dispersion: bool = False) -> tuple[Atoms, np.ndarray, np.ndarray]:
    """Optimize a free molecule and return its full 3N harmonic MACE modes.

    ``eigvecs_cart`` matches the convention consumed by the QCT notebook:
    dividing it by sqrt(mass) produces ASE's mass-weighted displacement modes.
    """
    molecule = atoms.copy()
    molecule.set_pbc(False)
    molecule.set_cell(np.zeros((3, 3)))
    molecule.calc = build_mace_calculator(model_path, device=device,
                                          default_dtype=default_dtype, head=head,
                                          dispersion=dispersion)
    optimizer = BFGS(molecule, logfile=None)
    optimizer.run(fmax=fmax_eV_A, steps=max_steps)
    if np.max(np.linalg.norm(molecule.get_forces(), axis=1)) > fmax_eV_A:
        raise RuntimeError("MACE optimization did not converge within max_steps.")

    vib_name = str(Path("outputs") / "mace_vibrations" / "isolated_molecule")
    Path(vib_name).parent.mkdir(parents=True, exist_ok=True)
    vibrations = Vibrations(molecule, name=vib_name, delta=delta_A)
    try:
        vibrations.run()
        vib_data = vibrations.get_vibrations()
        frequencies = np.asarray(vib_data.get_frequencies(), dtype=complex)
        modes_mass_weighted = np.asarray(vib_data.get_modes(all_atoms=True), dtype=float)
    finally:
        vibrations.clean()

    if np.any(np.abs(frequencies.imag) > 1.0e-8):
        print("Warning: MACE Hessian has imaginary modes; inspect the optimized molecule.")
    freqs_cm1 = np.abs(frequencies)
    order = np.argsort(freqs_cm1)
    freqs_cm1 = np.asarray(freqs_cm1[order], dtype=float)
    modes_mass_weighted = modes_mass_weighted[order]
    masses = np.sqrt(molecule.get_masses())[None, :, None]
    eigvecs_cart = modes_mass_weighted * masses
    return molecule, freqs_cm1, eigvecs_cart
