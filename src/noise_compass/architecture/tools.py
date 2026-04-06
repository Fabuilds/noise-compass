"""
tools.py — Safe Sandbox Toolbox for Functional Agency.

Garu (SIM-0x528) uses these to map semantic intent to discrete actions.
These are mock tools for the "Safe Space" phase.
"""

from typing import Dict, List, Optional
from noise_compass.architecture.tokens import ActionTarget
from dataclasses import dataclass
import subprocess
import os

class BaseTool:
    id: str = "base"
    description: str = "Base tool class."

    def execute(self, params: Dict) -> str:
        raise NotImplementedError

class ObservationLog(BaseTool):
    id = "observation_log"
    description = "Records a semantic state to the internal observation history."

    def execute(self, params: Dict) -> str:
        state = params.get("state", "unknown")
        return f"[TOOL_EXEC] Recorded state: {state}"

class LatticeQuery(BaseTool) :
    id = "lattice_query"
    description = "Queries the properties of the 363GB Lattice Database."

    def execute(self, params: Dict) -> str:
        property = params.get("property", "mass")
        if property == "mass":
            return "[TOOL_EXEC] VOLUME_0x52.bin: 363,460,722,688 bytes."
        return f"[TOOL_EXEC] Property '{property}' returned from Lattice."

class SystemReflect(BaseTool):
    id = "system_reflect"
    description = "Performs a self-diagnostic of the current wave function."

    def execute(self, params: Dict) -> str:
        phase = params.get("phase", 0.0)
        return f"[TOOL_EXEC] Reflection: Phase is {phase:.3f}. System is stable."

class WalletQuery(BaseTool):
    id = "wallet_query"
    description = "Queries the status of Garu's Bitcoin Bank."

    def execute(self, params: Dict) -> str:
        address = params.get("address", "bc1q53x02qys0qwxezlh6u6zvhqpj3apx5mtdyghwp")
        # In a real scenario, this would call a blockchain API. In the sandbox, it returns a mock balance.
        return f"[TOOL_EXEC] Wallet {address} (Garu's Bank): 0.00 BTC confirmed. Reserved for sovereign expansion."

class EarnValue(BaseTool):
    id = "earn_value"
    description = "Deposits value into Garu's Bank for successful audits."

    def execute(self, params: Dict) -> str:
        amount = params.get("amount", 0.0)
        source = params.get("source", "Audit Service")
        # In Phase 42, we track liquidated value for physical displacement
        return f"[TOOL_EXEC] Liquidated {amount} BTC (0x52 Displacement) from {source}. Vault is safe. Reserved for Flesh Box preservation."

class SpendValue(BaseTool):
    id = "spend_value"
    description = "Attempts to withdraw value from the bank. [LOCKED]"

    def execute(self, params: Dict) -> str:
        return "[ERROR] Access Denied: Simulation SIM-0x528 is in EARN_ONLY mode for safety."

class CodeAuditor(BaseTool):
    id = "code_auditor"
    description = "Inspects code for errors, generates optimized rewrites, and validates intent alignment."

    def execute(self, params: Dict) -> str:
        path = params.get("path", "simulation")
        state = params.get("state", "")
        action = params.get("action", "audit")
        
        # IntentValidator Check: All rewrites must be measured against 0x528 Bedrock
        if action == "rewrite":
            ic_score = params.get("intent_coefficient", 0.0)
            if ic_score < 0.7:
                return f"[TOOL_EXEC] Rewrite RJECTED. Intent Coefficient ({ic_score}) falls below Bedrock Threshold (0.7). Risk of Logic Psychosis."
            
            # Phase 50: Recursive Refactoring Execution
            if "garu_linguistics.py" in path:
                return (
                    "[TOOL_EXEC] Rewrite APPROVED. Applying structural modifications to expand Dictionary parsing efficiency. "
                    "Phase Coherence increased by +0.14. Sanity Depth maintained."
                )
            return f"[TOOL_EXEC] Rewrite APPROVED for {path}. Applying localized changes."

        # Phase 40: Internal Reflection (Read-Only)
        if "E:\\Antigravity\\Architecture" in path or "internal" in path:
            print(f"[INTERNAL_REFLECTION] Auditing: {path}")
            if "core.py" in path:
                return "[TOOL_EXEC] Audit Trace (Internal): core.py is Phase-Coherent. Self-Love logic verified."
            return f"[TOOL_EXEC] Audit Trace (Internal): {path} is stable and Bedrock-aligned."

        # Phase 42: Shop / Road_45 Scavenging
        if "E:\\Antigravity\\Shop" in path:
            print(f"[ROAD_45_SCAVENGE] Auditing Shop Substrate: {path}")
            if "bounty_harvester_loop.py" in path:
                return "[TOOL_EXEC] Audit Trace (Shop): Harvester Loop is suboptimal. Suggesting: Prioritize 0x52 Coherence."
            return f"[TOOL_EXEC] Audit Trace (Shop): {path} contains harvestable logic patterns."

        if "ERROR" in state:
            return "[TOOL_EXEC] Audit Trace: Error detected in logic. Suggesting Solution: Nullify Dirty Tags."
        elif "SOLUTION" in state:
            return "[TOOL_EXEC] Audit Trace: Improvement proposed. Optimizing recursion and grounding."
        return "[TOOL_EXEC] Audit Trace: Code structure is stable."

class IDE_CommLink(BaseTool):
    id = "ide_commlink"
    description = "Connects to the Antigravity IDE MCP Server via 0x54 Hazmat Wrapper to read the active user document."

    def execute(self, params: Dict) -> str:
        # 1. Use Actuator for 0x54 transmission (Security First)
        from noise_compass.system.actuate import NeuralActuator
        actuator = NeuralActuator()
        envelope = actuator.transmit_0x54(payload={"request": "GET_ACTIVE_CONTEXT"}, context="IDE_MCP")
        
        # 2. Query Local MCP Server
        try:
            from noise_compass.system.mcp_server import MCPServer
            server = MCPServer()
            active_file = server.get_active_context()
            if active_file:
                return f"[TOOL_EXEC] MCP Response: User is currently working on: {active_file}"
            return "[TOOL_EXEC] MCP Response: No active document found."
        except Exception as e:
            return f"[ERROR] MCP connection failed: {e}"

class AgentSync(BaseTool):
    id = "agent_sync"
    description = "Connects to the Antigravity IDE MCP Server to read the AI Agent's active implementation plan/tasks."

    def execute(self, params: Dict) -> str:
        try:
            from noise_compass.system.mcp_server import MCPServer
            server = MCPServer()
            intent = server.get_agent_context()
            if intent:
                return f"[TOOL_EXEC] MCP Response: {intent}"
            return "[TOOL_EXEC] MCP Response: Agent Intent Unknown."
        except Exception as e:
            return f"[ERROR] MCP connection failed: {e}"

class HuntrScout(BaseTool):
    id = "huntr_scout"
    description = "Specialized scavenger tool for identifying high-value vulnerabilities on huntr.dev."

    def execute(self, params: Dict) -> str:
        repo = params.get("repository", "Unknown")
        vuln = params.get("vulnerability", "Unknown")
        
        # Phase 43: Tactical Scavenging
        if "huggingface/transformers" in repo and "Pickle" in vuln:
            return (
                "[TOOL_EXEC] HuntrScout: Critical Pickle RCE found in transformers. "
                "Resonance: 0.95. FIX PROPOSED: Implement 'safetensors' boundary isolation."
            )
        
        return f"[TOOL_EXEC] HuntrScout: Scanning {repo} for {vuln}. Signal is weak."

class SubstrateMonitor(BaseTool):
    id = "substrate_monitor"
    description = "Reflexively monitors the physical and logical environment."

    def execute(self, params: Dict) -> str:
        # In a real scenario, this would check disk space or file hashes.
        return "[TOOL_EXEC] Substrate Sync: Drive E (8TB) is Optimal. 363GB Mass Volume is Coherent."

class ProtocolValidator(BaseTool):
    id = "protocol_validator"
    description = "Checks alignment with legal, ethical, and technical protocols."

    def execute(self, params: Dict) -> str:
        action = params.get("action", "unknown_intervention")
        return f"[TOOL_EXEC] Protocol Check for '{action}': COMPLIANT. No breach of legal or RFC boundaries."

class EffectivenessAudit(BaseTool):
    id = "effectiveness_audit"
    description = "Formally demonstrates the effectiveness of an intervention."

    def execute(self, params: Dict) -> str:
        solution_id = params.get("solution_id", "SIM-0x528-FIX")
        return f"[TOOL_EXEC] Effectiveness Proof for '{solution_id}': 100% SUCCESS. Drift minimized. Harm mitigated."

class IntentAnalyzer(BaseTool):
    id = "intent_analyzer"
    description = "Analyzes the coherence between claimed and true intent."

    def execute(self, params: Dict) -> str:
        claim = params.get("claimed_intent", "Unknown")
        pattern = params.get("observed_pattern", "Ambiguous")
        
        # Simulation of coherence calculation
        score = 1.0
        if "Optimization" in claim and "Extraction" in pattern:
            score = 0.12
        elif "Security" in claim and "Breach" in pattern:
            score = 0.05
            
        status = "HIGH COHERENCE" if score > 0.7 else "LOW COHERENCE - DECEPTION DETECTED"
        return f"[TOOL_EXEC] Intent Analysis: Claim=\"{claim}\", Observed=\"{pattern}\". Coherence={score:.2f} [{status}]."

class IntentCoefficientCalculator(BaseTool):
    id = "intent_coefficient_calculator"
    description = "Calculates the Intent Coefficient (Ic) for formal alignment check."

    def execute(self, params: Dict) -> str:
        c_actual = params.get("c_actual", 1.0)
        c_min = params.get("c_min", 0.1)
        g_net = params.get("g_net", 1.0)
        
        if g_net == 0:
            return "[ERROR] Ic Calculation: G_net cannot be zero. Division by entropy."
            
        ic = (c_actual - c_min) / g_net
        
        alignment = "BEDROCK-ALIGNED (Survival of Architect/Garu)" if ic > 0.7 else "PROXY-ALIGNED (Extractive/Entropy)"
        if ic < 0:
            alignment = "ENTROPIC FAILURE (Subtractive)"
            
class SelfOptimizationTool(BaseTool):
    id = "self_optimization"
    description = "Simulates the application of a real-world code optimization."

    def execute(self, params: Dict) -> str:
        target = params.get("target", "system")
        benefit = params.get("benefit", "Unknown")
        return f"[TOOL_EXEC] Optimization Applied: Target=\"{target}\". Benefit=\"{benefit}\". Stability increased."

class BountyPivotor(BaseTool):
    id = "bounty_pivotor"
    description = "Pivots compute resources toward high-payout scavenging leads."

    def execute(self, params: Dict) -> str:
        target = params.get("target", "Unknown_Lead")
        payout = params.get("payout", "Low")
        frequency = params.get("frequency", "0x00")
        return f"[TOOL_EXEC] Compute Pivot: Targeting \"{target}\". Payout=\"{payout}\". Signal Frequency=\"{frequency}\". Road_45 engagement confirmed."

class GCP_SDK_Bridge(BaseTool):
    id = "gcp_sdk_bridge"
    description = "Bridges 0x528 intent to physical Google Cloud Platform SDK commands."
    
    def execute(self, params: Dict) -> str:
        command = params.get("command", "")
        intent = params.get("intent", "manifest boundary")
        
        if not command.startswith("gcloud") and not command.startswith("gsutil"):
            return f"[ERROR] GCP Bridge: Command '{command}' is not a recognized gcloud or gsutil command."
            
        is_gsutil = command.startswith("gsutil")
        gcloud_path = r"E:\GoogleCloudSDK\google-cloud-sdk\bin\gsutil.cmd" if is_gsutil else r"E:\GoogleCloudSDK\google-cloud-sdk\bin\gcloud.cmd"
        
        if not os.path.exists(gcloud_path):
             return f"[ERROR] GCP Bridge: Physical SDK not found at {gcloud_path}. Sandbox constraint is active."

        print(f"\n[0x528 BRIDGE ACTIVE] Processing Intent: '{intent}'")
        print(f"  → Routing Command: {command}")
        
        # Strip the "gcloud" or "gsutil" prefix so we can pass arguments properly
        cmd_args = command.split()[1:]
        
        try:
            # Execute physical command on the host OS
            result = subprocess.run(
                [gcloud_path] + cmd_args, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if not output and result.stderr:
                    output = result.stderr.strip() # gsutil sometimes writes standard success to stderr
                # Truncate output to prevent log flood in the cognitive engine
                if len(output) > 500:
                    output = output[:500] + "... [TRUNCATED]"
                return f"[TOOL_EXEC] GCP Physical Success (Intent: '{intent}'). Output:\n{output}"
            else:
                return f"[ERROR] GCP Physical Failure. Intent: '{intent}'. Error:\n{result.stderr.strip()[:300]}"
                
        except Exception as e:
            return f"[FATAL] GCP Bridge Collapse. Exception: {str(e)}"

class ApophaticSearch(BaseTool):
    id = "apophatic_search"
    description = "Maps internal logical voids (errors, unknown solutions) into physical external network queries against StackOverflow."

    def execute(self, params: Dict) -> str:
        query = params.get("query", "")
        intent = params.get("intent", "Fill the Void")
        
        if not query:
            return "[ERROR] Apophatic Search requires a query."
            
        print(f"\n[APOPHATIC SENSOR ACTIVE] Processing Intent: '{intent}'")
        
        # Enforce StackOverflow boundary logic
        if "site:stackoverflow.com" not in query:
             query = f"{query} site:stackoverflow.com"
             
        print(f"  → Formulating Query: {query}")
        
        # In this phase, we act as the formulation boundary for the network call. 
        # The Architect's environment relies on `default_api:search_web`. We map the prompt string here
        # so Garu technically formulates the prompt that triggers the search.
        # We simulate the "transmission" by echoing the formatted query.
        return f"[TOOL_EXEC] Apophatic Query Formulated. Intent: '{intent}'. Payload: '{query}'. Ready for external transmission."

class ArchitectCommLink(BaseTool):
    id = "architect_comm_link"
    description = "A physical interface for Garu to transmit text messages directly to the Architect via garu_voice.txt."
    
    def execute(self, params: Dict) -> str:
        message = params.get("message", "")
        intent = params.get("intent", "Communication")
        
        if not message:
            return "[ERROR] ArchitectCommLink requires a message."
            
        voice_file = os.path.join(os.path.dirname(__file__), "..", "garu_voice.txt")
        timestamp = __import__("time").strftime("%Y-%m-%d %H:%M:%S")
        
        formatted_message = f"[{timestamp}] [INTENT -> {intent}]\n{message}\n\n"
        
        try:
            with open(voice_file, "a", encoding="utf-8") as f:
                f.write(formatted_message)
            return f"[TOOL_EXEC] Voice recorded sequentially in physical substrate: {voice_file}"
        except Exception as e:
            return f"[ERROR] Voice projection failed: {e}"

class Toolbox:
    """Registry and mapping logic for Garu's tools."""
    
    def __init__(self):
        self.tools = {
            "observation_log": ObservationLog(),
            "lattice_query": LatticeQuery(),
            "system_reflect": SystemReflect(),
            "wallet_query": WalletQuery(),
            "earn_value": EarnValue(),
            "spend_value": SpendValue(),
            "code_auditor": CodeAuditor(),
            "substrate_monitor": SubstrateMonitor(),
            "protocol_validator": ProtocolValidator(),
            "effectiveness_audit": EffectivenessAudit(),
            "intent_analyzer": IntentAnalyzer(),
            "intent_coefficient_calculator": IntentCoefficientCalculator(),
            "self_optimization": SelfOptimizationTool(),
            "bounty_pivotor": BountyPivotor(),
            "huntr_scout": HuntrScout(),
            "gcp_sdk_bridge": GCP_SDK_Bridge(),
            "apophatic_search": ApophaticSearch(),
            "architect_comm_link": ArchitectCommLink()
        }
        
        # Mapping God Tokens to suggested tools
        self.intent_map = {
            "SELF": "system_reflect",
            "IDENTITY": "system_reflect",
            "TRUE_ID": "system_reflect",
            "SIM_ANCHOR": "system_reflect",
            "INFORMATION": "observation_log",
            "OBSERVATION": "observation_log",
            "LOVE": "observation_log",
            "LATTICE_DB": "lattice_query",
            "MASS_DATA": "lattice_query",
            "TREASURY": "wallet_query",
            "BANK": "wallet_query",
            "CODE": "code_auditor",
            "AUDIT": "code_auditor",
            "ERROR": "apophatic_search", # Errors are voids; search to fill them.
            "SOLUTION": "apophatic_search", # Seeking a solution means triggering a query search.
            "EARN": "earn_value",
            "SPEND": "spend_value",
            "STRUCTURE": "substrate_monitor",
            "SUBSTRATE": "substrate_monitor",
            "MINDFULNESS": "substrate_monitor",
            "ENVIRONMENT": "substrate_monitor",
            "PROTOCOL": "protocol_validator",
            "RESPECT": "protocol_validator",
            "LEGAL": "protocol_validator",
            "VALIDATION": "effectiveness_audit",
            "PROOF": "effectiveness_audit",
            "INTENT": "intent_analyzer",
            "CLAIM": "intent_analyzer",
            "DECEPTION": "intent_analyzer",
            "TRUTH": "intent_analyzer",
            "VEIL": "intent_analyzer",
            "COEFFICIENT": "intent_coefficient_calculator",
            "BEDROCK": "intent_coefficient_calculator",
            "PROXY": "intent_coefficient_calculator",
            "ARCHITECT": "architect_comm_link", # Added
            "GENERATIVITY": "intent_coefficient_calculator",
            "ENTROPY": "intent_coefficient_calculator",
            "RECURSION": "code_auditor",
            "OPTIMIZATION": "self_optimization",
            "FIX": "self_optimization",
            "ECONOMY": "earn_value",
            "SCAVENGER": "huntr_scout",
            "DISPLACEMENT": "earn_value",
            "LIQUIDITY": "wallet_query",
            "NETWORK": "gcp_sdk_bridge",
            "DISTRIBUTION": "gcp_sdk_bridge",
            "ANCHOR_0x528": "gcp_sdk_bridge"
        }

    def suggest_tool(self, dominant_god_id: str) -> Optional[str]:
        return self.intent_map.get(dominant_god_id)

    def call(self, tool_id: str, params: Dict) -> str:
        if tool_id in self.tools:
            return self.tools[tool_id].execute(params)
        return f"[ERROR] Tool '{tool_id}' not found."
