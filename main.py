import datetime
import os
import urllib.request
from src.orbital import load_satellites_from_tle, propagate_constellation_vectorized
from src.performance import compute_ground_station_metrics
from src.visualization import display_dashboard

def get_tle_file_path():
    possible_paths = [
        os.path.join("data", "tle", "starlink.txt"),
        os.path.join("data", "tle", "starlink.tle"),
        os.path.join("data", "starlink.tle")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def run_simulation():
    print("==================================================")
    print("  SIMULATEUR DE CONSTELLATION LEO (STARLINK)     ")
    print("==================================================")
    
    tle_path = get_tle_file_path()
    if not tle_path:
        print("[ERREUR] Fichier TLE introuvable.")
        return

    print(f"[1/4] Chargement des TLE depuis {tle_path}...")
    satellites = load_satellites_from_tle(tle_path)

    start_time = datetime.datetime.now(datetime.timezone.utc)
    duration_minutes = 120
    step_seconds = 60

    times_list = [
        start_time + datetime.timedelta(seconds=i * step_seconds)
        for i in range(duration_minutes)
    ]
    time_labels = [t.strftime("%H:%M") for t in times_list]

    print("[2/4] Propagation des orbites vectorisée...")
    positions_dict, t_skyfield = propagate_constellation_vectorized(satellites, times_list)

    print("[3/4] Calcul des métriques & détection des Handovers...")
    GS_LAT, GS_LON = 14.7167, -17.4677
    metrics = compute_ground_station_metrics(
        satellites, positions_dict, t_skyfield, GS_LAT, GS_LON, min_elevation=25.0
    )

    print(f"      -> {len(metrics['handovers'])} handovers détectés sur 2 heures.")

    print("[4/4] Affichage de l'interface...")
    display_dashboard(satellites, positions_dict, metrics, time_labels, GS_LAT, GS_LON)

if __name__ == "__main__":
    run_simulation()
