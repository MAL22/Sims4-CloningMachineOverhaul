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


class CMOSimInfoTestInjector(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        'tests_interactions': TunableMapping(
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
        return
        try:
            # key = get_resource_key(TuningId.CLONING_MACHINE_OBJECT, Types.OBJECT)
            definition_manager = services.definition_manager()
            sa_list = list(cls.cloning_machine_interactions.values())
            tuning = super(DefinitionManager, definition_manager).get(TuningId.CLONING_MACHINE_OBJECT)

        except Exception as e:
            _log.write(e)


'''    for tuning_id in [TuningId.CLONE_ON_SPAWN_FAILURE, TuningId.CLONE_ON_SPAWN_SUCCESS,
                      TuningId.CLONE_POST_SPAWN_FAILURE, TuningId.CLONE_POST_SPAWN_SUCCESS]:
        key = get_resource_key(tuning_id, Types.INTERACTION)
        tuning = get_instance_manager(Types.INTERACTION)._tuned_classes.get(key)
        if tuning:
            for test in tuning.test_globals:
                if type(test) is SimInfoTest:
                    test.ages = test.ages + [Age.TODDLER]'''


@injector(InstanceManager, 'load_data_into_class_instances')
def cmo_load_data_into_class_instances(original, self, *args, **kwargs) -> None:
    original(self)

    for tuning_id in [TuningId.CLONE_ON_SPAWN_FAILURE, TuningId.CLONE_ON_SPAWN_SUCCESS,
                      TuningId.CLONE_POST_SPAWN_FAILURE, TuningId.CLONE_POST_SPAWN_SUCCESS]:
        key = get_resource_key(tuning_id, Types.INTERACTION)
        tuning = get_instance_manager(Types.INTERACTION)._tuned_classes.get(key)
        if tuning:
            for test in tuning.test_globals:
                if type(test) is SimInfoTest:
                    test.ages = test.ages + [Age.TODDLER]
