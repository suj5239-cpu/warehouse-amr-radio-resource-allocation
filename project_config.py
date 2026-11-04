import numpy as np
from pathlib import Path


# =========================================================
# File paths
# =========================================================

# project_config.py가 저장된 프로젝트 루트
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

BS_CENTER = np.array([3.0, 5.0, 2.7], dtype=float)   # antenna 위치와 동일

RX_HEIGHT = 0.5


# =========================================================
# PHY parameters
# =========================================================

FREQ_HZ = 5.8e9
BW_HZ = 20e6

N_SC = 64
DF_HZ = BW_HZ / N_SC

NF_DB = 7.0
P_REF_DBM = -5.0

# 한 subcarrier가 차지하는 대역폭에 대한 잡음 전력
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

# 각 grid cell의 경계가 아니라 중심 좌표
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

MATERIALS = {
    "perimeter": dict(mode="reflect", alpha_db_per_m=0.0,  rho=0.70,
                      color=(0.36, 0.39, 0.44)),
    "concrete":  dict(mode="transmit", alpha_db_per_m=50.0, rho=0.0,
                      color=(0.55, 0.55, 0.55)),
    "wood":      dict(mode="transmit", alpha_db_per_m=8.0,  rho=0.0,
                      color=(0.78, 0.57, 0.24)),
}

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