"""
Module HANDOVER
Rôle : Gérer le changement de satellite servant
"""

from src.performance import is_visible, compute_elevation_angle


class HandoverEvent:
    """Représente un événement de handover"""
    
    def __init__(self, timestamp, old_sat, new_sat, old_elevation, new_elevation):
        self.timestamp = timestamp
        self.old_sat = old_sat
        self.new_sat = new_sat
        self.old_elevation = old_elevation
        self.new_elevation = new_elevation
    
    def __repr__(self):
        return f"Handover: {self.old_sat} -> {self.new_sat} at {self.timestamp}"


class HandoverManager:
    """Gère le processus de handover"""
    
    def __init__(self, threshold=25.0):
        self.current_satellite = None
        self.handover_history = []
        self.threshold = threshold
    
    def find_best_satellite(self, satellites_with_metrics):
        """
        Trouve le meilleur satellite parmi ceux visibles.
        
        Args:
            satellites_with_metrics (list): Liste de tuples (satellite, métriques)
                où métriques contient 'elevation' et 'visible'
        
        Returns:
            tuple: (meilleur_satellite, metriques) ou (None, None) si aucun visible
        """
        visible_satellites = []
        
        for sat, metrics in satellites_with_metrics:
            if metrics['visible']:
                visible_satellites.append((sat, metrics))
        
        if not visible_satellites:
            return None, None
        
        # Choisir celui avec le plus grand angle d'élévation
        best = max(visible_satellites, key=lambda x: x[1]['elevation'])
        return best[0], best[1]
    
    def update(self, satellites_with_metrics, timestamp):
        """
        Met à jour le satellite servant et gère les handovers.
        
        Args:
            satellites_with_metrics (list): Liste de tuples (satellite, métriques)
            timestamp (datetime): Instant actuel
        
        Returns:
            tuple: (satellite_servant, handover_event) ou (None, None)
        """
        best_sat, best_metrics = self.find_best_satellite(satellites_with_metrics)
        
        handover_event = None
        
        if best_sat is None:
            # Aucun satellite visible
            self.current_satellite = None
            return None, None
        
        if self.current_satellite is None:
            # Premier satellite
            self.current_satellite = best_sat
            return best_sat, None
        
        if self.current_satellite.norad_id != best_sat.norad_id:
            # Changement de satellite : handover
            old_elevation = None
            for sat, metrics in satellites_with_metrics:
                if sat.norad_id == self.current_satellite.norad_id:
                    old_elevation = metrics['elevation']
                    break
            
            if old_elevation is None:
                old_elevation = 0
            
            handover_event = HandoverEvent(
                timestamp=timestamp,
                old_sat=self.current_satellite.name,
                new_sat=best_sat.name,
                old_elevation=old_elevation,
                new_elevation=best_metrics['elevation']
            )
            
            self.handover_history.append(handover_event)
            self.current_satellite = best_sat
        
        return self.current_satellite, handover_event
    
    def get_handover_count(self):
        """Retourne le nombre de handovers"""
        return len(self.handover_history)
    
    def get_handover_history(self):
        """Retourne l'historique des handovers"""
        return self.handover_history
