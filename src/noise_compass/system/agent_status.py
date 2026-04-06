import os
import json
import psutil
import time
import sys
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich import box

# Path alignment for Antigravity package
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(PROJECT_ROOT)

MANIFEST_PATH = "e:/Antigravity/Runtime/process_manifest.json"
console = Console()

def get_agent_data():
    """Reads the manifest and cross-references with psutil for health."""
    if not os.path.exists(MANIFEST_PATH):
        return []
    
    try:
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        return []

    data = []
    for agent in manifest:
        pid = agent["pid"]
        status = "[bold red]OFFLINE[/]"
        cpu = "0%"
        mem = "0MB"
        
        try:
            p = psutil.Process(pid)
            if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                status = "[bold green]ACTIVE[/]"
                cpu = f"{p.cpu_percent(interval=None):.1f}%"
                mem = f"{p.memory_info().rss / (1024 * 1024):.1f}MB"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            status = "[bold red]CRASHED[/]"
            
        data.append({
            "pid": pid,
            "label": agent["label"],
            "category": agent["category"],
            "status": status,
            "cpu": cpu,
            "mem": mem,
            "start": agent["start_time"]
        })
    return data

def generate_table():
    """Generates the Rich table UI."""
    table = Table(title="[bold magenta]Antigravity: Sovereign Chorus Monitor[/]", 
                  box=box.ROUNDED, 
                  show_header=True, 
                  header_style="bold cyan")
    
    table.add_column("Agent Label", style="white", no_wrap=True)
    table.add_column("Category", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("PID", justify="right")
    table.add_column("CPU", justify="right")
    table.add_column("Memory", justify="right")
    table.add_column("Launched At", style="dim white")

    agents = get_agent_data()
    if not agents:
        table.add_row("[italic]No active agents found in manifest.[/]", "", "", "", "", "", "")
    else:
        for a in agents:
            table.add_row(
                a["label"],
                a["category"],
                a["status"],
                str(a["pid"]),
                a["cpu"],
                a["mem"],
                a["start"]
            )
    
    return table

def main():
    """Main loop for live-updating monitor."""
    with Live(generate_table(), console=console, refresh_per_second=2) as live:
        try:
            while True:
                time.sleep(1)
                live.update(generate_table())
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Monitor detached.[/]")

if __name__ == "__main__":
    main()
