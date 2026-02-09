# EROS Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Installation

No dependencies needed for the core demo:

```bash
python eros_demo.py
```

For Kimi K2.5 integration:

```bash
pip install aiohttp asyncio
```

### Running the Demo

**Basic Demo (Simulated Agents)**
```bash
python eros_demo.py
```

Expected output: 11-agent swarm building a web application across 3 teams

**Real-World Example (30 Agents)**
```bash
python real_world_example.py
```

Expected output: E-commerce platform build with 5 specialized teams

**Test Suite**
```bash
pip install pytest pytest-asyncio
pytest eros_tests.py -v
```

### Your First EROS Swarm (5 Lines of Code)

```python
from eros_core import SovereignOrchestrator

# 1. Define project DNA
orchestrator = SovereignOrchestrator(
    project_id="MY-PROJECT",
    global_constraints={"theme": "dark", "standard": "PEP8"}
)

# 2. Create manager
manager = orchestrator.create_manager()

# 3. Spawn agents
agent1 = manager.spawn_intern("backend_code")
agent2 = manager.spawn_intern("frontend_code")

# 4. Execute tasks
import asyncio
result = asyncio.run(agent1.execute_task(
    {"goal": "build API", "estimated_steps": 3},
    orchestrator.belief_registry.sync()
))

# 5. Check results
print(f"Status: {result['status']}")
```

### Integrating with Kimi K2.5 API

```python
from kimi_integration import KimiConfig, KimiEROSManager
from eros_core import SovereignOrchestrator

# Configure your Kimi API
config = KimiConfig(
    api_key="YOUR_KIMI_API_KEY",
    model="moonshot-v1-128k"
)

# Initialize EROS with real Kimi agents
orchestrator = SovereignOrchestrator("PROD-001", {})
manager = KimiEROSManager("manager_0", orchestrator.belief_registry, config)

# Spawn real Kimi-powered agent
agent = manager.spawn_intern("python_developer")

# Execute with monitoring
result = await agent.execute_task(
    {
        "goal": "Write a REST API endpoint",
        "constraints": ["FastAPI", "Type hints", "Docstrings"]
    },
    orchestrator.belief_registry.sync()
)

print(result)
```

### Key Files

| File | Purpose |
|------|---------|
| `eros_core.py` | Core architecture (Orchestrator, Managers, Agents) |
| `eros_demo.py` | Working demonstration with 11 agents |
| `kimi_integration.py` | Real Kimi K2.5 API integration |
| `real_world_example.py` | E-commerce platform with 30 agents |
| `eros_tests.py` | Comprehensive test suite |
| `README.md` | Full documentation |

### Understanding the Architecture

```
CEO (Tier 1)
    ↓ [Status Pulses Only]
Managers (Tier 2) [Monitor every 2s]
    ↓ [Task Assignment]
Interns (Tier 3) [Execute & Report]
    ↓ [Sync Before Each Turn]
Belief Registry (Shared DNA)
```

### Customization

**Change monitoring frequency:**
```python
manager.monitoring_interval = 1.0  # Check every 1 second
```

**Adjust manager capacity:**
```python
manager.max_interns = 15  # Up to 15 agents per manager
```

**Custom PAD thresholds:**
```python
# In PADTelemetry.is_healthy()
return (
    self.pleasure > 0.3 and  # Stricter goal alignment
    self.arousal < 0.6 and   # More sensitive to stalling
    self.dominance > 0.4     # Higher certainty required
)
```

### Common Use Cases

**1. Code Generation Swarm**
```python
constraints = {
    "language": "Python",
    "style": "PEP8",
    "min_test_coverage": 80
}
```

**2. Content Creation Swarm**
```python
constraints = {
    "tone": "professional",
    "format": "markdown",
    "max_length": 1000
}
```

**3. Research Swarm**
```python
constraints = {
    "sources_required": True,
    "citation_format": "APA",
    "depth": "comprehensive"
}
```

### Troubleshooting

**Issue: Agents not completing tasks**
- Check `monitoring_interval` (may be too long)
- Verify belief constraints are clear
- Review PAD telemetry for insights

**Issue: Too many interventions**
- PAD thresholds may be too strict
- Increase `pleasure` threshold to 0.1
- Decrease `arousal` threshold to 0.9

**Issue: Manager at capacity**
- Create additional managers
- Or increase `max_interns` per manager

### Next Steps

1. **Run the demos** to see EROS in action
2. **Read the README.md** for architecture details
3. **Explore eros_tests.py** for usage patterns
4. **Integrate with Kimi API** for production use
5. **Customize for your use case**

### Getting Help

- Review README.md for detailed documentation
- Check eros_tests.py for example patterns
- Examine real_world_example.py for complex scenarios

---

**Happy Swarming! 🐝**
