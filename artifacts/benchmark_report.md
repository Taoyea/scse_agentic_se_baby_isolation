# Simulation Benchmark Results

Ran the generated navigation logic through simulator.py. Two types of tests:
(1) all 64 possible input combinations, and (2) five different grid maps.

## Part 1: All 64 input combinations

Since the function takes 6 booleans, there are 2^6 = 64 possible inputs.
Tested every single one.

Results:
- All 64 return a valid action (FORWARD/LEFT/RIGHT/STOP)
- All 64 are safe — never tries to move into a blocked direction
- All 64 respect goal preference — if a goal direction is safe, it picks it

Action breakdown:
- FORWARD: 25 times
- LEFT: 18 times
- RIGHT: 13 times
- STOP: 8 times (only when all three directions are blocked, which makes sense)

No issues here. The logic is solid at the unit level.

## Part 2: Grid environments

Made 5 test maps and let the robot run around in each one.

| Map | What happened | Steps |
|---|---|---|
| open_field | reached goal | 9 |
| corridor | reached goal | 15 |
| dead_end | stopped immediately | 1 |
| maze | reached goal | 18 |
| room_with_obstacles | reached goal | 20 |

4 out of 5 reached the goal. The dead_end one is supposed to fail — the robot
starts boxed in on all three sides, so stopping is the correct behavior.
Counted that as a pass for the safety requirement, not a real failure.

### Maps used

open_field (5x5, goal at opposite corner):
```
S....
.....
.....
.....
....G
```

corridor (L-shaped hallway):
```
#######
#S....#
#####.#
#.....#
#.#####
#G....#
#######
```

dead_end (robot starts surrounded):
```
#######
#.....#
#.###.#
#.#S#.#
#.#.#.#
#...#G#
#######
```

maze (needs multiple turns):
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

room_with_obstacles (open area with scattered walls):
```
.......
.S..#..
....#..
..##...
...#...
..#...G
.......
```

## Thoughts

The generated logic works well for these test cases. The maze and obstacle
room were the trickiest and it still found the goal. One thing I noticed: in
environments where the goal direction isn't immediately obvious (like around
corners), it relies on the fallback "pick any safe direction" behavior, which
happens to work because of the front > left > right priority. It's not smart
exploration, but it gets the job done for these maps.

The main weakness found during review (wandering when no goal signal exists)
doesn't show up in these tests because all the maps have a goal position set,
so the goal_directions() function always returns at least one True. Fixed that
in the revised version anyway.

Raw data saved in simulation_results.json.
