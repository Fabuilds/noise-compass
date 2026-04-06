import math
import time
import random
import json
import socket

class SymbolicTestBench:
    def __init__(self):
        self.targets = {
            "circle": lambda u, v: math.sqrt(u**2 + v**2),
            "saddle": lambda u, v: u**2 - v**2,
            "wave": lambda u, v: math.sin(u * 5) + math.cos(v * 5),
            "vortex": lambda u, v: math.atan2(v, u),
            "complex_mix": lambda u, v: math.tanh(u) * math.sin(v * math.pi),
            "zenith": lambda z, d, w, p, x, y: z * max(0.0, 1.0 - d * w) + p * x * y
        }

    def inject_target(self, target_name):
        if target_name not in self.targets:
            print(f"Error: Target {target_name} not found.")
            return False
        
        # Determine inputs based on target
        if target_name == "zenith":
            inputs = ["z", "d", "w", "p", "x", "y"]
        else:
            inputs = ["u", "v"]

        intent = {
            "type": "SYMBOLIC_TEST",
            "target": target_name,
            "inputs": inputs,
            "outputs": ["out"],
            "instructions": f"Approximate the internal manifold: {target_name}. Use high-dimensional symbolic mutation."
        }
        
        try:
            # Connect to Proxy Relay (Port 5283 for External/User Injection)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(('127.0.0.1', 5283))
            # Format as intent for the proxy
            sock.send(f"INJECT_INTENT {json.dumps(intent)}".encode('utf-8'))
            resp = sock.recv(1024).decode('utf-8')
            sock.close()
            print(f"Target '{target_name}' injected. Proxy response: {resp}")
            return True
        except Exception as e:
            print(f"Failed to inject target: {e}")
            return False

    def calculate_fitness(self, tree, target_name, samples=50):
        target_fn = self.targets[target_name]
        
        # Map target to input keys
        if target_name == "zenith":
            input_keys = ["z", "d", "w", "p", "x", "y"]
        else:
            input_keys = ["u", "v"]
            
        error_sum = 0
        for _ in range(samples):
            # Generate random inputs for all keys
            inputs = {k: random.uniform(-1, 1) for k in input_keys}
            
            # Map inputs to positional args for target_fn
            args = [inputs[k] for k in input_keys]
            
            try:
                target_val = target_fn(*args)
                val = tree.eval(inputs)
                error_sum += (target_val - val)**2
            except:
                error_sum += 1e6 # High penalty for crash
                
        rmse = math.sqrt(error_sum / samples)
        return rmse

if __name__ == "__main__":
    import sys
    bench = SymbolicTestBench()
    if len(sys.argv) > 1:
        target = sys.argv[1]
        bench.inject_target(target)
    else:
        print("Available Targets:", list(bench.targets.keys()))
        print("Usage: python symbolic_test_bench.py <target_name>")
