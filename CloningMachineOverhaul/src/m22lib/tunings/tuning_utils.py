from collections import namedtuple
from sims4.collections import _ImmutableSlotsBase, make_immutable_slots_class
from sims4.resources import get_resource_key
from typing import Optional, Type
from server_commands.tuning_commands import get_managers
from sims4.tuning.instances import HashedTunedInstanceMetaclass


def get_tuning(id_: int, exclude_obj: bool = True) -> Optional[HashedTunedInstanceMetaclass]:
    managers = get_managers()
    if exclude_obj:
        managers.pop('objects')
    for label in managers:
        instance_manager = managers.get(label, None)
        key = get_resource_key(id_, instance_manager.TYPE)
        tuning = instance_manager.get(key)
        if tuning:
            return tuning
    return None


"""def load_resource(resource_type: Types, resource_key: int) -> tuple[bool, Any]:
    resource_manger = services.get_instance_manager(resource_type)

    if resource_manger:
        potential_resource = resource_manger.get(resource_key)

        return potential_resource is not None, potential_resource
    else:
        return False, None"""


def namedtuple_to_immutable_slots(tup: namedtuple) -> Type[_ImmutableSlotsBase]:
    """ Converts a named tuple object to an ImmutableSlots object. """
    return make_immutable_slots_class(tup._fields)(tup._asdict())
