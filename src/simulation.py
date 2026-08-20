"""
Module SIMULATION (Version corrigée)
"""
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.tle_loader import load_tle_from_file
from src.orbital import get_position, get_velocity, init_all_satellites
from src.performance import compute_all_metrics
from src.handover import HandoverManager


class Simulation:
    def __init__(self, tle_file=None, satellites=None, station_name="Dakar", station_pos=None,
                 start_time=None, duration_hours=6, time_step=30):
        self.station_name = station_name
        self.station_pos = station_pos
        self.time_step = time_step

        if satellites is not None:
            self.satellites = satellites
            print(f"✅ {len(satellites)} satellites utilisés")
        elif tle_file is not None:
            print("📡 Chargement des TLE...")
            self.satellites = load_tle_from_file(tle_file)
        else:
            raise ValueError("Il faut fournir soit tle_file soit satellites")

        print("🔄 Initialisation des modèles orbitaux...")
        init_all_satellites(self.satellites)

        if start_time is None:
            self.start_time = datetime.now()
        else:
            self.start_time = start_time

        self.end_time = self.start_time + timedelta(hours=duration_hours)
        total_seconds = duration_hours * 3600
        self.num_steps = int(total_seconds / time_step) + 1

        print(f"📊 Simulation : {duration_hours}h, pas de {time_step}s")
        print(f"   Début : {self.start_time}")
        print(f"   Fin   : {self.end_time}")
        print(f"   Étapes: {self.num_steps}")

        self.handover_manager = HandoverManager()
        self.results = None

    def run(self):
        print("🚀 Lancement de la simulation...")
        times = []
        visible_count = []
        current_satellite_id = []
        rtt_values = []
        doppler_values = []
        elevation_values = []

        current_time = self.start_time
        total_steps = self.num_steps
        step_counter = 0

        for step in range(total_steps):
            if step % 100 == 0 and step > 0:
                progress = (step / total_steps) * 100
                print(f"   Progression: {progress:.1f}%")

            times.append(current_time)
            satellites_metrics = []

            for sat in self.satellites:
                try:
                    pos = get_position(sat, current_time)
                    vel = get_velocity(sat, current_time)
                    metrics = compute_all_metrics(pos, vel, self.station_pos)
                    satellites_metrics.append((sat, metrics))
                except Exception:
                    continue

            visible = [m['visible'] for _, m in satellites_metrics]
            visible_count.append(sum(visible))

            best_sat, handover_event = self.handover_manager.update(
                satellites_metrics, current_time
            )

            if best_sat is not None:
                current_satellite_id.append(best_sat.norad_id)
                for sat, metrics in satellites_metrics:
                    if sat.norad_id == best_sat.norad_id:
                        rtt_values.append(metrics['rtt'])
                        doppler_values.append(metrics['doppler'])
                        elevation_values.append(metrics['elevation'])
                        break
            else:
                current_satellite_id.append(None)
                rtt_values.append(np.nan)
                doppler_values.append(np.nan)
                elevation_values.append(np.nan)

            current_time += timedelta(seconds=self.time_step)

        print("✅ Simulation terminée")
        print(f"   Handovers: {self.handover_manager.get_handover_count()}")

        self.results = SimulationResults(
            times=times,
            visible_count=visible_count,
            current_satellite_id=current_satellite_id,
            rtt_values=rtt_values,
            doppler_values=doppler_values,
            elevation_values=elevation_values,
            handovers=self.handover_manager.get_handover_history(),
            station_name=self.station_name
        )
        return self.results


class SimulationResults:
    def __init__(self, times, visible_count, current_satellite_id,
                 rtt_values, doppler_values, elevation_values,
                 handovers, station_name):
        self.times = times
        self.visible_count = visible_count
        self.current_satellite_id = current_satellite_id
        self.rtt_values = rtt_values
        self.doppler_values = doppler_values
        self.elevation_values = elevation_values
        self.handovers = handovers
        self.station_name = station_name

    def to_dataframe(self):
        return pd.DataFrame({
            'time': self.times,
            'visible_satellites': self.visible_count,
            'current_satellite': self.current_satellite_id,
            'rtt_ms': self.rtt_values,
            'doppler_hz': self.doppler_values,
            'elevation_deg': self.elevation_values
        })

    def get_rtt_stats(self):
        valid_rtt = [r for r in self.rtt_values if not np.isnan(r)]
        if valid_rtt:
            return {
                'min': min(valid_rtt),
                'max': max(valid_rtt),
                'mean': np.mean(valid_rtt),
                'std': np.std(valid_rtt)
            }
        return None

    def get_handover_count(self):
        return len(self.handovers)
