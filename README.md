# QCT POSCAR generator

This repository contains the `QCT_POSCAR_generator.ipynb` notebook used to build molecule/surface initial configurations for QCT workflows.

The notebook is configured so you only provide VASP outputs as inputs. It reads `vasprun.xml` for the isolated molecule and the surface trajectory, then generates the molecular vibrational `.npz` cache automatically inside the notebook.

## Project layout

```text
.
├── QCT_POSCAR_generator.ipynb
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

The notebook also generates:

- `inputs/molecule/vibrational_modes.npz`

## Generality and assumptions

The workflow is generic with respect to the molecule and surface species: nothing is hard-coded to SO2 or to a specific slab composition.

The main assumptions are:

- `inputs/molecule/vasprun.xml` must come from an isolated-molecule calculation that contains vibrational modes (`IBRION=5` or `IBRION=6`).
- `inputs/surface/vasprun.xml` must contain an ionic trajectory that ASE can read as a sequence of frames.
- The surface normal is assumed to be along `+z`, and the molecule is launched toward `-z`.
- The molecule is treated as a free molecule for the ZPE initialization, so the vibrational modes must correspond to that isolated molecule, not to the adsorbed system.
- Output POSCAR atom ordering is preserved intentionally so it stays consistent with the saved velocity arrays.

Generated POSCAR files, velocity archives, and metadata are written to:

- `outputs/qct_poscars/`

## GitHub notes

- The local virtual environment `.venv/` is ignored.
- Generated outputs are ignored, except for placeholder files that keep the folder structure in Git.
- Input directories are tracked but their contents are ignored by default, which avoids committing heavy or private VASP files accidentally.
