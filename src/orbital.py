import numpy as np
from skyfield.api import load, EarthSatellite

def load_satellites_from_tle(tle_file_path):
    """
    Charge les satellites à partir d'un fichier TLE local.
    """
    ts = load.timescale()
    satellites = load.tle_file(tle_file_path, ts=ts)
    return satellites

def propagate_constellation_vectorized(satellites, times_list):
    """
    Calcule les positions (x, y, z) géocentriques en km
    pour TOUS les satellites et TOUS les pas de temps simultanément.
    
    Retourne:
        dict: {sat_name: array_3d de shape (3, N_steps)}
    """
    ts = load.timescale()
    # Conversion de la liste de datetimes UTC en un objet Time vectorisé Skyfield
    t_skyfield = ts.utc(
        [t.year for t in times_list],
        [t.month for t in times_list],
        [t.day for t in times_list],
        [t.hour for t in times_list],
        [t.minute for t in times_list],
        [t.second for t in times_list]
    )
    
    positions = {}
    for sat in satellites:
        geocentric = sat.at(t_skyfield)
        positions[sat.name] = geocentric.position.km  # Matrice (3, N_steps)
        
    return positions, t_skyfield
