# 🤖 Robot Maze Solver (A* Visualization)

An interactive maze generator and pathfinding visualizer built with **Streamlit**.
This project demonstrates how the **A* (A-star) search algorithm** explores a maze and finds the shortest path from start to goal.

---

## 🚀 Features

* 🧩 **Random Maze Generation**
  Uses the **Recursive Division algorithm** to generate unique mazes every time.

* 🧠 **A* Pathfinding Algorithm**
  Finds the optimal path using:

  * Cost function: `f(n) = g(n) + h(n)`
  * Heuristic: **Manhattan Distance**

* 🎥 **Step-by-Step Animation**
  Watch the algorithm explore the maze in real time:

  * Visited nodes appear gradually
  * Final path is revealed at the end

* 🤖 **Moving Robot Visualization**
  A robot icon moves cell-by-cell through the maze as the algorithm progresses.

* 📊 **Live Metrics**

  * Path Length
  * Nodes Visited
  * Open Cells
  * Grid Size

* 🎛 **Interactive Controls**

  * Grid size selection
  * Animation speed control
  * Generate new maze
  * Solve maze

---

## 🖼️ How It Works

1. A maze is generated using recursive division.
2. The A* algorithm starts from the top-left corner.
3. It explores nodes based on:

   * Distance traveled so far (`g`)
   * Estimated distance to goal (`h`)
4. The algorithm continues until it reaches the goal.
5. The shortest path is reconstructed and displayed.

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **Matplotlib**
* **NumPy**

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/robot-maze.git
cd robot-maze
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run maze_app.py
```

---

## 📁 Project Structure

```
robot-maze/
│
├── maze_app.py          # Main Streamlit application
├── requirements.txt     # Dependencies
└── README.md
```

---

## ⚙️ Requirements

Example `requirements.txt`:

```
streamlit
matplotlib
numpy
```

---

## 🧠 About A*

A* is a graph traversal and pathfinding algorithm widely used in:

* Robotics 🤖
* Game AI 🎮
* Navigation systems 🗺️

It guarantees the **shortest path** as long as the heuristic is admissible (which Manhattan distance is in grid-based movement).

---

## 🎯 Future Improvements

* ⏸ Pause / Resume animation
* ⏭ Step-by-step manual control
* 🎨 Highlight frontier (open set)
* 🔀 Compare with BFS / DFS
* ⚡ Performance optimizations

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙌 Acknowledgments

Inspired by classic pathfinding visualizations and maze generation algorithms.

---

💡 *Feel free to fork, modify, and experiment with different algorithms!*
