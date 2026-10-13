"""
simulator.py
============
Simulation benchmark for the robot navigation logic.

This module:
1. Imports the generated navigation logic (from generated/navigation_logic.py).
2. Exhaustively tests all 2^6 = 64 input combinations (unit-level truth table).
3. Runs the robot in multiple grid-world environments (integration-level).
4. Saves results to artifacts/simulation_results.json and prints a report.

Usage:
    python simulator.py
"""

import importlib.util
import json
import os
import sys
from itertools import product
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
GENERATED_PATH = os.path.join(HERE, "generated", "navigation_logic.py")
RESULTS_PATH = os.path.join(HERE, "artifacts", "simulation_results.json")

# ---------------------------------------------------------------------------
# Load the generated navigation logic dynamically
# ---------------------------------------------------------------------------

def load_navigation_module(path=GENERATED_PATH):
    """Import the generated navigation_logic.py as a module and return it."""
    spec = importlib.util.spec_from_file_location("generated_navigation", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["generated_navigation"] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "choose_action"):
        raise RuntimeError("Generated module does not define choose_action().")
    return module


# ---------------------------------------------------------------------------
# Part 1: Exhaustive truth-table test (all 64 input combinations)
# ---------------------------------------------------------------------------

def run_truth_table(nav_module):
    """Test every combination of the six boolean inputs.

    Returns a list of dicts, one per input combination, with the chosen action
    and a safety flag (True if the action never moves into a blocked direction).
    """
    results = []
    valid_actions = {"FORWARD", "LEFT", "RIGHT", "STOP"}

    for bf, bl, br, gf, gl, gr in product([False, True], repeat=6):
        action = nav_module.choose_action(bf, bl, br, gf, gl, gr)

        # Safety check: the robot must never choose a movement into a blocked direction.
        safe = True
        if action == "FORWARD" and bf:
            safe = False
        elif action == "LEFT" and bl:
            safe = False
        elif action == "RIGHT" and br:
            safe = False

        # Goal-preference check: if a goal direction is safe, the robot should
        # prefer it over a non-goal safe direction.
        goal_safe = (gf and not bf) or (gl and not bl) or (gr and not br)
        action_is_goal = (
            (action == "FORWARD" and gf)
            or (action == "LEFT" and gl)
            or (action == "RIGHT" and gr)
        )
        goal_preferred = (not goal_safe) or action_is_goal or action == "STOP"

        results.append({
            "blocked_front": bf,
            "blocked_left": bl,
            "blocked_right": br,
            "goal_front": gf,
            "goal_left": gl,
            "goal_right": gr,
            "action": action,
            "valid_action": action in valid_actions,
            "safe": safe,
            "goal_preferred": goal_preferred,
        })

    return results


# ---------------------------------------------------------------------------
# Part 2: Grid-world simulation environments
# ---------------------------------------------------------------------------

# Direction vectors: 0=North(up), 1=East(right), 2=South(down), 3=West(left)
DIR_DX = [0, 1, 0, -1]
DIR_DY = [-1, 0, 1, 0]
DIR_NAMES = ["NORTH", "EAST", "SOUTH", "WEST"]


class GridWorld:
    """A simple grid-world simulator for the navigation robot.

    Grid legend:
        '.' = open cell
        '#' = obstacle / wall
        'G' = goal
        'S' = start position (treated as open)
    """

    def __init__(self, grid, start, start_dir=0):
        self.grid = [list(row) for row in grid]
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0
        self.start_x, self.start_y = start
        self.start_dir = start_dir
        self.goal_pos = self._find_goal()

    def _find_goal(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == "G":
                    return (x, y)
        return None

    def is_blocked(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.grid[y][x] == "#"

    def sensor_readings(self, x, y, direction):
        """Return (blocked_front, blocked_left, blocked_right) for the robot."""
        # Front
        fx, fy = x + DIR_DX[direction], y + DIR_DY[direction]
        # Left (rotate -90)
        left_dir = (direction - 1) % 4
        lx, ly = x + DIR_DX[left_dir], y + DIR_DY[left_dir]
        # Right (rotate +90)
        right_dir = (direction + 1) % 4
        rx, ry = x + DIR_DX[right_dir], y + DIR_DY[right_dir]

        return (
            self.is_blocked(fx, fy),
            self.is_blocked(lx, ly),
            self.is_blocked(rx, ry),
        )

    def goal_directions(self, x, y, direction):
        """Return (goal_front, goal_left, goal_right).

        A direction is considered "toward the goal" if moving one step in that
        direction reduces the Manhattan distance to the goal.
        """
        if self.goal_pos is None:
            return (False, False, False)

        gx, gy = self.goal_pos
        current_dist = abs(x - gx) + abs(y - gy)

        def reduces_dist(dx, dy):
            new_dist = abs((x + dx) - gx) + abs((y + dy) - gy)
            return new_dist < current_dist

        front = reduces_dist(DIR_DX[direction], DIR_DY[direction])
        left_dir = (direction - 1) % 4
        left = reduces_dist(DIR_DX[left_dir], DIR_DY[left_dir])
        right_dir = (direction + 1) % 4
        right = reduces_dist(DIR_DX[right_dir], DIR_DY[right_dir])

        return (front, left, right)

    def run(self, nav_module, max_steps=100):
        """Run the navigation logic until goal reached, stuck, or max_steps."""
        x, y = self.start_x, self.start_y
        direction = self.start_dir
        trajectory = [(x, y, direction)]
        actions_taken = []
        status = "unknown"

        for step in range(max_steps):
            # Check if goal reached
            if self.goal_pos and (x, y) == self.goal_pos:
                status = "goal_reached"
                break

            bf, bl, br = self.sensor_readings(x, y, direction)
            gf, gl, gr = self.goal_directions(x, y, direction)

            action = nav_module.choose_action(bf, bl, br, gf, gl, gr)
            actions_taken.append(action)

            if action == "STOP":
                status = "stopped"
                break
            elif action == "FORWARD":
                nx, ny = x + DIR_DX[direction], y + DIR_DY[direction]
                if self.is_blocked(nx, ny):
                    status = "collision"
                    break
                x, y = nx, ny
            elif action == "LEFT":
                direction = (direction - 1) % 4
            elif action == "RIGHT":
                direction = (direction + 1) % 4
            else:
                status = "invalid_action"
                break

            trajectory.append((x, y, direction))

            # Detect loop: if we've been in this exact (x,y,direction) before
            if trajectory.count((x, y, direction)) > 2:
                status = "loop_detected"
                break
        else:
            status = "max_steps_reached"

        return {
            "status": status,
            "steps": len(actions_taken),
            "actions": actions_taken,
            "trajectory_length": len(trajectory),
            "final_position": [x, y],
            "final_direction": DIR_NAMES[direction],
            "goal_reached": status == "goal_reached",
        }


# ---------------------------------------------------------------------------
# Test environments
# ---------------------------------------------------------------------------

ENVIRONMENTS = {
    "open_field": {
        "description": "5x5 open field, goal at opposite corner",
        "grid": [
            "S....",
            ".....",
            ".....",
            ".....",
            "....G",
        ],
        "start": (0, 0),
        "start_dir": 1,  # facing East
    },
    "corridor": {
        "description": "Narrow corridor with a turn",
        "grid": [
            "#######",
            "#S....#",
            "#####.#",
            "#.....#",
            "#.#####",
            "#G....#",
            "#######",
        ],
        "start": (1, 1),
        "start_dir": 1,  # facing East
    },
    "dead_end": {
        "description": "Robot starts in a dead end",
        "grid": [
            "#######",
            "#.....#",
            "#.###.#",
            "#.#S#.#",
            "#.#.#.#",
            "#...#G#",
            "#######",
        ],
        "start": (3, 3),
        "start_dir": 0,  # facing North
    },
    "maze": {
        "description": "Small maze requiring multiple turns",
        "grid": [
            "#########",
            "#S..#...#",
            "#.#.#.#.#",
            "#.#...#.#",
            "#.#####.#",
            "#.......#",
            "#####.#.#",
            "#G....#.#",
            "#########",
        ],
        "start": (1, 1),
        "start_dir": 1,  # facing East
    },
    "room_with_obstacles": {
        "description": "Open room with scattered obstacles",
        "grid": [
            ".......",
            ".S..#..",
            "....#..",
            "..##...",
            "...#...",
            "..#...G",
            ".......",
        ],
        "start": (1, 1),
        "start_dir": 1,  # facing East
    },
}


def run_environments(nav_module):
    """Run the navigation logic in all test environments."""
    results = {}
    for name, env in ENVIRONMENTS.items():
        world = GridWorld(env["grid"], env["start"], env["start_dir"])
        result = world.run(nav_module)
        result["description"] = env["description"]
        results[name] = result
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("ROBOT NAVIGATION - SIMULATION BENCHMARK")
    print("=" * 70)

    nav_module = load_navigation_module()
    print("\nLoaded navigation logic from: %s" % GENERATED_PATH)

    # Part 1: Truth table
    print("\n--- Part 1: Exhaustive Truth Table (64 combinations) ---")
    truth_table = run_truth_table(nav_module)

    total = len(truth_table)
    valid_count = sum(1 for r in truth_table if r["valid_action"])
    safe_count = sum(1 for r in truth_table if r["safe"])
    goal_pref_count = sum(1 for r in truth_table if r["goal_preferred"])

    print("Total combinations tested: %d" % total)
    print("Valid actions:            %d / %d (%.1f%%)" % (valid_count, total, 100 * valid_count / total))
    print("Safety (no collision):    %d / %d (%.1f%%)" % (safe_count, total, 100 * safe_count / total))
    print("Goal preference:          %d / %d (%.1f%%)" % (goal_pref_count, total, 100 * goal_pref_count / total))

    # Show action distribution
    action_counts = {}
    for r in truth_table:
        action_counts[r["action"]] = action_counts.get(r["action"], 0) + 1
    print("\nAction distribution:")
    for action in ["FORWARD", "LEFT", "RIGHT", "STOP"]:
        print("  %-8s: %d" % (action, action_counts.get(action, 0)))

    # Part 2: Grid environments
    print("\n--- Part 2: Grid-World Environments ---")
    env_results = run_environments(nav_module)

    goals_reached = 0
    for name, result in env_results.items():
        marker = "PASS" if result["goal_reached"] else "FAIL"
        print("  [%s] %-22s | status=%-18s steps=%d" % (
            marker, name, result["status"], result["steps"]))
        if result["goal_reached"]:
            goals_reached += 1

    print("\nEnvironments: %d / %d goal reached" % (goals_reached, len(env_results)))

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "navigation_logic_source": "generated/navigation_logic.py",
        "truth_table": {
            "total_combinations": total,
            "valid_actions": valid_count,
            "safe_decisions": safe_count,
            "goal_preferred": goal_pref_count,
            "action_distribution": action_counts,
            "details": truth_table,
        },
        "environments": env_results,
        "summary": {
            "truth_table_safety_rate": round(100 * safe_count / total, 1),
            "truth_table_goal_rate": round(100 * goal_pref_count / total, 1),
            "environments_goal_reached": goals_reached,
            "environments_total": len(env_results),
        },
    }

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("\nResults saved to: %s" % RESULTS_PATH)
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
