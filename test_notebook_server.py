"""Tests for BlackRoad Notebook Server."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["NOTEBOOK_DB"] = str(Path(tempfile.mkdtemp()) / "test_notebooks.db")
sys.path.insert(0, str(Path(__file__).parent))
from main import Cell, JupyterService, Notebook, init_db


class TestCell(unittest.TestCase):
    def test_to_ipynb_code(self):
        cell = Cell(cell_type="code", source="x = 1")
        d = cell.to_ipynb()
        self.assertEqual(d["cell_type"], "code")
        self.assertIn("outputs", d)

    def test_to_ipynb_markdown(self):
        cell = Cell(cell_type="markdown", source="# Hello")
        d = cell.to_ipynb()
        self.assertEqual(d["cell_type"], "markdown")
        self.assertNotIn("outputs", d)

    def test_from_ipynb_list_source(self):
        data = {"cell_type": "code", "source": ["x = 1\n", "y = 2"], "outputs": [], "execution_count": None}
        cell = Cell.from_ipynb(data)
        self.assertIn("x = 1", cell.source)
        self.assertIn("y = 2", cell.source)


class TestJupyterService(unittest.TestCase):
    def setUp(self):
        init_db()
        self.svc = JupyterService()
        self.tmp = Path(tempfile.mkdtemp())

    def test_notebook_create_and_load(self):
        nb = self.svc.notebook_create("Test NB", str(self.tmp / "test.ipynb"))
        self.assertTrue(Path(nb.path).exists())
        loaded = self.svc.notebook_load(nb.id)
        self.assertEqual(loaded.id, nb.id)
        self.assertEqual(loaded.name, "Test NB")

    def test_notebook_create_with_cells(self):
        cells = [{"cell_type": "code", "source": "print('hello')"}]
        nb = self.svc.notebook_create("With Cells", str(self.tmp / "cells.ipynb"), cells=cells)
        loaded = self.svc.notebook_load(nb.id)
        self.assertEqual(len(loaded.cells), 1)

    def test_notebook_execute_success(self):
        cells = [{"cell_type": "code", "source": "x = 2 + 2\nprint(x)"}]
        nb = self.svc.notebook_create("Exec Test", str(self.tmp / "exec.ipynb"), cells=cells)
        results = self.svc.notebook_execute(nb.id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "success")
        self.assertIn("4", results[0].output)

    def test_notebook_execute_error(self):
        cells = [{"cell_type": "code", "source": "raise ValueError('fail')"}]
        nb = self.svc.notebook_create("Err Test", str(self.tmp / "err.ipynb"), cells=cells)
        results = self.svc.notebook_execute(nb.id)
        self.assertEqual(results[0].status, "error")

    def test_notebook_export_script(self):
        cells = [{"cell_type": "code", "source": "x = 1"}]
        nb = self.svc.notebook_create("Export Test", str(self.tmp / "export.ipynb"), cells=cells)
        out = self.svc.notebook_export(nb.id, fmt="script")
        self.assertTrue(out.endswith(".py"))
        self.assertTrue(Path(out).exists())

    def test_notebook_list(self):
        self.svc.notebook_create("List NB", str(self.tmp / "list.ipynb"))
        items = self.svc.notebook_list()
        self.assertGreaterEqual(len(items), 1)

    def test_execution_history(self):
        cells = [{"cell_type": "code", "source": "print(42)"}]
        nb = self.svc.notebook_create("Hist Test", str(self.tmp / "hist.ipynb"), cells=cells)
        self.svc.notebook_execute(nb.id)
        hist = self.svc.execution_history(nb.id)
        self.assertGreaterEqual(len(hist), 1)


if __name__ == "__main__":
    unittest.main()
