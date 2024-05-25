from heapq import heappush, heappop, heapify


class Node:
    def __init__(self, position, parent=None, g_cost=0, h_cost=0):
        self.position = position  # (row, col) coordinates
        self.parent = parent
        self.g_cost = g_cost  # Cost from start to current node
        self.h_cost = h_cost  # Heuristic cost estimate to end
        self.f_cost = self.g_cost + self.h_cost  # Total cost

    def __lt__(self, other):
        return self.f_cost < other.f_cost


class CelluvoyerGrid:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_valid(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] != 1  # 1 represents obstacle

    def get_neighbors(self, row, col):
        '''neighbors = []
        corners_permutation_one = [(-1, 0), (1, 0), (-1, 1), (0, 1), (-1, -1), (0, -1)]
        corners_permutation_two = [(-1, 1), (-1, 0), (-1, 1), (1, 1), (1, 0), (1, -1)]
        corners_permutation_three = [(-1, -1), (0, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]
        corners_permutation_four = [(-1, -1), (-1, 0), (0, 1), (1, -1), (1, -1), (0, -1)]
        for drow, dcol in corners_permutation_four:
            new_row = row + drow
            new_col = col + dcol
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors'''
        neighbors = []
        # Define movement based on even or odd rows (honeycomb grid)
        if row % 2 == 0:  # Even row
            corners_permutation = [[0, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0]]
        else:  # Odd row
            corners_permutation = [[-1, -1], [0, -1], [1, -1], [1, 0], [0, 1], [-1, 0]]
        for drow, dcol in corners_permutation:
            new_row = row + drow
            new_col = col + dcol
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        return neighbors

    @staticmethod
    def manhattan_distance(point1, point2):
        # Adjust for honeycomb grid movement (consider diagonal distance)
        dx = abs(point1[0] - point2[0])
        dy = abs(point1[1] - point2[1])
        return dx + max(0, dy - (dx % 2))  # Manhattan distance with diagonal adjustment

    @staticmethod
    def a_star_search(grid, start, end, max_paths=3):
        open_set = []
        closed_set = set()
        came_from = {}
        g_score = {start: 0}

        heappush(open_set, Node(start))

        while open_set:
            current = heappop(open_set)
            if current.position == end:
                paths = CelluvoyerGrid.reconstruct_path(came_from, current, max_paths)
                return paths

            closed_set.add(current.position)

            for neighbor in grid.get_neighbors(*current.position):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score.get(neighbor, float('inf'))
                new_g_score = current.g_cost + 1  # Movement cost (adjust if needed)

                if new_g_score < tentative_g_score:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g_score
                    h_cost = CelluvoyerGrid.manhattan_distance(neighbor, end)
                    f_cost = new_g_score + h_cost
                    heappush(open_set, Node(neighbor, current, new_g_score, h_cost))

        return []  # No path found

    @staticmethod
    def reconstruct_path(came_from, current, max_paths):
        paths = []
        for i in range(max_paths):  # Explore up to max_paths
            path = []
            while current:
                path.append(current.position)
                current = came_from.get(current.position)
            if not path:  # No path found for this iteration (e.g., dead end)
                break
            path.reverse()  # Reverse to get path from start to end
            paths.append(path)
        return paths

    @staticmethod
    def d_star_lite(grid, start, end):
        open_set = []
        closed_set = set()
        came_from = {}
        g_score = {start: 0}

        for cell in grid:
            row, col = cell
            node = Node(cell, float('inf'))
            open_set.append(node)

        start_node = Node(start, 0)
        start_node.rhs = CelluvoyerGrid.manhattan_distance(start, end)
        open_set[grid.index(start)] = start_node
        g_score[start] = 0

        while open_set:
            current = min(open_set, key=lambda x: x.key)  # Select node with lowest key
            if current.position == end:
                path = []
                while current:
                    path.append(current.position)
                    current = came_from.get(current.position)
                path.reverse()  # Reverse to get path from start to end
                return path

            open_set.remove(current)
            closed_set.add(current.position)

            for neighbor in grid.get_neighbors(*current.position):
                if neighbor in closed_set:
                    continue
                tentative_g_score = g_score.get(neighbor, float('inf'))
                new_g_score = current.g_cost + 1  # Movement cost (adjust if needed)

                if new_g_score < tentative_g_score:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g_score
                    CelluvoyerGrid.update_vertex(grid, neighbor, new_g_score, end)

        return []  # No path found

    @staticmethod
    def update_vertex(grid, cell, new_g_score, end):
        row, col = cell
        node_index = grid.index(cell)
        open_set = grid.open_set  # Access the open_set from the grid
        node = open_set[node_index]

        if node.g_cost == new_g_score:
            return  # No change, avoid redundant updates

        node.g_cost = new_g_score
        node.f_cost = node.g_cost + node.h_cost  # Update the total cost

        # Update neighbors' costs if necessary
        for neighbor in grid.get_neighbors(row, col):
            neighbor_node = open_set[grid.index(neighbor)]
            if neighbor_node.g_cost > node.g_cost + 1:  # Adjust the cost if the new path is better
                neighbor_node.g_cost = node.g_cost + 1
                neighbor_node.f_cost = neighbor_node.g_cost + neighbor_node.h_cost

                # Update the parent node
                neighbor_node.parent = node

                # Re-heapify to maintain the priority queue order
                heapify(open_set)


# Example usage
'''grid = [  # 0 represents empty cell, 1 represents obstacle
    [0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
]'''
grid = [[0, 1, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0]]
start = (0, 0)
end = (4, 4)

celluvoyer = CelluvoyerGrid(grid)
paths = CelluvoyerGrid.a_star_search(celluvoyer, start, end, max_paths=2)

if paths:
    print("Found paths:")
    for path in paths:
        print(path)
else:
    print("No path found")
