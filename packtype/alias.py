# Copyright 2023-2025, Peter Birch, mailto:peter@intuity.io
# SPDX-License-Identifier: Apache-2.0
#

from collections import defaultdict
from typing import Any



class MetaAlias(type):
    UNIQUE_ID: dict[str, int] = defaultdict(lambda: 0)

    def __call__(self, *args, **kwds):
        return self._PT_ALIAS(*args, **kwds)

    def __getitem__(self, to_alias: Any):
        from .base import Base
        assert issubclass(to_alias, Base), "Can only alias a Packtype type"
        return MetaAlias.get_variant(self, to_alias)

    @staticmethod
    def get_variant(alias: "Alias", to_alias: Any):
        # NOTE: Don't share aliases between creations as this prevents the
        #       parent being distinctly tracked (a problem when they are used as
        #       typedefs on a package)
        uid = MetaAlias.UNIQUE_ID[alias.__name__]
        MetaAlias.UNIQUE_ID[alias.__name__] += 1
        return type(
            alias.__name__ + f"_{to_alias.__name__}_{uid}",
            (alias,),
            {"_PT_ALIAS": to_alias},
        )


class Alias(metaclass=MetaAlias):
    _PT_ALIAS: Any | None = None
