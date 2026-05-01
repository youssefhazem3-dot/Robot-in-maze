import random

def init_grid(cols, rows):
    return [[1] * cols for _ in range(rows)]

def gen_div(maze, cols, rows):
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            maze[r][c] = 0
    divide(maze, 1, 1, cols - 2, rows - 2)

def divide(maze, x, y, w, h):
    if w < 3 or h < 3:
        return
    horizontal = (h > w) or (w == h and random.random() < 0.5)

    if horizontal:
        wy = y + 1 + (random.randrange((h - 2) // 2 + 1)) * 2
        px = x + random.randrange((w + 1) // 2) * 2
        for c in range(x, x + w):
            maze[wy][c] = 1
        maze[wy][px] = 0
        divide(maze, x, y, w, wy - y)
        divide(maze, x, wy + 1, w, h - (wy - y + 1))
    else:
        wx = x + 1 + (random.randrange((w - 2) // 2 + 1)) * 2
        py = y + random.randrange((h + 1) // 2) * 2
        for r in range(y, y + h):
            maze[r][wx] = 1
        maze[py][wx] = 0
        divide(maze, x, y, wx - x, h)
        divide(maze, wx + 1, y, w - (wx - x + 1), h)

def astar(maze, start, goal, cols, rows):
    import heapq
    h = lambda x, y: abs(x - goal[0]) + abs(y - goal[1])
    g = {start: 0}
    came_from = {}
    open_set = [(h(*start), start)]

    while open_set:
        _, cur = heapq.heappop(open_set)
        if cur == goal:
            path = []
            while cur in came_from:
                path.append(cur)
                cur = came_from[cur]
            path.append(start)
            return path[::-1]

        cx, cy = cur
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 0:
                ng = g[cur] + 1
                if ng < g.get((nx, ny), float('inf')):
                    came_from[(nx, ny)] = cur
                    g[(nx, ny)] = ng
                    heapq.heappush(open_set, (ng + h(nx, ny), (nx, ny)))
    return None  # no path

def print_maze(maze, path=None, start=None, goal=None):
    path_set = set(path) if path else set()
    for r, row in enumerate(maze):
        line = ""
        for c, cell in enumerate(row):
            pos = (c, r)
            if pos == start:      line += "S "
            elif pos == goal:     line += "G "
            elif pos in path_set: line += "· "
            elif cell == 1:       line += "█ "
            else:                 line += "  "
        print(line)

# --- Run ---
COLS, ROWS = 21, 21
maze = init_grid(COLS, ROWS)
gen_div(maze, COLS, ROWS)

start = (1, 1)
goal  = (COLS - 2, ROWS - 2)
path  = astar(maze, start, goal, COLS, ROWS)

print_maze(maze, path, start, goal)
print(f"\nPath length: {len(path) - 1} steps" if path else "\nNo path found.")
