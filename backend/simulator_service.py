# =========================================================
# ThreatX — Controlled Background Traffic Simulation
# =========================================================

import os
import random
import threading
import time
from datetime import datetime

import pandas as pd

from backend.database import SessionLocal
from backend.model_service import predict_threat
from backend.models import TrafficLog, Alert


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "UNSW_NB15_testing-set.csv"
)


# =========================================================
# SIMULATION SETTINGS
# =========================================================

DELAY_SECONDS = 2


# =========================================================
# ATTACK CATEGORIES
# =========================================================

ATTACK_CATEGORIES = [
    "Normal",
    "Generic",
    "Exploits",
    "Fuzzers",
    "DoS",
    "Reconnaissance",
    "Analysis",
    "Backdoor",
    "Shellcode",
    "Worms"
]


# =========================================================
# CATEGORY SELECTION
# =========================================================

# These weights control how frequently categories are sampled.
#
# This does NOT change the ML prediction.
# It only controls which dataset row is selected.

CATEGORY_WEIGHTS = {

    "Normal": 25,

    "Generic": 18,

    "Exploits": 15,

    "Fuzzers": 12,

    "DoS": 10,

    "Reconnaissance": 8,

    "Analysis": 5,

    "Backdoor": 3,

    "Shellcode": 3,

    "Worms": 1
}


# =========================================================
# DATASET FEATURES
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

    "is_sm_ips_ports"
]


# =========================================================
# THREAT SEVERITY
# =========================================================

def get_severity(attack_category):

    if not attack_category:
        return "Low"


    critical_attacks = {
        "DoS",
        "Backdoor",
        "Shellcode"
    }


    high_attacks = {
        "Exploits",
        "Fuzzers",
        "Generic"
    }


    medium_attacks = {
        "Reconnaissance",
        "Analysis"
    }


    if attack_category in critical_attacks:
        return "Critical"


    if attack_category in high_attacks:
        return "High"


    if attack_category in medium_attacks:
        return "Medium"


    return "Low"


# =========================================================
# SIMULATION SERVICE
# =========================================================

class SimulationService:

    def __init__(self):

        self.running = False

        self.thread = None

        self.dataset = None

        self.category_data = {}

        self.sample_number = 0

        self.last_prediction = None

        self.last_dataset_category = None

        self.last_error = None

        self.last_activity = None

        self.lock = threading.Lock()


    # =====================================================
    # LOAD DATASET
    # =====================================================

    def load_dataset(self):

        if self.dataset is not None:
            return self.dataset


        print(
            "Loading UNSW-NB15 dataset..."
        )


        if not os.path.exists(
            DATASET_PATH
        ):

            raise FileNotFoundError(
                f"Dataset not found: {DATASET_PATH}"
            )


        self.dataset = pd.read_csv(
            DATASET_PATH
        )


        print(
            f"Dataset loaded: "
            f"{len(self.dataset)} rows"
        )


        # ---------------------------------------------
        # PREPARE CATEGORY POOLS
        # ---------------------------------------------

        if "attack_cat" not in self.dataset.columns:

            raise ValueError(
                "Dataset does not contain attack_cat column."
            )


        self.dataset["attack_cat"] = (
            self.dataset["attack_cat"]
            .fillna("Normal")
            .astype(str)
            .str.strip()
        )


        for category in ATTACK_CATEGORIES:

            category_rows =self.dataset[
                    self.dataset["attack_cat"] == category
                ]


            if len(category_rows) > 0:

                self.category_data[
                    category
                ] = category_rows


                print(
                    f"[SIMULATION] "
                    f"{category}: "
                    f"{len(category_rows)} rows"
                )


        return self.dataset


    # =====================================================
    # SELECT CATEGORY
    # =====================================================

    def select_category(self):

        available_categories = [

            category

            for category in CATEGORY_WEIGHTS

            if category in self.category_data

            and len(
                self.category_data[category]
            ) > 0
        ]


        if not available_categories:

            raise RuntimeError(
                "No usable simulation categories found."
            )


        weights = [

            CATEGORY_WEIGHTS[category]

            for category in available_categories

        ]


        return random.choices(
            available_categories,
            weights=weights,
            k=1
        )[0]


    # =====================================================
    # SELECT DATASET ROW
    # =====================================================

    def select_row(self):

        category =self.select_category()


        category_rows =self.category_data[
                category
            ]


        random_index =random.randint(
                0,
                len(category_rows) - 1
            )


        row =category_rows.iloc[
                random_index
            ]


        return category, row


    # =====================================================
    # PREPARE SAMPLE
    # =====================================================

    def prepare_sample(self, row):

        sample = {}


        for column in FEATURE_COLUMNS:

            value = row[column]


            if pd.isna(value):

                value = 0


            if hasattr(
                value,
                "item"
            ):

                try:

                    value = value.item()

                except Exception:

                    pass


            sample[column] = value


        return sample


    # =====================================================
    # PROCESS ONE SAMPLE
    # =====================================================

    def process_sample(self):

        db = None


        try:

            self.load_dataset()


            # -----------------------------------------
            # SELECT CONTROLLED DATASET SAMPLE
            # -----------------------------------------

            dataset_category, row =self.select_row()


            sample =self.prepare_sample(
                    row
                )


            # -----------------------------------------
            # ML PREDICTION
            # -----------------------------------------

            result =predict_threat(
                    sample
                )


            # -----------------------------------------
            # DATABASE
            # -----------------------------------------

            db =SessionLocal()


            # -----------------------------------------
            # TRAFFIC LOG
            # -----------------------------------------

            traffic_log =TrafficLog(

                    timestamp=datetime.utcnow(),

                    prediction=result[
                        "prediction"
                    ],

                    attack_category=result.get(
                        "attack_category"
                    ),

                    confidence=float(
                        result.get(
                            "confidence",
                            0
                        )
                    ),

                    protocol=sample.get(
                        "proto"
                    ),

                    service=sample.get(
                        "service"
                    ),

                    state=sample.get(
                        "state"
                    )
                )


            db.add(
                traffic_log
            )


            # -----------------------------------------
            # CREATE ALERT
            # -----------------------------------------

            if (
                result["prediction"]
                == "Attack"
            ):

                attack_category =result.get(
                        "attack_category"
                    )


                severity =get_severity(
                        attack_category
                    )


                description = (

                    f"{attack_category} attack "
                    f"detected. ML confidence: "

                    f"{result['confidence'] * 100:.2f}%. "

                    f"Protocol: "
                    f"{sample.get('proto', '-')}, "

                    f"Service: "
                    f"{sample.get('service', '-')}, "

                    f"State: "
                    f"{sample.get('state', '-')}"

                )


                alert =Alert(

                        timestamp=datetime.utcnow(),

                        type=str(
                            attack_category
                        ),

                        severity=severity,

                        description=description,

                        status="active"

                    )


                db.add(
                    alert
                )


            # -----------------------------------------
            # COMMIT
            # -----------------------------------------

            db.commit()


            # -----------------------------------------
            # UPDATE STATE
            # -----------------------------------------

            self.sample_number += 1

            self.last_prediction =result

            self.last_dataset_category =dataset_category

            self.last_error = None

            self.last_activity =datetime.utcnow().isoformat()


            # -----------------------------------------
            # TERMINAL OUTPUT
            # -----------------------------------------

            print(

                f"[SIMULATION] "

                f"Sample #{self.sample_number} | "

                f"Dataset: {dataset_category} | "

                f"ML: {result.get('prediction')} | "

                f"Category: "
                f"{result.get('attack_category')} | "

                f"Confidence: "
                f"{result.get('confidence', 0) * 100:.2f}%"

            )


        except Exception as error:

            if db:

                db.rollback()


            self.last_error =str(error)


            print(
                "[SIMULATION] Error:",
                error
            )


        finally:

            if db:

                db.close()


    # =====================================================
    # SIMULATION LOOP
    # =====================================================

    def simulation_loop(self):

        print(
            "[SIMULATION] "
            "Controlled simulation started."
        )


        while self.running:

            self.process_sample()


            time.sleep(
                DELAY_SECONDS
            )


        print(
            "[SIMULATION] "
            "Controlled simulation stopped."
        )


    # =====================================================
    # START
    # =====================================================

    def start(self):

        with self.lock:

            if self.running:

                return False


            try:

                self.load_dataset()

            except Exception as error:

                self.last_error =str(error)

                print(
                    "[SIMULATION] "
                    "Cannot start:",
                    error
                )

                return False


            self.running = True


            self.thread =threading.Thread(

                    target=self.simulation_loop,

                    daemon=True

                )


            self.thread.start()


            return True


    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        with self.lock:

            if not self.running:

                return False


            self.running = False

            return True


    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        return {

            "running":
                self.running,

            "sample_count":
                self.sample_number,

            "last_dataset_category":
                self.last_dataset_category,

            "last_prediction":
                self.last_prediction,

            "last_activity":
                self.last_activity,

            "last_error":
                self.last_error

        }


# =========================================================
# GLOBAL SERVICE
# =========================================================

simulation_service =SimulationService()