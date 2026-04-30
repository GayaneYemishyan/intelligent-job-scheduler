# test_network_routing.py — tests for NetworkRouting (weighted graph + Dijkstra)
# Run: pytest tests/test_network_routing.py -v

import math
import pytest
from network_routing import NetworkRouting


class TestGraphConstruction:

    def setup_method(self):
        self.net = NetworkRouting()

    def test_add_machine_creates_node(self):
        self.net.add_machine("A")
        assert "A" in self.net.nodes

    def test_add_machine_idempotent(self):
        self.net.add_machine("A")
        self.net.add_machine("A")
        assert self.net.nodes.count("A") == 1

    def test_add_connection_creates_both_nodes(self):
        self.net.add_connection("A", "B", 5)
        assert "A" in self.net.nodes and "B" in self.net.nodes

    def test_add_connection_is_undirected(self):
        self.net.add_connection("A", "B", 7)
        assert any(n == "B" for n, _ in self.net._graph["A"])
        assert any(n == "A" for n, _ in self.net._graph["B"])

    def test_add_connection_negative_weight_raises(self):
        with pytest.raises(ValueError):
            self.net.add_connection("A", "B", -1)

    def test_add_connection_zero_weight_raises(self):
        with pytest.raises(ValueError):
            self.net.add_connection("A", "B", 0)

    def test_edge_count(self):
        self.net.add_connection("A", "B", 1)
        self.net.add_connection("B", "C", 2)
        assert self.net.edge_count == 2

    def test_remove_machine(self):
        self.net.add_connection("A", "B", 3)
        removed = self.net.remove_machine("A")
        assert removed is True
        assert "A" not in self.net.nodes
        for neighbours in self.net._graph.values():
            assert all(n != "A" for n, _ in neighbours)

    def test_remove_nonexistent_machine(self):
        assert self.net.remove_machine("GHOST") is False

    def test_remove_connection(self):
        self.net.add_connection("A", "B", 5)
        self.net.remove_connection("A", "B")
        assert self.net.edge_count == 0


class TestDijkstra:

    def setup_method(self):
        self.net = NetworkRouting()

    def test_direct_path_cost(self):
        self.net.add_connection("S", "A", 4)
        assert self.net.get_path_cost("S", "A") == 4

    def test_shortest_path_prefers_cheaper_route(self):
        self.net.add_connection("S", "A", 2)
        self.net.add_connection("A", "B", 3)
        self.net.add_connection("S", "B", 10)
        assert self.net.get_path_cost("S", "B") == 5

    def test_unreachable_node_returns_inf(self):
        self.net.add_machine("Isolated")
        self.net.add_machine("S")
        assert self.net.get_path_cost("S", "Isolated") == math.inf

    def test_path_to_self_is_zero(self):
        self.net.add_machine("S")
        assert self.net.get_path_cost("S", "S") == 0.0

    def test_get_full_path_hops(self):
        self.net.add_connection("S", "A", 1)
        self.net.add_connection("A", "B", 1)
        path, cost = self.net.get_full_path("S", "B")
        assert path == ["S", "A", "B"]
        assert cost == 2

    def test_get_full_path_unreachable(self):
        self.net.add_machine("S")
        self.net.add_machine("X")
        path, cost = self.net.get_full_path("S", "X")
        assert path == []
        assert cost == math.inf

    def test_find_optimal_machine_picks_cheapest(self):
        self.net.add_connection("S", "A", 10)
        self.net.add_connection("S", "B", 3)
        best, cost = self.net.find_optimal_machine("S", ["A", "B"])
        assert best == "B"
        assert cost == 3

    def test_find_optimal_machine_empty_candidates(self):
        self.net.add_machine("S")
        best, cost = self.net.find_optimal_machine("S", [])
        assert best is None
        assert cost == math.inf

    def test_find_optimal_no_reachable_candidate(self):
        self.net.add_machine("S")
        self.net.add_machine("Isolated")
        best, cost = self.net.find_optimal_machine("S", ["Isolated"])
        assert best is None

    def test_dijkstra_triangle(self):
        self.net.add_connection("S", "A", 6)
        self.net.add_connection("S", "B", 2)
        self.net.add_connection("A", "B", 3)
        assert self.net.get_path_cost("S", "A") == 5

    def test_source_not_in_graph_returns_inf(self):
        self.net.add_machine("A")
        assert self.net.get_path_cost("MISSING", "A") == math.inf
