import os
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec

METRICS_PATH = "Q:/quantum_metrics.parquet"

def run_visualizer():
    plt.ion() # Interactive mode
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('Quantum Semantic Decay (RAM Disk Parquet Tracking)', fontsize=16)
    
    # Grid spec for 3 panels left, 1 3D panel right
    gs = GridSpec(3, 2, figure=fig)
    
    ax_dist = fig.add_subplot(gs[0, 0])
    ax_vel = fig.add_subplot(gs[1, 0])
    ax_ent = fig.add_subplot(gs[2, 0])
    
    ax_3d = fig.add_subplot(gs[:, 1], projection='3d')
    ax_ent_twin = ax_ent.twinx()
    
    print(f"Waiting for telemetry from {METRICS_PATH}...")
    
    while True:
        if os.path.exists(METRICS_PATH):
            try:
                df = pd.read_parquet(METRICS_PATH)
                if df.empty: 
                    time.sleep(1)
                    continue
                
                loops = df['loop'].values
                dists = df['dist'].values
                vels = df['vel'].values
                interf = df['interf'].values
                ent = df['entropy'].values
                eps = df['eps'].values
                
                ax_dist.clear()
                ax_vel.clear()
                ax_ent.clear()
                ax_ent_twin.clear()
                ax_3d.clear()
                
                # Panel 1: Orbital Decay (Distance)
                ax_dist.plot(loops, dists, color='purple', label='Distance to Self')
                ax_dist.set_title('Orbital Decay (Distance to Origin)')
                ax_dist.grid(True, alpha=0.3)
                
                # Panel 2: Contextual Delta
                ax_vel.plot(loops, vels, color='teal', label='Contextual Delta')
                ax_vel.set_title('Contextual Delta (Velocity)')
                ax_vel.set_yscale('log')
                ax_vel.grid(True, alpha=0.3)
                
                # Panel 3: Attention Entropy & Phase Shift Background
                ax_ent.plot(loops, ent, color='coral', label='Attention Entropy')
                ax_ent_twin.plot(loops, eps, color='red', linestyle='--', alpha=0.5, label='Epsilon Tripwire')
                ax_ent.set_title('Attention Entropy & Epsilon Tripwire')
                ax_ent.set_xlabel('Loop Iteration')
                ax_ent.grid(True, alpha=0.3)
                
                # 3D Phase-Space Graph
                ax_3d.plot(dists, vels, interf, color='indigo', linewidth=1.5, alpha=0.7)
                ax_3d.scatter(dists[-1], vels[-1], interf[-1], color='red', s=50, label='Singularity')
                ax_3d.set_title('3D Phase-Space Orbit (Dist, Vel, Interf)')
                ax_3d.set_xlabel('Distance to Self')
                ax_3d.set_ylabel('Velocity')
                ax_3d.set_zlabel('Phase Shift (w_n)')
                ax_3d.legend()
                
                plt.pause(1)
            except Exception as e:
                time.sleep(1)
        else:
            time.sleep(1)

if __name__ == "__main__":
    run_visualizer()
