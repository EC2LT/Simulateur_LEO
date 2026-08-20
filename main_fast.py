"""
Simulateur Starlink - Version rapide avec 100 satellites
"""

import os
from datetime import datetime
from src.tle_loader import load_tle_from_file
from src.simulation import Simulation
from src.visualization import (
    plot_rtt, plot_doppler, plot_visible_satellites, 
    plot_elevation, create_3d_globe
)


def get_station_pos(lat, lon, alt=0):
    import math
    R = 6371.0
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = (R + alt) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (R + alt) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (R + alt) * math.sin(lat_rad)
    return (x, y, z)


def main():
    print("=" * 60)
    print("   SIMULATEUR STARLINK - VERSION RAPIDE")
    print("=" * 60)
    
    station_name = "Dakar"
    station_lat = 14.7167
    station_lon = -17.4677
    station_pos = get_station_pos(station_lat, station_lon)
    
    print(f"\n📍 Station sol : {station_name}")
    tle_file = "data/tle/starlink.txt"
    
    if not os.path.exists(tle_file):
        print(f"⚠️ Fichier TLE introuvable")
        return
    
    # Charger seulement 100 satellites
    print("📡 Chargement de 100 satellites...")
    satellites = load_tle_from_file(tle_file, max_satellites=100)
    
    if len(satellites) == 0:
        print("❌ Aucun satellite chargé")
        return
    
    print(f"✅ {len(satellites)} satellites chargés")
    
    # Lancer la simulation AVEC les satellites chargés
    print("🚀 Lancement de la simulation...")
    sim = Simulation(
        satellites=satellites,  # On passe directement les satellites
        station_name=station_name,
        station_pos=station_pos,
        start_time=datetime.now(),
        duration_hours=1,
        time_step=30
    )
    
    results = sim.run()
    
    # Afficher les résultats
    print("\n📊 RÉSULTATS")
    stats = results.get_rtt_stats()
    if stats:
        print(f"   RTT moyen: {stats['mean']:.2f} ms")
        print(f"   RTT min: {stats['min']:.2f} ms")
        print(f"   RTT max: {stats['max']:.2f} ms")
    
    print(f"   Handovers: {results.get_handover_count()}")
    
    # Visualisations
    print("\n📊 Visualisations...")
    plot_rtt(results)
    plot_doppler(results)
    plot_visible_satellites(results)
    plot_elevation(results)
    
    print("✅ Terminé")


if __name__ == "__main__":
    main()
