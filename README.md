# Communication-Aware Radio Resource Allocation for Warehouse AMRs

This project builds a custom indoor radio-propagation scene with Sionna RT and
uses its channel fingerprint to plan paths and subcarrier allocation for two
autonomous mobile robots (AMRs). The analysis compares baseline, bandwidth-
optimized, communication-aware, and joint path/allocation strategies.

## Contents

Preparation. [Warehouse Scene Construction](#preparation-warehouse-scene-construction)

1. [Channel Fingerprint Map Generation](#1-channel-fingerprint-map-generation)
2. [Multi-AMR Path Planning and Subcarrier Allocation](#2-multi-amr-path-planning-and-subcarrier-allocation)
3. [Allocation and Path-Planning Ablation](#3-allocation-and-path-planning-ablation)
4. [Pareto Frontier and QoS Sensitivity Analysis](#4-pareto-frontier-and-qos-sensitivity-analysis)
5. [Animation and Online-Fading Robustness Evaluation](#5-animation-and-online-fading-robustness-evaluation)

## Preparation. Warehouse Scene Construction

[`scene.ipynb`](scene.ipynb) creates the warehouse geometry, exports the PLY
meshes, and writes the Mitsuba/Sionna RT scene XML. It uses the shared room,
obstacle, and material definitions in [`project_config.py`](project_config.py)
and registers the custom material in
[`project_radio_material.py`](project_radio_material.py).

## 1. Channel Fingerprint Map Generation

[`01_channel_fingerprint_map.ipynb`](01_channel_fingerprint_map.ipynb) traces
propagation paths, computes the channel frequency response and per-subcarrier
SNR across the receiver grid, and saves the resulting fingerprint as
`results/data/fingerprint.npz`.

## 2. Multi-AMR Path Planning and Subcarrier Allocation

[`02_multi_amr_path_planning.ipynb`](02_multi_amr_path_planning.ipynb) creates the occupancy
grid, generates candidate A* paths for both AMRs, compares four allocation and
planning schemes, and saves `results/data/path_planning_results.npz`. The
shared Shannon-rate and subcarrier-allocation helpers are in
[`simulator.py`](simulator.py).

## 3. Allocation and Path-Planning Ablation

[`03_allocation_path_ablation.ipynb`](03_allocation_path_ablation.ipynb) loads the path-planning results
and visualizes time-varying bandwidth shares, bottleneck throughput, and the
contribution of bandwidth allocation versus communication-aware path planning.

## 4. Pareto Frontier and QoS Sensitivity Analysis

[`04_pareto_qos_analysis.ipynb`](04_pareto_qos_analysis.ipynb) constructs the mission-time versus
minimum-throughput Pareto frontier and evaluates the effect of varying the QoS
threshold.

## 5. Animation and Online-Fading Robustness Evaluation

[`05_animation_robustness.ipynb`](05_animation_robustness.ipynb) renders the baseline and joint
strategy animations, then replays the selected paths under Rayleigh fading to
compare offline and online performance.

## Execution Order

Run the notebooks in this order:

```text
scene.ipynb
  -> 1. Channel Fingerprint Map Generation
  -> 2. Multi-AMR Path Planning and Subcarrier Allocation
  -> 3. Allocation and Path-Planning Ablation
  -> 4. Pareto Frontier and QoS Sensitivity Analysis
  -> 5. Animation and Online-Fading Robustness Evaluation
```

Steps 3–5 require `results/data/path_planning_results.npz`; steps 2 and 5 also
require `results/data/fingerprint.npz`. The included result files reproduce the
published figures and animations without rerunning the ray tracer.

## Project Layout

```text
.
├── README.md
├── requirements.txt              # Reproducible Python dependencies
├── project_config.py             # Shared paths, model, mission, and planning settings
├── project_radio_material.py     # Custom Mitsuba/Sionna RT material plugin
├── simulator.py                  # Rate calculation and bandwidth-allocation helpers
├── scene.ipynb                   # Scene and mesh/XML generation
├── 01_channel_fingerprint_map.ipynb   # 1. Channel fingerprint map generation
├── 02_multi_amr_path_planning.ipynb     # 2. Path planning and allocation evaluation
├── 03_allocation_path_ablation.ipynb          # 3. Ablation analysis
├── 04_pareto_qos_analysis.ipynb             # 4. Pareto and QoS analysis
├── 05_animation_robustness.ipynb         # 5. Animation and robustness analysis
├── scene/
│   ├── scene_interaction.xml     # Generated radio scene
│   └── meshes/                   # Generated PLY geometry
└── results/
    ├── data/                     # Channel fingerprint and planning result arrays
    ├── figures/                  # Published PNG figures
    └── animations/               # Published MP4 animations
```

## Setup

Use Python 3.11, then install the fixed Sionna RT version and supporting
packages from the project root:

```bash
python -m pip install -r requirements.txt
```

A CUDA-enabled Mitsuba variant is recommended for practical ray-tracing
runtime. The animation notebook uses `imageio-ffmpeg` and falls back to GIF
output if an FFmpeg writer is unavailable.

## Git Notes

Notebook outputs are cleared before commit to keep the repository small. The
versioned `scene/` and `results/` assets are the reproducible inputs and final
outputs that belong with the project.
