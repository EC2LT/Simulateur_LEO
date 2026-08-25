import numpy as np
from skyfield.api import load

def load_satellites_from_tle(tle_path):
    """
    Charge les satellites depuis le fichier TLE et filtre exclusivement 
    la constellation Starlink (LEO) pour écarter les satellites GEO/MEO.
    """
    raw_satellites = load.tle_file(tle_path)
    
    # Filtre strict : Uniquement les satellites Starlink
    starlink_satellites = [
        sat for sat in raw_satellites 
        if "STARLINK" in sat.name.upper()
    ]
    
    print(f"  └─ {len(starlink_satellites)} satellites Starlink (LEO) retenus sur {len(raw_satellites)} TLE au total.")
    return starlink_satellites

def propagate_constellation_vectorized(satellites, times_list):
    """
    Propage les orbites de l'ensemble des satellites retenus sur l'intervalle temporel donné.
    """
    ts = load.timescale()
    
    t_skyfield = ts.utc([t.year for t in times_list],
                        [t.month for t in times_list],
                        [t.day for t in times_list],
                        [t.hour for t in times_list],
                        [t.minute for t in times_list],
                        [t.second for t in times_list])
    
    positions_dict = {}
    
    for sat in satellites:
        geocentric = sat.at(t_skyfield)
        positions_dict[sat.name] = geocentric.position.km
        
    return positions_dict, t_skyfield
