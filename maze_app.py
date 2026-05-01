import streamlit as st
import random
import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ── Page config ──
st.set_page_config(page_title="Robot Maze", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .main { background-color: #0d0d0d; }
    .block-container { padding-top: 2rem; }

    h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.4rem;
        letter-spacing: -0.02em;
        color: #f0f0f0;
    }
    .subtitle {
        font-family: 'JetBrains Mono', monospace;
        color: #555;
        font-size: 0.85rem;
        margin-top: -1rem;
        margin-bottom: 2rem;
        letter-spacing: 0.08em;
    }
    .metric-box {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #555;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 700;
        color: #e0e0e0;
    }
    .stButton > button {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        border-radius: 6px;
        border: 1px solid #333;
        background: #1a1a1a;
        color: #ccc;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #252525;
        border-color: #555;
        color: #fff;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #666;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .status-bar {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #4ecdc4;
        background: #0f1f1f;
        border: 1px solid #1a3333;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Maze generation ──
def init_grid(cols, rows):
    return [[1] * cols for _ in range(rows)]


def divide(maze, x, y, w, h):
    if w < 3 or h < 3:
        return
    horizontal = (h > w) or (w == h and random.random() < 0.5)
    if horizontal:
        options = list(range(y + 1, y + h - 1, 2))
        if not options:
            return
        wy = random.choice(options)
        px_options = list(range(x, x + w, 2))
        px = random.choice(px_options) if px_options else x
        for c in range(x, x + w):
            maze[wy][c] = 1
        maze[wy][px] = 0
        divide(maze, x, y, w, wy - y)
        divide(maze, x, wy + 1, w, h - (wy - y + 1))
    else:
        options = list(range(x + 1, x + w - 1, 2))
        if not options:
            return
        wx = random.choice(options)
        py_options = list(range(y, y + h, 2))
        py = random.choice(py_options) if py_options else y
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


# ── A* solver ──
def astar(maze, start, goal, cols, rows):
    def h(x, y):
        return abs(x - goal[0]) + abs(y - goal[1])

    g_score = {start: 0}
    came_from = {}
    visited = set()
    open_heap = [(h(*start), 0, start)]
    frontier = set([start])
    all_visited = []

    while open_heap:
        f, g, cur = heapq.heappop(open_heap)
        if cur in visited:
            continue
        visited.add(cur)
        frontier.discard(cur)
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
                    frontier.add((nx, ny))

    return None, all_visited


# ── Plotting ──
def draw_maze(maze, cols, rows, path=None, visited=None, start=None, goal=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0d0d0d')
    ax.set_facecolor('#0d0d0d')

    # Draw cells
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == 1:
                color = '#1e1e1e'
            else:
                color = '#141414'
            rect = patches.Rectangle((c, rows - r - 1), 1, 1,
                                      linewidth=0, facecolor=color)
            ax.add_patch(rect)

    # Visited cells
    if visited:
        for (vx, vy) in visited:
            rect = patches.Rectangle((vx, rows - vy - 1), 1, 1,
                                      linewidth=0, facecolor='#0a2a2a')
            ax.add_patch(rect)

    # Path
    if path:
        for (px, py) in path:
            rect = patches.Rectangle((px, rows - py - 1), 1, 1,
                                      linewidth=0, facecolor='#4ecdc4')
            ax.add_patch(rect)

    # Start
    if start:
        sx, sy = start
        circle = plt.Circle((sx + 0.5, rows - sy - 0.5), 0.35,
                             color='#f7c59f', zorder=5)
        ax.add_patch(circle)
        ax.text(sx + 0.5, rows - sy - 0.5, '🤖', ha='center', va='center',
                fontsize=10, zorder=6)

    # Goal
    if goal:
        gx, gy = goal
        circle = plt.Circle((gx + 0.5, rows - gy - 0.5), 0.35,
                             color='#ff6b6b', zorder=5)
        ax.add_patch(circle)
        ax.text(gx + 0.5, rows - gy - 0.5, '🎯', ha='center', va='center',
                fontsize=10, zorder=6)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0)
    return fig


# ── App ──
st.markdown("<h1>🤖 Robot Maze</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">A* PATHFINDING VISUALIZER · RECURSIVE DIVISION</p>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.markdown("### Controls")
    size = st.select_slider("Grid Size", options=[11, 15, 21, 25, 31, 41], value=21)
    gen_btn = st.button("⟳ New Maze", use_container_width=True)
    st.markdown("---")
    solve_btn = st.button("▶ Solve", use_container_width=True)
    show_visited = st.checkbox("Show visited cells", value=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem; color: #444; line-height: 1.8;'>
    ALGORITHM<br>
    <span style='color:#666'>A* · Manhattan distance</span><br><br>
    MAZE GEN<br>
    <span style='color:#666'>Recursive Division</span>
    </div>
    """, unsafe_allow_html=True)

# Session state
if 'maze' not in st.session_state or gen_btn:
    maze, cols, rows = gen_maze(size)
    st.session_state.maze = maze
    st.session_state.cols = cols
    st.session_state.rows = rows
    st.session_state.path = None
    st.session_state.visited = None
    st.session_state.solved = False

maze = st.session_state.maze
cols = st.session_state.cols
rows = st.session_state.rows
start = (1, 1)
goal = (cols - 2, rows - 2)

# Solve
if solve_btn:
    path, visited = astar(maze, start, goal, cols, rows)
    st.session_state.path = path
    st.session_state.visited = visited
    st.session_state.solved = True

# Status
if st.session_state.solved and st.session_state.path:
    st.markdown(f'<div class="status-bar">✓ Path found — {len(st.session_state.path) - 1} steps · {len(st.session_state.visited)} nodes visited</div>', unsafe_allow_html=True)
elif st.session_state.solved and not st.session_state.path:
    st.markdown('<div class="status-bar" style="color:#ff6b6b;border-color:#3a1a1a;background:#1a0f0f;">✗ No path found</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-bar" style="color:#555;border-color:#1a1a1a;background:#111;">Ready — hit Solve</div>', unsafe_allow_html=True)

# Metrics
m1, m2, m3, m4 = st.columns(4)
path_len = len(st.session_state.path) - 1 if st.session_state.path else "—"
visited_count = len(st.session_state.visited) if st.session_state.visited else "—"
total_open = sum(1 for r in range(rows) for c in range(cols) if maze[r][c] == 0)

with m1:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Path Length</div><div class="metric-value">{path_len}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Nodes Visited</div><div class="metric-value">{visited_count}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Open Cells</div><div class="metric-value">{total_open}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Grid Size</div><div class="metric-value">{cols}×{rows}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Draw
visited_to_show = st.session_state.visited if show_visited else None
fig = draw_maze(maze, cols, rows,
                path=st.session_state.path,
                visited=visited_to_show,
                start=start, goal=goal)
st.pyplot(fig)
plt.close(fig)
