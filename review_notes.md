# Review Notes

Reviewed the navigation logic that Qwen generated (in generated/navigation_logic.py).
Went through it line by line and also ran it in the simulator to see if anything breaks.

## What the code does

The function takes 6 booleans: whether front/left/right are blocked, and whether
the goal is in front/left/right. It checks goal directions first (front, then left,
then right) and moves there if it's not blocked. If none of the goal directions are
safe, it just picks any safe direction in the same order. If everything is blocked,
it stops.

## Does it meet the brief?

- Prefers goal direction when safe? Yes, lines 3-8 check goal_* first.
- Never moves into a blocked direction? Yes, every if has `not blocked_*`.
- Stops when no safe direction? Yes, line 19 returns STOP.
- Uses only FORWARD/LEFT/RIGHT/STOP? Yes.

So the core requirements are all covered. The 64-input truth table test in
simulator.py confirms no collisions ever happen.

## Problems I found

### 1. Wanders when there's no goal info (the main one)

If all three goal_* flags are False — meaning the robot doesn't know where the
goal is — the code still moves. It falls through to lines 11-16 and picks
FORWARD (or LEFT, or RIGHT) just because it's safe.

Tested this: `choose_action(False, False, False, False, False, False)` returns
"FORWARD". That seems wrong. If the robot has no idea where the goal is, it
should probably stop and wait instead of driving around randomly. In a real
robot this could happen if the goal tracker loses signal or something.

Fixed this in navigation_logic_revised.py — added a check so if there's no goal
signal at all, it returns STOP.

### 2. Priority is hard-coded front > left > right

When multiple goal directions are safe at the same time (like if the goal is
diagonally front-right), it always picks front first. The brief doesn't say
what to do here so technically any deterministic choice is fine, but front-first
might not always be the shortest path. Didn't change this since it's not wrong,
just arbitrary.

### 3. No input checking

The function doesn't verify that inputs are actually booleans. If something
passes in None or a string by accident, Python's truthiness would handle it
but maybe not in the way you'd expect. Added bool() coercion in the revised
version. Not a big deal for the simulation though.

### 4. No comments / docstring

The generated code has basically no documentation — just two inline comments.
For a 19-line function it's readable enough, but added a proper docstring in
the revised version.

## What's good about it

- It's actually safe. You can't get it to move into a blocked direction no
  matter what inputs you give it (verified all 64 combinations).
- Simple and easy to follow, no weird state or side effects.
- Goal preference works correctly — always picks a goal direction over a
  non-goal direction when both are safe.
- The STOP fallback works — tested the dead_end environment and it stops
  immediately like it should.

## Revised version

navigation_logic_revised.py fixes issues 1 and 3, and adds a docstring for
issue 4. Issue 2 (priority order) left as-is since the brief allows any
deterministic tie-breaking. Ran test_revised.py to make sure the revised
version still passes all 64 truth-table checks — it does.
