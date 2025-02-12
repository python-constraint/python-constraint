import numpy as np
from time import perf_counter
import pytest

@pytest.mark.skip
def get_performance_factor(repeats=3):
    """Run microbenchmarks to indicate how much faster / slower this system is compared to the reference."""

    def cpu_1():
        """Matrix multiplication"""
        A = np.random.random((1000, 1000))
        B = np.random.random((1000, 1000))
        return np.dot(A, B)

    def cpu_2():
        """Element-wise arithmetic"""
        A = np.random.random(10**6)
        B = np.random.random(10**6)
        return A + B
    
    def cpu_3():
        """Addition"""
        N = 10**6
        return [i + i for i in range(N)]
    
    def cpu_4():
        """Multiplication"""
        N = 10**6
        return [i * i for i in range(N)]
    
    def cpu_5():
        """Division"""
        N = 10**6
        return [i / i for i in range(1, N+1)]

    def mem_1():
        """Array copying"""
        A = np.random.random(10**6)
        return np.copy(A)
    
    def mem_2():
        """Array slicing"""
        A = np.random.random(10**6)
        return A[::2]
    
    def mem_3():
        """Dictionary lookup"""
        N = 10**3
        keys = list(range(N))
        values = list(range(N))
        lst = list(zip(keys, values))
        return [next((v for k, v in lst if k == i), None) for i in range(N)]
    
    def cache_1():
        """Sequential array sum"""
        A = np.random.random(10**6)
        return np.sum(A)

    def cache_2():
        """Strided array sum"""
        A = np.random.random(10**6)
        return np.sum(A[::2])
    
    # run the benchmarks
    benchmarks = [cpu_1, cpu_2, cpu_3, cpu_4, cpu_5, mem_1, mem_2, mem_3, cache_1, cache_2]
    raw_data = [list() for _ in range(repeats)]
    for i in range(repeats):
        for f in benchmarks:
            start = perf_counter()
            f()
            duration = perf_counter() - start
            raw_data[i].append(duration)

    # calculate statistics
    benchmark_data = np.array(raw_data)
    benchmark_mean = benchmark_data.mean(axis=0)
    relative_std = (benchmark_data.std(axis=0) / np.abs(benchmark_mean))
    mean_relative_std = max(np.mean(relative_std), 0.025)

    # calculate the performance factor relative to the reference
    reference_benchmark_mean = np.array([0.03569697, 0.04690351, 0.1586863, 0.13609187, 0.13637274, 0.01238605, 0.01072952, 0.07484022, 0.01054054, 0.01030138])
    performance_factor: float = np.mean(benchmark_mean / reference_benchmark_mean)
    return performance_factor, mean_relative_std

performance_factor, mean_relative_std = get_performance_factor()
