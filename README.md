# ⚡ Intelligent Job Scheduler AI
### Smart Scheduling. Zero Chaos.

> A high-performance, AI-augmented job scheduling system that combines hand-crafted data structures with machine learning — automatically deciding **what** to run, **in what order**, and **on which machine**, in real time.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![HuggingFace](https://img.shields.io/badge/Models-HuggingFace-yellow?style=flat-square&logo=huggingface)](https://huggingface.co/gayaneyemishyan/job-scheduler)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-90%2B%20passing-brightgreen?style=flat-square)]()

---

## 📖 What Is This?

**Intelligent Job Scheduler AI** is a university project built for a Data Structures and Algorithms course. It is a two-part system:

- **FlowDesk** — A web-based task scheduling engine that manages priorities, dependencies, deadlines, and fairness using hand-crafted data structures and algorithms.
- **CORAE** *(Cost-Optimized Resource Allocation Engine)* — A cloud resource allocation engine that finds the best machine for each job using an AVL tree, a hash map, and Dijkstra's shortest-path algorithm.

Together they form a complete pipeline: FlowDesk decides **what runs next and in what order**. CORAE decides **which machine runs it and at what cost**.

A third layer of **machine learning models** — hosted on HuggingFace — adds predictive capabilities: failure prediction, runtime estimation, resource demand forecasting, and workload clustering.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔗 **Dependency Management** | Define task dependencies — the system enforces the order automatically |
| ⚡ **Priority Queue** | Binary max-heap dispatches the most urgent task first, always |
| 🛡 **Anti-Starvation** | Low-priority tasks gain weight over time — nothing waits forever |
| ⏱ **Critical Path Detection** | Automatically highlights the task chain controlling your deadline |
| 🌲 **Best-Fit Allocation** | AVL tree finds the tightest-capacity server in O(log n) |
| 🗺 **Cost-Optimal Routing** | Dijkstra's algorithm picks the cheapest network path to each machine |
| 🔮 **Failure Prediction** | LightGBM flags jobs likely to fail before they are dispatched |
| 📊 **Demand Forecasting** | LSTM predicts future resource needs from historical time-series |
| 📜 **Full History Log** | Every task logged with timestamp, outcome, and delay annotation |
| 🖥 **Live Dashboard** | Web UI with dependency graph, priority queue view, and analytics |

---

## 🏗 Architecture

```
intelligent-job-scheduler/
│
├── core/                        # All data structures — built from scratch
│   ├── dag.py                   # Directed Acyclic Graph (adjacency list)
│   ├── heap.py                  # Binary Max-Heap with HeapMap wrapper
│   ├── hashmap.py               # Open-addressing hash map with tombstones
│   ├── history.py               # Doubly linked list history log
│   └── task.py                  # Task model
│
├── api/                         # Scheduler orchestration layer
│   └── scheduler.py             # Wires all core components together
│
├── CORAE/                       # Cost-Optimized Resource Allocation Engine
│   ├── structures.py            # AVL Tree + Machine/Job dataclasses
│   ├── engine.py                # Allocation engine (AVL + HashMap + Dijkstra)
│   ├── network_routing.py       # Weighted graph + Dijkstra's algorithm
│   ├── job_simulator.py         # Random job generator for testing
│   └── app.py                   # Flask REST API (11 endpoints)
│
├── web/                         # FlowDesk web application
│   └── app.py                   # Flask + Jinja2 + Firebase/JSON persistence
│
├── models/                      # ML model files
│   ├── failure_predictor_lgbm.pkl
│   ├── failure_predictor_scaler.pkl
│   └── ...
│
├── tests/                       # Full test suite (90+ assertions)
│   ├── test_dag.py
│   ├── test_heap.py
│   ├── test_hashmap.py
│   ├── test_history.py
│   ├── test_starvation.py
│   ├── test_critical_path_boost.py
│   └── test_scheduler.py
│
├── visualisation/               # Dependency graph and analytics
├── app.py                       # ML prediction API (Flask)
├── index.html                   # Landing page
├── signin.html                  # Sign-in page
├── dashboard.html               # Full SaaS dashboard
└── requirements.txt
```

---

## 🧱 Data Structures

Every data structure in this project was implemented from scratch — no library abstractions.

### 📊 Binary Max-Heap — `core/heap.py`
The ready queue. Tasks are ordered by **effective priority**:

```
effective_priority = base_priority + 0.1 × wait_time_hours
```

- Each task stores its own `heap_index` for O(log n) update and cancellation
- In-place swap-and-drop cancellation — no sentinel values
- `rebuild_heap` uses Floyd's bottom-up algorithm for O(n) bulk rebalancing
- **HeapMap wrapper** keeps the heap and hash map perfectly synchronized

### 🔗 Directed Acyclic Graph — `core/dag.py`
Dependency enforcement using an adjacency list with three parallel dictionaries: `successors`, `predecessors`, and `in_degree`.

- **Cycle detection** via DFS before any edge is committed
- **Kahn's topological sort** for dependency ordering — O(V + E)
- **Critical path algorithm** — forward pass over topological order, backtrack from max finish time
- Tasks on the critical path receive an automatic `CRITICAL_PATH_BOOST`

### #️⃣ Open-Addressing Hash Map — `core/hashmap.py`
Linear probing with tombstone deletion.

- Load factor threshold: **0.70** (counts both live entries and tombstones)
- Rehashing purges tombstones and doubles table size
- Backs the HeapMap wrapper, the history log's node lookup, and the web layer

### 📜 Doubly Linked List — `core/history.py`
History log for completed and cancelled tasks.

- O(1) head insertion, O(1) arbitrary removal via companion hash map
- O(1) tail eviction when capacity cap is exceeded

### 🌲 AVL Tree — `CORAE/structures.py`
Self-balancing binary search tree for best-fit server lookup by capacity.

- All 4 rotation cases: LL, RR, LR, RL
- Best-fit search in O(log n)
- Balance factor maintained at all times — height ≤ 1.44 × log₂(n)

---

## 🧠 Algorithms

| Algorithm | File | Complexity | Purpose |
|---|---|---|---|
| Kahn's Topological Sort | `core/dag.py` | O(V + E) | Dependency ordering |
| DFS Cycle Detection | `core/dag.py` | O(V + E) | Reject circular dependencies |
| Critical Path | `core/dag.py` | O(V + E) | Deadline chain detection |
| Heapify Up/Down | `core/heap.py` | O(log n) | Priority queue maintenance |
| Anti-Starvation | `core/heap.py` | O(n) | Fairness guarantee |
| Dijkstra's Shortest Path | `CORAE/network_routing.py` | O((V+E) log V) | Cost-optimal routing |
| AVL Rotations | `CORAE/structures.py` | O(log n) | Best-fit server lookup |
| Floyd's Heap Build | `core/heap.py` | O(n) | Bulk priority refresh |

---

## 🤖 ML Models

All models are hosted on HuggingFace: [gayaneyemishyan/job-scheduler](https://huggingface.co/gayaneyemishyan/job-scheduler)

| Model | Type | Purpose |
|---|---|---|
| `resource_lstm.keras` | LSTM | Time-series resource demand forecasting |
| `resource_xgb.pkl` | XGBoost Regressor | Capacity requirement prediction |
| `failure_predictor_lgbm.pkl` | LightGBM Classifier | Failure prediction before dispatch |
| `anomaly_autoencoder.keras` | Autoencoder | Unsupervised anomaly detection |
| `anomaly_iso_forest.pkl` | Isolation Forest | Outlier detection complement |
| `workload_kmeans.pkl` | K-Means | Workload clustering |
| `workload_hdbscan.pkl` | HDBSCAN | Density-based workload clustering |
| `runtime_predictor.pkl` | Random Forest | Job duration estimation |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/GayaneYemishyan/intelligent-job-scheduler.git
cd intelligent-job-scheduler

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/ -v

---


**Response:**
```json
{
  "status": "Success",
  "confidence": "91.4%",
  "raw_probability": 0.914,
  "input": { ... }
}
```

---

## 🧪 Testing

The test suite covers every component in isolation and end-to-end.

```bash
pytest tests/ -v
```

| Test File | What It Covers |
|---|---|
| `test_dag.py` | DAG construction, cycle detection, topological sort, critical path — 80+ assertions |
| `test_heap.py` | Push/pop ordering, update_priority, in-place cancellation, rebuild_heap |
| `test_hashmap.py` | Put/get/delete, tombstone correctness, resize at 70% load, stress tests |
| `test_history.py` | Doubly linked list pointer integrity, capacity eviction, filter methods |
| `test_starvation.py` | Effective priority formula, crossover points, heap ordering after refresh |
| `test_critical_path_boost.py` | Boost not accumulating, boost revoked when path shifts |
| `test_scheduler.py` | Full lifecycle: submit → next_task → complete → kill → update_priority |

---

## 👥 Team

| Name | Role | Primary Contributions |
|---|---|---|
| **Gayane Yemishyan** | Scheduling Core & ML | DAG, Cycle Detection, Kahn's Sort, Critical Path, Doubly Linked List, ML Models |
| **Monika Yepremyan** | Queue Engine | Binary Max-Heap, HeapMap Wrapper, Hash Map, Anti-Starvation, Priority Update |
| **Lilit Zalinyan** | Routing & QA | Weighted Graph, Dijkstra's Algorithm, Job Simulator, 90+ Tests |
| **Viktorya Margaryan** | Resource Layer | AVL Tree, Allocation Engine, Flask REST API, Web Dashboard |



[MIT](LICENSE)

