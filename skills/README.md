# Agent Skills

This directory contains standardized **Skills** that can be utilized by AI agents. A Skill is a self-contained package of instructions (`SKILL.md`), documentation (`README.md`), and executable tools (`scripts/`).

## Structure

Each skill follows this structure:

```
skills/
└── <skill-name>/
    ├── README.md           # Documentation: Inputs, Outputs, Usage
    ├── SKILL.md            # The system prompt / instructions for the Agent
    ├── scripts/            # Executable scripts (bash, python, etc.)
    └── examples/           # (Optional) Example inputs/outputs
```

## Usage

To use a skill:
1.  Load the `SKILL.md` into the agent's context.
2.  Ensure the agent has access to run the scripts in `scripts/`.
3.  Provide the necessary inputs as defined in `README.md`.

## Methodology

These skills implement the **Context Engineering Methodology**, breaking down complex workflows into atomic, reproducible capabilities.
