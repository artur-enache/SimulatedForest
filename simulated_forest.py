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

    @property.setter
    def tick(self, new_tick: int) -> None:
        self._tick = new_tick

    def find_path(self, start_instance: LivingBeing, target_instance: str = None) -> list:
        
        pass

test = Forest(5)
print('\n'.join(str(item) for item in test.matrix))