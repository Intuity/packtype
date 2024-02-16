# Copyright 2023, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
from math import ceil, log2

class BitVector:
    """
    Bit vector acts as the storage mechanism that backs Packtype structs, unions,
    and other types allowing for different projections of the same bits to be
    made in an efficient manner.

    :param width: Width of the bit vector
    :param value: Initial value for the bit vector, defaults to 0
    """

    def __init__(self, width: int | None = None, value: int = 0) -> None:
        self.__width = width
        self.__value = value

    @property
    def width(self) -> int:
        """ Return the bit vector width """
        return self.__width

    @property
    def value(self) -> int:
        """ Return the bit vector value """
        return self.__value

    def __int__(self) -> int:
        return self.__value

    @functools.lru_cache()
    def create_window(self, msb: int, lsb: int) -> "BitVectorWindow":
        """
        Create a window into a section of the bit vector that can be used to
        either project a value from a wider range or update a specific part of
        the full bit vector.

        :param msb: MSB of the window
        :param lsb: LSB of the window
        :returns:   A BitVectorWindow matching the request
        """
        assert self.__width is None or msb < self.__width, (
            f"MSB of {msb} exceeds width {self.__width}"
        )
        assert lsb >= 0, f"LSB of {lsb} is not supported"
        return BitVectorWindow(self, msb, lsb)

    def extract(self, msb: int, lsb: int) -> int:
        """
        Extract a specific window of the bit vector.

        :param msb: MSB of the window
        :param lsb: LSB of the window
        :returns:   Value extracted from the window
        """
        return (self.__value >> lsb) & ((1 << (msb - lsb + 1)) - 1)

    def set(self, value: int, msb: int | None = None, lsb: int | None = None) -> None:
        """
        Set the value of a specific window of the bit vector.

        :param value: Value to set
        :param msb:   MSB of the window, defaults to width - 1
        :param lsb:   LSB of the window, defaults to 0
        """
        # Coerce the value to an integer
        value = int(value)
        # If no MSB/LSB provided, overwrite the entire value
        if msb is None and lsb is None:
            self.__value = value
        # Otherwise mask and insert the value
        else:
            # If width is not set, attempt to infer it
            width = self.__width
            if width is None:
                width = int(ceil(log2(max(value, self.__value))))
            # Default LSB/MSB
            lsb = lsb if lsb is not None else 0
            msb = msb if msb is not None else (width - 1)
            # Sanity chedck arguments
            assert msb < width, f"MSB of {msb} exceeds width {width}"
            assert lsb >= 0, f"LSB of {lsb} is not supported"
            # Update value with masking
            mask = ((1 << (msb - lsb + 1)) - 1) << lsb
            inv_mask = ((1 << width) - 1) ^ mask
            self.__value = (self.__value & inv_mask) | ((value << lsb) & mask)


class BitVectorWindow:
    """
    Supports easy access to a specific range of a wider BitVector, allowing the
    value of the range to be read or written.

    :param bitvector: Points at the parent BitVector
    :param msb:       MSB of the window
    :param lsb:       LSB of the window
    """

    def __init__(self, bitvector: BitVector, msb: int, lsb: int) -> None:
        self.__bitvector = bitvector
        self.__msb = msb
        self.__lsb = lsb

    @property
    def msb(self) -> int:
        """ Return the window's MSB """
        return self.__msb

    @property
    def lsb(self) -> int:
        """ Return the window's LSB """
        return self.__lsb

    @property
    def width(self) -> int:
        """ Return the window's width """
        return (self.__msb - self.__lsb) + 1

    def __int__(self) -> int:
        """ Cast the window to an int by extracting the right bit range """
        return self.__bitvector.extract(self.__msb, self.__lsb)

    def create_window(self, msb: int, lsb: int) -> "BitVectorWindow":
        """
        Derive a new window within this one, testing that the requested MSB/LSB
        do not exceed the bounds.

        :param msb: MSB of the new window (relative to this window's LSB)
        :param lsb: LSB of the new window (relative to this window's LSB)
        :returns:   The new window
        """
        assert lsb >= 0, f"LSB of {lsb} is not supported"
        assert msb < self.width, f"MSB of {msb} is not supported"
        return self.__bitvector.create_window(msb+self.__lsb, lsb+self.__lsb)

    def set(self, value: int, msb: int | None = None, lsb: int | None = None) -> None:
        """
        Set the value of a specific sub-window of this bit vector window.

        :param value: Value to set
        :param msb:   MSB of the sub-window, defaults to width - 1
        :param lsb:   LSB of the sub-window, defaults to 0
        """
        msb = (self.width - 1) if msb is None else msb
        lsb = 0 if lsb is None else lsb
        assert lsb >= 0, f"LSB of {lsb} is not supported"
        assert msb < self.width, f"MSB of {msb} is not supported"
        return self.__bitvector.set(value, msb+self.__lsb, lsb+self.__lsb)
