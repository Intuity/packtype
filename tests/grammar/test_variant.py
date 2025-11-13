# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

import pytest

from packtype.grammar import parse_string
from packtype.grammar.declarations import VariantError
from packtype.grammar.transformer import TransformerError
from packtype.utils import get_width

from ..fixtures import reset_registry

assert reset_registry


def test_parse_variant():
    """Parse package with variants using different configurations"""
    pkg_def = """
    package the_package {
        A : constant = 1

        variants {
            default {
                B : constant = A + 2 // 3
                C : constant = B + 3 // 6
            }
            other {
                B : constant = A + 10 // 11
                C : constant = B + 20 // 31
            }
        }

        type_a_t : scalar[A]

        variants {
            default {
                type_x_t : scalar[B]
            }
            another {
                type_y_t : scalar[C]
            }
        }
    }
    """
    # Default pathway
    pkg_default = next(parse_string(pkg_def))
    assert len(pkg_default._PT_FIELDS) == 5
    assert int(pkg_default.A) == 1
    assert int(pkg_default.B) == 3
    assert int(pkg_default.C) == 6
    assert get_width(pkg_default.type_a_t) == 1
    assert get_width(pkg_default.type_x_t) == 3
    assert not hasattr(pkg_default, "type_y_t")
    # Unused variants (also follows default pathway)
    pkg_default = next(parse_string(pkg_def, variants=["blah", "blergh"]))
    assert len(pkg_default._PT_FIELDS) == 5
    assert int(pkg_default.A) == 1
    assert int(pkg_default.B) == 3
    assert int(pkg_default.C) == 6
    assert get_width(pkg_default.type_a_t) == 1
    assert get_width(pkg_default.type_x_t) == 3
    assert not hasattr(pkg_default, "type_y_t")
    # Enable 'other'
    pkg_default = next(parse_string(pkg_def, variants=["X", "Y", "other"]))
    assert len(pkg_default._PT_FIELDS) == 5
    assert int(pkg_default.A) == 1
    assert int(pkg_default.B) == 11
    assert int(pkg_default.C) == 31
    assert get_width(pkg_default.type_a_t) == 1
    assert get_width(pkg_default.type_x_t) == 11
    assert not hasattr(pkg_default, "type_y_t")
    # Enable 'other' and 'another'
    pkg_default = next(parse_string(pkg_def, variants=["X", "Y", "other", "another"]))
    assert len(pkg_default._PT_FIELDS) == 5
    assert int(pkg_default.A) == 1
    assert int(pkg_default.B) == 11
    assert int(pkg_default.C) == 31
    assert get_width(pkg_default.type_a_t) == 1
    assert not hasattr(pkg_default, "type_x_t")
    assert get_width(pkg_default.type_y_t) == 31


def test_parse_variant_missing_default():
    """Check an error is raised when a variant can't be resolved"""
    pkg_def = """
    package the_package {
        variants {
            some_cond {
                A : constant = 123
            }
        }
    }
    """
    with pytest.raises(TransformerError) as excinfo:
        next(parse_string(pkg_def))
    assert "Variant at N/A:3 is missing a default case." in str(excinfo.value)


def test_parse_variant_multiple_default():
    """Check an error is raised when multiple variants are marked as default"""
    pkg_def = """
    package the_package {
        variants {
            default {
                A : constant = 123
            }
            default {
                B : constant = 456
            }
            other {
                C : constant = 789
            }
        }
    }
    """
    with pytest.raises(VariantError) as excinfo:
        next(parse_string(pkg_def))
    assert "Multiple default variants defined" in str(excinfo.value)


def test_parse_variant_complex_condition():
    """Check that condition parsing works as expected"""
    pkg_def = """
    package the_package {
        variants {
            a and b {
                A : constant = 1
            }
            default {}
        }
        variants {
            c and d {
                B : constant = 2
            }
            default {}
        }
        variants {
            a or b {
                C : constant = 3
            }
            default {}
        }
        variants {
            c or d {
                D : constant = 4
            }
            default {}
        }
        variants {
            a and b or c and d {
                E : constant = 5
            }
            default {}
        }
        variants {
            a or b and c or d {
                F : constant = 6
            }
            default {}
        }
    }
    """
    # With nothing defined, we should not see anything
    pkg = next(parse_string(pkg_def))
    for field in ("A", "B", "C", "D", "E", "F"):
        assert not hasattr(pkg, field)
    # With a and c we should get C, D, F
    pkg = next(parse_string(pkg_def, variants=["a", "c"]))
    for field in ("C", "D", "F"):
        assert hasattr(pkg, field)
    for field in ("A", "B", "E"):
        assert not hasattr(pkg, field)
    # With b and d we should get C, D, F
    pkg = next(parse_string(pkg_def, variants=["b", "d"]))
    for field in ("C", "D", "F"):
        assert hasattr(pkg, field)
    for field in ("A", "B", "E"):
        assert not hasattr(pkg, field)
    # With a and b we should get A, C, E, F
    pkg = next(parse_string(pkg_def, variants=["a", "b"]))
    for field in ("A", "C", "E", "F"):
        assert hasattr(pkg, field)
    for field in ("B", "D"):
        assert not hasattr(pkg, field)
    # With c and d we should get B, D, E, F
    pkg = next(parse_string(pkg_def, variants=["c", "d"]))
    for field in ("B", "D", "E", "F"):
        assert hasattr(pkg, field)
    for field in ("A", "C"):
        assert not hasattr(pkg, field)
    # With b and d we should get C, D, F
    pkg = next(parse_string(pkg_def, variants=["b", "d"]))
    for field in ("C", "D", "F"):
        assert hasattr(pkg, field)
    for field in ("A", "B", "E"):
        assert not hasattr(pkg, field)


def test_parse_variant_first_match():
    """Check that only the first matching variant is taken"""
    pkg_def = """
    package the_package {
        variants {
            default {
                X : constant = 1
            }
            a {
                A : constant = 2
            }
            b {
                B : constant = 3
            }
        }
    }
    """
    # With nothing defined, we should only see X
    pkg = next(parse_string(pkg_def))
    assert pkg.X == 1
    for field in ("A", "B"):
        assert not hasattr(pkg, field)
    # With 'a' we should only see A
    pkg = next(parse_string(pkg_def, variants=["a"]))
    assert pkg.A == 2
    for field in ("X", "B"):
        assert not hasattr(pkg, field)
    # With 'a', 'b' we should only see A
    pkg = next(parse_string(pkg_def, variants=["a", "b"]))
    assert pkg.A == 2
    for field in ("X", "B"):
        assert not hasattr(pkg, field)
    # With 'a', 'b' we should only see A (regardless of variant order on CLI)
    pkg = next(parse_string(pkg_def, variants=["b", "a"]))
    assert pkg.A == 2
    for field in ("X", "B"):
        assert not hasattr(pkg, field)
    # With 'b' we should only see B
    pkg = next(parse_string(pkg_def, variants=["b"]))
    assert pkg.B == 3
    for field in ("X", "A"):
        assert not hasattr(pkg, field)
