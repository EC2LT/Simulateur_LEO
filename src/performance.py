import numpy as np
from skyfield.api import wgs84

def compute_ground_station_metrics(satellites, positions_dict, t_skyfield, gs_lat, gs_lon, min_elevation=25.0):
    ts_len = len(t_skyfield)
    gs_location = wgs84.latlon(gs_lat, gs_lon)

    rtt_list = []
    doppler_list = []
    elevation_list = []
    visible_count_list = []
    active_sats = []
    handovers = []

    current_sat = None
    c = 299792.458  # km/s
    f0 = 12e9       # Bande Ku (12 GHz)

    for i in range(ts_len):
        t = t_skyfield[i]
        visible_sats_at_t = []
        
        for sat in satellites:
            difference = sat - gs_location
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()
            
            elev_deg = alt.degrees
            if elev_deg >= min_elevation:
                pos = topocentric.position.km
                vel = topocentric.velocity.km_per_s
                range_rate = np.dot(pos, vel) / np.linalg.norm(pos)
                
                visible_sats_at_t.append({
                    'sat': sat,
                    'name': sat.name,
                    'elevation': elev_deg,
                    'distance': distance.km,
                    'range_rate': range_rate
                })

        visible_count_list.append(len(visible_sats_at_t))

        if not visible_sats_at_t:
            current_sat = None
            rtt_list.append(np.nan)
            doppler_list.append(0)
            elevation_list.append(0)
            active_sats.append("Aucun")
            continue

        visible_sats_at_t.sort(key=lambda x: x['elevation'], reverse=True)
        best_sat_info = visible_sats_at_t[0]

        # RÈGLE DE HANDOVER (Hystérésis de 10°)
        if current_sat is None:
            current_sat_info = best_sat_info
            if i > 0:
                handovers.append(i)
        else:
            match = next((s for s in visible_sats_at_t if s['name'] == current_sat['name']), None)
            
            # Conserve le satellite tant qu'il reste à au moins 40° ET n'est pas dépassé de 10°
            if match and match['elevation'] > 40.0 and (best_sat_info['elevation'] - match['elevation'] < 10.0):
                current_sat_info = match
            else:
                current_sat_info = best_sat_info
                handovers.append(i)

        current_sat = current_sat_info

        # Calcul RTT Aller-Retour Terre-Satellite-Terre (ms) + Latence minimale de traitement (~15ms)
        rtt_prop_ms = (2 * current_sat_info['distance'] / c) * 1000.0
        rtt_total_ms = rtt_prop_ms + 15.0  # Latence matérielle/traitement

        # Doppler (kHz)
        doppler_hz = - (current_sat_info['range_rate'] / c) * f0

        rtt_list.append(rtt_total_ms)
        doppler_list.append(doppler_hz)
        elevation_list.append(current_sat_info['elevation'])
        active_sats.append(current_sat_info['name'])

    return {
        "rtt": np.array(rtt_list),
        "doppler": np.array(doppler_list),
        "elevation": np.array(elevation_list),
        "visible_count": np.array(visible_count_list),
        "active_sats": active_sats,
        "handovers": handovers
    }
