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

from api import create, retrieve, retrieve_one, update, delete, count
import sqlobject as so


def so_create(class_, **kw):
    return class_(**kw)
so_create = create.when('issubclass(class_, so.SQLObject)')(so_create)

def so_retrieve(class_, **kw):
    return list(select_from_kw(class_, **kw))
so_retrieve = retrieve.when('issubclass(class_, so.SQLObject)') \
                (so_retrieve)

def so_retrieve_one(class_, **kw):
    results = so_retrieve(class_, **kw)
    count = len(results)
    if count == 0:
        return None
    elif count == 1:
        return results[0]
    else:
        raise LookupError, 'Received %d results.' % count
so_retrieve_one = retrieve_one.when(
            'issubclass(class_, so.SQLObject)')(so_retrieve_one)

def so_update(obj, **kw):
    obj.set(**kw)
so_update = update.when('isinstance(obj, so.SQLObject)')(so_update)

def so_delete(obj):
    obj.destroySelf()
so_delete = delete.when('isinstance(obj, so.SQLObject)')(so_delete)

def so_count(class_, **kw):
    select = select_from_kw(class_, **kw)
    return select.count()
so_count = count.when('issubclass(class_, so.SQLObject)')(so_count)

def select_from_kw(class_, **kw):
    "Returns a select object for a given set of keywords."
    and_list = []
    for key, value in kw.iteritems():
        query_col = getattr(class_.q, key)
        and_list.append(query_col==kw[key])
    if len(and_list) == 0:
        select = class_.select()
    elif len(and_list) == 1:
        select = class_.select(and_list[0])
    else:
        select = class_.select(so.AND(*and_list))
    return select
