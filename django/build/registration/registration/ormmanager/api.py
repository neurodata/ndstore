# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

import dispatch

def create(class_, **kw):
    "Returns a new class_ object created using the keyword arguments."
    raise NotImplementedError
create = dispatch.generic()(create)

def retrieve(class_, **kw):
    """Returns a list of existing class_ objects using the keyword arguments.
    
    Should return an empty list if there are no matching objects.
    If no keywords are provided, should return all class_ objects."""
    raise NotImplementedError
retrieve = dispatch.generic()(retrieve)

def retrieve_one(class_, **kw):
    """Returns a single class_ object using the keyword arguments.
    
    Should return None if there is no matching object.
    Should raise a LookupError when more than one object
    matches."""
    raise NotImplementedError
retrieve_one = dispatch.generic()(retrieve_one)

def update(obj, **kw):
    "Update an object using the keyword arguments."
    raise NotImplementedError
update = dispatch.generic()(update)

def delete(obj):
    "Remove an object from the database."
    raise NotImplementedError
delete = dispatch.generic()(delete)

def count(class_, **kw):
    "Count the number of objects with the given keyword arguments."
    raise NotImplementedError
count = dispatch.generic()(count)

__all__ = [create, retrieve, retrieve_one, update, delete, count]
