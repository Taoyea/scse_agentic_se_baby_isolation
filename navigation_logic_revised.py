"""
navigation_logic_revised.py
===========================
Revised navigation logic based on code review (see review_notes.md).

Changes from the AI-generated original (generated/navigation_logic.py):
1. When no goal-direction signal is present (all goal_* flags False), the
   robot stops instead of wandering in an arbitrary safe direction. This is
   the safer default when goal information is unavailable.
2. Explicit boolean coercion for all inputs (defensive input validation).
3. Full docstring and type annotations.
4. Core safety and goal-preference logic is unchanged — the original was
   already correct on those dimensions.
"""


def choose_action(
    blocked_front: bool,
    blocked_left: bool,
    blocked_right: bool,
    goal_front: bool,
    goal_left: bool,
    goal_right: bool,
) -> str:
    """Decide the robot's next action based on sensor and goal inputs.

    Args:
        blocked_front: True if the path directly ahead is blocked.
        blocked_left:  True if the path to the left is blocked.
        blocked_right: True if the path to the right is blocked.
        goal_front:    True if the goal lies ahead.
        goal_left:     True if the goal lies to the left.
        goal_right:    True if the goal lies to the right.

    Returns:
        One of "FORWARD", "LEFT", "RIGHT", or "STOP".

    Behaviour:
        1. Prefer moving toward the goal whenever that direction is safe.
        2. If no goal direction is safe but goal information is available,
           pick any safe direction (priority: front > left > right).
        3. If no goal information is available at all, stop (safer default).
        4. If no safe direction exists, stop.
    """
    # Defensive input normalisation
    blocked_front = bool(blocked_front)
    blocked_left = bool(blocked_left)
    blocked_right = bool(blocked_right)
    goal_front = bool(goal_front)
    goal_left = bool(goal_left)
    goal_right = bool(goal_right)

    has_goal_signal = goal_front or goal_left or goal_right

    # 1. Prefer moving toward the goal whenever that direction is safe
    if goal_front and not blocked_front:
        return "FORWARD"
    if goal_left and not blocked_left:
        return "LEFT"
    if goal_right and not blocked_right:
        return "RIGHT"

    # 2. If we have goal info but no goal direction is safe, explore any safe direction
    if has_goal_signal:
        if not blocked_front:
            return "FORWARD"
        if not blocked_left:
            return "LEFT"
        if not blocked_right:
            return "RIGHT"

    # 3. No goal signal available, or no safe direction — stop
    return "STOP"
