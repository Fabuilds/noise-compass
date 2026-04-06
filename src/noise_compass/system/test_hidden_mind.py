import os
import sys
import random
import time

# Mocking necessary parts of Ouroboros to test Hidden Mind logging
sys.path.append("E:/Antigravity/Runtime")
import phase1_color_compass

class MockOuroboros:
    def __init__(self):
        self.mode = "test"
        self.hidden_mind_path = f"e:/Antigravity/Runtime/ouroboros_{self.mode}_hidden_mind.txt"
        
    def log_hidden_mind(self, screen, stability, nodes):
        """Outputs the wave interference substrate to the hidden mind log."""
        timestamp = time.strftime("%H:%M:%S")
        ascii_screen = phase1_color_compass.screen_to_ascii(screen)
        log_entry = (
            f"\n--- [HIDDEN MIND] [{timestamp}] ---\n"
            f"Stability: {stability:.4f} | Nodes: {len(nodes)}\n"
            f"{ascii_screen}\n"
        )
        try:
            with open(self.hidden_mind_path, "a", encoding='utf-8') as f:
                f.write(log_entry)
            print(f"[TEST] Hidden Mind logged to {self.hidden_mind_path}")
        except Exception as e:
            print(f"[TEST] Error logging: {e}")

    def test_dream(self):
        print("[TEST] Simulating Dream Cycle...")
        pairs = [
            (random.randint(0, 255), random.randint(0, 255))
            for _ in range(3)
        ]
        screen = phase1_color_compass.build_screen(pairs)
        sw = phase1_color_compass.detect_standing_wave(screen)
        self.log_hidden_mind(screen, sw['stability'], sw['node_cols'])

if __name__ == "__main__":
    oro = MockOuroboros()
    oro.test_dream()
