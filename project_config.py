import numpy as np
from pathlib import Path


# =========================================================
# File paths
# =========================================================

# Project root containing project_config.py
PROJECT_DIR = Path(__file__).resolve().parent

# Generated geometry and radio-scene definition
SCENE_DIR = PROJECT_DIR / "scene"
MESH_DIR = SCENE_DIR / "meshes"
SCENE_XML = SCENE_DIR / "scene_interaction.xml"

# Generated experiment data and presentation assets
RESULTS_DIR = PROJECT_DIR / "results"
DATA_DIR = RESULTS_DIR / "data"
FIGURES_DIR = RESULTS_DIR / "figures"
ANIMATIONS_DIR = RESULTS_DIR / "animations"

FINGERPRINT_PATH = DATA_DIR / "fingerprint.npz"
PATH_PLANNING_RESULTS_PATH = DATA_DIR / "path_planning_results.npz"


# =========================================================
# Room and Base Station
# =========================================================

ROOM_X = 18.0
ROOM_Y = 10.0
ROOM_Z = 3.0

BS_CENTER = np.array([3.0, 5.0, 2.7], dtype=float)   # Same as the antenna position

RX_HEIGHT = 0.5


# =========================================================
# PHY parameters
# =========================================================

FREQ_HZ = 5.8e9
BW_HZ = 20e6

N_SC = 64
DF_HZ = BW_HZ / N_SC  # Bandwidth per subcarrier (312,500 Hz)

NF_DB = 7.0
# Reference transmit power per subcarrier, used for the SNR fingerprint.
# All N_SC active: total power = P_REF_DBM + 10*log10(N_SC) ≈ 13.06 dBm.
P_REF_DBM = -5.0

# Noise power over the bandwidth of one subcarrier
NOISE_SC_DBM = (
    -174.0
    + 10.0 * np.log10(DF_HZ)
    + NF_DB
)

# QoS requirement
R_QOS_REQUIRED_MBPS = 30.0
R_QOS_REQUIRED_BPS = R_QOS_REQUIRED_MBPS * 1e6


# =========================================================
# Receiver grid
# =========================================================

GRID_RES = 0.5

N_COLS = int(round(ROOM_X / GRID_RES))   # 36
N_ROWS = int(round(ROOM_Y / GRID_RES))   # 20

# Grid-cell centers rather than boundaries
CELL_X = (np.arange(N_COLS) + 0.5) * GRID_RES
CELL_Y = (np.arange(N_ROWS) + 0.5) * GRID_RES

RX_POINTS = np.array([
    [x, y, RX_HEIGHT]
    for y in CELL_Y
    for x in CELL_X
], dtype=float)


# =========================================================
# AMR mission and planning parameters
# =========================================================

AMR1_START_XY = np.array([1.0, 2.0])
AMR1_GOAL_XY = np.array([17.0, 8.0])
AMR2_START_XY = np.array([17.0, 2.0])
AMR2_GOAL_XY = np.array([1.0, 8.0])

AMR1_SPEED_MPS = 0.5
AMR2_SPEED_MPS = 0.5
AMR1_START_TIME_S = 0.0
AMR2_START_TIME_S = 0.0

OBSTACLE_BUFFER_M = 0.2
SIM_DT_S = 0.1
N_PATH_CANDIDATES = 30
MAX_PATH_RATIO = 1.5
MAX_CANDIDATE_ATTEMPT_FACTOR = 30
RANDOM_SEED = 42

AMR1_LINK_OFFSET_DB = 0.0
AMR2_LINK_OFFSET_DB = -7.0


# =========================================================
# Materials and Obstacles
# =========================================================

# Radio interaction modes and attenuation; geometry is built in scene.ipynb.
MATERIALS = {
    "perimeter": dict(mode="reflect", alpha_db_per_m=0.0,  rho=0.70,
                      color=(0.36, 0.39, 0.44)),
    "concrete":  dict(mode="transmit", alpha_db_per_m=50.0, rho=0.0,
                      color=(0.55, 0.55, 0.55)),
    "wood":      dict(mode="transmit", alpha_db_per_m=8.0,  rho=0.0,
                      color=(0.78, 0.57, 0.24)),
}

# Full obstacle dimensions define navigation footprints and visualizations.
# Ray tracing instead uses one zero-thickness vertical plane per obstacle,
# with effective thickness carried by the custom material for penetration loss.
# Pillar/cabinet planes face the BS; interior walls use explicit proxy_normal.
OBSTACLES = [
    dict(name="Wall_S", kind="box", center=(9.0, 2.5),
         size=(0.3, 5.0, 2.7), material="concrete", proxy_normal=(1.0, 0.0)),
    dict(name="Wall_N", kind="box", center=(9.0, 7.75),
         size=(0.3, 4.5, 2.7), material="concrete", proxy_normal=(1.0, 0.0)),

    dict(name="Pillar_BS", kind="cylinder", center=(5.0, 5.0),
         radius=0.3, height=2.7, material="concrete"),
    dict(name="Pillar_SW", kind="cylinder", center=(3.5, 1.0),
         radius=0.3, height=3.0, material="concrete"),
    dict(name="Pillar_NW", kind="cylinder", center=(3.5, 9.0),
         radius=0.3, height=3.0, material="concrete"),
    dict(name="Pillar_SE", kind="cylinder", center=(15.0, 1.0),
         radius=0.3, height=3.0, material="concrete"),
    dict(name="Pillar_NE", kind="cylinder", center=(15.0, 9.0),
         radius=0.3, height=3.0, material="concrete"),
    dict(name="Pillar_E", kind="cylinder", center=(16.0, 5.0),
         radius=0.4, height=3.0, material="concrete"),

    dict(name="Cab_S1", kind="box", center=(6.0, 3.0),
         size=(0.6, 0.6, 2.0), material="wood"),
    dict(name="Cab_N1", kind="box", center=(6.0, 7.0),
         size=(0.6, 0.6, 2.0), material="wood"),
    dict(name="Cab_S2", kind="box", center=(13.0, 3.0),
         size=(0.6, 0.6, 2.0), material="wood"),
    dict(name="Cab_N2", kind="box", center=(13.0, 7.0),
         size=(0.6, 0.6, 2.0), material="wood"),
]
