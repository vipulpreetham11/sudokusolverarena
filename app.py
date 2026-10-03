import streamlit as st
import time
import copy

st.set_page_config(page_title="Sudoku Solver Arena", page_icon="🧩", layout="wide")

EXAMPLE_PUZZLE = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    /* ---- force light mode everywhere, regardless of OS/browser theme ---- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    .main, .block-container {
        background-color: #FFFFFF !important;
        color: #1B1B1F !important;
    }
    .block-container {padding-top: 2rem; max-width: 1100px;}

    /* bordered cards (st.container(border=True)) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D7DCE6 !important;
        border-radius: 10px !important;
    }

    h1, h2, h3, p, span, label, div, .stMarkdown, .stCaption {
        color: #1B1B1F !important;
    }
    .section-label {
        font-weight: 700 !important; color: #1E2761 !important; font-size: 0.95rem;
        text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.4rem;
    }

    /* ---- number input cells ---- */
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-testid="stNumberInputStepDown"],
    div[data-testid="stNumberInputStepUp"] { display: none !important; }
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        text-align: center;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E2761 !important;
        padding: 0.45rem 0 !important;
        border: 1px solid #D7DCE6 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stNumberInput"] input:focus {
        border: 1px solid #1E2761 !important;
        box-shadow: 0 0 0 2px rgba(30,39,97,0.15) !important;
    }
    div[data-testid="column"]:nth-child(3n) div[data-testid="stNumberInput"] input {
        border-right: 2.5px solid #1E2761 !important;
    }
    div[data-testid="column"]:nth-child(1) div[data-testid="stNumberInput"] input {
        border-left: 2.5px solid #1E2761 !important;
    }

    .row-divider { height: 2.5px; background: #1E2761; margin: 1px 0; border-radius: 2px; }

    .status-msg {
        padding: 0.6rem 0.9rem; border-radius: 8px; font-size: 0.95rem; font-weight: 600;
    }
    .status-info    { background: #EAF0FB !important; color: #1E2761 !important; }
    .status-success { background: #E8F5E9 !important; color: #1B5E20 !important; }
    .status-error   { background: #FDECEA !important; color: #B3261E !important; }
    .status-warn    { background: #FFF4E5 !important; color: #8A5300 !important; }

    /* ---- live grid table ---- */
    .live-grid { border-collapse: collapse; margin: 0 auto; background: #FFFFFF; }
    .live-grid td {
        width: 34px; height: 34px; text-align: center; vertical-align: middle;
        font-size: 1.05rem; font-weight: 600; color: #1B1B1F !important;
        border: 1px solid #D7DCE6; background: #FFFFFF;
    }
    .live-grid tr:nth-child(3n) td { border-bottom: 2.5px solid #1E2761; }
    .live-grid td:nth-child(3n) { border-right: 2.5px solid #1E2761; }
    .live-grid tr:first-child td { border-top: 2.5px solid #1E2761; }
    .live-grid td:first-child { border-left: 2.5px solid #1E2761; }
    .live-grid td.empty { color: #C6CCD8 !important; }
    .live-grid td.highlight { background: #FFE9A8 !important; color: #7A4B00 !important; }
    .live-grid td.conflict { background: #FDECEA !important; color: #B3261E !important; }

    /* ---- buttons ---- */
    div[data-testid="stButton"] button {
        border-radius: 8px; font-weight: 600; padding: 0.5rem 1rem;
        background-color: #FFFFFF !important; color: #1B1B1F !important;
        border: 1px solid #D7DCE6 !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #1E2761 !important; color: #FFFFFF !important;
        border: 1px solid #1E2761 !important;
    }

    /* ---- sliders ---- */
    div[data-testid="stSlider"] label { color: #1B1B1F !important; }

    /* ---- st.metric stat cards ---- */
    [data-testid="stMetricValue"] { color: #1E2761 !important; }
    [data-testid="stMetricLabel"] { color: #595959 !important; }
</style>
""", unsafe_allow_html=True)
# ============================================================
# CORE LOGIC (unchanged — your algorithm)
# ============================================================

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def is_valid(board, r, c, val):
    for i in range(9):
        if board[r][i] == val or board[i][c] == val:
            return False
    br, bc = 3 * (r // 3), 3 * (c // 3)
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == val:
                return False
    return True

def find_conflicts(board):
    conflicts = set()
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == 0:
                continue
            board[r][c] = 0
            if not is_valid(board, r, c, v):
                conflicts.add((r, c))
            board[r][c] = v
    return conflicts

def solve_with_steps(board, max_steps=60000):
    steps = []
    stats = {"tries": 0, "backtracks": 0}
    board = copy.deepcopy(board)

    def backtrack():
        if len(steps) > max_steps:
            return False
        empty = find_empty(board)
        if not empty:
            steps.append({"action": "solved", "board": copy.deepcopy(board)})
            return True
        r, c = empty
        for val in range(1, 10):
            stats["tries"] += 1
            steps.append({"action": "try", "cell": (r, c), "value": val, "board": copy.deepcopy(board)})
            if is_valid(board, r, c, val):
                board[r][c] = val
                steps.append({"action": "place", "cell": (r, c), "value": val, "board": copy.deepcopy(board)})
                if backtrack():
                    return True
                board[r][c] = 0
                stats["backtracks"] += 1
                steps.append({"action": "backtrack", "cell": (r, c), "value": 0, "board": copy.deepcopy(board)})
        return False

    solved = backtrack()
    return solved, steps, stats

# ============================================================
# UI HELPERS
# ============================================================

def render_live_grid(board, highlight=None, conflicts=None):
    conflicts = conflicts or set()
    html = ['<table class="live-grid">']
    for r in range(9):
        html.append("<tr>")
        for c in range(9):
            v = board[r][c]
            cls = []
            if (r, c) == highlight:
                cls.append("highlight")
            if (r, c) in conflicts:
                cls.append("conflict")
            if v == 0:
                cls.append("empty")
            text = str(v) if v != 0 else "·"
            html.append(f'<td class="{" ".join(cls)}">{text}</td>')
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)

def status_box(text, kind="info"):
    return f'<div class="status-msg status-{kind}">{text}</div>'

# ============================================================
# PAGE HEADER
# ============================================================
st.markdown("### 🧩 Sudoku Solver Arena")
st.caption("Backtracking + Constraint Checking — visualized step by step")
st.write("")

if "grid" not in st.session_state:
    st.session_state.grid = copy.deepcopy(EXAMPLE_PUZZLE)

left, right = st.columns([3, 2], gap="large")

# ---------------- LEFT: INPUT GRID ----------------
with left:
    with st.container(border=True):
        st.markdown('<div class="section-label">Puzzle Input</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Load Example Puzzle", use_container_width=True):
                st.session_state.grid = copy.deepcopy(EXAMPLE_PUZZLE)
                st.rerun()
        with c2:
            if st.button("🗑️ Clear Grid", use_container_width=True):
                st.session_state.grid = [[0]*9 for _ in range(9)]
                st.rerun()

        st.write("")
        grid = st.session_state.grid
        for r in range(9):
            cols = st.columns(9, gap="small")
            for c in range(9):
                val = cols[c].number_input(
                    label=f"r{r}c{c}", min_value=0, max_value=9,
                    value=grid[r][c], key=f"cell_{r}_{c}",
                    label_visibility="collapsed"
                )
                grid[r][c] = val
            if r in (2, 5):
                st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-label">Controls</div>', unsafe_allow_html=True)
        speed = st.slider("Animation speed (sec/step)", 0.0, 0.3, 0.02, 0.01)
        step_sample = st.slider("Show every Nth step (higher = faster)", 1, 50, 5)
        bc1, bc2 = st.columns(2)
        validate_btn = bc1.button("✅ Validate Entries", use_container_width=True)
        solve_btn = bc2.button("▶️ Solve with Visualization", use_container_width=True, type="primary")

# ---------------- RIGHT: LIVE GRID + STATUS ----------------
with right:
    with st.container(border=True):
        st.markdown('<div class="section-label">Live Grid</div>', unsafe_allow_html=True)
        grid_placeholder = st.empty()
        grid_placeholder.markdown(render_live_grid(st.session_state.grid), unsafe_allow_html=True)

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="section-label">Status</div>', unsafe_allow_html=True)
        status_placeholder = st.empty()
        status_placeholder.markdown(status_box("Enter a puzzle, then Validate or Solve.", "info"), unsafe_allow_html=True)

    st.write("")
    stats_placeholder = st.container()

# ============================================================
# ACTIONS
# ============================================================
if validate_btn:
    conflicts = find_conflicts(st.session_state.grid)
    grid_placeholder.markdown(render_live_grid(st.session_state.grid, conflicts=conflicts), unsafe_allow_html=True)
    if conflicts:
        status_placeholder.markdown(status_box(f"⚠️ {len(conflicts)} conflicting cell(s) highlighted in red.", "error"), unsafe_allow_html=True)
    else:
        status_placeholder.markdown(status_box("✅ No conflicts — entries are valid.", "success"), unsafe_allow_html=True)

if solve_btn:
    conflicts = find_conflicts(st.session_state.grid)
    if conflicts:
        status_placeholder.markdown(status_box("⚠️ Fix conflicting entries before solving.", "error"), unsafe_allow_html=True)
    else:
        status_placeholder.markdown(status_box("⏳ Solving…", "info"), unsafe_allow_html=True)
        start = time.time()
        solved, steps, stats = solve_with_steps(st.session_state.grid)
        elapsed = time.time() - start

        for i, step in enumerate(steps):
            if i % step_sample != 0 and step["action"] != "solved":
                continue
            cell = step.get("cell")
            grid_placeholder.markdown(render_live_grid(step["board"], highlight=cell), unsafe_allow_html=True)
            action = step["action"]
            if action == "try":
                status_placeholder.markdown(status_box(f"Trying <b>{step['value']}</b> at row {cell[0]+1}, col {cell[1]+1}", "info"), unsafe_allow_html=True)
            elif action == "place":
                status_placeholder.markdown(status_box(f"✅ Placed <b>{step['value']}</b> at row {cell[0]+1}, col {cell[1]+1}", "success"), unsafe_allow_html=True)
            elif action == "backtrack":
                status_placeholder.markdown(status_box(f"↩️ Backtracking at row {cell[0]+1}, col {cell[1]+1}", "warn"), unsafe_allow_html=True)
            elif action == "solved":
                status_placeholder.markdown(status_box("🎉 Solved!", "success"), unsafe_allow_html=True)
            time.sleep(speed)

        with stats_placeholder:
            st.markdown('<div class="section-label">Run Statistics</div>', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Steps", len(steps))
            m2.metric("Backtracks", stats["backtracks"])
            m3.metric("Time", f"{elapsed:.2f}s")
            m4.metric("Result", "Solved" if solved else "Failed")

        if solved:
            st.session_state.grid = steps[-1]["board"]