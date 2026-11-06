# Communication-Aware Radio Resource Allocation for Warehouse AMRs

An end-to-end study of how radio conditions can inform the motion planning of
autonomous mobile robots (AMRs) in an indoor warehouse. The project combines a
custom Sionna RT scene, channel fingerprinting, candidate-path search, and
subcarrier allocation for two simultaneously moving AMRs.

## Overview

Conventional shortest-path planning can guide a robot through locations with
poor wireless coverage. This repository evaluates a communication-aware
alternative: select AMR paths and divide radio resources jointly, while meeting
a minimum-rate quality-of-service (QoS) target.

The implementation is a reproducible simulation study rather than a deployed
warehouse controller. All geometry, physical-layer settings, mission settings,
and planning parameters are defined in
[project_config.py](project_config.py).

## Project at a glance

| Item | Experiment design |
| --- | --- |
| Environment | Custom 18 m × 10 m indoor warehouse with walls, pillars, cabinets, and a base station |
| Propagation model | Sionna RT ray tracing at 5.8 GHz with LoS, specular reflection, and penetration |
| Antenna model | One BS antenna and one antenna per AMR (SISO links; no MIMO spatial multiplexing) |
| Radio resources | 20 MHz bandwidth split into 64 subcarriers |
| Channel representation | 0.5 m receiver grid (36 × 20 cells) with a per-subcarrier SNR fingerprint |
| AMR mission | Two AMRs travel between opposing warehouse corners at 0.5 m/s |
| Planning search | 30 occupancy-grid candidate paths per AMR; 900 path-pair evaluations |
| QoS target | Minimum sampled AMR rate of 30 Mbps |
| Link asymmetry | AMR 2 has a −7 dB link offset to create an unequal-channel scenario |

## Propagation and custom material model

The channel fingerprint in
[01_channel_fingerprint_map.ipynb](01_channel_fingerprint_map.ipynb) uses
Sionna RT at 5.8 GHz. The initial path search enables line-of-sight (LoS),
specular reflection, and refraction (used here to represent transmission or
penetration). It disables diffuse reflection, diffraction, and edge
diffraction, and searches paths with at most five interactions.

The final fingerprint retains paths with zero or one specular reflection from
an exterior wall. Transmission through interior obstacles is retained and does
not count toward that exterior-wall reflection limit. A zero-reflection path
can therefore include penetration; it is not necessarily an unobstructed LoS
path.

The scene uses the custom Mitsuba/Sionna RT material plugin in
[project_radio_material.py](project_radio_material.py):

- Exterior walls are reflection-only, with an amplitude reflection coefficient
  of `rho = 0.70`.
- Concrete obstacles are transmission-only, with an attenuation of 50 dB/m.
- Wooden cabinets are transmission-only, with an attenuation of 8 dB/m.
- For a transmitted path, attenuation uses the material thickness adjusted by
  the angle of incidence. Transmission continues straight through the surface,
  without changing direction.

The radio-scene geometry uses a zero-thickness vertical interaction plane for
each interior obstacle. Pillars and cabinets use planes facing the base station;
the interior walls use the explicit `proxy_normal` in the configuration.
Thickness is a material parameter used to calculate penetration loss, rather
than a solid mesh traversed by the ray. The circular and rectangular obstacle
footprints shown in plots and used for collision checking describe the full
navigation obstacles; they differ from these simplified radio interaction
surfaces.

This is a deliberately simplified, frequency-independent project material
model. It does not model simultaneous reflection and transmission at one
surface, diffuse scattering, diffraction, or measured frequency-dependent
electromagnetic material properties.

## Single-antenna experiment

The study deliberately uses a single antenna at the BS and a single antenna
at each AMR. Notebook 01 sets both transmitter and receiver arrays to `1 × 1`
with an isotropic, vertically polarized pattern. Each link is SISO. Multiple
AMRs and subcarriers do not introduce MIMO spatial streams: the users share
disjoint subcarrier groups, and the rate model includes no spatial-multiplexing
gain. Antenna count is held fixed during route and allocation comparisons.

## Transmit power and SNR convention

`P_REF_DBM = -5.0` is the reference transmit power **per subcarrier**. With all
64 subcarriers active at this power, the total is
`P_REF_DBM + 10 * log10(N_SC)`, approximately **13.06 dBm**. Noise is also
calculated per subcarrier using `DF_HZ = BW_HZ / N_SC = 312,500 Hz` and the
7 dB noise figure. The fingerprint thus stores per-subcarrier SNR, not SNR
computed using total-band transmit power or noise.

Both the path-profile example in notebook 01 and the planner in notebook 02
interpolate SNR in linear units and convert to dB for display. Averaging across
subcarriers also uses linear SNR before conversion to dB.

## End-to-end workflow

~~~text
Warehouse geometry
      ↓
Ray-traced channel fingerprint (SNR per grid cell and subcarrier)
      ↓
Candidate A* paths for two AMRs
      ↓
Path-pair evaluation + subcarrier allocation
      ↓
Pareto / QoS / fading robustness analysis
~~~

1. **Warehouse scene construction** builds PLY geometry and a Mitsuba/Sionna RT
   XML scene.
2. **Channel fingerprinting** traces propagation paths and evaluates a channel
   frequency response and SNR for each grid location.
3. **Path planning** produces candidate A* paths through unblocked grid cells, converts them
   into synchronized trajectories, and interpolates the radio fingerprint along
   each route.
4. **Resource allocation** assigns the 64 subcarriers over time and evaluates
   the bottleneck AMR rate and mission duration.
5. **Analysis** compares strategies, constructs a QoS-constrained Pareto
   frontier, and replays the chosen paths under Rayleigh fading.

## Planning and allocation assumptions

Notebook 02 uses eight-neighbor A* on the 0.5 m grid, with blocked diagonal
corners disallowed. Start and goal coordinates are snapped to the nearest grid
centers (for example, `[1.0, 2.0]` becomes `[0.75, 1.75]`). Obstacle footprints
are expanded by the configured 0.2 m buffer when classifying cell centers.
This discrete model does not check swept robot footprints, continuous edge
clearance, or AMR-to-AMR collisions. Selected routes are communication-study
trajectories, not a collision-safe multi-robot controller.

Each AMR receives its shortest route plus seeded random-waypoint A* routes,
limited to 1.5 times the shortest length. A waypoint route can revisit a cell;
compact signatures suppress near-duplicates. JOINT searches only these
30 × 30 candidates, so it is not a global optimum over all possible routes.
Among QoS-feasible pairs it minimizes mission time and breaks ties by higher
minimum rate. If no pair meets QoS, it returns the highest-minimum-rate pair
and explicitly marks it infeasible.

Both AMRs move at constant configured speeds and remain at their start before
departure and at their goal after arrival. Both continue to require radio
service until the later arrival. Rates and QoS are evaluated every 0.1 s plus
the exact final time; no continuous-time QoS guarantee is claimed.
`mean_rate_bps` is an arithmetic sample mean, including the endpoint, rather
than a time-weighted integral.

Opt-BW maximizes the lower AMR rate over all nonempty contiguous splits, with
AMR1 always receiving the lower-index subcarriers and AMR2 the higher-index
ones. This tests 63 splits for 64 subcarriers. Rates use the Shannon formula
and fixed power per active subcarrier; arbitrary subcarrier assignments,
interference, scheduling overhead, and modulation/coding limits are omitted.

Notebook 02 checks saved fingerprint dimensions, grid coordinates, and RF
frequencies against the configuration. The existing fingerprint format does
not record power, materials, or full geometry: regenerate steps 0–2 after
changing those settings, even if the dimension checks pass.

## What QoS satisfaction means here

The QoS constraint **is implemented**: at every evaluated time, both AMRs
must have a modeled rate at least equal to the configured target (30 Mbps by
default). Equivalently, the minimum over all saved times and both AMRs must
meet that target. Notebook 02 filters candidate pairs using this constraint
and chooses the fastest feasible pair. Its fallback is explicitly infeasible
when no candidate meets the target.

The default evaluation times are 0, 0.1, 0.2, ... seconds plus exact mission
completion. This establishes QoS at those discrete times, without proving a
lower bound for every time between them. A finer evaluation grid can check
sampling sensitivity, but remains a numerical check rather than an all-time
proof. The concise project claim is: **QoS-constrained planning with QoS
satisfied at all evaluated times in the static channel model**. The fading
replay in notebook 05 is a separate robustness experiment.

Notebook 03 reports the pass/fail status for each scheme. Its rates are
Shannon-model estimates, not measured packet throughput. The sample means
use each scheme's own mission horizon. Because the communication-aware
strategies can select different routes, their ablation contrasts describe
whole-strategy differences rather than fixed-route causal effects.

Notebook 04 loads the QoS target from the saved results and uses the same
selection rule as notebook 02. Its Pareto frontier and maximum feasible QoS
refer to the finite saved candidate set under the single-antenna model, not
to all possible routes or a universal SISO capacity limit. The QoS sweep
changes only the required rate. Its step curves use the actual frontier-rate
thresholds; red fallback markers indicate that no saved pair meets the target.
Minimum time under the QoS constraint is reported separately from minimum
time without that constraint. Which AMR first takes a longer route is derived
from the selected frontier rather than assumed in advance.

## Compared strategies

| Strategy | AMR route | Subcarrier allocation | Role in the comparison |
| --- | --- | --- | --- |
| **NAIVE** | Shortest path | Equal split | Mobility- and radio-unaware baseline |
| **+OPTBW** | Shortest path | Optimized split | Isolates the benefit of allocation |
| **+SMARTPATH** | Communication-aware path | Equal split | Isolates the benefit of route selection |
| **JOINT** | Communication-aware path | Optimized split | Joint planning and allocation strategy |

The primary performance views are mission time, instantaneous per-AMR rate,
bottleneck rate, feasible path pairs under the QoS target, and robustness to
online fading.

## Animation and fading replay

Notebook 05 exports **offline static-channel** NAIVE and JOINT animations at
nominal 2x speed and 10 fps for either MP4 or GIF. Frames use the nearest saved
simulation samples and include the exact mission endpoint; the final frame
hold adds a small playback-duration difference. The displayed clock is
simulation time. The background shows reference SNR, while displayed rates
include the per-AMR link offsets. No fading is shown in these videos.

The separate robustness experiment preserves the SISO model, routes, and
offline time-varying subcarrier splits. It applies unit-mean exponential
power gains (Rayleigh amplitudes) independently across saved times and
subcarriers for 30 realizations. Each subcarrier is assigned to only one AMR;
only that user's gain enters its rate. There is no online reoptimization,
Doppler, or correlated fading model. This is a simplified stress test of the
fingerprint, not a calibrated mobile-channel model. The fixed seed and scheme
order reproduce the experiment; schemes have separate random draws and may
have different mission lengths.

The reported ratio is **mean of each realization's minimum rate / offline
minimum rate**. It differs from the minimum of the mean trace. The shaded
mean ± one standard deviation is pointwise trial variability, not a confidence
interval or reliability bound. Mission QoS counts realizations that meet the
saved target at every evaluated sample. Sample outage counts failing samples,
not continuous-time outage duration. Static-channel QoS does not imply QoS
after adding this fading model; compare absolute rates and QoS counts as well
as relative loss. Trial traces and summaries are saved in
`results/data/robustness_results.npz`.

Notebook 05 reads the subcarrier bandwidth and room extent from the saved
fingerprint and checks planning rates against their saved SNR and allocations.
Obstacle outlines still come from `project_config.py`; regenerate the pipeline
after geometry changes.

## Selected outputs

| Warehouse radio scene | Paths selected by each strategy |
| --- | --- |
| ![3D warehouse radio scene](results/figures/scene_3d_overview.png) | ![Paths selected by scheme](results/figures/05_paths_by_scheme.png) |

| QoS-constrained Pareto frontier | Offline versus online fading replay |
| --- | --- |
| ![Pareto frontier](results/figures/11_pareto.png) | ![Offline versus online performance](results/figures/13_offline_vs_online.png) |

Additional figures are in [results/figures/](results/figures), and baseline
and joint-strategy animations are in
[results/animations/](results/animations).

## Notebooks and execution order

Run the notebooks in the following order when regenerating the complete
pipeline.

| Step | Notebook | Purpose | Main output |
| --- | --- | --- | --- |
| 0. | [scene.ipynb](scene.ipynb) | Build the warehouse mesh and radio-scene XML | scene/ |
| 1. | [01_channel_fingerprint_map.ipynb](01_channel_fingerprint_map.ipynb) | Generate the ray-traced channel fingerprint map | results/data/fingerprint.npz |
| 2. | [02_multi_amr_path_planning.ipynb](02_multi_amr_path_planning.ipynb) | Evaluate paths and allocations for both AMRs | results/data/path_planning_results.npz |
| 3. | [03_allocation_path_ablation.ipynb](03_allocation_path_ablation.ipynb) | Compare allocation and route-planning contributions | 00_bw_share.png, 01_throughput.png, 10_ablation_bars.png |
| 4. | [04_pareto_qos_analysis.ipynb](04_pareto_qos_analysis.ipynb) | Analyze the Pareto frontier and QoS sweep | 11_pareto.png, 12_qos_sweep.png |
| 5. | [05_animation_robustness.ipynb](05_animation_robustness.ipynb) | Render trajectory animations and evaluate fading robustness | 14_naive_animation.mp4, 15_joint_animation.mp4, 13_offline_vs_online.png, results/data/robustness_results.npz |

Notebook 02 saves its NPZ results before its optional inline animation preview.
Notebook 05 exports the video files.

Steps 3–5 can be run immediately using the included NPZ results. To regenerate
the analysis inputs, run steps 0–2 first.

## Quick start

The project uses Python 3.11 and pins the ray-tracing package version in
[requirements.txt](requirements.txt). From the repository root:

~~~bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
~~~

Open the notebooks in the execution order above. A CUDA-enabled Mitsuba setup
is recommended for practical ray-tracing runtimes. The animation notebook uses
imageio-ffmpeg and falls back to GIF output if an FFmpeg writer is not
available.

## Repository layout

~~~text
.
├── project_config.py              # Shared physical-layer, AMR, and planning settings
├── project_radio_material.py      # Custom Mitsuba/Sionna RT material plugin
├── simulator.py                   # Rate and subcarrier-allocation helpers
├── scene.ipynb                    # 0. Warehouse scene construction
├── 01_channel_fingerprint_map.ipynb
├── 02_multi_amr_path_planning.ipynb
├── 03_allocation_path_ablation.ipynb
├── 04_pareto_qos_analysis.ipynb
├── 05_animation_robustness.ipynb
├── scene/                         # Generated XML scene and PLY meshes
└── results/
    ├── data/                      # Fingerprint, planning, and fading-replay arrays
    ├── figures/                   # PNG figures shown in this README
    └── animations/                # MP4 trajectory animations
~~~

## Reproducibility notes

- **project_config.py** is the single source of truth for room geometry, PHY
  parameters, AMR start/goal positions, QoS, and candidate-path settings.
- **project_radio_material.py** contains the custom material registration used
  by the generated scene.
- Notebook cell outputs are intentionally cleared before commit; the versioned
  figures, animations, and NPZ files preserve the final experiment outputs.
  Run notebook 01 to regenerate its SNR heatmap and BS-to-AMR propagation-path
  plots.
- Rerunning scene generation, planning, or analysis notebooks can overwrite
  their corresponding generated assets in **scene/** and **results/**.
