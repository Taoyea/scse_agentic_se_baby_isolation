"""
test_revised.py
===============
Quick verification that the revised navigation logic passes the same
truth-table safety checks as the original.
"""

import sys
import os
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from navigation_logic_revised import choose_action

VALID_ACTIONS = {"FORWARD", "LEFT", "RIGHT", "STOP"}
failures = []

for bf, bl, br, gf, gl, gr in product([False, True], repeat=6):
    action = choose_action(bf, bl, br, gf, gl, gr)

    if action not in VALID_ACTIONS:
        failures.append(("invalid_action", bf, bl, br, gf, gl, gr, action))

    # Safety: never move into a blocked direction
    if action == "FORWARD" and bf:
        failures.append(("collision_front", bf, bl, br, gf, gl, gr, action))
    if action == "LEFT" and bl:
        failures.append(("collision_left", bf, bl, br, gf, gl, gr, action))
    if action == "RIGHT" and br:
        failures.append(("collision_right", bf, bl, br, gf, gl, gr, action))

    # Goal preference: if a goal direction is safe, should pick it (or stop)
    goal_safe = (gf and not bf) or (gl and not bl) or (gr and not br)
    action_is_goal = (
        (action == "FORWARD" and gf)
        or (action == "LEFT" and gl)
        or (action == "RIGHT" and gr)
    )
    if goal_safe and not action_is_goal and action != "STOP":
        failures.append(("goal_not_preferred", bf, bl, br, gf, gl, gr, action))

    # Revised behaviour: no goal signal -> should STOP
    if not (gf or gl or gr) and action != "STOP":
        failures.append(("no_goal_should_stop", bf, bl, br, gf, gl, gr, action))

if failures:
    print("FAILED: %d issues found" % len(failures))
    for f in failures[:10]:
        print(" ", f)
    sys.exit(1)
else:
    print("PASS: Revised logic passes all 64 truth-table checks")
    print("  - All outputs are valid actions")
    print("  - No collisions (100% safety)")
    print("  - Goal preference respected")
    print("  - No-goal-signal cases correctly return STOP")
