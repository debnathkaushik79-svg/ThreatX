# =========================================================
# ThreatX — Shared Feature Engineering
# =========================================================

import numpy as np
import pandas as pd


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the exact feature engineering used by the
    ThreatX targeted feature-engineered Random Forest.

    Input:
        Raw UNSW-NB15 network traffic features.

    Output:
        Original features + 22 engineered features.
    """

    df = df.copy()

    # -----------------------------------------------------
    # Existing 17 engineered features
    # -----------------------------------------------------

    # Bytes per packet
    df["sbytes_per_packet"] = (
        df["sbytes"] / (df["spkts"] + 1)
    )

    df["dbytes_per_packet"] = (
        df["dbytes"] / (df["dpkts"] + 1)
    )

    # Packet rates
    df["source_packet_rate"] = (
        df["spkts"] / (df["dur"] + 1e-6)
    )

    df["destination_packet_rate"] = (
        df["dpkts"] / (df["dur"] + 1e-6)
    )

    # Totals
    df["total_bytes"] = (
        df["sbytes"] + df["dbytes"]
    )

    df["total_packets"] = (
        df["spkts"] + df["dpkts"]
    )

    # Ratios
    df["byte_ratio"] = (
        df["sbytes"] / (df["dbytes"] + 1)
    )

    df["packet_ratio"] = (
        df["spkts"] / (df["dpkts"] + 1)
    )

    df["load_ratio"] = (
        df["sload"] / (df["dload"] + 1)
    )

    df["load_difference"] = (
        df["sload"] - df["dload"]
    )

    # Packet loss
    df["total_loss"] = (
        df["sloss"] + df["dloss"]
    )

    df["loss_ratio"] = (
        df["sloss"] / (df["dloss"] + 1)
    )

    # Timing
    df["packet_interval_ratio"] = (
        df["sinpkt"] / (df["dinpkt"] + 1e-6)
    )

    df["jitter_ratio"] = (
        df["sjit"] / (df["djit"] + 1e-6)
    )

    # Mean packet behavior
    df["mean_packet_difference"] = (
        df["smean"] - df["dmean"]
    )

    df["mean_packet_ratio"] = (
        df["smean"] / (df["dmean"] + 1)
    )

    # TCP handshake
    df["tcp_handshake_time"] = (
        df["synack"] + df["ackdat"]
    )

    # -----------------------------------------------------
    # Targeted features
    # -----------------------------------------------------

    # TTL relationship
    df["ttl_difference"] = (
        df["sttl"] - df["dttl"]
    )

    df["ttl_ratio"] = (
        df["sttl"] / (df["dttl"] + 1)
    )

    # TCP window relationship
    df["tcp_window_difference"] = (
        df["swin"] - df["dwin"]
    )

    df["tcp_window_ratio"] = (
        df["swin"] / (df["dwin"] + 1)
    )

    # Complete TCP handshake timing
    df["handshake_total"] = (
        df["synack"] + df["ackdat"] + df["tcprtt"]
    )

    # -----------------------------------------------------
    # Replace invalid numerical values
    # -----------------------------------------------------

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df