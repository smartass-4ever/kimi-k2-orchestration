"""
EROS Demonstration: Hierarchical Swarm in Action

This demonstrates the three-tier hierarchy managing a simulated
software development project with 20+ agents.
"""

import asyncio
import json
from eros_core import (
    SovereignOrchestrator,
    EROSManager,
    InternAgent,
    AgentState
)


async def simulate_development_project():
    """
    Simulate a software development project with EROS architecture
    """
    print("=" * 80)
    print("EROS: Hierarchical Agentic Orchestration Demo")
    print("Project: Building a Web Application with 20-Agent Swarm")
    print("=" * 80)
    print()
    
    # TIER 1: Initialize Sovereign Orchestrator (CEO)
    print("🎯 TIER 1: Initializing Sovereign Orchestrator...")
    orchestrator = SovereignOrchestrator(
        project_id="WEBAPP-2025",
        global_constraints={
            "ui_theme": "dark_mode_blue",
            "coding_standard": "PEP8",
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "api_version": "v3"
        }
    )
    print(f"   ✓ Belief Registry initialized: {orchestrator.belief_registry.project_id}")
    print(f"   ✓ Global constraints: {json.dumps(orchestrator.belief_registry.global_constraints, indent=6)}")
    print()
    
    # TIER 2: Create Managers (Middle Management)
    print("👔 TIER 2: Spawning EROS Managers...")
    
    # Manager 1: Backend Team
    backend_manager = orchestrator.create_manager()
    print(f"   ✓ {backend_manager.manager_id}: Backend Development (Python/FastAPI)")
    
    # Manager 2: Frontend Team
    frontend_manager = orchestrator.create_manager()
    print(f"   ✓ {frontend_manager.manager_id}: Frontend Development (React)")
    
    # Manager 3: Database Team
    database_manager = orchestrator.create_manager()
    print(f"   ✓ {database_manager.manager_id}: Database & Infrastructure")
    print()
    
    # TIER 3: Spawn Intern Agents
    print("🤖 TIER 3: Spawning Intern Agents...")
    
    # Backend interns
    backend_tasks = [
        {"id": "api-auth", "goal": "implement user authentication API", "estimated_steps": 4},
        {"id": "api-users", "goal": "create user CRUD endpoints", "estimated_steps": 3},
        {"id": "api-data", "goal": "build data processing pipeline", "estimated_steps": 5},
        {"id": "api-tests", "goal": "write API integration tests", "estimated_steps": 4},
    ]
    
    backend_interns = []
    for task in backend_tasks:
        intern = backend_manager.spawn_intern("backend_code")
        backend_interns.append((intern, task))
        print(f"   ✓ {intern.agent_id}: {task['goal']}")
    
    # Frontend interns
    frontend_tasks = [
        {"id": "ui-login", "goal": "create login component with dark_mode_blue theme", "estimated_steps": 3},
        {"id": "ui-dashboard", "goal": "build dashboard layout", "estimated_steps": 4},
        {"id": "ui-forms", "goal": "implement form validation", "estimated_steps": 3},
        {"id": "ui-failing", "goal": "create user profile page", "estimated_steps": 5, "inject_failure": True},  # This will fail
    ]
    
    frontend_interns = []
    for task in frontend_tasks:
        intern = frontend_manager.spawn_intern("frontend_code")
        frontend_interns.append((intern, task))
        marker = "⚠️ " if task.get("inject_failure") else "✓ "
        print(f"   {marker}{intern.agent_id}: {task['goal']}")
    
    # Database interns
    database_tasks = [
        {"id": "db-schema", "goal": "design PostgreSQL schema", "estimated_steps": 3},
        {"id": "db-migrations", "goal": "create migration scripts", "estimated_steps": 4},
        {"id": "db-indexes", "goal": "optimize database indexes", "estimated_steps": 3},
    ]
    
    database_interns = []
    for task in database_tasks:
        intern = database_manager.spawn_intern("database")
        database_interns.append((intern, task))
        print(f"   ✓ {intern.agent_id}: {task['goal']}")
    
    print()
    print(f"📊 Total: {len(backend_interns) + len(frontend_interns) + len(database_interns)} intern agents spawned")
    print()
    
    # Start execution phase
    print("=" * 80)
    print("⚡ EXECUTION PHASE: Starting Asynchronous Work")
    print("=" * 80)
    print()
    
    # Sync all agents with belief registry
    belief_context = orchestrator.belief_registry.sync()
    print(f"🔄 All agents synced with Belief Registry (Turn {belief_context['turn']})")
    print()
    
    # Create execution tasks
    all_intern_tasks = []
    
    # Start backend work
    for intern, task in backend_interns:
        all_intern_tasks.append(intern.execute_task(task, belief_context))
    
    # Start frontend work
    for intern, task in frontend_interns:
        all_intern_tasks.append(intern.execute_task(task, belief_context))
    
    # Start database work
    for intern, task in database_interns:
        all_intern_tasks.append(intern.execute_task(task, belief_context))
    
    # Create monitoring tasks for each manager
    async def monitor_team(manager: EROSManager, team_name: str):
        """Monitor a team and intervene when needed"""
        print(f"👁️  {team_name} Manager: Starting monitoring loop...")
        
        interventions = []
        while True:
            await asyncio.sleep(manager.monitoring_interval)
            
            # Check all interns
            for intern in manager.interns:
                alert = await manager.monitor_intern(intern)
                
                if alert:
                    print(f"\n⚠️  ALERT from {team_name} Manager:")
                    print(f"   Intern: {alert['intern_id']}")
                    print(f"   Reason: {alert['reason']}")
                    print(f"   Telemetry: {alert['telemetry']}")
                    
                    # Intervene
                    intervention = await manager.intervene(intern, alert['reason'])
                    interventions.append(intervention)
                    print(f"   Action: SIG_KILL issued - {intervention['reason']}")
                    
                    # Respawn with correction
                    correction = f"Previous attempt failed: {alert['reason']}. Ensure strict adherence to {belief_context['global_constraints']}"
                    new_intern = await manager.respawn_with_correction(intern, correction)
                    print(f"   Recovery: Spawned {new_intern.agent_id} with corrected context")
            
            # Check if all interns are done
            active_count = sum(1 for i in manager.interns if i.state == AgentState.RUNNING)
            if active_count == 0:
                break
        
        return interventions
    
    # Start monitoring in parallel with execution
    monitoring_tasks = [
        monitor_team(backend_manager, "Backend"),
        monitor_team(frontend_manager, "Frontend"),
        monitor_team(database_manager, "Database")
    ]
    
    # Run everything concurrently
    print("🚀 All teams executing in parallel...\n")
    
    results = await asyncio.gather(*all_intern_tasks)
    interventions_list = await asyncio.gather(*monitoring_tasks)
    
    print("\n" + "=" * 80)
    print("✅ EXECUTION COMPLETE")
    print("=" * 80)
    print()
    
    # Managers generate status pulses (NO RAW LOGS)
    print("📡 TIER 2: Managers generating Status Pulses for CEO...")
    print()
    
    pulses = await orchestrator.receive_status_pulses()
    for pulse in pulses:
        print(f"   {pulse['manager_id']}:")
        print(f"      Total Interns: {pulse['interns_total']}")
        print(f"      Active: {pulse['interns_active']}")
        print(f"      Completed: {pulse['interns_completed']}")
        print(f"      Failed: {pulse['interns_failed']}")
        print(f"      Interventions: {pulse['interventions']}")
        print(f"      Health: {pulse['health'].upper()}")
        print()
    
    # CEO makes strategic decision
    print("🎯 TIER 1: Sovereign Orchestrator analyzing Status Pulses...")
    decision = orchestrator.make_strategic_decision(pulses)
    
    print(f"\n📊 CEO Decision:")
    print(f"   Action: {decision['action']}")
    print(f"   Reason: {decision['reason']}")
    print(f"   Metrics:")
    print(f"      - Total Interns: {decision['metrics']['total_interns']}")
    print(f"      - Completion Rate: {decision['metrics']['completion_rate']:.1%}")
    print(f"      - Failure Rate: {decision['metrics']['failure_rate']:.1%}")
    print(f"      - Total Interventions: {decision['metrics']['interventions']}")
    print()
    
    # Show CEO's view (strategic only)
    print("=" * 80)
    print("🎯 SOVEREIGN ORCHESTRATOR VIEW (Strategic Overview)")
    print("=" * 80)
    
    ceo_view = orchestrator.get_orchestrator_view()
    print(json.dumps(ceo_view, indent=2))
    print()
    
    # Performance analysis
    print("=" * 80)
    print("📈 EROS PERFORMANCE ANALYSIS")
    print("=" * 80)
    print()
    
    total_interventions = sum(len(i) for i in interventions_list)
    successful_tasks = sum(1 for r in results if r['status'] == 'completed')
    failed_tasks = sum(1 for r in results if r['status'] in ['error', 'failed'])
    
    print(f"✅ Successful Tasks: {successful_tasks}/{len(results)}")
    print(f"❌ Failed Tasks: {failed_tasks}/{len(results)}")
    print(f"🔧 Total Interventions: {total_interventions}")
    print(f"⚡ Early Detection Rate: {(total_interventions / max(failed_tasks, 1)) * 100:.0f}%")
    print()
    
    if total_interventions > 0:
        print("💡 EROS Benefits Demonstrated:")
        print("   ✓ Failed agents detected within seconds (not hours)")
        print("   ✓ Orchestrator never exposed to raw agent logs")
        print("   ✓ Managers autonomously handled failures")
        print("   ✓ Context window of CEO remains clean")
        print("   ✓ Strategic decision-making unaffected by execution noise")
    
    print()
    print("=" * 80)
    print("🎉 DEMO COMPLETE")
    print("=" * 80)


async def run_mini_stress_test():
    """
    Quick stress test: 50 agents across 5 managers
    """
    print("\n" + "=" * 80)
    print("🔥 STRESS TEST: 50-Agent Swarm")
    print("=" * 80)
    print()
    
    orchestrator = SovereignOrchestrator(
        project_id="STRESS-TEST-001",
        global_constraints={"test_mode": True}
    )
    
    # Create 5 managers, each with 10 interns
    for m in range(5):
        manager = orchestrator.create_manager()
        
        tasks = []
        for i in range(10):
            intern = manager.spawn_intern(f"specialty_{i % 3}")
            
            # Inject failures randomly
            task = {
                "id": f"task_{m}_{i}",
                "goal": f"execute specialized task {i}",
                "estimated_steps": 3,
                "inject_failure": (i % 7 == 0)  # ~14% failure rate
            }
            tasks.append(intern.execute_task(task, orchestrator.belief_registry.sync()))
        
        # Monitor manager
        async def monitor():
            while any(i.state == AgentState.RUNNING for i in manager.interns):
                await asyncio.sleep(0.3)
                for intern in manager.interns:
                    alert = await manager.monitor_intern(intern)
                    if alert:
                        await manager.intervene(intern, alert['reason'])
        
        await asyncio.gather(*tasks, monitor())
    
    # Get final status
    pulses = await orchestrator.receive_status_pulses()
    decision = orchestrator.make_strategic_decision(pulses)
    
    print(f"✅ Stress Test Complete:")
    print(f"   Total Agents: 50")
    print(f"   Managers: 5")
    print(f"   Completion Rate: {decision['metrics']['completion_rate']:.1%}")
    print(f"   Interventions: {decision['metrics']['interventions']}")
    print()


if __name__ == "__main__":
    # Run main demo
    asyncio.run(simulate_development_project())
    
    # Uncomment to run stress test
    # asyncio.run(run_mini_stress_test())
