from __future__ import annotations

import unittest

from mypy.meet import is_overlapping_types
from mypy.state import state
from mypy.test.typefixture import TypeFixture
from mypy.types import (
    AnyType,
    LiteralType,
    NoneType,
    TupleType,
    TypeOfAny,
    TypeType,
    UnionType,
)


class MeetBranchCoverageTests(unittest.TestCase):
    def test_is_overlapping_types_union_left_non_strict(self) -> None:
        """Exercise branch where left is a Union and strict_optional is disabled (id 7)."""
        left = UnionType.make_union(
            [
                NoneType(),
                AnyType(TypeOfAny.unannotated),
            ]
        )
        right = AnyType(TypeOfAny.unannotated)

        original_strict = state.strict_optional
        state.strict_optional = False
        try:
            result = is_overlapping_types(left, right)
            self.assertIs(result, True)
        finally:
            state.strict_optional = original_strict

    def test_is_overlapping_types_type_type(self) -> None:
        """Exercise TypeType vs TypeType branch (id 27). Type[Any] vs Type[Any] overlaps."""
        any_type = AnyType(TypeOfAny.unannotated)
        left = TypeType.make_normalized(any_type)
        right = TypeType.make_normalized(any_type)

        result = is_overlapping_types(left, right)
        self.assertIs(result, True)

    def test_is_overlapping_types_tuple_vs_tuple(self) -> None:
        """Exercise tuple vs tuple branch (id 24). Two tuple types with overlapping elements overlap."""
        fx = TypeFixture()
        left = TupleType([fx.anyt, fx.anyt], fx.std_tuple)
        right = TupleType([fx.anyt, fx.anyt], fx.std_tuple)

        result = is_overlapping_types(left, right)
        self.assertIs(result, True)

    def test_is_overlapping_types_literal_same_value(self) -> None:
        """Exercise literal vs literal same-value path (ids 38/39). Same literal value overlaps."""
        fx = TypeFixture()
        left = LiteralType(1, fx.a)
        right = LiteralType(1, fx.a)

        result = is_overlapping_types(left, right)
        self.assertIs(result, True)
