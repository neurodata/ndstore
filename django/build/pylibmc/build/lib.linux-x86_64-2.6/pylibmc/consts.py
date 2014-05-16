# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Constants and functionality related to them"""

import _pylibmc

#: Mapping of exception name => class
errors = tuple(e for (n, e) in _pylibmc.exceptions)
# *Cough* Uhm, not the prettiest of things but this unpacks all exception
# objects and sets them on the package module object currently constructed.
import sys
modpkg = sys.modules[__name__.split(".", 1)[0]]
modself = sys.modules[__name__]
for name, exc in _pylibmc.exceptions:
    setattr(modself, name, exc)
    setattr(modpkg, name, exc)

all_behaviors = _pylibmc.all_behaviors
hashers, hashers_rvs = {}, {}
distributions, distributions_rvs = {}, {}
# Not the prettiest way of doing things, but works well.
for name in dir(_pylibmc):
    if name.startswith("hash_"):
        key, value = name[5:], getattr(_pylibmc, name)
        hashers[key] = value
        hashers_rvs[value] = key
    elif name.startswith("distribution_"):
        key, value = name[13:].replace("_", " "), getattr(_pylibmc, name)
        distributions[key] = value
        distributions_rvs[value] = key

class BehaviorDict(dict):
    def __init__(self, client, *args, **kwds):
        super(BehaviorDict, self).__init__(*args, **kwds)
        self.client = client

    def __setitem__(self, name, value):
        super(BehaviorDict, self).__setitem__(name, value)
        self.client.set_behaviors({name: value})

    def update(self, d):
        super(BehaviorDict, self).update(d)
        self.client.set_behaviors(d.copy())
