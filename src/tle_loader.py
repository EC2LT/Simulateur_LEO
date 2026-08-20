"""
Module TLE LOADER
Rôle : Charger les fichiers TLE et créer des objets Satellite
"""

from skyfield.api import EarthSatellite
import os
import re

class Satellite:
    """Représente un satellite Starlink avec ses données orbitales"""
    
    def __init__(self, name, norad_id, line1, line2):
        self.name = name
        self.norad_id = norad_id
        self.line1 = line1
        self.line2 = line2
        self.model = None
        self.inclination = None  # Sera extrait de la ligne TLE
    
    def __repr__(self):
        return f"Satellite({self.name}, NORAD: {self.norad_id})"


def extract_inclination(line2):
    """
    Extrait l'inclinaison depuis la ligne 2 du TLE.
    Positions 8-16 dans le format TLE.
    """
    try:
        return float(line2[8:16])
    except:
        return None


def load_tle_from_file(filepath, max_satellites=500, filter_by_inclination=True):
    """
    Charge les TLE depuis un fichier texte.
    
    Args:
        filepath (str): Chemin vers le fichier TLE
        max_satellites (int): Nombre maximum de satellites à charger
        filter_by_inclination (bool): Filtrer pour garder les inclinaisons utiles
    
    Returns:
        list: Liste d'objets Satellite
    """
    
    satellites = []
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier TLE introuvable : {filepath}")
    
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines if line.strip()]
    
    # Inclinaisons utiles pour Dakar (14.7°)
    # 53° donne une bonne couverture pour les latitudes tropicales
    # 97.6° (polaire) donne aussi une couverture
    useful_inclinations = [53.0, 70.0, 97.6, 43.0, 53.2]
    
    loaded = 0
    
    for i in range(0, len(lines), 3):
        if loaded >= max_satellites:
            break
            
        if i + 2 < len(lines):
            name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            
            # Extraire le NORAD ID
            try:
                norad_id = int(line1[2:7])
            except:
                norad_id = 0
            
            # Filtrer par inclinaison
            if filter_by_inclination:
                inclination = extract_inclination(line2)
                if inclination is None:
                    continue
                # Garder les satellites avec des inclinaisons proches des coquilles utiles
                # ou en dessous de 60° pour une meilleure visibilité depuis Dakar
                if inclination > 60.0:
                    continue
                # Si l'inclinaison est entre 40° et 60°, c'est bon
                if 40.0 <= inclination <= 60.0:
                    satellite = Satellite(name, norad_id, line1, line2)
                    satellite.inclination = inclination
                    satellites.append(satellite)
                    loaded += 1
            else:
                satellite = Satellite(name, norad_id, line1, line2)
                satellites.append(satellite)
                loaded += 1
    
    print(f"✅ {len(satellites)} satellites chargés sur {len(lines)//3} totaux")
    return satellites
