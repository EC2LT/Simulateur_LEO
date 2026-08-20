"""
Simulateur Starlink - Version Complète
Affiche le RTT, le Doppler, le nombre de satellites visibles, l'angle d'élévation, le globe 3D.
"""

import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt

# On s'assure que le backend de matplotlib est correct pour l'affichage
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Utilise Tkinter pour l'affichage interactif
except ImportError:
    pass

# Importation des modules du simulateur
from src.tle_loader import load_tle_from_file
from src.simulation import Simulation
from src.visualization import (
    plot_rtt,
    plot_doppler,
    plot_visible_satellites,
    plot_elevation,
    plot_handover_timeline,
    create_3d_globe,
)

def get_station_pos(lat, lon, alt=0):
    """
    Convertit les coordonnées géographiques (latitude, longitude, altitude)
    en coordonnées cartésiennes (x, y, z) en kilomètres.
    """
    import math
    R = 6371.0  # Rayon de la Terre en km
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = (R + alt) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (R + alt) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (R + alt) * math.sin(lat_rad)
    return (x, y, z)

def main():
    print("=" * 70)
    print("   SIMULATEUR STARLINK - CONSTELLATION LEO (VERSION COMPLÈTE)")
    print("=" * 70)
    
    # ---- Configuration de la station sol ----
    station_name = "Dakar"
    station_lat = 14.7167
    station_lon = -17.4677
    station_pos = get_station_pos(station_lat, station_lon)
    print(f"\n📍 Station sol : {station_name} (lat: {station_lat}°, lon: {station_lon}°)")
    
    # ---- Paramètres de la simulation ----
    # Pour un test rapide, on simule 2 heures avec 200 satellites.
    # Vous pouvez augmenter ces valeurs pour une simulation plus réaliste.
    DUREE_HEURES = 2
    PAS_TEMPS_SECONDES = 30
    NOMBRE_SATELLITES = 200
    
    print(f"\n⚙️  Paramètres :")
    print(f"   - Durée de simulation : {DUREE_HEURES} heures")
    print(f"   - Pas de temps : {PAS_TEMPS_SECONDES} secondes")
    print(f"   - Nombre de satellites : {NOMBRE_SATELLITES}")
    
    # ---- Chargement des fichiers TLE ----
    tle_file = "data/tle/starlink.txt"
    if not os.path.exists(tle_file):
        print(f"\n❌ Fichier TLE introuvable : {tle_file}")
        print("   Téléchargez-le depuis :")
        print("   https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
        return
    
    print("\n📡 Chargement des satellites...")
    satellites = load_tle_from_file(tle_file, max_satellites=NOMBRE_SATELLITES)
    
    if len(satellites) == 0:
        print("❌ Aucun satellite chargé. Vérifiez votre fichier TLE.")
        return
    print(f"✅ {len(satellites)} satellites chargés avec succès.")
    
    # ---- Lancement de la simulation ----
    print("\n🚀 Lancement de la simulation...")
    sim = Simulation(
        satellites=satellites,
        station_name=station_name,
        station_pos=station_pos,
        start_time=datetime.now(),
        duration_hours=DUREE_HEURES,
        time_step=PAS_TEMPS_SECONDES,
    )
    results = sim.run()
    
    # ---- Affichage des résultats statistiques ----
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS DE LA SIMULATION")
    print("=" * 70)
    
    stats = results.get_rtt_stats()
    if stats:
        print(f"\n📈 Statistiques du RTT depuis {station_name} :")
        print(f"   - RTT minimum : {stats['min']:.2f} ms")
        print(f"   - RTT maximum : {stats['max']:.2f} ms")
        print(f"   - RTT moyen   : {stats['mean']:.2f} ms")
        print(f"   - Écart-type  : {stats['std']:.2f} ms")
    else:
        print("\n⚠️ Aucune donnée RTT valide n'a été générée.")
    
    nb_handovers = results.get_handover_count()
    print(f"\n🔄 Nombre de handovers détectés : {nb_handovers}")
    
    # ---- Visualisations ----
    print("\n" + "=" * 70)
    print("📊 GÉNÉRATION DES VISUALISATIONS")
    print("=" * 70)
    
    # Les visualisations s'ouvrent chacune dans une fenêtre séparée.
    # Vous devez les fermer (clic sur la croix) pour passer à la suivante.

    print("\n1. Graphique du RTT (latence)...")
    plot_rtt(results)
    
    print("\n2. Graphique du Doppler...")
    plot_doppler(results)
    
    print("\n3. Graphique du nombre de satellites visibles...")
    plot_visible_satellites(results)
    
    print("\n4. Graphique de l'angle d'élévation...")
    plot_elevation(results)
    
    if results.handovers:
        print("\n5. Chronologie des handovers...")
        plot_handover_timeline(results)
    else:
        print("\n5. Pas de handover à afficher.")
    
    print("\n6. Globe 3D interactif...")
    # Le globe 3D s'ouvre dans votre navigateur. Vous pouvez zoomer, faire pivoter, etc.
    create_3d_globe(
        satellites=sim.satellites,
        time=datetime.now(),
        station_pos=station_pos,
    )
    
    print("\n" + "=" * 70)
    print("✅ Simulation terminée avec succès !")
    print("   Vous pouvez fermer les fenêtres de visualisation.")
    print("=" * 70)

if __name__ == "__main__":
    main()
