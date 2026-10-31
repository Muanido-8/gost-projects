# 👻 Ghost Projects

**Ghost Projects** is a desktop developer tool designed to investigate, analyze, and "resurrect" forgotten digital archives. It transforms the daunting task of understanding a legacy codebase into a structured investigation, providing a polished dashboard of findings, evidence, and a concrete recovery plan.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![PySide6](https://img.shields.io/badge/UI-PySide6-green.svg)

## 🕯️ Hacktoberfest 2026 — Week 4

Ghost Projects was built as a submission for the **Hacktoberfest Open-Source AI Challenge — Week 4**, under the theme **"Ghost in the Machine."**

The challenge invites developers to explore the intersection of open-source AI, forgotten digital history, and creative technology.

Inspired by the idea of bringing abandoned open-source projects back to life, Ghost Projects uses AI to investigate forgotten codebases, uncover their original purpose, reconstruct architectural insights, and suggest practical steps for their recovery.

🔗 **Challenge Announcement:** [Hacktoberfest Open-Source AI Challenge: Ghost in the Machine](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-ghost-in-the-machine-2850-in-prizes-across-21-3cho)

## 🌟 Features

- **🔍 Deep Project Scanning**: Automatically detects programming languages, frameworks, and project structures.
- **🧠 AI-Driven Investigation**: Analyzes the "ghost" of the project to recover its original intent and architectural design.
- **📂 Evidence Explorer**: A centralized repository of all clues and code excerpts found during the investigation.
- **📊 Investigation Dashboard**: A high-fidelity, dark-themed dashboard providing a bird's-eye view of project health and limitations.
- **🛠️ Resurrection Plan**: Generates a prioritized list of concrete actions required to bring the project back to life.

## 🚀 Getting Started

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package and project management.

### Prerequisites

- **Python 3.14+**
- **uv** installed on your system.

If you don't have uv:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Muanido-8/gost-projects.git
   cd gost-projects
   ```

2. **Configure Environment:**

   The application requires an environment file for API keys and configuration.

   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in the required credentials.

3. **Run the Application:**

   You don't need to manually create a virtual environment; `uv` handles it automatically.

   ```bash
   uv run ghost-projects
   ```

## 🛠️ Technical Architecture

- **Frontend**: Built with **PySide6**, utilizing a custom-designed dark theme inspired by modern developer tools.
- **Data Modeling**: Powered by **Pydantic** for strict schema validation of project assessments, evidence, and findings.
- **Investigation Engine**: A worker-based architecture that performs asynchronous scanning and AI analysis to keep the UI responsive.

## 📁 Project Structure

```text
ghost-projects/
├── src/
│   └── ghost_projects/
│       ├── ai/              # AI prompts and logic
│       ├── schemas/         # Pydantic models (Assessment, Evidence, etc.)
│       ├── services/        # Project scanner and business logic
│       └── ui/              # PySide6 views, components, and themes
├── tests/                   # Pytest suite
├── pyproject.toml            # Project metadata and dependencies
└── uv.lock                   # Deterministic lockfile
```

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## ⚠️ Challenges & Limitations

- **Limited Local Hardware:** Insufficient hardware resources to run large AI models like Gemma 31B locally (I have a very modest laptop😅).
- **Structured Output Compatibility:** The selected open-weight model did not reliably support the agent framework's `output_type` (openai agents sdk), frequently returning Markdown-formatted JSON instead of structured output.
- **Agent Turn Limits:** Complex investigations occasionally exceeded the maximum number of allowed agent turns, interrupting the analysis.
- **Context Limitations:** Analyzing large codebases while staying within model context and token limits.
- **Cloud Infrastructure Dependency:** Reliance on external AI services introduced connectivity, latency, and availability constraints.
- **Investigation Performance:** Balancing investigation depth, execution time, and resource consumption.

## Have fun, peace and love 😇✌️☺️​