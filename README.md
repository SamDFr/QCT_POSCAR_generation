# QCT POSCAR generator

This repository contains the `QCT_POSCAR_generator.ipynb` notebook used to build molecule/surface initial configurations for QCT workflows, and `MACE_quick_MD_check.ipynb` for short validation MD runs on the generated POSCAR files.

The notebook is configured so you only provide VASP outputs as inputs. It reads `vasprun.xml` for the isolated molecule and the surface trajectory, then generates the molecular vibrational `.npz` cache automatically inside the notebook.

## Project layout

```text
.
├── MACE_quick_MD_check.ipynb
├── QCT_POSCAR_generator.ipynb
├── model/
│   └── mace-mh-1.model
├── inputs/
│   ├── molecule/
│   └── surface/
├── outputs/
│   └── qct_poscars/
└── requirements.txt
```

## Setup

Create and activate the local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name qct-poscar-generator --display-name "Python (qct-poscar-generator)"
```

Then launch Jupyter from the repository root:

```bash
jupyter lab
```

## Expected input files

The notebook reads the following paths by default:

- `inputs/molecule/vasprun.xml`
- `inputs/surface/vasprun.xml`
- `model/mace-mh-1.model` for the quick MACE MD check notebook

The notebook also generates:

- `inputs/molecule/vibrational_modes.npz`

## Generality and assumptions

The workflow is generic with respect to the molecule and surface species: nothing is hard-coded to SO2 or to a specific slab composition.

The main assumptions are:

- `inputs/molecule/vasprun.xml` must come from an isolated-molecule calculation that contains vibrational modes (`IBRION=5` or `IBRION=6`).
- `inputs/surface/vasprun.xml` must contain an ionic trajectory that ASE can read as a sequence of frames.
- The surface normal is assumed to be along `+z`, and the molecule is launched toward `-z`.
- The molecule is treated as a free molecule for the ZPE initialization, so the vibrational modes must correspond to that isolated molecule, not to the adsorbed system.
- Output POSCAR atom ordering is preserved intentionally.

Generated POSCAR files and metadata are written to:

- `outputs/qct_poscars/`

The quick MACE validation notebook writes short MD trajectories and plots under:

- `outputs/mace_md_check/`

## Quick MACE MD check

`MACE_quick_MD_check.ipynb` is intended to validate one generated POSCAR quickly before larger-scale use.

It does the following:

- reads one `outputs/qct_poscars/POSCAR_*`
- reuses the positions and velocities stored in that POSCAR
- attaches the local model `model/mace-mh-1.model`
- runs a short constant-energy NVE trajectory with `VelocityVerlet`
- shows a `tqdm` progress bar during the run
- renders both static structure views and an in-notebook trajectory animation

## GitHub notes

- The local virtual environment `.venv/` is ignored.
- Generated outputs are ignored, except for placeholder files that keep the folder structure in Git.
- Input directories are tracked but their contents are ignored by default, which avoids committing heavy or private VASP files accidentally.
- The local `model/` directory contents are ignored by default, so large model binaries are not committed accidentally.
