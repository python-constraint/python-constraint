"""Module providing various search spaces for benchmarking, ordered on number of solutions."""

from constraint import Problem

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

def dedispersion():
    """Based on the Dedispersion search space in the paper."""
    benchmark_name = "dedispersion"
    expected_num_solutions = 11130

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

    return benchmark_name, problem, expected_num_solutions

def microhh():
    """Based on the MicroHH search space in the paper."""
    benchmark_name = "microhh"
    expected_num_solutions = 138600

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
    
    return benchmark_name, problem, expected_num_solutions

def hotspot():
    """Based on the Hotspot search space in the paper."""
    benchmark_name = "hotspot"
    expected_num_solutions = 349853

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

    return benchmark_name, problem, expected_num_solutions
