import psutil
import os

def list_python_processes():
    print(f"{'PID':<8} | {'Port':<8} | {'Command Line'}")
    print("-" * 60)
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in p.info['name'].lower():
                cmd = " ".join(p.info['cmdline']) if p.info['cmdline'] else "N/A"
                # Check for ports
                try:
                    connections = p.connections()
                    ports = [str(conn.laddr.port) for conn in connections if conn.status == 'LISTEN']
                    port_str = ",".join(ports) if ports else "None"
                except:
                    port_str = "Unknown"
                print(f"{p.info['pid']:<8} | {port_str:<8} | {cmd}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

if __name__ == "__main__":
    list_python_processes()
