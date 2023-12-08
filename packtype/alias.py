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

from .base import Base, MetaBase


class MetaAlias(MetaBase):
    def __call__(self, *args, **kwds):
        return self._PT_ALIAS(*args, **kwds)

    def __getitem__(self, to_alias: Base):
        assert issubclass(to_alias, Base), "Can only alias a Packtype type"
        return MetaAlias.get_variant(self, to_alias)

    @functools.lru_cache
    @staticmethod
    def get_variant(alias: "Alias", to_alias: Base):
        return type(
            alias.__name__ + f"_{to_alias.__name__}", (alias,), {"_PT_ALIAS": to_alias}
        )


class Alias(Base, metaclass=MetaAlias):
    _PT_ALIAS: Base | None = None
