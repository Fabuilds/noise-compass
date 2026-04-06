"""
flag_registry.py — FlagRegistry as first-class component.

The flags currently live in prose. This component makes them persistent,
attaching them to specific code locations, gap descriptions, or god-token candidates.
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class Flag:
    id: str
    target: str          # Code location, god-token ID, or gap ID
    state: str           # "STRUCTURAL", "SPECULATIVE", "SUPERPOSITION", "NEED_REFIND"
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class FlagRegistry:
    """
    A persistent registry of architectural flags.
    """
    
    def __init__(self, save_path: str = "E:/Antigravity/Architecture/archives/flag_registry.json"):
        self.save_path = Path(save_path)
        self.flags: Dict[str, Flag] = {}
        self.load()
        
    def raise_flag(self, flag_id: str, target: str, state: str, description: str, **metadata):
        """Raise or update a flag."""
        self.flags[flag_id] = Flag(
            id=flag_id,
            target=target,
            state=state,
            description=description,
            metadata=metadata
        )
        self.save()
        
    def get_flag(self, flag_id: str) -> Optional[Flag]:
        return self.flags.get(flag_id)
        
    def list_flags(self, state_filter: Optional[str] = None) -> List[Flag]:
        if state_filter:
            return [f for f in self.flags.values() if f.state == state_filter]
        return list(self.flags.values())
        
    def save(self):
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            data = {fid: {
                'id': f.id,
                'target': f.target,
                'state': f.state,
                'description': f.description,
                'timestamp': f.timestamp,
                'metadata': f.metadata
            } for fid, f in self.flags.items()}
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[REGR] Failed to save flags: {e}")
            
    def load(self):
        if not self.save_path.exists():
            return
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                for fid, d in data.items():
                    self.flags[fid] = Flag(**d)
        except Exception as e:
            print(f"[REGR] Failed to load flags: {e}")

    def handoff_output(self) -> str:
        """Generates the handoff text from the registry."""
        lines = ["# Architectural Flags Registry\n"]
        for f in sorted(self.flags.values(), key=lambda x: x.timestamp, reverse=True):
            lines.append(f"### {f.id} [{f.state}]")
            lines.append(f"**Target:** `{f.target}`")
            lines.append(f"{f.description}")
            if f.metadata:
                lines.append(f"**Metadata:** {f.metadata}")
            lines.append("")
        return "\n".join(lines)
