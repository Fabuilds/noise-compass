import sys
import traceback
from noise_compass.architecture.tokens import ArchiverMessage

try:
    a = ArchiverMessage(
        energy_level=0.0,
        sheet_index=0,
        causal_type='',
        soup_provenance='',
        gap_structure={},
        fisher_alignment=0.0,
        sinkhorn_iterations=0,
        orbital_state=None,
        timestamp=0.0,
        degeneracy=0.0,
        content_preview='',
        zone='',
        routing='',
        apophatic_constraints=[],
        god_token_activations=[],
        collapsed_state=None,
        witness_phase=0.0,
        apophatic_contact=None,
        is_apophatic=True
    )
    print("Success")
except Exception as e:
    traceback.print_exc()
