"""Test run times with benchmarks against reference times. File is called test_util_benchmarks to be ran as last test."""

import pytest
from random import random
from time import perf_counter
from math import sqrt

from .benchmarks import dedispersion, microhh, hotspot


# reference times (using A4000 on DAS6)
reference_microbenchmark_mean = [0.3784186691045761, 0.4737640768289566, 0.10726054509480794, 0.10744890073935191, 0.10979799057046573, 0.15360217044750848, 0.14483965436617532, 0.054416230569283165, 0.13835338006416956, 0.1371802551050981]    # noqa E501
reference_results = {
    "microhh": 1.1565620,
    "dedispersion": 0.1171140,
    "hotspot": 2.6839208,
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

    # calculate mean relative standard deviation and apply threshold (`max(np.mean(np_relative_std), 0.25)`)
    mean_relative_std = max(sum(relative_std) / len(relative_std), 0.25)

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
    print(f"Benchmark {benchmark_name}: reference: {round(reference_result, 3)}, run: {round(mean, 3)}, expected: {round(reference_result * performance_factor, 3)}")

@pytest.mark.skip
def run_and_check_benchmark(benchmark, benchmark_name, problem, expected_num_solutions):
    """Utility function to run and check a benchmark."""
    # run the benchmark
    solutions = benchmark(problem.getSolutions)
    benchmark_result = benchmark.stats.stats.mean
    benchmark_results[benchmark_name] = benchmark_result
    # check for valid outcome
    assert len(solutions) == expected_num_solutions
    # check for performance degradation
    check_benchmark_performance(benchmark_name, benchmark_result, benchmark.stats.stats.stddev)

def test_microhh(benchmark):
    run_and_check_benchmark(benchmark, *microhh())

def test_dedispersion(benchmark):
    run_and_check_benchmark(benchmark, *dedispersion())

def test_hotspot(benchmark):
    run_and_check_benchmark(benchmark, *hotspot())
