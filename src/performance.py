import numpy as np
from skyfield.api import load, wgs84

C_LIGHT = 299792.458  # Vitesse de la lumière en km/s
FREQ_KU = 12.0e9      # 12 GHz Bande Ku

def compute_ground_station_metrics(satellites, positions_dict, t_skyfield, gs_lat, gs_lon, min_elevation=25.0):
    ts = load.timescale()
    station = wgs84.latlon(gs_lat, gs_lon)
    num_steps = len(t_skyfield)

    best_elevation = np.full(num_steps, 0.0)
    best_distance = np.full(num_steps, np.nan)
    best_rtt = np.full(num_steps, np.nan)
    best_doppler = np.full(num_steps, 0.0)
    best_sat_names = [None] * num_steps
    visible_count = np.zeros(num_steps, dtype=int)

    gs_pos = station.at(t_skyfield).position.km  # Shape: (3, N_steps)

    for sat in satellites:
        sat_pos = positions_dict[sat.name]
        rel_pos = sat_pos - gs_pos
        distances = np.linalg.norm(rel_pos, axis=0)

        topocentric = (sat - station).at(t_skyfield)
        alt, _, _ = topocentric.altaz()
        elevations = alt.degrees

        visible_mask = elevations >= min_elevation
        visible_count += visible_mask.astype(int)

        velocities = topocentric.velocity.km_per_s
        radial_velocities = np.einsum('ij,ij->j', rel_pos, velocities) / distances
        doppler_shift = - (radial_velocities / C_LIGHT) * FREQ_KU

        # Calcul RTT physique réaliste : 2 x Distance / c + délai traitement (~12 ms)
        rtt_ms = ((2.0 * distances) / C_LIGHT) * 1000.0 + 12.0

        for i in range(num_steps):
            if visible_mask[i] and elevations[i] > best_elevation[i]:
                best_elevation[i] = elevations[i]
                best_distance[i] = distances[i]
                best_rtt[i] = rtt_ms[i]
                best_doppler[i] = doppler_shift[i]
                best_sat_names[i] = sat.name

    # Détection propre des Handovers (Commutations)
    handovers = []
    for i in range(1, num_steps):
        if best_sat_names[i] != best_sat_names[i-1] and best_sat_names[i] is not None and best_sat_names[i-1] is not None:
            handovers.append(i)

    # Nettoyage des valeurs RTT manquantes par interpolation si nécessaire
    nans = np.isnan(best_rtt)
    if np.any(nans):
        best_rtt[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(~nans), best_rtt[~nans])

    return {
        "elevation": best_elevation,
        "distance": best_distance,
        "rtt": best_rtt,
        "doppler": best_doppler,
        "visible_count": visible_count,
        "active_sats": best_sat_names,
        "handovers": handovers
    }
