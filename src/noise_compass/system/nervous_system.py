import psutil
import time
import socket

class NervousSystem:
    """Maps architectural dependencies and health via port discovery and TCP state."""
    
    ORGAN_PORTS = {
        5284: "PROXY_GATE",
        5285: "MAIN_CHAIN",
        5286: "APEX_LOBE",
        5287: "PRIMARY_TRIAD",
        8765: "DASHBOARD"
    }

    def map_substrate(self):
        """Discovers active organs and their functional 'synapses'."""
        report = []
        active_map = {}
        
        # 1. Discovery via Ports
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr.port in self.ORGAN_PORTS:
                if conn.pid and conn.pid > 0:
                    name = self.ORGAN_PORTS[conn.laddr.port]
                    active_map[name] = {"pid": conn.pid, "port": conn.laddr.port}
        
        # 2. Impact Analysis
        critical_count = 0
        for port, name in self.ORGAN_PORTS.items():
            if name in active_map:
                try:
                    p = psutil.Process(active_map[name]["pid"])
                    cpu = p.cpu_percent(interval=0.1)
                    mem = p.memory_info().rss / (1024**2)
                    report.append(f"  [ONLINE]  {name:15} | Port {port} | PID {p.pid:6} | CPU {cpu:4.1f}% | MEM {mem:6.1f}MB")
                except:
                    report.append(f"  [STALLED] {name:15} | Port {port} | UNRESPONSIVE")
            else:
                severity = "CRITICAL" if name in ["PROXY_GATE", "APEX_LOBE", "PRIMARY_TRIAD"] else "THROTTLED"
                if severity == "CRITICAL": critical_count += 1
                report.append(f"  [OFFLINE] {name:15} | Port {port} | IMPACT: {severity}")

        # 3. Final Verdict
        verdict = "HEALTHY"
        if critical_count > 0: verdict = "PARALYZED" if critical_count > 2 else "DEGRADED"
        
        return verdict, report

if __name__ == "__main__":
    ns = NervousSystem()
    verdict, lines = ns.map_substrate()
    print(f"--- NERVMAP SYSTEM VERDICT: {verdict} ---")
    for line in lines:
        print(line)
