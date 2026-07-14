# Contributing to ySEO-PRO-AI

We welcome contributions! Here's how to get started.

## Quick Start

```bash
git clone https://github.com/vadimc/ySEO-PRO-AI.git
cd ySEO-PRO-AI
npm install
python test_quick.py   # Verify Python engine
python test_agents.py  # Verify agent system
```

## How to Contribute

### Adding a New MCP Tool

1. Choose the appropriate tool file in `src/mcp/tools/`
2. Add your tool using the `server.tool()` pattern
3. Add the corresponding Python handler in `src/engine/bridge.py`
4. Document in `docs/TOOLS.md`

### Adding a New Fix Prescription

1. Add the issue check in `src/modules/inspector/checks.py`
2. Add the fix handler in `src/modules/doctor/fixer.py`
3. Register the prescription mapping

### Adding an Integration Plugin

1. Create a new file in `src/plugins/`
2. Implement the plugin interface
3. Register in the plugin registry

## Code Style

- **TypeScript**: ESLint + Prettier, strict mode
- **Python**: Type hints, docstrings, stdlib-only for core

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests: `python test_quick.py && python test_agents.py`
5. Commit with conventional format: `feat(module): description`
6. Push and open a PR

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
