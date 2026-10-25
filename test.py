"""A simple test script for the constraint module."""

from constraint import Problem

problem = Problem()

domain = ["a", "b"]

grid_size = 4
num_tiles = grid_size**2
tile_indices = range(num_tiles)
problem.addVariables(tile_indices, domain)

for row in range(grid_size):
    for col in range(grid_size):
        print(tile_indices[row * grid_size + col], end=" " if col < grid_size - 1 else "\n")


def not_equal(x, y):
    """Test that x and y are not equal."""
    return x != y


# enforces left-right not equal
for row in range(grid_size):
    for col in range(grid_size - 1):
        idx = row * grid_size + col
        idx_right = row * grid_size + col + 1
        problem.addConstraint(not_equal, [idx_right, idx])
        print("added constraint for left-right not equal:", idx, idx_right)

# # enforces up-down not equal
# for row in range(grid_size - 1):
#     for col in range(grid_size):
#         idx = row * grid_size + col
#         idx_down = (row + 1) * grid_size + col
#         problem.addConstraint(lambda d, c: c != d, [idx_down, idx])

# solution = problem.getSolution()

# if solution:
#     for row in range(grid_size):
#         for col in range(grid_size):
#             idx = row * grid_size + col
#             if col == grid_size - 1:
#                 print(f"{list(solution.values())[idx]}")
#             else:
#                 print(f"{list(solution.values())[idx]}", end="")

list, _, _ = problem.getSolutionsAsListDict()
for i, solution in enumerate(list):
    print(f"Solution {i}:")
    for row in range(grid_size):
        for col in range(grid_size):
            idx = row * grid_size + col
            if col == grid_size - 1:
                print(f"{solution[idx]}")
            else:
                print(f"{solution[idx]}", end="")

# [ds, cs, cvs] = problem._getArgs()
# print(ds)
# print(cs)
# print(cvs)
