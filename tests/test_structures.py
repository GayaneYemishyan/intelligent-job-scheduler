# test_structures.py — tests for Machine, Job dataclasses and AVL Tree
# Run: pytest tests/test_structures.py -v

import pytest
from structures import Machine, Job, AVLTree, AVLNode
from conftest import make_machine, make_job


# ===========================================================================
# Machine dataclass
# ===========================================================================

class TestMachine:

    def test_default_status_is_available(self):
        m = Machine("X", 32, 5)
        assert m.status == "available"

    def test_default_load_is_zero(self):
        m = Machine("X", 32, 5)
        assert m.current_load == 0.0

    def test_free_capacity(self):
        m = Machine("X", 100, 10, current_load=40.0)
        assert m.free_capacity == 60.0

    def test_free_capacity_fully_loaded(self):
        m = Machine("X", 50, 10, current_load=50.0)
        assert m.free_capacity == 0.0

    def test_job_history_default_empty(self):
        m = Machine("X", 32, 5)
        assert m.job_history == []

    def test_job_history_not_shared_between_instances(self):
        a = Machine("A", 10, 1)
        b = Machine("B", 10, 1)
        a.job_history.append("job-1")
        assert b.job_history == []

    def test_repr_contains_id(self):
        m = Machine("Server-Alpha", 64, 20)
        assert "Server-Alpha" in repr(m)


# ===========================================================================
# Job dataclass
# ===========================================================================

class TestJob:

    def test_default_priority(self):
        j = Job("J1", 30)
        assert j.priority == 1

    def test_custom_priority(self):
        j = Job("J2", 50, priority=5)
        assert j.priority == 5

    def test_repr_contains_job_id(self):
        j = Job("my-job", 25)
        assert "my-job" in repr(j)


# ===========================================================================
# AVL Tree — Insert & Inorder
# ===========================================================================

class TestAVLTreeInsert:

    def setup_method(self):
        self.tree = AVLTree()
        self.root = None

    def _insert(self, *machines):
        for m in machines:
            self.root = self.tree.insert(self.root, m)

    def test_single_insert(self):
        self._insert(make_machine("M1", 50))
        result = list(self.tree.inorder(self.root))
        assert len(result) == 1
        assert result[0].machine_id == "M1"

    def test_inorder_ascending(self):
        caps = [40, 10, 70, 25, 90]
        for i, c in enumerate(caps):
            self._insert(make_machine(f"M{i}", c))
        result = [m.capacity for m in self.tree.inorder(self.root)]
        assert result == sorted(caps)

    def test_empty_tree_inorder(self):
        assert list(self.tree.inorder(None)) == []

    def test_duplicate_capacity_both_inserted(self):
        self._insert(make_machine("A", 50), make_machine("B", 50))
        result = list(self.tree.inorder(self.root))
        assert len(result) == 2


# ===========================================================================
# AVL Tree — Balance
# ===========================================================================

class TestAVLTreeBalance:

    def setup_method(self):
        self.tree = AVLTree()
        self.root = None

    def _insert(self, *machines):
        for m in machines:
            self.root = self.tree.insert(self.root, m)

    def _check_balance(self, node):
        if node is None:
            return
        bf = AVLTree._balance_factor(node)
        assert abs(bf) <= 1, f"Unbalanced at {node}, bf={bf}"
        self._check_balance(node.left)
        self._check_balance(node.right)

    def test_balance_after_ascending_inserts(self):
        for i in range(1, 8):
            self._insert(make_machine(f"M{i}", i * 10))
        self._check_balance(self.root)

    def test_balance_after_descending_inserts(self):
        for i in range(7, 0, -1):
            self._insert(make_machine(f"M{i}", i * 10))
        self._check_balance(self.root)

    def test_balance_after_random_inserts(self):
        caps = [55, 23, 78, 11, 44, 90, 3, 66]
        for i, c in enumerate(caps):
            self._insert(make_machine(f"M{i}", c))
        self._check_balance(self.root)


# ===========================================================================
# AVL Tree — find_best_fit
# ===========================================================================

class TestAVLTreeBestFit:

    def setup_method(self):
        self.tree = AVLTree()
        self.root = None

    def _insert(self, *machines):
        for m in machines:
            self.root = self.tree.insert(self.root, m)

    def test_best_fit_exact_match(self):
        self._insert(make_machine("A", 30), make_machine("B", 60))
        result = self.tree.find_best_fit(self.root, 30)
        assert result is not None
        assert result.machine_id == "A"

    def test_best_fit_picks_smallest_sufficient(self):
        self._insert(make_machine("S", 10), make_machine("M", 50), make_machine("L", 100))
        result = self.tree.find_best_fit(self.root, 40)
        assert result is not None
        assert result.capacity == 50

    def test_best_fit_returns_none_when_all_too_small(self):
        self._insert(make_machine("A", 5), make_machine("B", 15))
        assert self.tree.find_best_fit(self.root, 50) is None

    def test_best_fit_skips_busy_machines(self):
        self._insert(make_machine("Busy", 50, status="busy"), make_machine("Free", 60))
        result = self.tree.find_best_fit(self.root, 45)
        assert result is not None
        assert result.machine_id == "Free"

    def test_best_fit_skips_offline_machines(self):
        self._insert(make_machine("Off", 50, status="offline"))
        assert self.tree.find_best_fit(self.root, 30) is None

    def test_best_fit_empty_tree(self):
        assert self.tree.find_best_fit(None, 10) is None

    def test_best_fit_all_busy_returns_none(self):
        for i in range(3):
            self._insert(make_machine(f"M{i}", (i+1)*20, status="busy"))
        assert self.tree.find_best_fit(self.root, 10) is None


# ===========================================================================
# AVL Tree — Delete
# ===========================================================================

class TestAVLTreeDelete:

    def setup_method(self):
        self.tree = AVLTree()
        self.root = None

    def _insert(self, *machines):
        for m in machines:
            self.root = self.tree.insert(self.root, m)

    def _check_balance(self, node):
        if node is None:
            return
        bf = AVLTree._balance_factor(node)
        assert abs(bf) <= 1
        self._check_balance(node.left)
        self._check_balance(node.right)

    def test_delete_only_node(self):
        self._insert(make_machine("A", 50))
        self.root = self.tree.delete(self.root, "A")
        assert self.root is None

    def test_delete_leaf(self):
        self._insert(make_machine("A-10", 10), make_machine("B-30", 30),
                     make_machine("C-60", 60))
        self.root = self.tree.delete(self.root, "A-10")
        ids = {m.machine_id for m in self.tree.inorder(self.root)}
        assert "A-10" not in ids
        assert ids == {"B-30", "C-60"}

    def test_delete_node_with_two_children(self):
        caps = [50, 20, 80, 10, 30]
        for i, c in enumerate(caps):
            self._insert(make_machine(f"M{i}", c))
        self.root = self.tree.delete(self.root, "M0")
        ids = {m.machine_id for m in self.tree.inorder(self.root)}
        assert "M0" not in ids
        assert len(ids) == 4

    def test_delete_nonexistent_is_safe(self):
        self._insert(make_machine("A", 50))
        self.root = self.tree.delete(self.root, "GHOST")
        assert len(list(self.tree.inorder(self.root))) == 1

    def test_delete_maintains_balance(self):
        for i in range(1, 8):
            self._insert(make_machine(f"M{i}", i * 10))
        self.root = self.tree.delete(self.root, "M4")
        self._check_balance(self.root)

    def test_delete_all_nodes(self):
        ids = [f"M{i}" for i in range(5)]
        for i, mid in enumerate(ids):
            self._insert(make_machine(mid, (i+1)*10))
        for mid in ids:
            self.root = self.tree.delete(self.root, mid)
        assert self.root is None
