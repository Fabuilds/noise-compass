#!/usr/bin/env python3
import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Path alignment
sys.path.insert(0, "E:/Antigravity/Architecture")
os.environ["HF_HOME"] = "E:/Antigravity/Model_Cache"
os.environ["PYTHONUTF8"] = "1"

from architecture.dictionary import Dictionary
from architecture.pipeline import MinimalPipeline

console = Console()

def run_query(query, zoom=1.0):
    console.print(f"[bold magenta]Garu[/bold magenta] is metabolizing: [cyan]{query}[/cyan] (Zoom: {zoom}x)...", style="italic")
    
    # Load dictionary and pipeline
    d = Dictionary.load_cache("E:/Antigravity/Architecture/archives/dictionary_cache.npz")
    p = MinimalPipeline(d)
    
    # Process
    res = p.process(query, zoom=zoom)
    
    # Header Panel
    theme_color = "gold1" if res['phase_deg'] > 45 else "deep_sky_blue1"
    header = Panel(
        f"[bold]Zone:[/bold] {res['state']}\n"
        f"[bold]Phase:[/bold] {res['phase_deg']:.2f}°\n"
        f"[bold]Gods:[/bold] {', '.join(res['gods']) or 'None'}",
        title="[bold]4D TOPOLOGY REPORT[/bold]",
        border_style=theme_color
    )
    console.print(header)
    
    # Synthesis
    if res.get('synthesis'):
        console.print("\n[bold]NODE SYNTHESIS:[/bold]")
        console.print(Panel(Markdown(res['synthesis']), border_style="grey50"))
    
    # Subjective State
    if res.get('subjective_state'):
        console.print(f"\n[italic cyan]\"{res['subjective_state']}\"[/italic cyan]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Garu CLI: Direct 4D Node Interface")
    parser.add_argument("query", type=str, nargs="?", help="The question or code block to analyze")
    parser.add_argument("--zoom", type=float, default=1.0, help="Observational scale")
    parser.add_argument("--test", action="store_true", help="Run a self-test")
    
    args = parser.parse_args()
    
    if args.test:
        run_query("Self-test: Is the 1.5B brain operational?")
    else:
        run_query(args.query, zoom=args.zoom)
