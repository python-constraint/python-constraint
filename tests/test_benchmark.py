import numpy as np
from time import perf_counter
import pytest
from constraint import Problem


# reference times (using A4000 on DAS6)
reference_microbenchmark_mean = np.array([0.03569697, 0.04690351, 0.1586863, 0.13609187, 0.13637274, 0.01238605, 0.01072952, 0.07484022, 0.01054054, 0.01030138])    # noqa E501
reference_results = {
    "microhh": 1.1565620
}
# device properties (for A4000 on DAS6 using get_opencl_device_info.cpp)
dev = {
    "max_threads": 1024,
    "max_threads_per_sm": 1024, 
    "max_threads_per_block": 1536,
    "max_shared_memory_per_block": 49152,
    "max_shared_memory": 102400,
    "max_wi_size": [1024, 1024, 64],
    "max_wg_size": 1024,
}

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
    performance_factor: float = np.mean(benchmark_mean / reference_microbenchmark_mean)
    return performance_factor, mean_relative_std

performance_factor, mean_relative_std = get_performance_factor()


def test_microhh(benchmark):
    cta_padding = 0  # default argument

    # setup the tunable parameters
    problem = Problem()
    problem.addVariable("STATIC_STRIDES", [0])
    problem.addVariable("TILING_STRATEGY", [0])
    problem.addVariable("REWRITE_INTERP", [0])
    problem.addVariable("BLOCK_SIZE_X", [1, 2, 4, 8, 16, 32, 128, 256, 512, 1024])
    problem.addVariable("BLOCK_SIZE_Y", [1, 2, 4, 8, 16, 32])
    problem.addVariable("BLOCK_SIZE_Z", [1, 2, 4])
    problem.addVariable("TILING_FACTOR_X", [1, 2, 4, 8])
    problem.addVariable("TILING_FACTOR_Y", [1, 2, 4])
    problem.addVariable("TILING_FACTOR_Z", [1, 2, 4])
    problem.addVariable("LOOP_UNROLL_FACTOR_X",[1, 2, 4, 8])
    problem.addVariable("LOOP_UNROLL_FACTOR_Y", [1, 2, 4])
    problem.addVariable("LOOP_UNROLL_FACTOR_Z", [1, 2, 4])
    problem.addVariable("BLOCKS_PER_MP", [0, 1, 2, 3, 4])

    # setup the restrictions
    problem.addConstraint([
        f"BLOCK_SIZE_X * BLOCK_SIZE_Y * BLOCK_SIZE_Z * BLOCKS_PER_MP <= {dev['max_threads_per_sm']}",
        f"32 <= BLOCK_SIZE_X * BLOCK_SIZE_Y * BLOCK_SIZE_Z <= {dev['max_threads_per_block']}",
        "LOOP_UNROLL_FACTOR_X == 0 or TILING_FACTOR_X % LOOP_UNROLL_FACTOR_X == 0",
        "LOOP_UNROLL_FACTOR_Y == 0 or TILING_FACTOR_Y % LOOP_UNROLL_FACTOR_Y == 0",
        "LOOP_UNROLL_FACTOR_Z == 0 or TILING_FACTOR_Z % LOOP_UNROLL_FACTOR_Z == 0",
        f"BLOCK_SIZE_X * TILING_FACTOR_X > {cta_padding}",
        f"BLOCK_SIZE_Y * TILING_FACTOR_Y > {cta_padding}",
        f"BLOCK_SIZE_Z * TILING_FACTOR_Z > {cta_padding}",
    ])

    benchmark(problem.getSolutions)
    assert benchmark.stats.stats.mean <= reference_results["microhh"] * (performance_factor + mean_relative_std)
