# Brent Detector - System Design

## 1. Overview

Brent Detector is a static analysis tool designed to identify highly depended-upon modules in a software codebase. These modules, referred to as "Brents", represent critical components that many other modules rely on.

Detecting Brents helps developers understand dependency bottlenecks, identify potential single points of failure, and improve system maintainability.

The system analyzes Python projects, extracts module dependencies using static analysis, builds a dependency graph, and ranks modules based on graph metrics.

---

## 2. Definition of Brent

A Brent is a module that is heavily depended upon by other modules in the system.

These modules are important because:

- They act as central components in the system.
- Failures in these modules can affect large portions of the codebase.
- They may indicate architectural bottlenecks.

The Brent Detector identifies such modules using dependency graph analysis.

---

## 3. Dependency Graph Model

The software system is modeled as a directed graph.

Graph Definition:

Node  
Represents a Python module (file).

Edge  
Represents an import dependency between modules.

Example:

views.py imports models.py

Graph Representation:

views.py  ----->  models.py

Another example:

api.py imports utils.py

api.py  ----->  utils.py

The direction of the edge indicates dependency.

If A imports B:

A depends on B.

---

## 4. Graph Metrics

The system computes several graph metrics to evaluate the importance of modules.

### 4.1 In-Degree

Number of modules that depend on a given module.

Example:

If three files import utils.py:

InDegree(utils.py) = 3

High in-degree means the module is widely used.

---

### 4.2 Out-Degree

Number of modules that a module depends on.

Example:

If api.py imports:

utils.py  
config.py  

Then:

OutDegree(api.py) = 2

---

### 4.3 Degree Centrality

Measures how central a node is within the dependency graph.

Higher centrality means the module plays an important role in the dependency network.

This metric is calculated using NetworkX.

---

## 5. Brent Scoring Formula

The Brent score combines dependency count and graph importance.

Formula:

BrentScore = (0.7 × InDegree) + (0.3 × DegreeCentrality)

Explanation:

InDegree captures how many modules depend on a module.

DegreeCentrality captures the module's overall position in the dependency graph.

Modules are ranked based on BrentScore.

The top 5% of modules are classified as Brents.

---

## 6. System Architecture

The Brent Detector follows a modular pipeline architecture.

Workflow:

Project Directory
        │
        ▼
File Scanner
        │
        ▼
AST Parser
        │
        ▼
Dependency Extractor
        │
        ▼
Dependency Graph Builder
        │
        ▼
Graph Metrics Calculator
        │
        ▼
Brent Ranking Engine
        │
        ▼
CLI Output

Each stage performs a specific task in the analysis pipeline.

---

## 7. System Components

The system is divided into several modules.

### 7.1 File Scanner

File: scanner.py

Responsibility:

- Traverse the project directory
- Locate all Python source files
- Return list of files for analysis

---

### 7.2 AST Parser

File: parser.py

Responsibility:

- Parse Python source code using the Python AST module
- Analyze import statements
- Extract dependency relationships

---

### 7.3 Dependency Graph Builder

File: graph_builder.py

Responsibility:

- Construct directed dependency graph
- Nodes represent modules
- Edges represent import relationships

The graph is implemented using NetworkX.

---

### 7.4 Graph Metrics Calculator

File: metrics.py

Responsibility:

- Compute graph metrics
- Calculate in-degree and out-degree
- Compute degree centrality

---

### 7.5 Brent Ranking Engine

File: brent_ranker.py

Responsibility:

- Calculate Brent scores
- Rank modules by importance
- Identify top Brent modules

---

### 7.6 CLI Interface

File: cli/main.py

Responsibility:

- Accept project path from the user
- Run the analysis pipeline
- Display results in the terminal

Example usage:

python cli/main.py /path/to/project

---

## 8. Example Workflow

User runs:

python cli/main.py my_project

Step 1  
The system scans the project directory.

Step 2  
Python files are parsed using AST.

Step 3  
Dependencies are extracted from import statements.

Step 4  
A directed dependency graph is constructed.

Step 5  
Graph metrics are calculated.

Step 6  
Brent scores are computed.

Step 7  
The system outputs the top-ranked Brent modules.

Example Output:

Modules analyzed: 210  
Dependencies found: 430  

Top Brents:

1. utils.py  
2. config.py  
3. models.py

---

## 9. Technology Stack

Programming Language  
Python

Static Code Analysis  
Python AST Module

Graph Processing  
NetworkX

Version Control  
Git and GitHub

Interface  
Command-Line Interface (CLI)

---

## 10. Limitations

Static analysis cannot detect runtime dependencies such as dynamic imports.

The current system only supports Python projects.

Dependency count does not always represent business importance.

---

## 11. Future Improvements

Possible future extensions include:

- Support for JavaScript or Java projects
- Graph visualization
- Web dashboard interface
- Call graph analysis
- Runtime dependency tracking

---

## 12. Conclusion

The Brent Detector provides an automated way to analyze software dependency structures and identify critical modules.

By modeling software as a dependency graph and applying graph metrics, the system highlights modules that are heavily depended upon.

These insights can help developers improve software architecture, reduce risk, and enhance maintainability.