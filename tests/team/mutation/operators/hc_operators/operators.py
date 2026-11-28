"""Three mutation operators written for the business rules of the Checks module.

HcStatusSwap   (rule BR3, state change): replaces a status word such as "up" with a wrong status.
HcActionSwap   (rules BR2/BR3, ping kind): replaces a ping kind such as "fail" with another kind.
HcLimitShift   (rule BR1, boundary): moves a limit (60, 31536000, 100, 200, 500) up or down by one.
A test suite that really checks the rules must fail for these mutants.
"""
import ast

import parso
from cosmic_ray.ast import is_number
from cosmic_ray.operators.operator import Example, Operator

STATUS_SWAPS = {
    "new": ["up", "paused"],
    "up": ["down", "new"],
    "down": ["up", "grace"],
    "grace": ["up", "down"],
    "paused": ["up", "new"],
    "started": ["up"],
}
ACTION_SWAPS = {
    "success": ["fail"],
    "fail": ["success", "start"],
    "start": ["fail", "log"],
    "log": ["start"],
    "ign": ["log"],
}
LIMITS = {60, 100, 200, 500, 31536000}


def string_value(node):
    """The text of a plain string node, or None if it is not a simple string."""
    if not isinstance(node, parso.python.tree.String):
        return None
    try:
        value = ast.literal_eval(node.value)
    except (ValueError, SyntaxError):
        return None
    return value if isinstance(value, str) else None


class _WordSwap(Operator):
    """Base class: replace a string literal by one of the words listed for it."""

    SWAPS = {}

    def mutation_positions(self, node):
        value = string_value(node)
        if value in self.SWAPS:
            for _ in self.SWAPS[value]:
                yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        new_word = self.SWAPS[string_value(node)][index]
        return parso.python.tree.String(node.prefix + f'"{new_word}"', node.start_pos)


class HcStatusSwap(_WordSwap):
    """Replace a check status word ("up", "down", "new", "grace", "paused", "started")."""

    SWAPS = STATUS_SWAPS

    @classmethod
    def examples(cls):
        return (
            Example('x = "up"', 'x = "down"'),
            Example('x = "up"', 'x = "new"', occurrence=1),
        )


class HcActionSwap(_WordSwap):
    """Replace a ping kind word ("success", "fail", "start", "log", "ign")."""

    SWAPS = ACTION_SWAPS

    @classmethod
    def examples(cls):
        return (
            Example('x = "fail"', 'x = "success"'),
            Example('x = "fail"', 'x = "start"', occurrence=1),
        )


class HcLimitShift(Operator):
    """Move a business-rule limit by +1 or -1 (the boundary mutants)."""

    OFFSETS = (+1, -1)

    def mutation_positions(self, node):
        if is_number(node) and node.value.isdigit() and int(node.value) in LIMITS:
            for _ in self.OFFSETS:
                yield (node.start_pos, node.end_pos)

    def mutate(self, node, index):
        value = int(node.value) + self.OFFSETS[index]
        return parso.python.tree.Number(node.prefix + str(value), node.start_pos)

    @classmethod
    def examples(cls):
        return (
            Example("x = 60", "x = 61"),
            Example("x = 60", "x = 59", occurrence=1),
        )
