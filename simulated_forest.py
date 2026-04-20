import random
from importlib.util import source_hash
from timeit import default_timer


class Forest:
    def __init__(self, dimensions: int) -> None:
        if not isinstance(dimensions, int):
            raise ValueError('Forest dimension has to be an integer.')

        if dimensions <= 0 or dimensions > 20:
            raise ValueError('Forest dimension must be between 1 and 20.')

        self._tick = 0
        self._dimensions = dimensions
        self._empty = '🟫'
        self._grass = '🌱'
        self._rabbit = '🐇'
        self._wolf = '🐺'

        # The matrix will store one ref to an instance of grass / rabbit / wolf, per cell
        self._matrix = []
        for _ in range(self._dimensions):
            self._matrix.append([ None for _ in range(self._dimensions) ])

    @property
    def matrix(self) -> list:
        return self._matrix

    @property
    def dimensions(self) -> int:
        return self._dimensions

    @property
    def tick(self) -> int:
        return self._tick

    @tick.setter
    def tick(self, new_tick: int) -> None:
        self._tick = new_tick

    def set_test_element(self, element, position):
        i, j = position
        self.matrix[i][j] = element

    def find_path(self, start_position: tuple[int], target_type: str = '') -> list:
        # N NE E SE S SW W NW
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        start_i, start_j = start_position
        visited = []
        queue = [(start_i, start_j, [(start_i, start_j)])]

        while queue:
            i, j, path = queue.pop(0)
            visited.append((i, j))
            for dir in directions:
                ni, nj = dir
                new_i = i + ni
                new_j = j + nj
                if new_i < 0 or new_j < 0 or new_i >= self.dimensions or new_j >= self.dimensions:
                    continue
                    
                #if type(self.matrix[new_i][new_j]).__name__ == target_type:
                if isinstance(self.matrix[new_i][new_j], target_type):
                    return path + [(new_i, new_j)]
                else:
                    if (new_i, new_j) not in visited:
                        visited.append((new_i, new_j))
                        queue.append((new_i, new_j, path + [(new_i, new_j)]))

        return -1

test = Forest(5)

# Bug: path is [(0, 0), (1, 1), (2, 2), (3, 1)] instead of [(0, 0), (1, 1), (2, 1), (3, 1)]; Why?
test.set_test_element(1, (3, 1))
print(test.find_path((0, 0), int))
print('\n'.join(str(item) for item in test.matrix))