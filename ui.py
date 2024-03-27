import random
import time
import tkinter as tk
from collections import deque
from tkinter import StringVar, messagebox, simpledialog
from typing import List, Literal
from queue import PriorityQueue
from util import BBFSNode, Node, time_execution, get_heuristics


class Ui:
    number_list_btns: List[tk.Button] = []
    number_list_int: List[int] = []
    target_number_list_int: List[int] = [*range(1, 10)]
    target_number_list_btns: List[tk.Button] = []
    root: tk.Tk
    moved = 0
    passed_time = 0
    start_time = 0.0
    timer_enable = False
    last_move = ""
    solve_algo_options = ["BFS", "DLS", "IDDFS", "Bidirection BFS", "A*","GBFS"]

    def __init__(
        self,
        root: tk.Tk | None = None,
        btn_size=10,
        grid_size=300,
        puase_time=0.2,
        allowed_moves=50,
        auto_solve=True,
        dls_limit: int = 5,
        iddfs_max_limit: int = 20,
    ) -> None:
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        self.btn_size = btn_size
        self.grid_size = grid_size
        self.puase_time = puase_time
        self.allowed_moves = allowed_moves
        self.dls_limit = dls_limit
        self.iddfs_max_limit = iddfs_max_limit
        self.solve_algo_string = tk.StringVar(self.root)
        self.solve_algo_string.set(self.solve_algo_options[0])
        self.auto_solve = auto_solve
        # creat main game btns
        self.creat_status_ui()
        self.number_list_btns = self.creat_main_btns(tk.LEFT)

        # creat target buttons
        self.target_number_list_btns = self.creat_main_btns(side=tk.RIGHT)
        self.set_click_event_for_target_btns()
        self.update_target_number_list_btn()

        self.fill_random_btns(self.number_list_int)
        self.update_number_list_btn()
        # main window keydown event
        self.root.bind("<Key>", self.window_key_down)

    def set_counter_text(self):
        self.lbl_counter_text.set(f"{self.moved}/{self.allowed_moves}")

    def set_timer_text(self):
        m, s = map(int, divmod(time.time() - self.start_time, 60))
        self.lbl_timer_text.set(f"{m:02d}/{s:02d}")

    def timer_update(self):
        m, s = map(int, divmod(time.time() - self.start_time, 60))
        self.set_timer_text()
        if self.timer_enable:
            self.root.after(1000, self.timer_update)

    def creat_status_ui(self):
        bar_top = tk.Frame(self.root)
        bar_bottm = tk.Frame(self.root)
        bar_bottm.grid_rowconfigure(0, weight=1)
        bar_bottm.grid_rowconfigure(1, weight=1)
        bar_bottm.grid_rowconfigure(2, weight=1)
        bar_bottm.grid_columnconfigure(0, weight=1)
        bar_top.grid_rowconfigure(0, weight=1)
        bar_top.grid_columnconfigure(0, weight=1)
        bar_top.grid_columnconfigure(1, weight=1)
        bar_top.grid_columnconfigure(2, weight=1)
        bar_top.grid_columnconfigure(3, weight=1)
        solve_algo_menu = tk.OptionMenu(
            bar_bottm, self.solve_algo_string, *self.solve_algo_options
        )
        solve_algo_menu.grid(row=0, column=0, sticky="ew")
        button_solve = tk.Button(
            bar_bottm, text="Solve puzzle", command=self.solve_puzzle
        )
        button_solve.grid(row=2, column=0, sticky="ew")
        button_auto_solve= tk.Button(
            bar_bottm, text=f"Auto solve: {self.auto_solve}",)
        #set button auto solve command
        button_auto_solve.configure(command=lambda btn=button_auto_solve: self.buton_auto_solve_click(btn))
        button_auto_solve.grid(row=1, column=0, sticky="ew")
        button_random_move = tk.Button(
            bar_top, text="Move Random N times", command=self.do_n_random_moves
        )
        button_random_move.grid(row=0, column=0)

        button_set_config = tk.Button(
            bar_top, text="Set this config", command=self.btn_set_config_click
        )
        button_set_config.grid(row=0, column=1)
        self.lbl_counter_text = StringVar()
        lbl_counter = tk.Label(bar_top, text="", textvariable=self.lbl_counter_text)
        lbl_counter.grid(row=0, column=2)
        self.lbl_timer_text = StringVar()
        lbl_timer = tk.Label(bar_top, text="", textvariable=self.lbl_timer_text)
        lbl_timer.grid(row=0, column=3)
        bar_top.pack(side=tk.TOP, fill="x")
        bar_bottm.pack(side=tk.BOTTOM, fill="x")
    def buton_auto_solve_click(self,button:tk.Button):
        self.auto_solve=not self.auto_solve
        button.configure(text=f"Auto solve: {self.auto_solve}")
        
    def get_allowed_moves(
        self,
        state: list[int] | None = None,
        last_move: str | None = None,
    ) -> List[str]:
        li = []
        if state is None:
            i = self.number_list_int.index(9)
        else:
            i = state.index(9)
        if i + 3 >= 0 and i + 3 < 9:
            li.append("W")
        if i - 3 >= 0 and i - 3 < 9:
            li.append("S")
        if i // 3 == (i - 1) // 3:
            li.append("D")
        if i // 3 == (i + 1) // 3:
            li.append("A")
        if last_move and last_move in li:
            li.remove(self.last_move)
        return li

    def get_game_state(self) -> list[int]:
        return self.number_list_int.copy()

    @classmethod
    def move_on_given_game_state(cls, move: str, state: list[int]):
        i = state.index(9)
        if move == "W":
            if i + 3 >= 0 and i + 3 < 9:
                state[i], state[i + 3] = (
                    state[i + 3],
                    state[i],
                )
        if move == "S":
            if i - 3 >= 0 and i - 3 < 9:
                state[i], state[i - 3] = (
                    state[i - 3],
                    state[i],
                )
        if move == "D":
            if i // 3 == (i - 1) // 3:
                state[i], state[i - 1] = (
                    state[i - 1],
                    state[i],
                )
        if move == "A":
            if i // 3 == (i + 1) // 3:
                state[i], state[i + 1] = (
                    state[i + 1],
                    state[i],
                )
        return state

    def random_move(self, n):
        for i in range(n):
            self.move_btn(
                m := random.choice(self.get_allowed_moves(last_move=self.last_move))
            )
            self.last_move = self.get_correspondence(m)
            time.sleep(self.puase_time)

    def do_n_random_moves(self):
        if n := self.show_int_input():
            self.random_move(n)
        else:
            print("Error whiel reading n for random moves")

    def window_key_down(self, event):
        key = event.keysym.upper()
        if key not in ("W", "S", "D", "A") or key not in self.get_allowed_moves():
            return
        if self.moved > self.allowed_moves:
            messagebox.showwarning("Cant move", "Max moves have been reached")
            return
        self.move_btn(key)
        if self.number_list_int == self.target_number_list_int:
            messagebox.showinfo(
                "You won", f"You have completed the puzzle in {self.moved} moves"
            )
            self.moved = 0
            self.set_counter_text()
            self.timer_enable = False
        self.moved += 1
        self.set_counter_text()

    def btn_set_config_click(self):
        self.target_number_list_int.clear()
        for i, y in enumerate(self.target_number_list_btns):
            if y.cget("text") != "":
                self.target_number_list_int.append(int(y.cget("text")))
            else:
                self.target_number_list_int.append(9)
        self.number_list_int = self.target_number_list_int.copy()
        self.update_number_list_btn()
        self.moved = 0
        self.set_counter_text()
        self.timer_enable = True
        self.start_time = time.time()
        self.root.after(1000, self.timer_update)

    def move_btn(self, move: str):
        self.move_on_given_game_state(move=move, state=self.number_list_int)
        self.update_number_list_btn()
        self.root.update()

    def update_number_list_btn(self):
        for i, y in enumerate(self.number_list_int):
            if y == 9:
                self.number_list_btns[i].config(text="")
            else:
                self.number_list_btns[i].config(text=y)

    def get_correspondence(self, move: str):
        li = {"A": "D", "D": "A", "W": "S", "S": "W"}
        return li[move]

    def update_target_number_list_btn(self):
        for i, y in enumerate(self.target_number_list_int):
            if y == 9:
                self.target_number_list_btns[i].config(text="")
            else:
                self.target_number_list_btns[i].config(text=y)

    def update_number_list_int(self):
        self.number_list_int.clear()
        for i in self.number_list_btns:
            self.number_list_int.append(
                int(i.cget("text") if i.cget("text") != "" else 9)
            )

    def fill_random_btns(self, lis: List[int]):
        n = [*range(1, 10)]
        random.shuffle(n)
        lis.clear()
        for i, y in enumerate(n):
            lis.append(y)

    def set_click_event_for_target_btns(self):
        for y, i in enumerate(self.target_number_list_btns):
            print(i.cget("text"))
            i.bind("<Button-1>", self.set_target_btn_int)

    def set_target_btn_int(self, event: tk.Event):
        if val := self.show_int_input():
            event.widget.config(text=val if val != 9 else "")
        else:
            print("Error while reading input")

    def show_int_input(self) -> int | None:
        val = simpledialog.askinteger("Enter number", "Enter a number for this cell")

        if val is not None:
            return val
        else:
            return None

    def creat_main_btns(
        self, side: Literal["left", "right", "top", "bottom"] = tk.LEFT
    ) -> List[tk.Button]:
        lis: List[tk.Button] = []
        btn_frame = tk.Frame(self.root, width=self.grid_size, height=self.grid_size)

        btn_frame.grid_rowconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_propagate(False)
        for i in range(3):
            btn_frame.grid_rowconfigure(i, weight=1)
            btn_frame.grid_columnconfigure(i, weight=1)
            for j in range(3):
                button = tk.Button(
                    btn_frame,
                    text="",
                    width=self.btn_size,
                    height=self.btn_size // 2,
                )
                button.grid(
                    row=i,
                    column=j,
                    columnspan=1,
                    pady=5,
                    padx=5,
                )
                lis.append(button)
        btn_frame.pack(side=side)

        return lis

    """
    the solve algorithms are here
    """

    @time_execution
    def bfs_search(
        self, target: tuple[int, ...], current: tuple[int, ...]
    ) -> tuple[str, ...]:
        checkd = set()
        que: deque[tuple[tuple[int, ...], tuple[str, ...]]] = deque()
        que.append((current, ()))
        while True:
            node, mlist = que.popleft()
            if node in checkd:
                continue
            moves = self.get_allowed_moves(
                list(node),
            )
            for i in moves:
                new_node = tuple(
                    self.move_on_given_game_state(move=i, state=list(node))
                )
                if new_node == target:
                    print(len(checkd), "checked for a*")

                    return mlist + (i,)
                if new_node not in checkd:
                    que.append((new_node, mlist + (i,)))
            checkd.add(node)

    @time_execution
    def bidirection_bfs(
        self, target: tuple[int, ...], current: tuple[int, ...]
    ) -> list[str]:
        # TODO: Use 2 sets of sets to save checked to make it faster
        checked: dict[tuple[int, ...], BBFSNode] = dict()
        que: deque[BBFSNode] = deque()
        que.append(BBFSNode(state=current, moves=[], direction="left"))
        que.append(BBFSNode(state=target, moves=[], direction="right"))
        while que:
            node: BBFSNode = que.popleft()

            if (
                node.state in checked
                and node.direction != checked[node.state].direction
            ):
                print(node, checked[node.state])
                return []

            for i in self.get_allowed_moves(
                list(node.state),
            ):
                new_node = BBFSNode(
                    state=tuple(
                        self.move_on_given_game_state(move=i, state=list(node.state))
                    ),
                    moves=node.moves + [i],
                    direction=node.direction,
                )
                if (
                    new_node.state in checked
                    and new_node.direction != checked[new_node.state].direction
                ):
                    return (
                        new_node.moves
                        if new_node.direction == "left"
                        else checked[new_node.state].moves
                    ) + (
                        [self.get_correspondence(x) for x in new_node.moves[::-1]]
                        if new_node.direction == "right"
                        else [
                            self.get_correspondence(x)
                            for x in checked[new_node.state].moves[::-1]
                        ]
                    )

                elif new_node not in checked:
                    que.append(new_node)
            checked[node.state] = node
        return []

    def DLS(
        self,
        target: tuple[int, ...],
        current: tuple[tuple[int, ...], list[str]],
        limit: int,
    ) -> list[str] | None:
        if target == current[0]:
            return current[1]
        elif limit == 0:
            return None
        else:
            for i in self.get_allowed_moves(list(current[0])):
                if n := self.DLS(
                    target=target,
                    current=(
                        tuple(self.move_on_given_game_state(i, list(current[0]))),
                        current[1] + [i],
                    ),
                    limit=limit - 1,
                ):
                    return n

    @time_execution
    def DLS_wrap(self, **kwargs):
        return self.DLS(**kwargs)

    @time_execution
    def IDDFS(
        self,
        target: tuple[int, ...],
        current: tuple[tuple[int, ...], list[str]],
        max_limit: int,
    ) -> tuple[list[str], int] | None:
        for i in range(1, max_limit + 1):
            if n := self.DLS(target=target, current=current, limit=i):
                return (n, i)
        return None

    @time_execution
    def GBFS(self, target: tuple[int, ...], current: tuple[int, ...]) -> list[str]:
        checkd: set[Node] = set()
        que: PriorityQueue[tuple[int, Node]] = PriorityQueue()
        que.put((get_heuristics(target, current), Node(moves=[], state=current)))
        while True:
            (
                pro,
                node,
            ) = que.get()
            if node in checkd:
                continue
            moves = self.get_allowed_moves(
                list(node.state),
            )
            for i in moves:
                new_node = Node(
                    state=tuple(
                        self.move_on_given_game_state(move=i, state=list(node.state))
                    ),
                    moves=node.moves + [i],
                )
                if new_node.state == target:
                    return node.moves + [i]
                if new_node not in checkd:
                    que.put(
                        (
                            get_heuristics(target=target, current=new_node.state),
                            new_node,
                        )
                    )
            checkd.add(node)

    @time_execution
    def A_Star(self, target: tuple[int, ...], current: tuple[int, ...]) -> list[str]:
        checkd: set[Node] = set()
        que: PriorityQueue[tuple[int, Node]] = PriorityQueue()
        que.put((get_heuristics(target, current), Node(moves=[], state=current)))
        while True:
            (
                pro,
                node,
            ) = que.get()
            if node in checkd:
                continue
            moves = self.get_allowed_moves(
                list(node.state),
            )
            for i in moves:
                new_node = Node(
                    state=tuple(
                        self.move_on_given_game_state(move=i, state=list(node.state))
                    ),
                    moves=node.moves + [i],
                )
                if new_node.state == target:
                    print(len(checkd), "checked for a*")
                    return node.moves + [i]
                if new_node not in checkd:
                    que.put(
                        (
                            get_heuristics(target=target, current=new_node.state)
                            + len(new_node.moves),
                            new_node,
                        )
                    )
            checkd.add(node)

    def solve_puzzle(self):
        target_state = self.target_number_list_int.copy()
        current_state = self.number_list_int.copy()
        answer = None
        match self.solve_algo_string.get():
            case "BFS":
                answer = self.bfs_search(
                    target=tuple(target_state), current=tuple(current_state)
                )
                print(f"bfs Answer is {answer} with len {len(answer)}")
            case "DLS":
                answer = self.DLS_wrap(
                    target=tuple(target_state),
                    current=(tuple(current_state), []),
                    limit=self.dls_limit,
                )
                if answer:
                    print(f"DLS Answer is {answer} with len {len(answer)}")
                else:
                    print(
                        f"Coundt find answer with DLS algorithm with max limit {self.dls_limit}"
                    )
            case "IDDFS":
                answer = self.IDDFS(
                    target=tuple(target_state),
                    current=(tuple(current_state), []),
                    max_limit=self.iddfs_max_limit,
                )
                if answer:
                    print(
                        f"IDDFS Answer is {answer[0]} with len {len(answer[0])} and deapth {answer[1]}"
                    )
                    answer = answer[0]
                else:
                    print(
                        f"Coundt find answer with IDDFS algorithm with max limit {self.iddfs_max_limit}"
                    )

            case "Bidirection BFS":
                answer = self.bidirection_bfs(
                    target=tuple(target_state), current=tuple(current_state)
                )
                print(f"bidirectional bfs Answer is {answer} with len {len(answer)}")
            case "GBFS":
                answer = self.GBFS(
                    target=tuple(target_state), current=tuple(current_state)
                )
                print(f"GBFS Answer is {answer} with len {len(answer)}")
            case "A*":
                answer = self.A_Star(
                    target=tuple(target_state), current=tuple(current_state)
                )
                print(f"A* Answer is {answer} with len {len(answer)}")
        if self.auto_solve and answer:
            for i in answer:
                self.move_btn(i)
                time.sleep(self.puase_time * 5)


if __name__ == "__main__":
    root = tk.Tk()
    ui = Ui(root, puase_time=0.05, auto_solve=False, dls_limit=10, iddfs_max_limit=14)

    ui.root.mainloop()
