
import numpy as np
from project_config import N_SC, DF_HZ


# =========================================================
# Shannon capacity 식 사용하여 subcarrier별 전송률 계산 [bit/s]
# =========================================================
def subcarrier_rate_bps(snr_sc_linear):
    snr_sc_linear = np.maximum(np.asarray(snr_sc_linear), 0.0)
    return DF_HZ * np.log2(1.0 + snr_sc_linear)


# =========================================================
# optimal subcarrier 분배 함수
# 최소 rate(초당 보내는 bit 수)를 maximize하도록
# =========================================================
def solve_opt_bw(snr1_sc, snr2_sc):
    """AMR1은 0~k-1, AMR2는 k~N_SC-1번 subcarrier 사용."""
    snr1_sc = np.asarray(snr1_sc)
    snr2_sc = np.asarray(snr2_sc)

    if snr1_sc.shape != snr2_sc.shape:
        raise ValueError("AMR1과 AMR2의 SNR shape이 다릅니다.")
    if snr1_sc.ndim != 2 or snr1_sc.shape[1] != N_SC:
        raise ValueError(f"SNR shape은 (T, {N_SC})여야 합니다.")

    # subcarrier별 전송률
    rate1_sc = subcarrier_rate_bps(snr1_sc)
    rate2_sc = subcarrier_rate_bps(snr2_sc)

    # 누적 전송률
    prefix1 = np.cumsum(rate1_sc, axis=1)[:, :-1]
    prefix2 = np.cumsum(rate2_sc, axis=1)[:, :-1]

    rate1_all_k = prefix1
    rate2_all_k = rate2_sc.sum(axis=1, keepdims=True) - prefix2

    # 각 k에서 두 AMR 중 낮은 rate를 선택
    common_rate_all_k = np.minimum(rate1_all_k, rate2_all_k)

    # 가장 낮은 rate를 가장 크게 만드는 k 선택
    best_idx = np.argmax(common_rate_all_k, axis=1)
    split_k = best_idx + 1

    # 각 시점에서 optimal k에서의 전송률 가져오기
    rows = np.arange(len(snr1_sc))
    rate1_bps = rate1_all_k[rows, best_idx]
    rate2_bps = rate2_all_k[rows, best_idx]
    min_rate_bps = np.minimum(rate1_bps, rate2_bps)

    return {
        "split_k": split_k,
        "rate1_bps": rate1_bps,
        "rate2_bps": rate2_bps,
        "min_rate_bps": min_rate_bps,
    }


# =========================================================
# optimal하게 분배하지 않고 32:32로 subcarrier 나누기
# =========================================================
def solve_equal_bw(snr1_sc, snr2_sc):
    """64개 subcarrier를 AMR1과 AMR2에 32개씩 고정 분배."""
    k = N_SC // 2

    rate1_sc = subcarrier_rate_bps(snr1_sc)
    rate2_sc = subcarrier_rate_bps(snr2_sc)

    rate1_bps = rate1_sc[:, :k].sum(axis=1)
    rate2_bps = rate2_sc[:, k:].sum(axis=1)

    return {
        "split_k": np.full(len(snr1_sc), k, dtype=int),
        "rate1_bps": rate1_bps,
        "rate2_bps": rate2_bps,
        "min_rate_bps": np.minimum(rate1_bps, rate2_bps),
    }
