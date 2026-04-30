# test_engine.py — tests for AllocationEngine (AVL + Hash Map + Dijkstra pipeline)
# Run: pytest tests/test_engine.py -v

import pytest
from structures import Machine
from network_routing import NetworkRouting
from engine import AllocationEngine
from conftest import make_job, make_machine, build_engine_with_machines


class TestRegistration:

    def setup_method(self):
        self.engine = build_engine_with_machines()

    def test_register_machine_appears_in_pool(self):
        self.engine.register_machine(Machine("NEW", 200, 50))
        ids = [m.machine_id for m in self.engine.get_all_machines()]
        assert "NEW" in ids

    def test_duplicate_register_ignored(self):
        before = len(self.engine.get_all_machines())
        self.engine.register_machine(Machine("M-10", 10, 2))
        after = len(self.engine.get_all_machines())
        assert before == after

    def test_get_machine_info(self):
        info = self.engine.get_machine_info("M-30")
        assert info is not None
        assert info.capacity == 30

    def test_get_machine_info_missing(self):
        assert self.engine.get_machine_info("GHOST") is None


class TestAllocation:

    def setup_method(self):
        self.engine = build_engine_with_machines()

    def test_allocate_returns_machine_id(self):
        result = self.engine.allocate(make_job(required=25), "Scheduler")
        assert result is not None
        assert isinstance(result, str)

    def test_allocated_machine_marked_busy(self):
        mid = self.engine.allocate(make_job(required=25), "Scheduler")
        assert self.engine.get_machine_info(mid).status == "busy"

    def test_allocate_fails_when_no_capacity(self):
        assert self.engine.allocate(make_job(required=9999), "Scheduler") is None

    def test_allocate_fails_on_empty_pool(self):
        net = NetworkRouting()
        net.add_machine("Scheduler")
        engine = AllocationEngine(network=net)
        assert engine.allocate(make_job(required=10), "Scheduler") is None

    def test_allocate_updates_job_history(self):
        mid = self.engine.allocate(make_job("J42", 25), "Scheduler")
        assert "J42" in self.engine.get_machine_info(mid).job_history

    def test_allocate_updates_current_load(self):
        mid = self.engine.allocate(make_job(required=25), "Scheduler")
        assert self.engine.get_machine_info(mid).current_load == 25

    def test_allocate_skips_busy_machine(self):
        mid1 = self.engine.allocate(make_job("J1", 8), "Scheduler")
        mid2 = self.engine.allocate(make_job("J2", 8), "Scheduler")
        assert mid1 != mid2


class TestRelease:

    def setup_method(self):
        self.engine = build_engine_with_machines()

    def test_release_marks_available(self):
        mid = self.engine.allocate(make_job(required=25), "Scheduler")
        self.engine.release_machine(mid)
        info = self.engine.get_machine_info(mid)
        assert info.status == "available"
        assert info.current_load == 0.0

    def test_release_nonexistent_returns_false(self):
        assert self.engine.release_machine("GHOST") is False

    def test_released_machine_can_be_reallocated(self):
        mid = self.engine.allocate(make_job("J1", 25), "Scheduler")
        self.engine.release_machine(mid)
        assert self.engine.allocate(make_job("J2", 25), "Scheduler") is not None


class TestRemove:

    def setup_method(self):
        self.engine = build_engine_with_machines()

    def test_remove_machine(self):
        assert self.engine.remove_machine("M-10") is True
        assert self.engine.get_machine_info("M-10") is None

    def test_remove_nonexistent_returns_false(self):
        assert self.engine.remove_machine("GHOST") is False

    def test_remove_then_pool_size_decreases(self):
        before = len(self.engine.get_all_machines())
        self.engine.remove_machine("M-10")
        assert len(self.engine.get_all_machines()) == before - 1


class TestPoolSummary:

    def setup_method(self):
        self.engine = build_engine_with_machines()

    def test_pool_summary_total(self):
        assert self.engine.pool_summary()["total"] == 4

    def test_pool_summary_all_available_at_start(self):
        summary = self.engine.pool_summary()
        assert summary["available"] == 4
        assert summary["busy"] == 0

    def test_pool_summary_after_allocation(self):
        self.engine.allocate(make_job(required=25), "Scheduler")
        summary = self.engine.pool_summary()
        assert summary["busy"] == 1
        assert summary["available"] == 3

    def test_get_all_machines_ascending_capacity(self):
        caps = [m.capacity for m in self.engine.get_all_machines()]
        assert caps == sorted(caps)
