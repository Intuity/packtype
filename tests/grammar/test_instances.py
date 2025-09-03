# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#


from packtype.grammar import parse_string

from ..fixtures import reset_registry

assert reset_registry


def test_parse_enum_instance():
    """Parse an instance of an enum within a package"""
    pkg = next(
        parse_string(
            """
            package the_package {
                enum fruit_e {
                    APPLE : constant
                    ORANGE : constant
                    PEAR : constant
                    BANANA : constant
                }

                BEST_FRUIT : fruit_e = fruit_e::APPLE
                WORST_FRUIT : fruit_e = fruit_e::BANANA
            }
            """
        )
    )

    assert isinstance(pkg.BEST_FRUIT, pkg.fruit_e)
    assert pkg.BEST_FRUIT is pkg.fruit_e.APPLE
    assert isinstance(pkg.WORST_FRUIT, pkg.fruit_e)
    assert pkg.WORST_FRUIT is pkg.fruit_e.BANANA


def test_parse_struct_instance():
    """Parse an instance of a struct within a package"""
    pkg = next(
        parse_string(
            """
            package the_package {
                enum month_e {
                    JAN : constant
                    FEB : constant
                    MAR : constant
                    APR : constant
                    MAY : constant
                    JUN : constant
                    JUL : constant
                    AUG : constant
                    SEP : constant
                    OCT : constant
                    NOV : constant
                    DEC : constant
                }

                struct date_t {
                    year : scalar[16]
                    month : month_e
                    day : scalar[5]
                }

                CHRISTMAS : date_t = {
                    year = 2025
                    month = month_e::DEC
                    day = 25
                }

                NEW_YEAR : date_t = {
                    year = 2026
                    month = month_e::JAN
                    day = 1
                }
            }
            """
        )
    )
    assert isinstance(pkg.CHRISTMAS, pkg.date_t)
    assert pkg.CHRISTMAS.year == 2025
    assert pkg.CHRISTMAS.month == pkg.month_e.DEC
    assert pkg.CHRISTMAS.day == 25
    assert isinstance(pkg.NEW_YEAR, pkg.date_t)
    assert pkg.NEW_YEAR.year == 2026
    assert pkg.NEW_YEAR.month == pkg.month_e.JAN
    assert pkg.NEW_YEAR.day == 1
