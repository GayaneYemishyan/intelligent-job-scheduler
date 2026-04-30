# test_job_simulator.py — tests for JobSimulator (random job generators)
# Run: pytest tests/test_job_simulator.py -v

from job_simulator import generate_jobs, generate_burst, generate_mixed_workload


class TestGenerateJobs:

    def test_count(self):
        assert len(generate_jobs(15)) == 15

    def test_unique_ids(self):
        jobs = generate_jobs(20)
        ids = [j.job_id for j in jobs]
        assert len(ids) == len(set(ids))

    def test_capacity_in_range(self):
        for j in generate_jobs(50, min_capacity=10, max_capacity=80):
            assert 10 <= j.required_capacity <= 80

    def test_priority_in_range(self):
        for j in generate_jobs(50):
            assert 1 <= j.priority <= 5

    def test_seeded_reproducible(self):
        a = generate_jobs(10, seed=42)
        b = generate_jobs(10, seed=42)
        assert [j.required_capacity for j in a] == [j.required_capacity for j in b]

    def test_different_seeds_differ(self):
        a = generate_jobs(10, seed=1)
        b = generate_jobs(10, seed=2)
        assert [j.required_capacity for j in a] != [j.required_capacity for j in b]

    def test_zero_count(self):
        assert generate_jobs(0) == []


class TestGenerateBurst:

    def test_count(self):
        assert len(generate_burst(10)) == 10

    def test_high_capacity(self):
        for j in generate_burst(30):
            assert j.required_capacity >= 60

    def test_high_priority(self):
        for j in generate_burst(20):
            assert j.priority >= 4


class TestGenerateMixedWorkload:

    def test_count(self):
        assert len(generate_mixed_workload(total=20)) == 20

    def test_has_small_jobs(self):
        jobs = generate_mixed_workload(total=30, seed=0)
        assert any(j.required_capacity <= 30 for j in jobs)

    def test_has_large_jobs(self):
        jobs = generate_mixed_workload(total=30, seed=0)
        assert any(j.required_capacity >= 70 for j in jobs)

    def test_seeded_reproducible(self):
        a = generate_mixed_workload(total=15, seed=7)
        b = generate_mixed_workload(total=15, seed=7)
        assert [j.job_id for j in a] == [j.job_id for j in b]
