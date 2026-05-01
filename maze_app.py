import reflex as rx
import random
import heapq
import asyncio

# ── Algorithms ──
def init_grid(cols, rows):
    return [[1] * cols for _ in range(rows)]

def divide(maze, x, y, w, h):
    if w < 3 or h < 3: return
    horizontal = (h > w) or (w == h and random.random() < 0.5)
    if horizontal:
        wy = random.choice(range(y + 1, y + h - 1, 2))
        px = random.choice(range(x, x + w, 2))
        for c in range(x, x + w): maze[wy][c] = 1
        maze[wy][px] = 0
        divide(maze, x, y, w, wy - y)
        divide(maze, x, wy + 1, w, h - (wy - y + 1))
    else:
        wx = random.choice(range(x + 1, x + w - 1, 2))
        py = random.choice(range(y, y + h, 2))
        for r in range(y, y + h): maze[r][wx] = 1
        maze[py][wx] = 0
        divide(maze, x, y, wx - x, h)
        divide(maze, wx + 1, y, w - (wx - x + 1), h)

def gen_maze(size):
    cols = rows = size if size % 2 == 1 else size + 1
    maze = init_grid(cols, rows)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1): maze[r][c] = 0
    divide(maze, 1, 1, cols - 2, rows - 2)
    return maze, cols, rows

def astar(maze, start, goal, cols, rows):
    def h(x, y): return abs(x - goal[0]) + abs(y - goal[1])
    g_score = {start: 0}
    came_from = {}
    open_heap = [(h(*start), 0, start)]
    all_visited = []
    while open_heap:
        _, g, cur = heapq.heappop(open_heap)
        if cur in all_visited: continue
        all_visited.append(cur)
        if cur == goal:
            path = []
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.append(start)
            return path[::-1], all_visited
        cx, cy = cur
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                ng = g + 1
                if ng < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = cur
                    g_score[(nx, ny)] = ng
                    heapq.heappush(open_heap, (ng + h(nx, ny), ng, (nx, ny)))
    return None, all_visited

# ── State ──
class MazeState(rx.State):
    maze: list[list[int]] = []
    cols: int = 21
    rows: int = 21
    path: list[tuple[int, int]] = []
    visited: list[tuple[int, int]] = []
    current_pos: tuple[int, int] = (1, 1)
    is_animating: bool = False
    speed: float = 0.5
    step_idx: int = 0
    phase: str = "search" # "search" or "path"

    def gen_new_maze(self):
        self.maze, self.cols, self.rows = gen_maze(21)
        self.path = []
        self.visited = []
        self.current_pos = (1, 1)
        self.is_animating = False
        self.step_idx = 0

    async def start_animation(self):
        if not self.is_animating:
            path, visited = astar(self.maze, (1, 1), (self.cols - 2, self.rows - 2), self.cols, self.rows)
            self.path = path
            self.visited = visited
            self.is_animating = True
            self.step_idx = 0
            self.phase = "search"
            
            # Animation Loop
            while self.is_animating:
                if self.phase == "search":
                    if self.step_idx < len(self.visited):
                        self.current_pos = self.visited[self.step_idx]
                        self.step_idx += 1
                    else:
                        self.phase = "path"
                        self.step_idx = 0
                elif self.phase == "path":
                    if self.step_idx < len(self.path):
                        self.current_pos = self.path[self.step_idx]
                        self.step_idx += 1
                    else:
                        self.is_animating = False
                
                yield # Update UI
                await asyncio.sleep(max(0.01, 1.0 - self.speed))

    def pause_animation(self):
        self.is_animating = False

# ── UI ──
def cell(r, c):
    # Determine color logic
    is_wall = MazeState.maze[r][c] == 1
    in_visited = MazeState.visited.contains((c, r))
    in_path = MazeState.path.contains((c, r))
    is_current = MazeState.current_pos == (c, r)
    
    return rx.box(
        rx.cond(is_current, "🤖", ""),
        bg=rx.cond(
            is_current, "#4ecdc4",
            rx.cond(in_path, "#0077be",
                rx.cond(in_visited, "#4ecdc4",
                    rx.cond(is_wall, "#1e1e1e", "#141414")
                )
            )
        ),
        width="20px", height="20px",
        display="flex", align_items="center", justify_content="center",
        font_size="10px"
    )

def index():
    return rx.vstack(
        rx.heading("🤖 Robot Maze", font_family="JetBrains Mono"),
        rx.hstack(
            # Sidebar
            rx.vstack(
                rx.button("New Maze", on_click=MazeState.gen_new_maze),
                rx.button("Start", on_click=MazeState.start_animation),
                rx.button("Pause", on_click=MazeState.pause_animation),
                rx.slider(on_change=MazeState.set_speed, min=0.1, max=0.9, default=0.5),
                width="200px"
            ),
            # Maze Grid
            rx.grid(
                rx.foreach(MazeState.maze, lambda row, r: rx.foreach(row, lambda _, c: cell(r, c))),
                grid_template_columns=rx.Var.create("repeat(21, 20px)"),
                gap="1px"
            )
        ),
        padding="2rem",
        bg="#0d0d0d",
        color="white",
        min_height="100vh"
    )

app = rx.App()
app.add_page(index)
