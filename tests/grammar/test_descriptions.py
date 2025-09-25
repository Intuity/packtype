# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from packtype.grammar import parse_string
from tests.fixtures import reset_registry

assert reset_registry


def test_multiline_docstring_package():
    """Test multiline docstring on package declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                This is a multiline docstring
                for the package.

                It can contain multiple lines
                and preserve formatting.
                """
            }
            '''
        )
    )
    assert (
        pkg.__doc__
        == "This is a multiline docstring\nfor the package.\n\n"
        + "It can contain multiple lines\nand preserve formatting."
    )


def test_multiline_docstring_constant():
    """Test multiline docstring on constant declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                MY_CONSTANT: constant = 42
                    """
                    This is a multiline docstring
                    for a constant.

                    It explains what the constant
                    represents and its purpose.
                    """
            }
            '''
        )
    )
    assert (
        pkg.MY_CONSTANT.__doc__
        == "This is a multiline docstring\nfor a constant.\n\n"
        + "It explains what the constant\nrepresents and its purpose."
    )


def test_multiline_docstring_scalar():
    """Test multiline docstring on scalar declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                my_scalar: scalar[8]
                    """
                    A scalar type with multiline
                    documentation.

                    This describes the purpose
                    and usage of the scalar.
                    """
            }
            '''
        )
    )
    assert (
        pkg.my_scalar.__doc__
        == "A scalar type with multiline\ndocumentation.\n\n"
        + "This describes the purpose\nand usage of the scalar."
    )


def test_multiline_docstring_struct():
    """Test multiline docstring on struct declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                struct my_struct {
                    """
                    A struct with multiline
                    documentation.

                    This struct contains multiple
                    fields and has detailed
                    documentation.
                    """
                    field1: scalar[8]
                        """
                        Each field
                        can have a multiline docstring too
                        """
                    field2: scalar[16]
                        """
                        Including this one
                        :)
                        """
                }
            }
            '''
        )
    )
    assert (
        pkg.my_struct.__doc__
        == "A struct with multiline\ndocumentation.\n\n"
        + "This struct contains multiple\nfields and has detailed\ndocumentation."
    )


def test_multiline_docstring_enum():
    """Test multiline docstring on enum declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                enum my_enum {
                    """
                    An enumeration with multiline
                    documentation.

                    This enum defines various
                    states and their meanings.
                    """
                    STATE_A
                    STATE_B
                    STATE_C
                }
            }
            '''
        )
    )
    assert (
        pkg.my_enum.__doc__
        == "An enumeration with multiline\ndocumentation.\n\n"
        + "This enum defines various\nstates and their meanings."
    )


def test_multiline_docstring_union():
    """Test multiline docstring on union declaration"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                This is also
                a multiline docstring
                """
                union my_union {
                    """
                    A union with multiline
                    documentation.

                    This union can hold different
                    types of data structures.
                    """
                    a: scalar[2]
                    b: scalar[2]
                }
            }
            '''
        )
    )
    assert (
        pkg.my_union.__doc__
        == "A union with multiline\ndocumentation.\n\n"
        + "This union can hold different\ntypes of data structures."
    )


def test_multiline_docstring_with_quotes():
    """Test multiline docstring containing quotes"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                This docstring contains "quoted text"
                and 'single quotes' as well.

                It also has "nested quotes" within
                the documentation.
                """
            }
            '''
        )
    )
    assert '"quoted text"' in pkg.__doc__
    assert "'single quotes'" in pkg.__doc__
    assert '"nested quotes"' in pkg.__doc__


def test_multiline_docstring_empty():
    """Test empty multiline docstring"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                """
            }
            '''
        )
    )
    assert pkg.__doc__ == ""


def test_multiline_docstring_single_line():
    """Test multiline docstring with single line content"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                Single line content
                """
            }
            '''
        )
    )
    assert pkg.__doc__ == "Single line content"


def test_multiline_docstring_with_special_characters():
    """Test multiline docstring with special characters and symbols"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                """
                Special characters: @#$%^&*()
                Math symbols: +-*/=<>!
                Brackets: []{}()
                Backslashes: \\ and forward slashes: /
                Inline quotes: ' and "
                """
            }
            '''
        )
    )
    assert "@#$%^&*()" in pkg.__doc__
    assert "+-*/=<>!" in pkg.__doc__
    assert "[]{}()" in pkg.__doc__
    assert "\\" in pkg.__doc__
    assert "/" in pkg.__doc__
    assert "'" in pkg.__doc__
    assert '"' in pkg.__doc__


def test_mixed_docstring_quotes_enum():
    """Test mixing single and triple quote docstrings on enum fields"""
    pkg = next(
        parse_string(
            '''
            package test_pkg {
                enum mixed_quotes_enum {
                    """
                    An enum with mixed quote styles
                    for documentation.
                    """
                    SINGLE_QUOTE
                        "Single line with single quotes"
                    TRIPLE_QUOTE
                        """
                        Multi-line with triple quotes

                        This has multiple lines
                        and formatting.
                        """
                    ANOTHER_SINGLE
                        "Another single line docstring"
                    FINAL_TRIPLE
                        """
                        Final field with triple quotes
                        and special characters: @#$%
                        """
                }
            }
            '''
        )
    )
    assert pkg.mixed_quotes_enum.__doc__ == "An enum with mixed quote styles\nfor documentation."
    assert pkg.mixed_quotes_enum.SINGLE_QUOTE.__doc__ == "Single line with single quotes"
    assert (
        pkg.mixed_quotes_enum.TRIPLE_QUOTE.__doc__
        == "Multi-line with triple quotes\n\nThis has multiple lines\nand formatting."
    )
    assert pkg.mixed_quotes_enum.ANOTHER_SINGLE.__doc__ == "Another single line docstring"
    assert (
        pkg.mixed_quotes_enum.FINAL_TRIPLE.__doc__
        == "Final field with triple quotes\nand special characters: @#$%"
    )
