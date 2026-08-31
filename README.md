# CodeBase Navigator AI 🧭

> **Understand Any Codebase. Navigate with Intelligence.**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/LTMani/codebase-navigator-ai)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-36%20passed-success.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-6--Tier%20Heuristic%20Clean%20Arch-purple.svg)](#architecture-intelligence)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An enterprise-grade, AI-powered platform for ingesting, parsing, understanding, and navigating unfamiliar software codebases through deep Abstract Syntax Tree (AST) code intelligence, dependency cycle detection, architecture classification, change blast radius calculation, and grounded conversational AI.

---

## 🌟 Key Features

### 1. 🌐 Multi-Language AST Parsers
- **Python**: Full `ast.NodeVisitor` parsing function definitions, class hierarchies, imports, decorators, cyclomatic complexity, Halstead metrics, and entry point detection.
- **JavaScript & TypeScript**: Interfaces, types, enums, arrow functions, ES6/CommonJS module resolution, and React component tree extraction.
- **Java**: Spring `@Service`, `@RestController`, `@Autowired` annotations, package namespaces, class hierarchies, and interfaces.
- **Go**: Package declarations, structs, interfaces, receiver methods, and goroutines.
- **Rust**: Traits, structs, enums, `impl` blocks, and async functions.
- **SQL**: Tables, views, foreign key constraints, and schema relationships.
- **HTML & CSS**: DOM hierarchy, stylesheet references, and template action routes.

### 2. 🕸️ Dependency Graph & Cycle Intelligence
- **Tarjan's Strongly Connected Components (SCC)**: Discovers circular dependency loops with \(O(V + E)\) efficiency.
- **PageRank Centrality**: Evaluates core architectural hub files and critical dependencies.
- **Blast Radius & Change Impact**: BFS reverse traversal computing exact change risk (0–100 score), affected API endpoints, and required regression test suites.

### 3. 🏛️ Layered Architecture Classification
Automatically categorizes modules across a 6-tier architecture:
1. **Presentation Layer**: UI templates, React/Vue components, CSS stylesheets.
2. **API & Routing Layer**: Express/Flask/FastAPI routers, HTTP endpoints, middleware guards.
3. **Application & Service Layer**: Domain business services, orchestrators, workflows.
4. **Domain & Entity Layer**: Core business models, schemas, validations, data transfer objects (DTOs).
5. **Data & Repository Layer**: Database queries, ORM models, migrations.
6. **Infrastructure & Utilities**: Helpers, logging, authentication, caching, third-party adapters.

### 4. 🤖 Grounded AI Codebase Copilot
- **Dual-Mode Intelligence**: Deterministic AST-grounded analysis + optional LLM providers (Google Gemini / OpenAI / Anthropic).
- **Intent Recognition**: Architectural explanations, call flow tracing, change impact estimation, and code search.
- **Zero Hallucinations**: Every response is grounded with exact line citations and AST symbols.

### 5. 🩺 Code Health & Technical Debt Engine
- **Maintainability Index (MI)**: Standard SEI formula based on Halstead volume, cyclomatic complexity, and lines of code.
- **Refactoring Advisor**: Identifies *God Objects*, *Long Methods*, *Feature Envy*, *Data Clumps*, and *Long Parameter Lists* with step-by-step remediation advice.
- **Security Scanner**: AST-based detection of SQL injections, hardcoded API secrets, insecure deserialization, command injections, and disabled SSL verification.
- **Clone Detection**: Token-normalized rolling Rabin-Karp hashing for duplicate code blocks (Type-1, Type-2, Type-3).

### 6. 🗺️ Developer Onboarding Roadmap
- Synthesizes personalized guided reading paths sorted by PageRank centrality and entry point significance.
- Generates interactive, graded 5-question comprehension quizzes assessing understanding of application architecture.

---

## 🏗️ System Architecture

```
                               ┌──────────────────────────────────────────────┐
                               │           Single Page Application (SPA)      │
                               │  Vanilla JS ES6 + Canvas Graph + CSS3 Dark  │
                               └──────────────────────┬───────────────────────┘
                                                      │ REST JSON API / Auth JWT
                                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       Flask REST API Backend                                      │
├───────────────────┬───────────────────┬───────────────────┬───────────────────┬───────────────────┤
│  Auth Blueprint   │ Project Blueprint │ Dependency Routes │ Architecture API  │  Copilot Routes   │
│  /api/auth/*      │ /api/projects/*   │ /api/*/graph      │ /api/*/layers     │  /api/*/copilot   │
└─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬─────────┘
          │                   │                   │                   │                   │
          ▼                   ▼                   ▼                   ▼                   ▼
┌───────────────────┬───────────────────┬───────────────────┬───────────────────┬───────────────────┐
│   AST Parsers     │  Dependency Graph │  Impact Engine    │ Health & Debt     │ Copilot Engine    │
│  Python, JS, TS,  │  Tarjan SCC,      │  Blast Radius,    │ Maintainability,  │ Intent Classifier │
│  Java, Go, Rust   │  PageRank Nodes   │  Reverse BFS      │ Code Smells       │ Grounded Context  │
└─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬─────────┴─────────┬─────────┘
          │                   │                   │                   │                   │
          └───────────────────┴─────────┬─────────┴───────────────────┴───────────────────┘
                                        │ SQLAlchemy ORM
                                        ▼
                         ┌─────────────────────────────┐
                         │   SQLite / PostgreSQL DB    │
                         └─────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Clone & Setup Environment
```bash
git clone https://github.com/LTMani/codebase-navigator-ai.git
cd codebase-navigator-ai

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full-Stack Web Application
```bash
python run.py
```
Open your browser at `http://localhost:5000` to access the interactive web suite.

---

## 💻 Interactive Command Line Interface (CLI)

The repository provides a terminal tool for instant code intelligence:

```bash
# Scan and index any local codebase directory
python cli.py scan ./fixtures/flask_ecommerce

# Audit codebase health, maintainability grade, and technical debt
python cli.py health ./fixtures/flask_ecommerce

# Generate a complete Markdown architecture audit report
python cli.py report ./fixtures/flask_ecommerce --output architecture_report.md
```

---

## 🧪 Running Automated Tests

Run the complete test suite (36 tests across all engines, parsers, and services):

```bash
python -m pytest -v tests/
```

---

## 📁 Project Structure

```
codebase-navigator-ai/
├── app/
│   ├── config.py                 # Multi-environment configuration
│   ├── extensions.py             # SQLAlchemy, JWT, CORS extensions
│   ├── middleware/               # Auth guards, security headers, request logger
│   ├── models/                   # SQLAlchemy domain entities & relationships
│   ├── parsers/                  # Multi-language AST parsers (Python, JS, TS, Java, Go, Rust, SQL, HTML/CSS)
│   ├── repositories/             # Clean Data Access Layer (DAL)
│   ├── routes/                   # 17 Flask REST API route blueprints
│   ├── schemas/                  # Pydantic input validation & serialization
│   ├── security/                 # Scrypt password hashing & JWT token provider
│   └── services/                 # Core code intelligence, graph algorithms, and AI copilot
├── frontend/
│   ├── static/
│   │   ├── css/                  # Developer dark-mode stylesheet suite
│   │   └── js/                   # Vanilla JS ES6 modules, Router, Store, Canvas Graph, Views
│   └── templates/
│       └── index.html            # SPA application shell
├── fixtures/                     # Comprehensive sample codebases (Flask, React/Node SaaS, Microservices)
├── tests/                        # 36 comprehensive test suites
├── cli.py                        # Terminal CLI application
├── run.py                        # Application entry point
├── pyproject.toml                # Project metadata and test configuration
└── requirements.txt              # Production and development dependencies
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
