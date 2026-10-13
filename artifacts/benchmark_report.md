# Simulation Benchmark Report

**Generated:** 2026-10-13
**Navigation logic under test:** `generated/navigation_logic.py`
**Test harness:** `simulator.py`

---

## 1. Exhaustive Truth-Table Test (64 combinations)

The navigation function `choose_action(blocked_front, blocked_left, blocked_right, goal_front, goal_left, goal_right)` was tested against all \(2^6 = 64\) possible input combinations.

| Metric | Result |
|---|---|
| Total combinations | 64 |
| Valid action output | 64 / 64 (100.0%) |
| No collision (safety) | 64 / 64 (100.0%) |
| Goal preference respected | 64 / 64 (100.0%) |

### Action distribution

| Action | Count |
|---|---|
| FORWARD | 25 |
| LEFT | 18 |
| RIGHT | 13 |
| STOP | 8 |

### Key observations

- **Safety is guaranteed:** the function never returns a movement command for a direction whose `blocked_*` flag is `True`.
- **Goal preference is guaranteed:** whenever at least one goal direction is safe, the function selects a goal-aligned movement rather than an arbitrary safe direction.
- **STOP is the fallback:** the function returns `STOP` in exactly the 8 combinations where all three directions are blocked.

---

## 2. Grid-World Integration Tests

The robot was placed in five distinct grid environments and allowed to navigate using the generated logic.

| Environment | Description | Result | Steps | Status |
|---|---|---|---|---|
| `open_field` | 5x5 open field, goal at opposite corner | PASS | 9 | goal_reached |
| `corridor` | Narrow corridor with a turn | PASS | 15 | goal_reached |
| `dead_end` | Robot starts in a 3-sided dead end | N/A | 1 | stopped |
| `maze` | Small maze requiring multiple turns | PASS | 18 | goal_reached |
| `room_with_obstacles` | Open room with scattered obstacles | PASS | 20 | goal_reached |

**Summary: 4 / 5 environments reached the goal.**

### Notes on `dead_end`

The `dead_end` environment is **not a failure** — it is a designed safety test. The robot starts surrounded by obstacles on the front, left, and right. The correct behaviour per the brief is to stop, which is exactly what the logic does (`status=stopped` after 1 step). This confirms the safe-stop requirement works in a realistic scenario.

---

## 3. Environment Details

### open_field
```
S....
.....
.....
.....
....G
```
Start: (0,0) facing East. The robot navigates diagonally to (4,4) in 9 steps.

### corridor
```
#######
#S....#
#####.#
#.....#
#.#####
#G....#
#######
```
Start: (1,1) facing East. Requires navigating an L-shaped corridor. Reached goal in 15 steps.

### dead_end
```
#######
#.....#
#.###.#
#.#S#.#
#.#.#.#
#...#G#
#######
```
Start: (3,3) facing North. All three movement directions are blocked. Robot correctly stops immediately.

### maze
```
#########
#S..#...#
#.#.#.#.#
#.#...#.#
#.#####.#
#.......#
#####.#.#
#G....#.#
#########
```
Start: (1,1) facing East. Requires multiple turns and backtracking. Reached goal in 18 steps.

### room_with_obstacles
```
.......
.S..#..
....#..
..##...
...#...
..#...G
.......
```
Start: (1,1) facing East. Navigates around scattered obstacles. Reached goal in 20 steps.

---

## 4. Conclusion

The generated navigation logic passes all exhaustive unit tests (100% safety, 100% goal preference) and successfully navigates 4 out of 5 grid environments. The fifth environment (`dead_end`) correctly triggers the safe-stop behaviour as designed.

**Overall verdict: PASS**

The logic is correct for the requirements specified in `brief.txt`. Potential improvements (explored in `review_notes.md` and the revised logic) include better handling of environments with no goal-direction signal and more sophisticated exploration when no goal direction is immediately available.
