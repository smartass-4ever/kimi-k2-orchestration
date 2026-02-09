"""
Kimi K2.5 API Integration for EROS
Sidecar SDK that wraps the Kimi API with EROS orchestration

This replaces the simulated InternAgent.execute_task() with real API calls
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, AsyncIterator
from dataclasses import dataclass
import time


@dataclass
class KimiConfig:
    """Configuration for Kimi K2.5 API"""
    api_key: str
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "moonshot-v1-128k"  # Kimi K2.5 model
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 300  # 5 minutes
    

class KimiInternAgent:
    """
    Real Kimi K2.5 powered intern agent
    Integrates with EROS monitoring and PAD telemetry
    """
    
    def __init__(self, 
                 agent_id: str,
                 specialty: str,
                 manager_id: str,
                 kimi_config: KimiConfig):
        self.agent_id = agent_id
        self.specialty = specialty
        self.manager_id = manager_id
        self.config = kimi_config
        
        # EROS monitoring integration
        self.output_buffer = []
        self.state = "idle"
        self.task = None
        self.start_time = None
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session is active"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
    
    async def execute_task(self, task: Dict, belief_context: Dict) -> Dict:
        """
        Execute task using Kimi K2.5 API with EROS belief context
        
        Args:
            task: Task specification with 'goal', 'context', etc.
            belief_context: Shared belief registry state
            
        Returns:
            Task result with streaming outputs for PAD monitoring
        """
        self.task = task
        self.state = "running"
        self.start_time = time.time()
        
        await self._ensure_session()
        
        # Build system prompt with belief context
        system_prompt = self._build_system_prompt(belief_context)
        
        # Build user prompt from task
        user_prompt = self._build_user_prompt(task)
        
        result = {
            "agent_id": self.agent_id,
            "task_id": task.get("id"),
            "outputs": [],
            "status": "in_progress",
            "belief_context_turn": belief_context.get("turn")
        }
        
        try:
            # Call Kimi API with streaming for real-time monitoring
            async for chunk in self._stream_completion(system_prompt, user_prompt):
                # Store in output buffer for PAD analysis
                self.output_buffer.append({
                    "timestamp": time.time(),
                    "content": chunk,
                    "delta": time.time() - self.start_time
                })
                
                result["outputs"].append(chunk)
                
                # Yield control to allow manager monitoring
                await asyncio.sleep(0)
            
            result["status"] = "completed"
            result["duration"] = time.time() - self.start_time
            self.state = "completed"
            
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error"] = "Task execution exceeded timeout limit"
            self.state = "failed"
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.state = "failed"
        
        return result
    
    def _build_system_prompt(self, belief_context: Dict) -> str:
        """
        Build system prompt that embeds belief registry constraints
        
        This ensures agent operates within project DNA
        """
        constraints = belief_context.get("global_constraints", {})
        
        system_prompt = f"""You are a specialized {self.specialty} agent working on project {belief_context.get('project_id')}.

CRITICAL CONSTRAINTS (Project DNA):
{json.dumps(constraints, indent=2)}

You MUST adhere to these constraints in ALL outputs. Any deviation will result in task failure.

Current project state: {belief_context.get('state')}
Turn: {belief_context.get('turn')}

Work efficiently and maintain alignment with project constraints.
If uncertain, state assumptions clearly.
"""
        return system_prompt
    
    def _build_user_prompt(self, task: Dict) -> str:
        """Build user prompt from task specification"""
        goal = task.get("goal", "")
        context = task.get("context", "")
        constraints = task.get("constraints", [])
        
        prompt_parts = [f"Task: {goal}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if constraints:
            prompt_parts.append("\nAdditional Constraints:")
            for c in constraints:
                prompt_parts.append(f"- {c}")
        
        # Add correction context if this is a respawn
        if task.get("context_correction"):
            prompt_parts.append(f"\n⚠️ CORRECTION FROM PREVIOUS ATTEMPT:")
            prompt_parts.append(task["context_correction"])
        
        return "\n".join(prompt_parts)
    
    async def _stream_completion(self, 
                                  system_prompt: str,
                                  user_prompt: str) -> AsyncIterator[str]:
        """
        Stream completion from Kimi API
        Yields chunks for real-time monitoring
        """
        url = f"{self.config.base_url}/chat/completions"
        
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": True  # Enable streaming for monitoring
        }
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                
                if not line or line == "data: [DONE]":
                    continue
                
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                yield content
                    
                    except json.JSONDecodeError:
                        continue
    
    def get_recent_output(self, n: int = 10) -> List[Dict]:
        """Get recent outputs for PAD telemetry"""
        return self.output_buffer[-n:]
    
    def kill(self, reason: str):
        """Manager-issued SIG_KILL"""
        self.state = "killed"
        self.output_buffer.append({
            "timestamp": time.time(),
            "content": f"TERMINATED: {reason}",
            "terminal": True
        })
        
        # Cancel any ongoing API requests
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()


class KimiEROSManager:
    """
    EROS Manager adapted for real Kimi agents
    Inherits monitoring logic, uses real API agents
    """
    
    def __init__(self, manager_id: str, belief_registry, kimi_config: KimiConfig):
        self.manager_id = manager_id
        self.belief_registry = belief_registry
        self.kimi_config = kimi_config
        
        self.interns: List[KimiInternAgent] = []
        self.max_interns = 10
        self.monitoring_interval = 2.0  # Check every 2 seconds for real API
        self.status_log = []
    
    def spawn_intern(self, specialty: str) -> KimiInternAgent:
        """Spawn Kimi-powered intern"""
        if len(self.interns) >= self.max_interns:
            raise ValueError(f"Manager {self.manager_id} at capacity")
        
        agent_id = f"{self.manager_id}_kimi_{len(self.interns)}"
        
        intern = KimiInternAgent(
            agent_id=agent_id,
            specialty=specialty,
            manager_id=self.manager_id,
            kimi_config=self.kimi_config
        )
        
        self.interns.append(intern)
        
        self.belief_registry.register_agent(agent_id, {
            "type": "kimi_intern",
            "specialty": specialty,
            "manager": self.manager_id,
            "model": self.kimi_config.model
        })
        
        return intern
    
    async def monitor_intern(self, intern: KimiInternAgent):
        """
        Real-time monitoring with PAD telemetry
        Uses same logic as simulated version with timeout protection
        """
        from eros_core import PADAnalyzer
        
        if intern.state != "running":
            return None
        
        # CRITICAL FIX: Prevent zombie monitoring - timeout stalled agents
        if intern.start_time and time.time() - intern.start_time > 600:  # 10 min max
            return {
                "manager_id": self.manager_id,
                "intern_id": intern.agent_id,
                "alert": "TIMEOUT",
                "telemetry": {"pleasure": 0.0, "arousal": 1.0, "dominance": 0.0},
                "reason": "Agent exceeded 10-minute execution timeout",
                "timestamp": time.time()
            }
        
        # Allow warm-up period
        if intern.start_time and time.time() - intern.start_time < 30:
            return None
        
        recent_outputs = intern.get_recent_output(n=5)
        if not recent_outputs or not intern.task:
            return None
        
        # Compute PAD
        pad = PADAnalyzer.analyze_output(
            recent_outputs,
            intern.task.get("goal", "")
        )
        
        # Health check
        if not pad.is_healthy():
            return {
                "manager_id": self.manager_id,
                "intern_id": intern.agent_id,
                "alert": "INTERVENTION_REQUIRED",
                "telemetry": {
                    "pleasure": pad.pleasure,
                    "arousal": pad.arousal,
                    "dominance": pad.dominance
                },
                "reason": self._diagnose_failure(pad),
                "timestamp": time.time()
            }
        
        return None
    
    def _diagnose_failure(self, pad) -> str:
        """Same diagnosis logic as core"""
        if pad.pleasure < 0.2:
            return "Low goal alignment - task divergence detected"
        if pad.arousal > 0.8:
            return "High arousal - agent stalling or infinite retry"
        if pad.dominance < 0.3:
            return "Low dominance - excessive uncertainty"
        return "Unknown failure mode"
    
    async def cleanup(self):
        """Cleanup all intern sessions"""
        cleanup_tasks = [intern.cleanup() for intern in self.interns]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)


# Example usage script
async def demo_kimi_integration():
    """
    Demo of EROS with real Kimi K2.5 API
    
    NOTE: Requires valid Kimi API key
    """
    from eros_core import SovereignOrchestrator
    
    # Configure Kimi
    kimi_config = KimiConfig(
        api_key="YOUR_KIMI_API_KEY",  # Replace with real key
        model="moonshot-v1-128k"
    )
    
    # Initialize EROS
    orchestrator = SovereignOrchestrator(
        project_id="KIMI-DEMO-001",
        global_constraints={
            "language": "Python",
            "style": "concise",
            "format": "markdown"
        }
    )
    
    # Create manager with Kimi config
    manager = KimiEROSManager(
        manager_id="manager_0",
        belief_registry=orchestrator.belief_registry,
        kimi_config=kimi_config
    )
    
    # Spawn Kimi agents
    code_agent = manager.spawn_intern("python_coding")
    doc_agent = manager.spawn_intern("documentation")
    
    # Execute tasks
    belief_context = orchestrator.belief_registry.sync()
    
    tasks = [
        code_agent.execute_task(
            {
                "id": "task_1",
                "goal": "Write a Python function to calculate Fibonacci numbers",
                "constraints": ["Use recursion", "Add docstring"]
            },
            belief_context
        ),
        doc_agent.execute_task(
            {
                "id": "task_2", 
                "goal": "Write markdown documentation for Fibonacci function",
                "context": "Explain time complexity"
            },
            belief_context
        )
    ]
    
    # Monitor in parallel
    async def monitor_loop():
        while any(i.state == "running" for i in manager.interns):
            await asyncio.sleep(manager.monitoring_interval)
            
            for intern in manager.interns:
                alert = await manager.monitor_intern(intern)
                if alert:
                    print(f"⚠️ Alert: {alert['reason']}")
                    intern.kill(alert['reason'])
    
    # Execute
    results = await asyncio.gather(*tasks, monitor_loop())
    
    # Cleanup
    await manager.cleanup()
    
    return results


if __name__ == "__main__":
    print("Kimi K2.5 Integration Module")
    print("This module provides real API integration for EROS")
    print()
    print("To use:")
    print("1. Set your Kimi API key in KimiConfig")
    print("2. Run: asyncio.run(demo_kimi_integration())")
