"""
EROS Test Suite
Comprehensive tests for all architecture components
"""

import asyncio
import pytest
from eros_core import (
    SovereignOrchestrator,
    EROSManager,
    InternAgent,
    BeliefRegistry,
    PADTelemetry,
    PADAnalyzer,
    AgentState
)


class TestBeliefRegistry:
    """Test the shared state substrate"""
    
    def test_initialization(self):
        registry = BeliefRegistry(
            project_id="TEST-001",
            global_constraints={"theme": "dark", "lang": "python"}
        )
        
        assert registry.project_id == "TEST-001"
        assert registry.global_constraints["theme"] == "dark"
        assert registry.state == "initialization"
        assert registry.turn_number == 0
    
    def test_sync(self):
        registry = BeliefRegistry("TEST-002", {"key": "value"})
        
        sync_data = registry.sync()
        
        assert sync_data["project_id"] == "TEST-002"
        assert sync_data["global_constraints"]["key"] == "value"
        assert sync_data["state"] == "initialization"
        assert sync_data["turn"] == 0
    
    def test_advance_turn(self):
        registry = BeliefRegistry("TEST-003", {})
        
        assert registry.turn_number == 0
        
        registry.advance_turn("phase_2")
        
        assert registry.turn_number == 1
        assert registry.state == "phase_2"
    
    def test_agent_registration(self):
        registry = BeliefRegistry("TEST-004", {})
        
        registry.register_agent("agent_1", {"specialty": "code"})
        
        assert "agent_1" in registry.agent_registry
        assert registry.agent_registry["agent_1"]["specialty"] == "code"
        assert registry.agent_registry["agent_1"]["turn"] == 0


class TestPADTelemetry:
    """Test PAD health monitoring"""
    
    def test_healthy_agent(self):
        pad = PADTelemetry(pleasure=0.8, arousal=0.3, dominance=0.7)
        
        assert pad.is_healthy() is True
    
    def test_unhealthy_low_pleasure(self):
        pad = PADTelemetry(pleasure=0.1, arousal=0.3, dominance=0.7)
        
        assert pad.is_healthy() is False
    
    def test_unhealthy_high_arousal(self):
        pad = PADTelemetry(pleasure=0.8, arousal=0.9, dominance=0.7)
        
        assert pad.is_healthy() is False
    
    def test_unhealthy_low_dominance(self):
        pad = PADTelemetry(pleasure=0.8, arousal=0.3, dominance=0.1)
        
        assert pad.is_healthy() is False
    
    def test_string_representation(self):
        pad = PADTelemetry(pleasure=0.75, arousal=0.25, dominance=0.65)
        
        result = str(pad)
        
        assert "P=0.75" in result
        assert "A=0.25" in result
        assert "D=0.65" in result


class TestPADAnalyzer:
    """Test PAD computation from agent outputs"""
    
    def test_analyze_successful_output(self):
        outputs = [
            {"content": "Successfully implemented authentication API"},
            {"content": "Completed user login endpoint"},
            {"content": "Processed authentication tokens"}
        ]
        goal = "implement authentication API"
        
        pad = PADAnalyzer.analyze_output(outputs, goal)
        
        # Should have good pleasure (goal alignment)
        assert pad.pleasure > 0.3
        # Should have low arousal (no errors)
        assert pad.arousal < 0.5
    
    def test_analyze_failing_output(self):
        outputs = [
            {"content": "Error: authentication failed"},
            {"content": "Retry attempt 1"},
            {"content": "Error: authentication failed"},
            {"content": "Retry attempt 2"}
        ]
        goal = "implement authentication API"
        
        pad = PADAnalyzer.analyze_output(outputs, goal)
        
        # Should have high arousal (errors and retries)
        assert pad.arousal > 0.4
    
    def test_analyze_uncertain_output(self):
        outputs = [
            {"content": "Maybe we should try this approach"},
            {"content": "Not sure if this is correct"},
            {"content": "Might work but uncertain"}
        ]
        goal = "implement feature"
        
        pad = PADAnalyzer.analyze_output(outputs, goal)
        
        # Should have low dominance (uncertainty)
        assert pad.dominance < 0.5
    
    def test_empty_output(self):
        pad = PADAnalyzer.analyze_output([], "some goal")
        
        assert pad.pleasure == 0.0
        assert pad.arousal == 0.0
        assert pad.dominance == 0.0


class TestInternAgent:
    """Test intern agent behavior"""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        intern = InternAgent("agent_1", "python_code", "manager_0")
        
        task = {
            "id": "task_1",
            "goal": "write Python function",
            "estimated_steps": 3
        }
        
        result = await intern.execute_task(task, {})
        
        assert result["status"] == "completed"
        assert result["agent_id"] == "agent_1"
        assert result["task_id"] == "task_1"
        assert len(result["outputs"]) == 3
        assert intern.state == AgentState.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_task_with_failure(self):
        intern = InternAgent("agent_2", "browser", "manager_0")
        
        task = {
            "id": "task_2",
            "goal": "navigate website",
            "estimated_steps": 5,
            "inject_failure": True
        }
        
        result = await intern.execute_task(task, {})
        
        assert result["status"] == "error"
        assert "error" in result
        assert intern.state == AgentState.FAILED
    
    def test_get_recent_output(self):
        intern = InternAgent("agent_3", "search", "manager_0")
        
        # Manually add outputs
        for i in range(15):
            intern.output_buffer.append({"step": i, "content": f"output {i}"})
        
        recent = intern.get_recent_output(n=5)
        
        assert len(recent) == 5
        assert recent[-1]["step"] == 14  # Most recent
    
    def test_kill(self):
        intern = InternAgent("agent_4", "code", "manager_0")
        intern.state = AgentState.RUNNING
        
        intern.kill("Test termination")
        
        assert intern.state == AgentState.KILLED
        assert "KILLED" in intern.output_buffer[-1]["content"]


class TestEROSManager:
    """Test manager coordination"""
    
    def test_spawn_intern(self):
        registry = BeliefRegistry("TEST-MGR", {})
        manager = EROSManager("manager_0", registry)
        
        intern = manager.spawn_intern("python_code")
        
        assert len(manager.interns) == 1
        assert intern.specialty == "python_code"
        assert intern.manager_id == "manager_0"
        assert "manager_0_intern_0" in registry.agent_registry
    
    def test_spawn_intern_at_capacity(self):
        registry = BeliefRegistry("TEST-MGR-CAP", {})
        manager = EROSManager("manager_1", registry)
        
        # Spawn max interns
        for i in range(manager.max_interns):
            manager.spawn_intern("specialty")
        
        # Try to spawn one more
        with pytest.raises(ValueError, match="at capacity"):
            manager.spawn_intern("overflow")
    
    @pytest.mark.asyncio
    async def test_monitor_healthy_intern(self):
        registry = BeliefRegistry("TEST-MON", {})
        manager = EROSManager("manager_2", registry)
        intern = manager.spawn_intern("code")
        
        # Simulate healthy work
        intern.state = AgentState.RUNNING
        intern.task = {"goal": "implement feature"}
        intern.output_buffer = [
            {"content": "Successfully implemented feature"},
            {"content": "Completed all tests"}
        ]
        
        alert = await manager.monitor_intern(intern)
        
        assert alert is None  # Healthy agent, no alert
    
    @pytest.mark.asyncio
    async def test_monitor_unhealthy_intern(self):
        registry = BeliefRegistry("TEST-MON-UNHEALTHY", {})
        manager = EROSManager("manager_3", registry)
        intern = manager.spawn_intern("code")
        
        # Simulate unhealthy work
        intern.state = AgentState.RUNNING
        intern.task = {"goal": "implement authentication"}
        intern.output_buffer = [
            {"content": "Error occurred"},
            {"content": "Retry attempt 1"},
            {"content": "Error occurred again"}
        ]
        
        alert = await manager.monitor_intern(intern)
        
        assert alert is not None
        assert alert["alert"] == "INTERVENTION_REQUIRED"
        assert "telemetry" in alert
    
    @pytest.mark.asyncio
    async def test_intervene(self):
        registry = BeliefRegistry("TEST-INTERVENE", {})
        manager = EROSManager("manager_4", registry)
        intern = manager.spawn_intern("code")
        intern.state = AgentState.RUNNING
        
        intervention = await manager.intervene(intern, "Test intervention")
        
        assert intervention["action"] == "SIG_KILL"
        assert intervention["manager_id"] == "manager_4"
        assert len(manager.status_log) == 1
        assert intern.state == AgentState.KILLED
    
    def test_get_status_pulse(self):
        registry = BeliefRegistry("TEST-PULSE", {})
        manager = EROSManager("manager_5", registry)
        
        # Create interns with various states
        intern1 = manager.spawn_intern("code")
        intern1.state = AgentState.COMPLETED
        
        intern2 = manager.spawn_intern("browser")
        intern2.state = AgentState.RUNNING
        
        intern3 = manager.spawn_intern("search")
        intern3.state = AgentState.FAILED
        
        pulse = manager.get_status_pulse()
        
        assert pulse["manager_id"] == "manager_5"
        assert pulse["interns_total"] == 3
        assert pulse["interns_active"] == 1
        assert pulse["interns_completed"] == 1
        assert pulse["interns_failed"] == 1
        assert pulse["health"] == "degraded"


class TestSovereignOrchestrator:
    """Test top-level orchestrator"""
    
    def test_initialization(self):
        orchestrator = SovereignOrchestrator(
            project_id="TEST-ORCH",
            global_constraints={"theme": "dark"}
        )
        
        assert orchestrator.belief_registry.project_id == "TEST-ORCH"
        assert len(orchestrator.managers) == 0
    
    def test_create_manager(self):
        orchestrator = SovereignOrchestrator("TEST-ORCH-2", {})
        
        manager1 = orchestrator.create_manager()
        manager2 = orchestrator.create_manager()
        
        assert len(orchestrator.managers) == 2
        assert manager1.manager_id == "manager_0"
        assert manager2.manager_id == "manager_1"
    
    @pytest.mark.asyncio
    async def test_receive_status_pulses(self):
        orchestrator = SovereignOrchestrator("TEST-ORCH-3", {})
        
        manager1 = orchestrator.create_manager()
        manager2 = orchestrator.create_manager()
        
        # Add some interns
        manager1.spawn_intern("code")
        manager2.spawn_intern("browser")
        
        pulses = await orchestrator.receive_status_pulses()
        
        assert len(pulses) == 2
        assert pulses[0]["manager_id"] == "manager_0"
        assert pulses[1]["manager_id"] == "manager_1"
    
    def test_make_strategic_decision_healthy(self):
        orchestrator = SovereignOrchestrator("TEST-ORCH-4", {})
        
        pulses = [
            {
                "manager_id": "manager_0",
                "interns_total": 5,
                "interns_active": 0,
                "interns_completed": 5,
                "interns_failed": 0,
                "interventions": 0
            }
        ]
        
        decision = orchestrator.make_strategic_decision(pulses)
        
        assert decision["action"] == "ADVANCE_PHASE"
        assert decision["metrics"]["completion_rate"] == 1.0
        assert decision["metrics"]["failure_rate"] == 0.0
    
    def test_make_strategic_decision_degraded(self):
        orchestrator = SovereignOrchestrator("TEST-ORCH-5", {})
        
        pulses = [
            {
                "manager_id": "manager_0",
                "interns_total": 10,
                "interns_active": 0,
                "interns_completed": 3,
                "interns_failed": 7,
                "interventions": 5
            }
        ]
        
        decision = orchestrator.make_strategic_decision(pulses)
        
        assert decision["action"] == "PAUSE_AND_RECALIBRATE"
        assert decision["metrics"]["failure_rate"] > 0.3
    
    def test_get_orchestrator_view(self):
        orchestrator = SovereignOrchestrator("TEST-ORCH-6", {"key": "val"})
        manager = orchestrator.create_manager()
        
        view = orchestrator.get_orchestrator_view()
        
        assert view["project_id"] == "TEST-ORCH-6"
        assert view["managers"] == 1
        assert view["belief_registry"]["constraints"]["key"] == "val"


# Integration Tests

class TestIntegrationScenarios:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_intervention(self):
        """Test complete workflow from CEO to intervention"""
        
        # Initialize system
        orchestrator = SovereignOrchestrator(
            "INTEGRATION-001",
            {"standard": "strict"}
        )
        
        manager = orchestrator.create_manager()
        
        # Spawn intern with failing task
        intern = manager.spawn_intern("test_agent")
        
        task = {
            "id": "fail_task",
            "goal": "complete task",
            "estimated_steps": 3,
            "inject_failure": True
        }
        
        belief_context = orchestrator.belief_registry.sync()
        
        # Start execution and monitoring in parallel
        async def monitor():
            await asyncio.sleep(0.1)
            alert = await manager.monitor_intern(intern)
            if alert:
                await manager.intervene(intern, alert["reason"])
        
        task_result, _ = await asyncio.gather(
            intern.execute_task(task, belief_context),
            monitor()
        )
        
        # Verify intervention occurred
        assert task_result["status"] in ["error", "failed"]
        
        # Check manager logged intervention
        pulses = await orchestrator.receive_status_pulses()
        assert pulses[0]["interns_failed"] > 0
        
        # CEO makes decision
        decision = orchestrator.make_strategic_decision(pulses)
        
        assert "action" in decision
        assert "metrics" in decision


# Performance Benchmarks

class TestPerformanceBenchmarks:
    """Performance and scaling tests"""
    
    @pytest.mark.asyncio
    async def test_manager_monitoring_overhead(self):
        """Measure monitoring overhead with many agents"""
        import time
        
        registry = BeliefRegistry("PERF-001", {})
        manager = EROSManager("perf_manager", registry)
        
        # Spawn max interns
        interns = []
        for i in range(10):
            intern = manager.spawn_intern(f"agent_{i}")
            intern.state = AgentState.RUNNING
            intern.task = {"goal": "test task"}
            intern.output_buffer = [{"content": "working"}]
            interns.append(intern)
        
        # Measure monitoring time
        start = time.time()
        
        for intern in interns:
            await manager.monitor_intern(intern)
        
        duration = time.time() - start
        
        # Should complete in under 100ms for 10 agents
        assert duration < 0.1
        print(f"Monitored 10 agents in {duration*1000:.2f}ms")


if __name__ == "__main__":
    print("Running EROS Test Suite...")
    print("Use: pytest eros_tests.py -v")
    print()
    print("Quick test:")
    
    # Run a quick smoke test
    async def smoke_test():
        orch = SovereignOrchestrator("SMOKE-TEST", {"mode": "test"})
        mgr = orch.create_manager()
        intern = mgr.spawn_intern("code")
        
        result = await intern.execute_task(
            {"id": "smoke", "goal": "test", "estimated_steps": 2},
            orch.belief_registry.sync()
        )
        
        print(f"✓ Smoke test passed: {result['status']}")
    
    asyncio.run(smoke_test())
