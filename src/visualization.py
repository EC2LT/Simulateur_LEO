import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def display_dashboard(satellites, positions_dict, metrics, time_labels, gs_lat, gs_lon):
    fig = plt.figure(figsize=(16, 9))
    fig.canvas.manager.set_window_title("Simulateur Starlink Dakar - Vue Unifiée & Handover")

    gs = GridSpec(2, 4, figure=fig, height_ratios=[1.4, 1.0], hspace=0.38, wspace=0.28)

    # 1. GLOBE 3D
    ax_3d = fig.add_subplot(gs[0, :], projection='3d')
    ax_3d.set_title("Couverture Spatiale en Temps Réel - Station Sol Dakar", fontsize=13, fontweight='bold', pad=10)

    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    r_earth = 6378.137
    x_earth = r_earth * np.outer(np.cos(u), np.sin(v))
    y_earth = r_earth * np.outer(np.sin(u), np.sin(v))
    z_earth = r_earth * np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax_3d.plot_surface(x_earth, y_earth, z_earth, color='#1e88e5', alpha=0.35, edgecolor='#0d47a1', linewidth=0.3)

    sat_names = list(positions_dict.keys())[:30]
    for sat_name in sat_names:
        pos = positions_dict[sat_name]
        ax_3d.plot(pos[0, :], pos[1, :], pos[2, :], color='#26a69a', alpha=0.5, linewidth=1.0)
        ax_3d.scatter(pos[0, -1], pos[1, -1], pos[2, -1], color='orange', s=20, alpha=0.9)

    lat_rad, lon_rad = np.radians(gs_lat), np.radians(gs_lon)
    gs_x = r_earth * np.cos(lat_rad) * np.cos(lon_rad)
    gs_y = r_earth * np.cos(lat_rad) * np.sin(lon_rad)
    gs_z = r_earth * np.sin(lat_rad)
    ax_3d.scatter(gs_x, gs_y, gs_z, color='red', s=180, marker='^', label='Station Sol Dakar', zorder=10)

    max_range = r_earth + 700.0
    ax_3d.set_xlim(-max_range, max_range)
    ax_3d.set_ylim(-max_range, max_range)
    ax_3d.set_zlim(-max_range, max_range)
    ax_3d.axis('off')
    ax_3d.legend(loc="upper right", frameon=True, facecolor='white', framealpha=0.9)

    # 2. GRAPHES DE PERFORMANCE 2D
    num_steps = len(time_labels)
    x_indices = np.arange(num_steps)
    tick_interval = max(1, num_steps // 6)
    tick_positions = x_indices[::tick_interval]
    tick_labels = [time_labels[i] for i in tick_positions]

    handovers = metrics["handovers"]

    # --- Graphique 1: RTT (ms) - COURBE CONTINU ET NETTE ---
    ax_rtt = fig.add_subplot(gs[1, 0])
    
    # Nettoyage des valeurs aberrantes avant affichage
    rtt_clean = np.copy(metrics["rtt"])
    rtt_clean[(rtt_clean < 15) | (rtt_clean > 60)] = np.nan
    
    # Remplacement des NaN par interpolation pour garantir la courbe
    nans = np.isnan(rtt_clean)
    if np.any(nans) and not np.all(nans):
        rtt_clean[nans] = np.interp(np.flatnonzero(nans), np.flatnonzero(~nans), rtt_clean[~nans])

    # Affichage en ligne continue identique au graphe Doppler
    ax_rtt.plot(x_indices, rtt_clean, color='#d32f2f', linewidth=1.8, label='RTT (ms)')
    ax_rtt.axhline(y=35, color='black', linestyle='--', alpha=0.6, label='Ref (~35ms)')
    
    # Lignes verticales oranges pour les Handovers
    for ho in handovers:
        ax_rtt.axvline(x=ho, color='orange', linestyle='--', alpha=0.6, linewidth=1.0)

    ax_rtt.set_title("RTT & Handovers (ms)", fontsize=10, fontweight='bold')
    ax_rtt.set_ylabel("ms")
    ax_rtt.set_xticks(tick_positions)
    ax_rtt.set_xticklabels(tick_labels, rotation=25, ha='right', fontsize=8)
    ax_rtt.set_ylim(20, 50)  # Échelle verrouillée pour la lisibilité
    ax_rtt.grid(True, linestyle=':', alpha=0.6)
    ax_rtt.legend(fontsize=7, loc='upper right')

    # --- Graphique 2: Décalage Doppler (Inchangé) ---
    ax_doppler = fig.add_subplot(gs[1, 1])
    ax_doppler.plot(x_indices, metrics["doppler"] / 1e3, color='#1976d2', linewidth=1.5)
    ax_doppler.set_title("Décalage Doppler (kHz)", fontsize=10, fontweight='bold')
    ax_doppler.set_ylabel("kHz")
    ax_doppler.set_xticks(tick_positions)
    ax_doppler.set_xticklabels(tick_labels, rotation=25, ha='right', fontsize=8)
    ax_doppler.grid(True, linestyle=':', alpha=0.6)

    # --- Graphique 3: Élévation Maximale (°) ---
    ax_elev = fig.add_subplot(gs[1, 2])
    ax_elev.plot(x_indices, metrics["elevation"], color='#2e7d32', linewidth=1.8)
    ax_elev.axhline(y=25, color='red', linestyle='--', label='Masque (25°)')
    
    for ho in handovers:
        ax_elev.axvline(x=ho, color='orange', linestyle='--', alpha=0.6, linewidth=1.0)

    ax_elev.set_title("Élévation Maximale (°)", fontsize=10, fontweight='bold')
    ax_elev.set_ylabel("Degrés")
    ax_elev.set_xticks(tick_positions)
    ax_elev.set_xticklabels(tick_labels, rotation=25, ha='right', fontsize=8)
    ax_elev.set_ylim(20, 92)
    ax_elev.grid(True, linestyle=':', alpha=0.6)
    ax_elev.legend(fontsize=7, loc='lower right')

    # --- Graphique 4: Satellites Visibles ---
    ax_vis = fig.add_subplot(gs[1, 3])
    ax_vis.bar(x_indices, metrics["visible_count"], color='#7b1fa2', alpha=0.75, width=0.8)
    ax_vis.set_title("Satellites Visibles (>=25°)", fontsize=10, fontweight='bold')
    ax_vis.set_ylabel("Nombre")
    ax_vis.set_xticks(tick_positions)
    ax_vis.set_xticklabels(tick_labels, rotation=25, ha='right', fontsize=8)
    ax_vis.grid(True, linestyle=':', alpha=0.6)

    fig.subplots_adjust(top=0.93, bottom=0.12, left=0.04, right=0.96, hspace=0.38, wspace=0.28)
    plt.show()
