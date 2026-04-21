import random

class Forest:
    def __init__(self, dimensions: int) -> None:
        if not isinstance(dimensions, int):
            raise ValueError('Forest dimension has to be an integer.')

        if dimensions <= 0 or dimensions > 20:
            raise ValueError('Forest dimension must be between 1 and 20.')

        # TODO: move the icons & ticker to a more appropriate place
        self._tick = 0
        self._dimensions = dimensions
        self._empty = '  '
        self._grass = '🌱'
        self._rabbit = '🐇'
        self._wolf = '🐺'
        self._test = '🪰'

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

    def update_position(self, element: object, position: list[tuple[[int]]]) -> None:
        i, j = position[0]
        self.matrix[i][j] = element

    def reset_forest(self) -> None:
        self._matrix = []
        for _ in range(self.dimensions):
            self._matrix.append([ None for _ in range(self.dimensions) ])

    def find_path(self, start_position: tuple[int] = None, target_type: str = None) -> list[tuple[int]]:
        # N NE E SE S SW W NW
        directions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

        if start_position:
            start_i, start_j = start_position
        else:
            start_i = random.randint(0, self.dimensions - 1)
            start_j = random.randint(0, self.dimensions - 1)

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

                # Allows the method to find nearest empty cell, used for spawning instances
                if target_type:
                    if isinstance(self.matrix[new_i][new_j], target_type):
                        return path + [(new_i, new_j)]
                    else:
                        if (new_i, new_j) not in visited:
                            visited.append((new_i, new_j))
                            queue.append((new_i, new_j, path + [(new_i, new_j)]))
                else:
                    if not self.matrix[new_i][new_j]:
                        return [(new_i, new_j)]

        return -1

    def update_forest(self, instances: list[object]) -> None:
        if not instances:
            raise ValueError('Cannot update an empty forest.')

        queue = []
        for entity in instances:
            queue.append((entity, entity.position))

        self.reset_forest()
        while queue:
            entity, new_position = queue.pop(0)
            self.update_position(entity, new_position)
            entity.position = new_position

    def draw_matrix(self):
        output_matrix = []
        for _ in range(self.dimensions):
            output_matrix.append([ None for _ in range(self.dimensions) ])

        for i in range(self.dimensions):
            for j in range(self.dimensions):
                output_matrix[i][j] = self._empty if not self.matrix[i][j] else self._test

        print('\n'.join(str(item) for item in output_matrix))


class TestClass:
    def __init__(self, position):
        self._position = position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

test_forest = Forest(5)
test_forest.reset_forest()
test_obj1 = TestClass(test_forest.find_path())
test_obj2 = TestClass(test_forest.find_path())
test_forest.update_forest([test_obj1, test_obj2])

test_forest.draw_matrix()
print(test_forest.find_path((0, 0), TestClass))
print(test_forest.find_path((0, 0), None))


# Bug: when only one element is in the matrix at (3, 1), find_path (0,0)
# returns [(0, 0), (1, 1), (2, 2), (3, 1)] instead of [(0, 0), (1, 1), (2, 1), (3, 1)]
# It looks like the algorithm prefers diagonal paths, more specifically the SE direction