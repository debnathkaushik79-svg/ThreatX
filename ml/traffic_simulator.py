# =========================================================
# ThreatX — Continuous Traffic Simulator
# =========================================================

import time
import random

import pandas as pd
import requests


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000/api/predict"

DATASET_PATH = (
    r"C:\Users\KAUSHIK\Downloads\Cyber\ThreatX"
    r"\data\UNSW_NB15_testing-set.csv"
)

# Time between traffic samples
DELAY_SECONDS = 2


# =========================================================
# MODEL INPUT FEATURES
# =========================================================

FEATURE_COLUMNS = [
    "dur",
    "proto",
    "service",
    "state",
    "spkts",
    "dpkts",
    "sbytes",
    "dbytes",
    "rate",
    "sttl",
    "dttl",
    "sload",
    "dload",
    "sloss",
    "dloss",
    "sinpkt",
    "dinpkt",
    "sjit",
    "djit",
    "swin",
    "stcpb",
    "dtcpb",
    "dwin",
    "tcprtt",
    "synack",
    "ackdat",
    "smean",
    "dmean",
    "trans_depth",
    "response_body_len",
    "ct_srv_src",
    "ct_state_ttl",
    "ct_dst_ltm",
    "ct_src_dport_ltm",
    "ct_dst_sport_ltm",
    "ct_dst_src_ltm",
    "is_ftp_login",
    "ct_ftp_cmd",
    "ct_flw_http_mthd",
    "ct_src_ltm",
    "ct_srv_dst",
    "is_sm_ips_ports",
]


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():

    print("=" * 60)
    print("ThreatX Continuous Traffic Simulator")
    print("=" * 60)

    print("\nLoading UNSW-NB15 dataset...")

    try:

        df = pd.read_csv(DATASET_PATH)

        print("Dataset loaded successfully.")
        print(f"Rows    : {len(df)}")
        print(f"Columns : {len(df.columns)}")

        return df

    except FileNotFoundError:

        print("\nERROR: Dataset file not found.")
        print(f"Expected:")
        print(DATASET_PATH)

        return None

    except Exception as e:

        print("\nERROR loading dataset:")
        print(e)

        return None


# =========================================================
# PREPARE SAMPLE
# =========================================================

def prepare_sample(row):

    sample = {}

    for column in FEATURE_COLUMNS:

        value = row[column]

        # Handle missing values
        if pd.isna(value):
            value = 0

        # Convert NumPy values to Python values
        if hasattr(value, "item"):

            try:
                value = value.item()

            except Exception:
                pass

        sample[column] = value

    return sample


# =========================================================
# SEND SAMPLE
# =========================================================

def send_sample(sample, original_row, sample_number):

    try:

        response = requests.post(
            API_URL,
            json=sample,
            timeout=10
        )

        print("\n" + "-" * 60)

        print(
            f"Traffic Sample #{sample_number}"
        )

        print("-" * 60)

        print(
            f"API Status : {response.status_code}"
        )

        if response.status_code != 200:

            print("API Error:")
            print(response.text)

            return False

        result = response.json()

        # -------------------------------------------------
        # Dataset information
        # -------------------------------------------------

        original_label = original_row.get(
            "label",
            "Unknown"
        )

        original_category = original_row.get(
            "attack_cat",
            "Unknown"
        )

        print(
            f"Dataset Label       : {original_label}"
        )

        print(
            f"Dataset Category    : {original_category}"
        )

        # -------------------------------------------------
        # ThreatX prediction
        # -------------------------------------------------

        prediction = result.get(
            "prediction",
            "Unknown"
        )

        attack_category = result.get(
            "attack_category"
        )

        confidence = result.get(
            "confidence",
            0
        )

        log_id = result.get(
            "log_id"
        )

        alert_id = result.get(
            "alert_id"
        )

        print(
            f"ThreatX Prediction  : {prediction}"
        )

        print(
            f"Attack Category     : {attack_category}"
        )

        print(
            f"Confidence          : "
            f"{confidence * 100:.2f}%"
        )

        print(
            f"Database Log ID     : {log_id}"
        )

        print(
            f"Alert ID            : {alert_id}"
        )

        return True

    except requests.exceptions.ConnectionError:

        print("\nERROR: Cannot connect to FastAPI.")

        print(
            "Make sure the backend is running:"
        )

        print(
            "python -m uvicorn backend.main:app --reload"
        )

        return False

    except requests.exceptions.Timeout:

        print(
            "\nERROR: API request timed out."
        )

        return False

    except Exception as e:

        print(
            "\nERROR sending sample:"
        )

        print(e)

        return False


# =========================================================
# CONTINUOUS SIMULATION
# =========================================================

def run_simulation(df):

    print("\n" + "=" * 60)
    print("LIVE TRAFFIC SIMULATION STARTED")
    print("=" * 60)

    print(
        f"\nDelay between samples: "
        f"{DELAY_SECONDS} seconds"
    )

    print(
        "\nPress CTRL+C to stop simulation."
    )

    print("\n")

    sample_number = 1

    try:

        while True:

            # Pick random traffic record
            random_index = random.randint(
                0,
                len(df) - 1
            )

            row = df.iloc[random_index]

            # Prepare API request
            sample = prepare_sample(row)

            # Send to ThreatX
            success = send_sample(
                sample,
                row,
                sample_number
            )

            if success:

                sample_number += 1

            print(
                f"\nNext sample in "
                f"{DELAY_SECONDS} seconds..."
            )

            time.sleep(
                DELAY_SECONDS
            )

    except KeyboardInterrupt:

        print("\n\n" + "=" * 60)
        print("LIVE SIMULATION STOPPED")
        print("=" * 60)

        print(
            f"\nTotal samples processed: "
            f"{sample_number - 1}"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    df = load_dataset()

    if df is None:
        return

    run_simulation(df)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()