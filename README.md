# cdk-sleep-py-qdev

![CI](https://github.com/obstreperous-ai/cdk-sleep-py-qdev/workflows/CI/badge.svg)

**Event-Driven Sleep Audio Pipeline** - A TDD-first AWS CDK Python project for issue-driven development.

## Project Philosophy

This project follows a **Test-Driven Development (TDD) first** approach with **pure issue-driven development**:

1. 🔴 **Red**: Write a failing test that defines desired behavior
2. 🟢 **Green**: Write minimal code to make the test pass  
3. 🔄 **Refactor**: Clean up while keeping tests green
4. 📝 **Document**: Keep ARCHITECTURE.md and Mermaid diagrams in sync

Every feature begins with a GitHub issue and is implemented test-first.

## Quick Start

### Prerequisites

- Python 3.9+ 
- AWS CDK CLI: `npm install -g aws-cdk`
- AWS credentials configured

### Setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

**1. Create a virtual environment:**

MacOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```
python -m venv .venv
.venv\Scripts\activate.bat
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**3. Run tests (TDD approach):**
```bash
pytest tests/ -v
```

**4. Synthesize CloudFormation:**
```bash
cdk synth
```

**5. Deploy to AWS:**
```bash
cdk deploy
```

## Development Workflow

### TDD Cycle

1. Create/update a test in `tests/unit/`
2. Run `pytest` - test should fail (Red)
3. Implement minimal code in `cdk_base/`
4. Run `pytest` - test should pass (Green)
5. Refactor and ensure tests stay green
6. Update `ARCHITECTURE.md` with changes
7. Commit and push (CI runs automatically)

### Testing

Run all tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=cdk_base --cov-report=term-missing
```

### CI/CD Pipeline

The GitHub Actions CI pipeline (`.github/workflows/ci.yml`) automatically:
- Runs pytest with coverage
- Synthesizes CDK stacks
- Validates CloudFormation templates
- Tests against Python 3.9, 3.10, 3.11, and 3.12

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation, including Mermaid diagrams and component specifications.
