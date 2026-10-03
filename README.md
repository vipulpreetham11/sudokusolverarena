# Sudoku Solver Arena

An interactive Sudoku solver that visualizes the backtracking algorithm step by step.

## How to Run

1. Clone this repo

git clone https://github.com/YOUR_USERNAME/sudoku-solver-arena.git
cd sudoku-solver-arena


2. Install the required package

pip install streamlit


3. Run the app

streamlit run app.py


4. It will open automatically in your browser at `http://localhost:8501`

## How to Use

1. Type a puzzle into the grid (0 = empty cell), or click **Load Example Puzzle**
2. Click **Validate Entries** to check for rule conflicts
3. Click **Solve with Visualization** to watch the algorithm solve it step by step
4. View the solved grid and stats (steps, backtracks, time taken) once it finishes

## Built With

- Python
- Streamlit
