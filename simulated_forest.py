import random, time

class Forest:
    def __init__(self, dimensions: int) -> None:
        if not isinstance(dimensions, int):
            raise ValueError('Forest dimension has to be an integer.')

        if dimensions <= 0 or dimensions > 20:
            raise ValueError('Forest dimension must be between 1 and 20.')

        # TODO: move the icons & ticker to a more appropriate place
        self._tick = 0
        self._dimensions = dimensions
        self._reserved = 'R'

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
            start_i, start_j = start_position[0]
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

                if target_type:
                    if isinstance(self.matrix[new_i][new_j], target_type):
                        return path + [(new_i, new_j)]
                    elif not self.matrix[new_i][new_j]:
                        if (new_i, new_j) not in visited:
                            visited.append((new_i, new_j))
                            queue.append((new_i, new_j, path + [(new_i, new_j)]))
                # Allows the method to find nearest empty cell, used for spawning instances
                else:
                    if not self.matrix[new_i][new_j]:
                        # Entities that are about to be spawned, are not aware of each other's positions
                        self.matrix[new_i][new_j] = self._reserved
                        return [(new_i, new_j)]

        return -1

    def update_forest(self, instances: list[object]) -> None:
        if not instances:
            raise ValueError('Cannot update an empty forest.')

        queue = []
        for entity in instances:
            if entity.position:
                queue.append((entity, entity.position))
            else:
                pass

        self.reset_forest()
        while queue:
            entity, new_position = queue.pop(0)
            self.update_position(entity, new_position)
            entity.position = new_position

    def is_empty(self, position) -> bool:
        i, j = position[0]
        return True if not self.matrix[i][j] else False

    def draw_matrix(self):
        self._empty = '  '
        self._grass = '🌱'
        self._rabbit = '🐇'
        self._wolf = '🐺'
        self._test = '🪰'

        instance_icons = {
            'Empty': '  ',
            'Grass': '🌿',
            'Rabbit': '🐰',
            'Wolf': '🐯'
        }

        output_matrix = []
        for _ in range(self.dimensions):
            output_matrix.append([ None for _ in range(self.dimensions) ])

        for i in range(self.dimensions):
            for j in range(self.dimensions):
                if not self.matrix[i][j]:
                    output_matrix[i][j] = self._empty
                else:
                    match_icon = type(self.matrix[i][j]).__name__
                    output_matrix[i][j] = instance_icons[match_icon]

        print('\n'.join(str(item) for item in output_matrix))

    def draw_debug_matrix(self):
        print('\n'.join(str(item) for item in self.matrix))

class LivingBeing:
    def __init__(self, position = (0, 0)):
        self._position = position
        self._current_health = None
        self._current_hunger = None

    def __str__(self):
        return f'{self.__class__.__name__}. Total: {self.instance_count}; Current health: {self.current_health}; Current hunger: {self.current_hunger}'

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

    @position.deleter
    def position(self):
        del self._position

    @property
    def current_health(self):
        return self._current_health

    @current_health.setter
    def current_health(self, new_health):
        self._current_health = new_health

    @property
    def current_hunger(self):
        return self._current_hunger

    @current_hunger.setter
    def current_hunger(self, new_hunger):
        self._current_hunger = new_hunger

    def can_reproduce(self, forest_instance: Forest):
        pass

class Grass(LivingBeing):
    instance_count = 0
    parents_required = 3
    max_health = 50
    health_attrition = 2
    reproduction_period = 10

    def __init__(self, position = (0, 0)):
        Grass.instance_count += 1
        super().__init__(position)
        self._current_health = Grass.max_health

    # Override parent method, Grass does not have hunger
    def __str__(self):
        return f'{self.__class__.__name__}. Total: {self.instance_count}; Current health: {self.current_health}; Current hunger: N/A'

class Rabbit(LivingBeing):
    instance_count = 0
    parents_required = 3
    max_hunger = 100
    hunger_threshold = 50
    hunger_attrition = 5
    max_health = 100
    health_attrition = 10
    reproduction_period = 5

    def __init__(self, position = (0, 0)):
        Rabbit.instance_count += 1
        super().__init__(position)
        self._current_hunger = Rabbit.max_hunger
        self._current_health = Rabbit.max_health

class Wolf(LivingBeing):
    instance_count = 0
    parents_required = 2
    max_hunger = 150
    hunger_threshold = 50
    hunger_attrition = 5
    max_health = 100
    health_attrition = 5
    reproduction_period = 25

    def __init__(self, position = (0, 0)):
        Wolf.instance_count += 1
        super().__init__(position)
        self._current_hunger = Wolf.max_hunger
        self._current_health = Wolf.max_health

# DEBUG SECTION - Game loop
ticks = 0
beings = []

start_rabbits = 4
start_grass = 6
start_wolf = 2

beings.extend([Rabbit() for _ in range(start_rabbits)])
beings.extend([Grass() for _ in range(start_grass)])
beings.extend([Wolf() for _ in range(start_wolf)])

while beings:
    ticks += 1
    for index, being in enumerate(beings):
        if isinstance(being, Grass):
            being.current_health -= being.health_attrition
            if being.current_health <= 0:
                beings.pop(index)
            elif ticks % being.reproduction_period == 0 and being.parents_required >= being.instance_count:
                print(f'Grass reproduced!')
                beings.append(Grass())
        else:
            being.current_hunger -= being.hunger_attrition
            if being.current_hunger < being.hunger_threshold:
                being.current_health -= being.health_attrition
                if being.current_health <= 0:
                    print(f'{being.__class__.__name__} died!')
                    beings.pop(index)
                elif isinstance(being, Rabbit):
                    try:
                        to_kill = next(x for x in beings if isinstance(x, Grass))
                    except:
                        to_kill = None
                else:
                    try:
                        to_kill = next(x for x in beings if isinstance(x, Rabbit))
                    except:
                        to_kill = None

                if to_kill:
                    # TO CONTINUE: the decrement here does not work
                    to_kill.instance_count -= 1
                    beings.pop(beings.index(to_kill))
                    being.current_health = being.max_health
                    being.current_hunger = being.max_hunger

            elif ticks % being.reproduction_period == 0 and being.parents_required >= being.instance_count:
                if isinstance(being, Rabbit):
                    print(f'Rabbit reproduced!')
                    beings.append(Rabbit())
                else:
                    print(f'Wolf reproduced!')
                    beings.append(Wolf())
    print(f'Grass: {Grass.instance_count} | Rabbits: {Rabbit.instance_count} | Wolves: {Wolf.instance_count}')
    time.sleep(1)

print(f'You forest survived for {ticks} iterations!')

# Bug: when only one element is in the matrix at (3, 1), find_path (0,0)
# returns [(0, 0), (1, 1), (2, 2), (3, 1)] instead of [(0, 0), (1, 1), (2, 1), (3, 1)]
# It looks like the algorithm prefers diagonal paths

# Bug: two entities searching for food at the same time can receive the same path; while moving, one instance
# overwrites the other in the forest matrix