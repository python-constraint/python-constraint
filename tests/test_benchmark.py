from random import random
from time import perf_counter
import pytest
from constraint import Problem
from math import sqrt


# reference times (using A4000 on DAS6)
reference_microbenchmark_mean = [0.3784186691045761, 0.4737640768289566, 0.10726054509480794, 0.10744890073935191, 0.10979799057046573, 0.15360217044750848, 0.14483965436617532, 0.054416230569283165, 0.13835338006416956, 0.1371802551050981]    # noqa E501
reference_results = {
    "microhh": 1.1565620,
    "dedispersion": 0.1171140,
    "hotspot": 2.6839208,
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
# collect benchmark times
benchmark_results = dict()

@pytest.mark.skip
def get_performance_factor(repeats=3):
    """Run microbenchmarks to indicate how much slower this system is compared to the reference."""

    def cpu_1():
        """Matrix multiplication"""
        size = 100
        A = [[random() for _ in range(size)] for _ in range(size)]
        B = [[random() for _ in range(size)] for _ in range(size)]
        result = [[sum(A[i][k] * B[k][j] for k in range(size)) for j in range(size)] for i in range(size)]
        return result

    def cpu_2():
        """Element-wise arithmetic"""
        N = 10**6
        A = [random() for _ in range(N)]
        B = [random() for _ in range(N)]
        return [A[i] + B[i] for i in range(N)]
    
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
        N = 10**6
        A = [random() for _ in range(N)]
        return A.copy()

    def mem_2():
        """Array slicing"""
        N = 10**6
        A = [random() for _ in range(N)]
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
        N = 10**6
        A = [random() for _ in range(N)]
        return sum(A)

    def cache_2():
        """Strided array sum"""
        N = 10**6
        A = [random() for _ in range(N)]
        return sum(A[::2])
    
    # run the benchmarks
    benchmarks = [cpu_1, cpu_2, cpu_3, cpu_4, cpu_5, mem_1, mem_2, mem_3, cache_1, cache_2]
    raw_data = [list() for _ in range(repeats)]
    for i in range(repeats):
        for f in benchmarks:
            start = perf_counter()
            f()
            duration = perf_counter() - start
            raw_data[i].append(duration)

    # non-Numpy implementation of statistics calculation
    transposed_data = list(zip(*raw_data))  # transpose the raw_data to get columns as rows

    # calculate mean along axis=0 (column-wise) (`benchmark_data.mean(axis=0)`)
    benchmark_mean = [sum(column) / len(column) for column in transposed_data]

    # calculate standard deviation along axis=0 (column-wise)
    def stddev(column, mean):
        variance = sum((x - mean) ** 2 for x in column) / len(column)
        return sqrt(variance)

    # calculate relative standard deviation (`(benchmark_data.std(axis=0) / abs(np_benchmark_mean))`)
    benchmark_std = [stddev(column, mean) for column, mean in zip(transposed_data, benchmark_mean)]
    relative_std = [(s / abs(m)) if m != 0 else 0 for s, m in zip(benchmark_std, benchmark_mean)]

    # calculate mean relative standard deviation and apply threshold (`max(np.mean(np_relative_std), 0.125)`)
    mean_relative_std = max(sum(relative_std) / len(relative_std), 0.125)

    # calculate performance factor  (`np.mean(np_benchmark_mean / reference_microbenchmark_mean)`)
    performance_factor = sum(bm / rm for bm, rm in zip(benchmark_mean, reference_microbenchmark_mean)) / len(benchmark_mean)
    return performance_factor, mean_relative_std

performance_factor, mean_relative_std = get_performance_factor()
print(f"\nSystem performance factor: {round(performance_factor, 3)}")

@pytest.mark.skip
def check_benchmark_performance(benchmark_name, mean, std):
    """Utility function to check whether the performance of a benchmark is within the expected range and print information."""
    reference_result = reference_results[benchmark_name]
    assert  mean - std * 2 <= reference_result * (performance_factor + mean_relative_std * 2)
    print(f"Reference: {round(reference_result, 3)}, benchmark: {round(mean, 3)}, expected: {round(reference_result * performance_factor, 3)}")


def test_microhh(benchmark):
    """Based on the MicroHH search space in the paper."""
    benchmark_name = "microhh"

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

    # run the benchmark and check for valid outcome and performance degradation
    solutions = benchmark(problem.getSolutions)
    reference_result = reference_results[benchmark_name]
    benchmark_result = benchmark.stats.stats.mean
    benchmark_results[benchmark_name] = benchmark_result
    assert len(solutions) == 138600
    check_benchmark_performance(benchmark_name, benchmark_result, benchmark.stats.stats.stddev)


def test_dedispersion(benchmark):
    """Based on the Dedispersion search space in the paper."""
    benchmark_name = "dedispersion"

    # setup the tunable parameters
    problem = Problem()
    problem.addVariable("block_size_x", [1, 2, 4, 8] + [16 * i for i in range(1, 3)])
    problem.addVariable("block_size_y", [8 * i for i in range(4, 33)])
    problem.addVariable("block_size_z", [1])
    problem.addVariable("tile_size_x", [i for i in range(1, 5)])
    problem.addVariable("tile_size_y", [i for i in range(1, 9)])
    problem.addVariable("tile_stride_x", [0, 1])
    problem.addVariable("tile_stride_y", [0, 1])
    problem.addVariable("loop_unroll_factor_channel", [
        0
    ])

    # setup the restrictions
    check_block_size = "32 <= block_size_x * block_size_y <= 1024"
    check_tile_stride_x = "tile_size_x > 1 or tile_stride_x == 0"
    check_tile_stride_y = "tile_size_y > 1 or tile_stride_y == 0"
    problem.addConstraint([check_block_size, check_tile_stride_x, check_tile_stride_y])

    # run the benchmark and check for valid outcome and performance degradation
    solutions = benchmark(problem.getSolutions)
    reference_result = reference_results[benchmark_name]
    benchmark_result = benchmark.stats.stats.mean
    benchmark_results[benchmark_name] = benchmark_result
    assert len(solutions) == 11130
    check_benchmark_performance(benchmark_name, benchmark_result, benchmark.stats.stats.stddev)


def test_hotspot(benchmark):
    """Based on the Hotspot search space in the paper."""
    benchmark_name = "hotspot"

    # constants
    temporal_tiling_factor = [i for i in range(1, 11)]
    max_tfactor = max(temporal_tiling_factor)

    # setup the tunable parameters
    problem = Problem()
    problem.addVariable("block_size_x", [1, 2, 4, 8, 16] + [32 * i for i in range(1, 33)])
    problem.addVariable("block_size_y", [2**i for i in range(6)])
    problem.addVariable("tile_size_x", [i for i in range(1, 11)])
    problem.addVariable("tile_size_y", [i for i in range(1, 11)])
    problem.addVariable("temporal_tiling_factor", temporal_tiling_factor)
    problem.addVariable("max_tfactor", [max_tfactor])
    problem.addVariable("loop_unroll_factor_t", [i for i in range(1, max_tfactor + 1)])
    problem.addVariable("sh_power", [0, 1])
    problem.addVariable("blocks_per_sm", [0, 1, 2, 3, 4])

    # setup the restrictions
    problem.addConstraint([
        "block_size_x*block_size_y >= 32",
        "temporal_tiling_factor % loop_unroll_factor_t == 0",
        f"block_size_x*block_size_y <= {dev['max_threads']}",
        f"(block_size_x*tile_size_x + temporal_tiling_factor * 2) * (block_size_y*tile_size_y + temporal_tiling_factor * 2) * (2+sh_power) * 4 <= {dev['max_shared_memory_per_block']}",
        f"blocks_per_sm == 0 or (((block_size_x*tile_size_x + temporal_tiling_factor * 2) * (block_size_y*tile_size_y + temporal_tiling_factor * 2) * (2+sh_power) * 4) * blocks_per_sm <= {dev['max_shared_memory']})",
    ])

    # run the benchmark and check for valid outcome and performance degradation
    solutions = benchmark(problem.getSolutions)
    reference_result = reference_results[benchmark_name]
    benchmark_result = benchmark.stats.stats.mean
    benchmark_results[benchmark_name] = benchmark_result
    assert len(solutions) == 349853
    check_benchmark_performance(benchmark_name, benchmark_result, benchmark.stats.stats.stddev)
