import streamlit as st
import random
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

st.set_page_config(page_title="Robot Maze", page_icon="🤖", layout="wide")

# ── Maze generation ──
def init_grid(cols, rows):
    return [[1] * cols for _ in range(rows)]

def divide(maze, x, y, w, h):
    if w < 3 or h < 3:
        return
    horizontal = (h > w) or (w == h and random.random() < 0.5)

    if horizontal:
        wy = random.randrange(y + 1, y + h - 1, 2)
        px = random.randrange(x, x + w, 2)
        for c in range(x, x + w):
            maze[wy][c] = 1
        maze[wy][px] = 0
        divide(maze, x, y, w, wy - y)
        divide(maze, x, wy + 1, w, h - (wy - y + 1))
    else:
        wx = random.randrange(x + 1, x + w - 1, 2)
        py = random.randrange(y, y + h, 2)
        for r in range(y, y + h):
            maze[r][wx] = 1
        maze[py][wx] = 0
        divide(maze, x, y, wx - x, h)
        divide(maze, wx + 1, y, w - (wx - x + 1), h)

def gen_maze(size):
    cols = rows = size if size % 2 == 1 else size + 1
    maze = init_grid(cols, rows)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            maze[r][c] = 0
    divide(maze, 1, 1, cols - 2, rows - 2)
    return maze, cols, rows

# ── A* generator ──
def astar_gen(maze, start, goal, cols, rows):
    def h(x, y):
        return abs(x - goal[0]) + abs(y - goal[1])

    g_score = {start: 0}
    came_from = {}
    visited = set()
    open_heap = [(h(*start), 0, start)]

    while open_heap:
        f, g, cur = heapq.heappop(open_heap)

        if cur in visited:
            continue

        visited.add(cur)
        yield cur, visited.copy(), None

        if cur == goal:
            path = []
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.append(start)
            yield cur, visited.copy(), path[::-1]
            return

        cx, cy = cur
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                ng = g + 1
                if ng < g_score.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = cur
                    g_score[(nx, ny)] = ng
                    heapq.heappush(open_heap, (ng + h(nx, ny), ng, (nx, ny)))

# ── Drawing ──
def draw_maze(maze, cols, rows, path=None, visited=None, robot=None, goal=None):
    fig, ax = plt.subplots(figsize=(6, 6))

    for r in range(rows):
        for c in range(cols):
            color = '#1e1e1e' if maze[r][c] == 1 else '#141414'
            ax.add_patch(patches.Rectangle((c, rows-r-1), 1, 1, color=color))

    if visited:
        for (x, y) in visited:
            ax.add_patch(patches.Rectangle((x, rows-y-1), 1, 1, color='#0a2a2a'))

    if path:
        for (x, y) in path:
            ax.add_patch(patches.Rectangle((x, rows-y-1), 1, 1, color='#4ecdc4'))

    if robot:
        ax.text(robot[0]+0.5, rows-robot[1]-0.5, "🤖", ha='center', va='center')

    if goal:
        ax.text(goal[0]+0.5, rows-goal[1]-0.5, "🎯", ha='center', va='center')

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.axis('off')
    return fig

# ── UI ──
st.title("🤖 Robot Maze")

with st.sidebar:
    size = st.select_slider("Grid Size", [11,15,21,25,31], value=21)
    speed = st.slider("Speed", 0.001, 0.05, 0.01)

    col1, col2 = st.columns(2)
    start_btn = col1.button("▶ Start")
    pause_btn = col2.button("⏸ Pause")

    reset_btn = st.button("🔄 Reset")

# ── State init ──
if "maze" not in st.session_state or reset_btn:
    maze, cols, rows = gen_maze(size)
    st.session_state.maze = maze
    st.session_state.cols = cols
    st.session_state.rows = rows
    st.session_state.gen = None
    st.session_state.running = False
    st.session_state.visited = set()
    st.session_state.path = None
    st.session_state.robot = (1,1)

maze = st.session_state.maze
cols = st.session_state.cols
rows = st.session_state.rows
start = (1,1)
goal = (cols-2, rows-2)

# ── Control logic ──
if start_btn:
    if st.session_state.gen is None:
        st.session_state.gen = astar_gen(maze, start, goal, cols, rows)
    st.session_state.running = True

if pause_btn:
    st.session_state.running = False

# ── Animation loop ──
placeholder = st.empty()

# Always draw something first (IMPORTANT FIX)
fig = draw_maze(
    maze,
    cols,
    rows,
    path=st.session_state.path,
    visited=st.session_state.visited,
    robot=st.session_state.robot,
    goal=goal
)
placeholder.pyplot(fig)
plt.close(fig)

# ── Animation step ──
if st.session_state.running:
    try:
        cur, visited, path = next(st.session_state.gen)

        st.session_state.robot = cur
        st.session_state.visited = visited

        if path:
            st.session_state.path = path
            st.session_state.running = False

    except StopIteration:
        st.session_state.running = False

    time.sleep(speed)
    st.rerun()
