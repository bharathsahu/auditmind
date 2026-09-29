# AuditMind — QA Bug & Deficiency Log

> **Repository Status**: Clean — Zero Critical or High Blocking Bugs  
> **Date**: September 29, 2026  

---

## 1. Defect Summary Table

| Bug ID | Severity | Module | Description | Steps to Reproduce | Expected Result | Actual Result | Resolution / Fix Status |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **BUG-001** | Low | Documentation | Missing `pytest` in base Python runtime path | Run `pytest` directly in shell | Executes test suite | Command not found if pytest uninstalled | **FIXED**: Created `test_runner.py` using Python standard library `unittest`. |
| **BUG-002** | Info | Deployment | External Hindsight URL fallback timing | Disconnect network & submit query | Local RRF fallback triggers | Seamless failover to local BM25+Dense RRF hybrid search | **FIXED**: Reduced HTTP timeout to 0.5s for instant local failover. |

---

## 2. Overall Defect Classification Summary

- **CRITICAL**: `0`
- **HIGH**: `0`
- **MEDIUM**: `0`
- **LOW**: `1` (Addressed via `test_runner.py`)
- **INFO**: `1` (Addressed via RRF fallback optimization)
