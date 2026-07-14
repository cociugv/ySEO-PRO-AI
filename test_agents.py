"""Test agent system for ySEO-PRO-AI."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.crew.base_agent import BaseAgent, AgentResult
from src.crew.orchestrator import CrewOrchestrator

# Test 1: Agent initialization
print("TEST 1: Crew Orchestrator Init")
config = {
    "platform": {"name": "ySEO-PRO-AI", "version": "1.0.0"},
    "targets": {"languages": ["en", "ro", "de"]},
    "modules": {
        "inspector": {"timeout_seconds": 10},
        "doctor": {"dry_run": True},
    },
    "integrations": {"indexnow": {"key": "test-key"}},
}
crew = CrewOrchestrator(config)

agents = crew.list_agents()
assert len(agents) == 6, f"Expected 6 agents, got {len(agents)}"
agent_names = [a["name"] for a in agents]
assert "inspector" in agent_names
assert "doctor" in agent_names
assert "polyglot" in agent_names
assert "sentinel" in agent_names
assert "publisher" in agent_names
assert "strategist" in agent_names
print(f"  PASSED: {len(agents)} agents initialized")

# Test 2: Agent capabilities
print("\nTEST 2: Agent Capabilities")
for agent in agents:
    assert agent["capabilities"], f"{agent['name']} has no capabilities"
    assert agent["modules"], f"{agent['name']} has no modules"
print("  PASSED: All agents have capabilities and modules defined")

# Test 3: Task routing
print("\nTEST 3: Task Routing")
assert "inspector" in CrewOrchestrator.TASK_ROUTING["audit"]
assert "doctor" in CrewOrchestrator.TASK_ROUTING["fix"]
assert "sentinel" in CrewOrchestrator.TASK_ROUTING["monitor"]
assert "publisher" in CrewOrchestrator.TASK_ROUTING["publish"]
assert "strategist" in CrewOrchestrator.TASK_ROUTING["compete"]
assert len(CrewOrchestrator.TASK_ROUTING["full"]) == 6
print("  PASSED: Task routing maps correctly")

# Test 4: AgentResult structure
print("\nTEST 4: AgentResult Structure")
result = AgentResult(
    agent_name="test",
    success=True,
    summary="Test result",
    issues_found=5,
    fixes_applied=3,
    recommendations=["Do X", "Do Y"],
    elapsed_seconds=1.5,
)
d = result.to_dict()
assert d["agent"] == "test"
assert d["success"] is True
assert d["issues_found"] == 5
assert d["fixes_applied"] == 3
assert len(d["recommendations"]) == 2
print("  PASSED: AgentResult serialization OK")

# Test 5: Strategist programmatic generation (no network needed)
print("\nTEST 5: Strategist Programmatic Pages")
from src.modules.architect.generator import ProgrammaticGenerator
gen = ProgrammaticGenerator({
    "brand_name": "yLink.pro",
    "base_url": "https://ylink.pro",
    "languages": ["en", "ro", "de"],
})

cities = [
    {"name": "Berlin", "country": "Germany"},
    {"name": "Bucharest", "country": "Romania"},
]
pages = gen.generate_city_pages(cities)
assert len(pages) == 2
assert "Berlin" in pages[0].title
assert pages[0].page_type == "city"
assert len(pages[0].keywords) > 0

competitors = [{"name": "Bitly"}, {"name": "TinyURL"}]
vs_pages = gen.generate_comparison_pages(competitors)
assert len(vs_pages) == 2
assert "Bitly" in vs_pages[0].title
assert vs_pages[0].page_type == "versus"
print(f"  PASSED: Generated {len(pages)} city + {len(vs_pages)} comparison pages")

# Test 6: Template engine
print("\nTEST 6: Template Engine")
from src.modules.architect.templates import TemplateEngine
engine = TemplateEngine()

result = engine.render("Hello {name}, welcome to {city}!", {"name": "Vadim", "city": "Berlin"})
assert result == "Hello Vadim, welcome to Berlin!", f"Got: {result}"

result2 = engine.render("{missing|default_val} test", {})
assert result2 == "default_val test", f"Got: {result2}"
print("  PASSED: Template rendering OK")

print("\n" + "=" * 50)
print("  ALL AGENT TESTS PASSED!")
print("=" * 50)
