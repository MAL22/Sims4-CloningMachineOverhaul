from datetime import datetime
import inspect
import os

import services
from cloningmachineoverhaul.enums.tunings import TuningId
from m22lib.exceptions.exception_watcher import error_watcher
from m22lib.tunings.tuning_utils import get_tuning
from m22lib.utils.files import M22LogFileManager
from m22lib.utils.injector import injector
from sims.sim_info_tests import SimInfoTest
from sims.sim_info_types import Age
from sims4.resources import Types, get_resource_key
from sims4.tuning.instance_manager import InstanceManager
from services import get_instance_manager
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableMapping, Tunable, HasTunableReference
from objects.definition_manager import DefinitionManager


_log = M22LogFileManager()


class TunableCloningMachineInteractions(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'cloning_machine_interactions': TunableMapping(
            description='',
            key_type=Tunable(description='', tunable_type=str, default="None"),
            value_type=TunableReference(
                description='',
                manager=get_instance_manager(Types.INTERACTION)
            )
        )
    }


class CloningInteractionsInjector(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'cloning_machine_interactions': TunableMapping(
            description='',
            key_type=Tunable(description='', tunable_type=str, default="None"),
            value_type=TunableReference(
                description='',
                manager=get_instance_manager(Types.INTERACTION)
            )
        )
    }

    @classmethod
    @error_watcher()
    def _tuning_loaded_callback(cls):
        global _log
        try:
            # key = get_resource_key(TuningId.CLONING_MACHINE_OBJECT, Types.OBJECT)
            definition_manager = services.definition_manager()
            sa_list = list(cls.cloning_machine_interactions.values())
            tuning = super(DefinitionManager, definition_manager).get(TuningId.CLONING_MACHINE_OBJECT)

            if tuning and hasattr(tuning, '_super_affordances'):
                tuning._super_affordances += tuple(sa_list)
                _log.write(f"injected {len(sa_list)} super affordance(s)...")
        except Exception as e:
            _log.write(e)


'''@injector(InstanceManager, 'load_data_into_class_instances')
def cmo_load_data_into_class_instances(original, self, *args, **kwargs) -> None:
    original(self)

    key = get_resource_key(TuningId.CLONING_MACHINE_OBJECT, Types.OBJECT)
    obj_tuning = self._tuned_classes.get(key)
    if obj_tuning is not None:
        obj_tuning._super_affordances = obj_tuning._super_affordances + (
            get_tuning(TuningId.CMO_CLONE_AGE),
            get_tuning(TuningId.CMO_CLONE_GENDER),
            get_tuning(TuningId.CMO_CLONE_FRAME),
            get_tuning(TuningId.CMO_CLONE_RELBIT),
            get_tuning(TuningId.CMO_CLONE_SIM_REMOTE_TURN_ON),
            get_tuning(TuningId.CLONE_SIM_PICKED_CONTINUATION),
            get_tuning(TuningId.CMO_SAMPLE_PICKER),
        )

    for tuning_id in [TuningId.CLONE_ON_SPAWN_FAILURE, TuningId.CLONE_ON_SPAWN_SUCCESS,
                      TuningId.CLONE_POST_SPAWN_FAILURE, TuningId.CLONE_POST_SPAWN_SUCCESS]:
        key = get_resource_key(tuning_id, Types.INTERACTION)
        tuning = get_instance_manager(Types.INTERACTION)._tuned_classes.get(key)
        if tuning:
            for test in tuning.test_globals:
                if type(test) is SimInfoTest:
                    test.ages = test.ages + [Age.TODDLER]'''

