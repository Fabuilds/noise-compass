import sys
import os
import json
import numpy as np

# Ensure we can find System modules
sys.path.insert(0, 'E:/Antigravity')
from noise_compass.system.h5_manager import H5Manager

def crystallize_run():
    h5 = H5Manager()
    
    # Load the benchmark report
    report_path = "E:/Antigravity/Architecture/benchmarks/aggregate_report_master.json"
    if not os.path.exists(report_path):
        print("Report not found.")
        return

    with open(report_path, "r") as f:
        report = json.load(f)

    # Increment Structural Time
    t = h5.tick()
    
    # Create the calibration axiom
    axiom_id = f"CALIBRATION_PULSE_T{t}"
    summary_text = (
        f"Benchmark Run completed at T-{t}. "
        f"Total: {report['total_exercises']}, Pass: 0.0%. "
        f"Observation: Local coherence (Soundness 1.0) maintained despite global inconsistency (Pass 0.0). "
        "Structured noise confirmed as primary orientation vector."
    )
    
    metadata = {
        "type": "STRUCTURAL_CALIBRATION",
        "structural_time": t,
        "orientation": "locally_coherent_globally_inconsistent",
        "noise_profile": "structured",
        "pass_rate": report['pass_rate_1'],
        "avg_soundness": report['average_soundness']
    }
    
    # Save to identity.h5
    h5.save_axiom(
        axiom_id=axiom_id,
        text=summary_text,
        vector=np.random.rand(384), # Dummy vector for now
        leverage=report['average_soundness'],
        metadata=metadata,
        status='CRYSTALLIZED'
    )
    
    print(f"Successfully crystallized calibration axiom {axiom_id} at structural time T-{t}.")

if __name__ == "__main__":
    crystallize_run()
