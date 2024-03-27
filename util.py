from functools import wraps
import time
from typing import Literal


class BBFSNode:
    def __init__(
        self,
        moves: list[str],
        state: tuple[int, ...],
        direction: Literal["left", "right"],
    ) -> None:
        self.moves = moves.copy()
        self.state = state
        self.direction: Literal["left", "right"] = direction

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        return "".join(map(str, self.state))

    def __str__(self) -> str:
        return "".join(map(str, self.state))


class Node:
    def __init__(
        self,
        moves: list[str],
        state: tuple[int, ...],
    ) -> None:
        self.moves = moves.copy()
        self.state = state

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        return "".join(map(str, self.state))

    def __str__(self) -> str:
        return "".join(map(str, self.state))

    def __eq__(self, __value: object) -> bool:
        if type(__value) == Node:
            return self.state == __value.state
        return False

    def __lt__(self, other) -> bool:
        return len(self.moves) < len(other.moves)


def time_execution(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Function {func.__name__} Took {total_time:.4f} seconds")
        return result

    return timeit_wrapper

    # def get_heuristics(target: tuple[int, ...], current: tuple[int, ...]) -> int:
    return sum([1 if target.index(i) == current.index(i) else 0 for i in target])


def get_heuristics(target: tuple[int, ...], current: tuple[int, ...]) -> int:
    distance = 0
    for i in range(3):
        for j in range(3):
            val = current[i * 3 + j]
            if val != 9:
                golindex = target.index(val)
                gol_row, goal_col = divmod(golindex, 3)
                distance += abs(i - gol_row) + abs(j - goal_col)
    return distance