"""
Exécuté par GitHub Actions (voir .github/workflows/garmin-sync.yml).
Ne stocke jamais de mot de passe : reprend une session déjà ouverte à partir
du secret GARMIN_TOKENS_B64 (généré une fois en local avec generate_tokens.py).

Écrit data/garmin-sessions.json au format attendu par l'app cockpit-sport.html.
"""
import base64
import io
import json
import os
import sys
import tarfile
from datetime import datetime, timedelta
from pathlib import Path

import garminconnect

TOKEN_DIR = Path("/tmp/garmin_tokens")
OUTPUT_FILE = Path("data/garmin-sessions.json")
DAYS_BACK = 10  # marge large pour couvrir la semaine + une éventuelle interruption de sync

TYPE_MAP = {
    "running": "course",
    "trail_running": "course",
    "treadmill_running": "course",
    "cycling": "velo",
    "mountain_biking": "velo",
    "road_biking": "velo",
    "indoor_cycling": "velo",
    "lap_swimming": "natation",
    "open_water_swimming": "natation",
    "strength_training": "muscu",
    "indoor_cardio": "muscu",
}


def restore_tokens():
    b64 = os.environ["GARMIN_TOKENS_B64"]
    buf = io.BytesIO(base64.b64decode(b64))
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        tar.extractall("/tmp")
    return TOKEN_DIR


def map_type(activity):
    type_key = (activity.get("activityType") or {}).get("typeKey", "")
    name = (activity.get("activityName") or "").lower()
    if "hyrox" in name:
        return "hyrox"
    return TYPE_MAP.get(type_key, "autre")


def to_session(activity):
    dist_m = activity.get("distance") or 0
    dur_s = activity.get("duration") or 0
    start = activity.get("startTimeLocal", "")[:10]
    return {
        "id": f"garmin_{activity['activityId']}",
        "date": start,
        "type": map_type(activity),
        "distance_km": round(dist_m / 1000, 2) if dist_m else None,
        "duration_min": round(dur_s / 60) if dur_s else None,
        "tonnage_kg": None,
        "notes": activity.get("activityName") or "",
        "source": "garmin",
    }


def main():
    token_dir = restore_tokens()
    client = garminconnect.Garmin()
    client.login(tokenstore=str(token_dir))

    end = datetime.now().date()
    start = end - timedelta(days=DAYS_BACK)
    activities = client.get_activities_by_date(start.isoformat(), end.isoformat())

    sessions = [to_session(a) for a in activities]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(sessions, ensure_ascii=False, indent=2))
    print(f"{len(sessions)} activités écrites dans {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erreur de synchro Garmin : {e}", file=sys.stderr)
        sys.exit(1)
