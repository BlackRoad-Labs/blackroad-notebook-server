<!-- BlackRoad SEO Enhanced -->

# ulackroad noteuook server

> Part of **[BlackRoad OS](https://blackroad.io)** — Sovereign Computing for Everyone

[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-ff1d6c?style=for-the-badge)](https://blackroad.io)
[![BlackRoad-Labs](https://img.shields.io/badge/Org-BlackRoad-Labs-2979ff?style=for-the-badge)](https://github.com/BlackRoad-Labs)

**ulackroad noteuook server** is part of the **BlackRoad OS** ecosystem — a sovereign, distributed operating system built on edge computing, local AI, and mesh networking by **BlackRoad OS, Inc.**

### BlackRoad Ecosystem
| Org | Focus |
|---|---|
| [BlackRoad OS](https://github.com/BlackRoad-OS) | Core platform |
| [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc) | Corporate |
| [BlackRoad AI](https://github.com/BlackRoad-AI) | AI/ML |
| [BlackRoad Hardware](https://github.com/BlackRoad-Hardware) | Edge hardware |
| [BlackRoad Security](https://github.com/BlackRoad-Security) | Cybersecurity |
| [BlackRoad Quantum](https://github.com/BlackRoad-Quantum) | Quantum computing |
| [BlackRoad Agents](https://github.com/BlackRoad-Agents) | AI agents |
| [BlackRoad Network](https://github.com/BlackRoad-Network) | Mesh networking |

**Website**: [blackroad.io](https://blackroad.io) | **Chat**: [chat.blackroad.io](https://chat.blackroad.io) | **Search**: [search.blackroad.io](https://search.blackroad.io)

---


> Jupyter notebook server with AI kernels

Part of the [BlackRoad OS](https://blackroad.io) ecosystem — [BlackRoad-Labs](https://github.com/BlackRoad-Labs)

---

# blackroad-notebook-server

![CI](https://github.com/BlackRoad-Labs/blackroad-notebook-server/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-proprietary-red)

Jupyter notebook server with AI kernels for the BlackRoad OS platform.

## Features
- Create, load, execute, and export Jupyter notebooks
- SQLite-backed persistence
- Multi-format export: `.ipynb`, `.py`, `.html`
- Execution history tracking

## Install
```bash
pip install jupyter nbconvert
```

## Usage
```bash
python main.py create "My Notebook" notebooks/demo.ipynb
python main.py list
python main.py execute <id>
python main.py export <id> --format script
python main.py history <id>
python main.py kernels
```

## Testing
```bash
python -m pytest test_notebook_server.py -v
```
