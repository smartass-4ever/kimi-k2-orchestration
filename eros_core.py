"""
EROS: Hierarchical Agentic Orchestration for Extreme Scale Swarms
Proof of Concept Implementation

This implements a hierarchical swarm architecture with:
- Tier 1: Sovereign Orchestrator (CEO)
- Tier 2: EROS Managers (Middle Management)
- Tier 3: Intern Agents (Execution)
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import re
from collections import deque


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    RUNNING = "running"
    STALLED = "stalled"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


@dataclass
class PADTelemetry:
    """
    PAD (Pleasure-Arousal-Dominance) Telemetry
    3-dimensional vector for monitoring agent health
    """
    pleasure: float  # 0.0-1.0: Success correlation with goal
    arousal: float   # 0.0-1.0: Energy/activity level (high = potential stalling)
    dominance: float # 0.0-1.0: Certainty vs hesitation
    
    def is_healthy(self) -> bool:
        """Check if agent is operating within healthy parameters"""
        return (
            self.pleasure > 0.2 and  # Making progress
            self.arousal < 0.8 and   # Not stalling/looping
            self.dominance > 0.3     # Has reasonable certainty
        )
    
    def __str__(self):
        return f"PAD(P={self.pleasure:.2f}, A={self.arousal:.2f}, D={self.dominance:.2f})"


class BeliefRegistry:
    """
    Shared immutable-per-turn state that defines project DNA
    Implements the Blackboard Pattern for agent coordination
    
    PRODUCTION NOTE: For multi-manager concurrent access, this requires:
    - asyncio.Lock() for state mutations
    - OR distributed store (Redis) with atomic operations
    - Current implementation is single-threaded safe only
    """
    
    def __init__(self, project_id: str, global_constraints: Dict[str, Any]):
        self.project_id = project_id
        self.global_constraints = global_constraints
        self.state = "initialization"
        self.turn_number = 0
        self.agent_registry: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()  # CRITICAL: Prevent race conditions
        
    def sync(self) -> Dict[str, Any]:
        """Agents sync with registry before every turn"""
        return {
            "project_id": self.project_id,
            "global_constraints": self.global_constraints,
            "state": self.state,
            "turn": self.turn_number
        }
    
    async def advance_turn(self, new_state: str):
        """
        Advance to next turn with new state
        THREAD-SAFE: Uses lock to prevent race conditions
        """
        async with self._lock:
            self.turn_number += 1
            self.state = new_state
        
    async def register_agent(self, agent_id: str, metadata: Dict):
        """
        Register an agent in the shared registry
        THREAD-SAFE: Uses lock to prevent concurrent modification
        """
        async with self._lock:
            self.agent_registry[agent_id] = {
                **metadata,
                "registered_at": time.time(),
                "turn": self.turn_number
            }
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "constraints": self.global_constraints,
            "state": self.state,
            "turn": self.turn_number,
            "agents": len(self.agent_registry)
        }


class InternAgent:
    """
    Tier 3: Specialized execution agent
    Focused on single tool/task, operates in "instant mode"
    """
    
    def __init__(self, agent_id: str, specialty: str, manager_id: str):
        self.agent_id = agent_id
        self.specialty = specialty  # e.g., "code", "browser", "search"
        self.manager_id = manager_id
        self.state = AgentState.IDLE
        self.output_buffer = deque(maxlen=100)  # Rolling window of recent outputs
        self.task: Optional[Dict] = None
        self.start_time: Optional[float] = None
        
    async def execute_task(self, task: Dict, belief_context: Dict) -> Dict:
        """
        Execute assigned task with belief context
        Simulates actual agent work (replace with real Kimi API calls)
        """
        self.task = task
        self.state = AgentState.RUNNING
        self.start_time = time.time()
        
        # Simulate work with periodic output
        result = {
            "agent_id": self.agent_id,
            "task_id": task.get("id"),
            "outputs": [],
            "status": "in_progress"
        }
        
        # Simulate incremental work (in real impl, this would be streaming API response)
        for step in range(task.get("estimated_steps", 5)):
            await asyncio.sleep(0.1)  # Simulate work
            
            output = f"Step {step + 1}: Processing {self.specialty} for {task.get('goal', 'unknown')}"
            self.output_buffer.append({
                "timestamp": time.time(),
                "content": output,
                "step": step + 1
            })
            result["outputs"].append(output)
            
            # Simulate potential failure modes
            if task.get("inject_failure") and step == 2:
                result["status"] = "error"
                result["error"] = "Simulated failure: hallucination detected"
                self.state = AgentState.FAILED
                return result
        
        result["status"] = "completed"
        result["duration"] = time.time() - self.start_time
        self.state = AgentState.COMPLETED
        return result
    
    def get_recent_output(self, n: int = 10) -> List[Dict]:
        """Get n most recent outputs for telemetry analysis"""
        return list(self.output_buffer)[-n:]
    
    def kill(self, reason: str):
        """Manager-issued SIG_KILL"""
        self.state = AgentState.KILLED
        self.output_buffer.append({
            "timestamp": time.time(),
            "content": f"KILLED: {reason}",
            "terminal": True
        })


class PADAnalyzer:
    """
    Analyzes agent output to compute PAD telemetry
    Lightweight heuristic implementation (can be replaced with ML model)
    """
    
    @staticmethod
    def analyze_output(outputs: List[Dict], task_goal: str) -> PADTelemetry:
        """
        Compute PAD vector from recent outputs
        """
        if not outputs:
            return PADTelemetry(pleasure=0.0, arousal=0.0, dominance=0.0)
        
        # Extract text content
        texts = [o.get("content", "") for o in outputs]
        combined_text = " ".join(texts).lower()
        
        # P (Pleasure): Goal alignment - simple keyword matching
        goal_keywords = set(task_goal.lower().split())
        output_keywords = set(combined_text.split())
        overlap = len(goal_keywords & output_keywords)
        pleasure = min(1.0, overlap / max(len(goal_keywords), 1))
        
        # A (Arousal): Detect stalling - repetition and error patterns
        error_signals = ["error", "failed", "retry", "trying again", "unable"]
        error_count = sum(1 for signal in error_signals if signal in combined_text)
        
        # Check for repetitive patterns (stalling indicator)
        repetition_score = 0.0
        if len(texts) >= 3:
            recent = texts[-3:]
            if len(set(recent)) < len(recent):  # Duplicates detected
                repetition_score = 0.4
        
        arousal = min(1.0, (error_count * 0.2) + repetition_score)
        
        # D (Dominance): Certainty - look for confident language
        uncertain_signals = ["maybe", "might", "uncertain", "not sure", "trying"]
        confident_signals = ["completed", "success", "done", "processed"]
        
        uncertain_count = sum(1 for signal in uncertain_signals if signal in combined_text)
        confident_count = sum(1 for signal in confident_signals if signal in combined_text)
        
        dominance = max(0.0, min(1.0, (confident_count - uncertain_count * 0.5) / 5))
        
        return PADTelemetry(
            pleasure=pleasure,
            arousal=arousal,
            dominance=dominance
        )


class EROSManager:
    """
    Tier 2: Middle Management Layer
    Manages 4-10 intern agents with asynchronous sampling
    """
    
    def __init__(self, manager_id: str, belief_registry: BeliefRegistry):
        self.manager_id = manager_id
        self.belief_registry = belief_registry
        self.interns: List[InternAgent] = []
        self.max_interns = 10
        self.monitoring_interval = 0.5  # Check interns every 500ms
        self.status_log: List[Dict] = []
        
    def spawn_intern(self, specialty: str) -> InternAgent:
        """Spawn a new intern agent"""
        if len(self.interns) >= self.max_interns:
            raise ValueError(f"Manager {self.manager_id} at capacity")
        
        agent_id = f"{self.manager_id}_intern_{len(self.interns)}"
        intern = InternAgent(agent_id, specialty, self.manager_id)
        self.interns.append(intern)
        
        # Register in belief registry (async safe)
        # Note: In production, wrap this in asyncio.create_task() or await it
        asyncio.create_task(self.belief_registry.register_agent(agent_id, {
            "type": "intern",
            "specialty": specialty,
            "manager": self.manager_id
        }))
        
        return intern
    
    async def monitor_intern(self, intern: InternAgent) -> Optional[Dict]:
        """
        Asynchronous sampling: peek at intern logs to verify alignment
        Returns status pulse if intervention needed
        """
        if intern.state not in [AgentState.RUNNING]:
            return None
        
        # CRITICAL FIX: Allow 30-second warm-up period to avoid cold-start false positives
        if intern.start_time and time.time() - intern.start_time < 30:
            return None  # Skip monitoring during initialization
        
        # Get recent output
        recent_outputs = intern.get_recent_output(n=5)
        if not recent_outputs or not intern.task:
            return None
        
        # Compute PAD telemetry
        pad = PADAnalyzer.analyze_output(
            recent_outputs,
            intern.task.get("goal", "")
        )
        
        # Check health
        if not pad.is_healthy():
            # Agent is failing - prepare status pulse
            return {
                "manager_id": self.manager_id,
                "intern_id": intern.agent_id,
                "alert": "INTERVENTION_REQUIRED",
                "telemetry": asdict(pad),
                "reason": self._diagnose_failure(pad),
                "timestamp": time.time()
            }
        
        return None
    
    def _diagnose_failure(self, pad: PADTelemetry) -> str:
        """Diagnose failure mode from PAD telemetry"""
        if pad.pleasure < 0.2:
            return "Low goal alignment - task divergence detected"
        if pad.arousal > 0.8:
            return "High arousal - agent stalling or infinite retry loop"
        if pad.dominance < 0.3:
            return "Low dominance - agent showing excessive uncertainty"
        return "Unknown failure mode"
    
    async def intervene(self, intern: InternAgent, reason: str) -> Dict:
        """
        Issue SIG_KILL and prepare recovery
        """
        intern.kill(reason)
        
        # Log intervention
        intervention_log = {
            "timestamp": time.time(),
            "manager_id": self.manager_id,
            "intern_id": intern.agent_id,
            "action": "SIG_KILL",
            "reason": reason,
            "task_id": intern.task.get("id") if intern.task else None
        }
        self.status_log.append(intervention_log)
        
        return intervention_log
    
    async def respawn_with_correction(self, 
                                     failed_intern: InternAgent,
                                     correction: str) -> InternAgent:
        """
        Respawn intern with corrected context
        """
        # Create new intern with same specialty
        new_intern = self.spawn_intern(failed_intern.specialty)
        
        # Prepare corrected task
        if failed_intern.task:
            corrected_task = failed_intern.task.copy()
            corrected_task["context_correction"] = correction
            corrected_task["previous_attempt"] = failed_intern.agent_id
            
        return new_intern
    
    def get_status_pulse(self) -> Dict:
        """
        Generate high-level status pulse for Sovereign Orchestrator
        Contains NO raw logs, only strategic summary
        """
        active_interns = sum(1 for i in self.interns if i.state == AgentState.RUNNING)
        completed_interns = sum(1 for i in self.interns if i.state == AgentState.COMPLETED)
        failed_interns = sum(1 for i in self.interns if i.state in [AgentState.FAILED, AgentState.KILLED])
        
        return {
            "manager_id": self.manager_id,
            "timestamp": time.time(),
            "interns_total": len(self.interns),
            "interns_active": active_interns,
            "interns_completed": completed_interns,
            "interns_failed": failed_interns,
            "interventions": len(self.status_log),
            "health": "healthy" if failed_interns == 0 else "degraded"
        }


class SovereignOrchestrator:
    """
    Tier 1: The CEO
    Global strategy and belief definition
    CONSTRAINT: Zero interaction with raw agent logs
    """
    
    def __init__(self, project_id: str, global_constraints: Dict[str, Any]):
        self.belief_registry = BeliefRegistry(project_id, global_constraints)
        self.managers: List[EROSManager] = []
        self.strategic_log: List[Dict] = []
        
    def create_manager(self) -> EROSManager:
        """Spawn a new EROS manager"""
        manager_id = f"manager_{len(self.managers)}"
        manager = EROSManager(manager_id, self.belief_registry)
        self.managers.append(manager)
        return manager
    
    async def receive_status_pulses(self) -> List[Dict]:
        """
        Receive ONLY high-level status pulses from managers
        No raw agent logs allowed
        """
        pulses = []
        for manager in self.managers:
            pulse = manager.get_status_pulse()
            pulses.append(pulse)
        return pulses
    
    def make_strategic_decision(self, pulses: List[Dict]) -> Dict:
        """
        Make strategic decisions based on aggregated status
        """
        total_interns = sum(p["interns_total"] for p in pulses)
        total_active = sum(p["interns_active"] for p in pulses)
        total_completed = sum(p["interns_completed"] for p in pulses)
        total_failed = sum(p["interns_failed"] for p in pulses)
        total_interventions = sum(p["interventions"] for p in pulses)
        
        # Calculate health metrics
        completion_rate = total_completed / total_interns if total_interns > 0 else 0
        failure_rate = total_failed / total_interns if total_interns > 0 else 0
        
        # Make strategic decision
        decision = {
            "timestamp": time.time(),
            "turn": self.belief_registry.turn_number,
            "metrics": {
                "total_interns": total_interns,
                "active": total_active,
                "completed": total_completed,
                "failed": total_failed,
                "completion_rate": completion_rate,
                "failure_rate": failure_rate,
                "interventions": total_interventions
            }
        }
        
        # Strategic actions
        if failure_rate > 0.3:
            decision["action"] = "PAUSE_AND_RECALIBRATE"
            decision["reason"] = "High failure rate detected - belief constraints may be unclear"
        elif completion_rate > 0.8:
            decision["action"] = "ADVANCE_PHASE"
            decision["reason"] = "Swarm performing well - advance to next phase"
        else:
            decision["action"] = "CONTINUE_MONITORING"
            decision["reason"] = "Swarm operating within normal parameters"
        
        self.strategic_log.append(decision)
        return decision
    
    def get_orchestrator_view(self) -> Dict:
        """
        CEO's view: strategic overview only, no execution details
        """
        return {
            "project_id": self.belief_registry.project_id,
            "state": self.belief_registry.state,
            "turn": self.belief_registry.turn_number,
            "managers": len(self.managers),
            "last_decision": self.strategic_log[-1] if self.strategic_log else None,
            "belief_registry": self.belief_registry.to_dict()
        }
