# =========================================================
# ThreatX — FastAPI Backend
# =========================================================
from backend.simulator_service import simulation_service
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from collections import defaultdict

from backend.database import get_db
from backend.model_service import predict_threat
from backend.models import TrafficLog, Alert


app = FastAPI(
    title="ThreatX API",
    description=(
        "ML-based cybersecurity threat detection and "
        "network intrusion monitoring API."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "ThreatX API is running",
        "status": "online"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ThreatX ML API"
    }


# =========================================================
# TRAFFIC REQUEST
# =========================================================

class TrafficRequest(BaseModel):

    id: int | None = Field(
        default=None,
        description="Optional network traffic record ID"
    )

    dur: float
    proto: str
    service: str
    state: str
    spkts: float
    dpkts: float
    sbytes: float
    dbytes: float
    rate: float
    sttl: float
    dttl: float
    sload: float
    dload: float
    sloss: float
    dloss: float
    sinpkt: float
    dinpkt: float
    sjit: float
    djit: float
    swin: float
    stcpb: float
    dtcpb: float
    dwin: float
    tcprtt: float
    synack: float
    ackdat: float
    smean: float
    dmean: float
    trans_depth: float
    response_body_len: float
    ct_srv_src: float
    ct_state_ttl: float
    ct_dst_ltm: float
    ct_src_dport_ltm: float
    ct_dst_sport_ltm: float
    ct_dst_src_ltm: float
    is_ftp_login: float
    ct_ftp_cmd: float
    ct_flw_http_mthd: float
    ct_src_ltm: float
    ct_srv_dst: float
    is_sm_ips_ports: float


# =========================================================
# PREDICTION
# =========================================================

@app.post("/api/predict")
def predict(
    request: TrafficRequest,
    db: Session = Depends(get_db)
):
    try:
        traffic_data = request.model_dump()

        # =========================
        # ML PREDICTION
        # =========================

        result = predict_threat(traffic_data)

        # =========================
        # SAVE TRAFFIC LOG
        # =========================

        traffic_log = TrafficLog(
            prediction=result["prediction"],
            attack_category=result.get("attack_category"),
            confidence=result["confidence"],
            protocol=request.proto,
            service=request.service,
            state=request.state
        )

        db.add(traffic_log)
        db.commit()
        db.refresh(traffic_log)

        # =========================
        # CREATE ALERT FOR ATTACK
        # =========================

        alert_id = None

        if result["prediction"] == "Attack":

            attack_category = result.get(
                "attack_category",
                "Unknown"
            )

            confidence = result["confidence"]

            # ---------------------------------
            # Demo severity rules
            # ---------------------------------

            if attack_category in ["DoS", "Backdoor", "Shellcode"]:
                severity = "Critical"

            elif attack_category in ["Exploits", "Fuzzers", "Generic"]:
                severity = "High"

            elif attack_category in ["Reconnaissance", "Analysis"]:
                severity = "Medium"

            else:
                severity = "Low"

            # ---------------------------------
            # Create alert description
            # ---------------------------------

            description = (
                f"{attack_category} attack detected. "
                f"ML confidence: {confidence:.2%}. "
                f"Protocol: {request.proto}, "
                f"Service: {request.service}, "
                f"State: {request.state}."
            )

            alert = Alert(
                type=attack_category,
                severity=severity,
                description=description,
                status="active"
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)

            alert_id = alert.id

        # =========================
        # RESPONSE
        # =========================

        result["log_id"] = traffic_log.id
        result["alert_id"] = alert_id

        return result

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
# =========================================================
# GET TRAFFIC LOGS
# =========================================================

@app.get("/api/traffic")
def get_traffic(
    db: Session = Depends(get_db)
):

    try:

        logs = (
            db.query(TrafficLog)
            .order_by(TrafficLog.timestamp.desc())
            .limit(100)
            .all()
        )

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "prediction": log.prediction,
                "attack_category": log.attack_category,
                "confidence": log.confidence,
                "protocol": log.protocol,
                "service": log.service,
                "state": log.state
            }
            for log in logs
        ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve traffic logs: {str(e)}"
        )

# =========================================================
# GET ALERTS
# =========================================================

@app.get("/api/alerts")
def get_alerts(
    db: Session = Depends(get_db)
):

    try:

        alerts = (
            db.query(Alert)
            .order_by(Alert.timestamp.desc())
            .limit(100)
            .all()
        )

        return [
            {
                "id": alert.id,
                "timestamp": alert.timestamp,
                "type": alert.type,
                "severity": alert.severity,
                "description": alert.description,
                "status": alert.status
            }
            for alert in alerts
        ]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve alerts: {str(e)}"
        )

@app.get("/api/statistics")
def get_statistics(db: Session = Depends(get_db)):

    traffic_logs = (
        db.query(TrafficLog)
        .order_by(TrafficLog.timestamp.desc())
        .limit(500)
        .all()
    )

    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc())
        .limit(500)
        .all()
    )

    total_traffic = len(traffic_logs)

    normal_traffic = sum(
        1 for log in traffic_logs
        if log.prediction == "Normal"
    )

    attack_traffic = sum(
        1 for log in traffic_logs
        if log.prediction == "Attack"
    )

    critical_alerts = sum(
        1 for alert in alerts
        if alert.severity == "Critical"
    )

    high_alerts = sum(
        1 for alert in alerts
        if alert.severity == "High"
    )

    medium_alerts = sum(
        1 for alert in alerts
        if alert.severity == "Medium"
    )

    low_alerts = sum(
        1 for alert in alerts
        if alert.severity == "Low"
    )

    attack_distribution = {}

    for log in traffic_logs:

        if log.prediction != "Attack":
            continue

        category = log.attack_category or "Unknown"

        attack_distribution[category] = (
            attack_distribution.get(category, 0) + 1
        )

    return {
        "total_traffic": total_traffic,
        "normal_traffic": normal_traffic,
        "attack_traffic": attack_traffic,

        "normal_percentage": (
            round((normal_traffic / total_traffic) * 100, 2)
            if total_traffic > 0
            else 0
        ),

        "attack_percentage": (
            round((attack_traffic / total_traffic) * 100, 2)
            if total_traffic > 0
            else 0
        ),

        "total_alerts": len(alerts),
        "critical_alerts": critical_alerts,
        "high_alerts": high_alerts,
        "medium_alerts": medium_alerts,
        "low_alerts": low_alerts,

        "attack_distribution": attack_distribution
    }

# =========================================================
# TIME-SERIES ANALYTICS
# =========================================================

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):

    traffic_logs = (
        db.query(TrafficLog)
        .order_by(TrafficLog.timestamp.asc())
        .limit(500)
        .all()
    )

    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.asc())
        .limit(500)
        .all()
    )

    traffic_buckets = defaultdict(
        lambda: {
            "total": 0,
            "normal": 0,
            "attack": 0
        }
    )

    alert_buckets = defaultdict(int)

    attack_category_buckets = defaultdict(
        lambda: defaultdict(int)
    )

    # =====================================================
    # PROCESS TRAFFIC
    # =====================================================

    for log in traffic_logs:

        if not log.timestamp:
            continue

        bucket_time = log.timestamp.replace(
            second=0,
            microsecond=0
        )

        bucket_key = bucket_time.isoformat()

        traffic_buckets[bucket_key]["total"] += 1

        if log.prediction == "Attack":

            traffic_buckets[bucket_key]["attack"] += 1

            category = (
                log.attack_category
                or "Unknown"
            )

            attack_category_buckets[
                bucket_key
            ][category] += 1

        else:

            traffic_buckets[bucket_key]["normal"] += 1

    # =====================================================
    # PROCESS ALERTS
    # =====================================================

    for alert in alerts:

        if not alert.timestamp:
            continue

        bucket_time = alert.timestamp.replace(
            second=0,
            microsecond=0
        )

        bucket_key = bucket_time.isoformat()

        alert_buckets[bucket_key] += 1

    # =====================================================
    # CREATE TRAFFIC TIMELINE
    # =====================================================

    all_times = sorted(
        set(
            traffic_buckets.keys()
        ).union(
            alert_buckets.keys()
        )
    )

    timeline = []

    for timestamp in all_times:

        traffic_data = traffic_buckets.get(
            timestamp,
            {
                "total": 0,
                "normal": 0,
                "attack": 0
            }
        )

        timeline.append({

            "timestamp": timestamp,

            "total": traffic_data["total"],

            "normal": traffic_data["normal"],

            "attack": traffic_data["attack"],

            "alerts": alert_buckets.get(
                timestamp,
                0
            )

        })

    # =====================================================
    # CREATE ATTACK CATEGORY TIMELINE
    # =====================================================

    attack_timeline = []

    for timestamp in all_times:

        categories = dict(
            attack_category_buckets.get(
                timestamp,
                {}
            )
        )

        attack_timeline.append({

            "timestamp": timestamp,

            "categories": categories

        })

    # =====================================================
    # RETURN
    # =====================================================

    return {

        "timeline": timeline[-30:],

        "attack_timeline":
            attack_timeline[-30:]

    }

# =========================================================
# SIMULATION CONTROL
# =========================================================

@app.post("/api/simulation/start")
def start_simulation():

    started = simulation_service.start()

    return {
        "success": started,
        "running": simulation_service.running,
        "message": (
            "Traffic simulation started."
            if started
            else (
                "Traffic simulation is already running "
                "or could not be started."
            )
        )
    }


@app.post("/api/simulation/stop")
def stop_simulation():

    stopped = simulation_service.stop()

    return {
        "success": True,
        "running": simulation_service.running,
        "message": (
            "Traffic simulation stopped."
            if stopped
            else "Traffic simulation is already stopped."
        )
    }


@app.get("/api/simulation/status")
def simulation_status():

    return simulation_service.status()