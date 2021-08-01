import services
import sims4
from cloningmachineoverhaul.enums.cloning_params import SexualPreference, Sex, Genitalia, Fertility, RelationshipBit, VoiceActor
from cloningmachineoverhaul.enums.interactions import EAAffordances, CMOAffordances
from cloningmachineoverhaul.enums.tunings import TuningId
from m22lib.utils.files import M22ConfigFileManager, M22LogFileManager
from m22lib.tunings.tuning_utils import get_tuning
from sims4.resources import get_resource_key, Types

CLONE_SETTINGS_FILENAME = 'cmo_settings'
LOG_FILENAME_PREFIX = 'CloningMachineOverhaul_log'


class CloningSettings:
    def __init__(self, age: int = 0, gender: int = 0, relationship_bit: int = RelationshipBit.SIBLING,
                 sex: int = Sex.AUTOMATIC, genitalia: int = Genitalia.AUTOMATIC, fertility: int = Fertility.AUTOMATIC,
                 sexual_preference: int = SexualPreference.AUTOMATIC, voice_actor: int = VoiceActor,
                 voice_pitch: int = 0, voice_effect: int = 0):

        self.settings_manager = M22ConfigFileManager(CLONE_SETTINGS_FILENAME, log_filename=LOG_FILENAME_PREFIX)
        self._cloning_settings = self.settings_manager.read()
        self._log = M22LogFileManager(LOG_FILENAME_PREFIX, timestamped_filename=False)

        self._age = self._get_setting('age', age)
        self._gender = self._get_setting('gender', gender)
        self._relationship_bit = self._get_setting('relationship_bit', relationship_bit)
        self._sex = self._get_setting('sex', sex)
        self._genitalia = self._get_setting('genitalia', genitalia)
        self._fertility = self._get_setting('fertility', fertility)
        self._sexual_preference = self._get_setting('sexual_preference', sexual_preference)
        self._voice_actor = self._get_setting('voice_actor', voice_actor)
        self._voice_pitch = self._get_setting('voice_pitch', voice_pitch)
        self._voice_effect = self._get_setting('voice_effect', voice_effect)

        self._offspring_genealogy = get_tuning(TuningId.CMO_CLONE_SIM_PICKED_CONTINUATION).outcome._success_actions.basic_extras[1]._tuned_values.set_genealogy
        self._inject_relbits()

    def _set_setting(self, setting: str, value: int):
        self._cloning_settings[setting] = int(value)
        self._log.write('Updated {} to {}'.format(setting, value))
        self.settings_manager.save(self._cloning_settings)

    def _get_setting(self, setting: str, default_value: int = -1) -> int:
        if setting not in self._cloning_settings:
            return default_value
        return self._cloning_settings[setting]

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value >= 0:
            self._age = value
            self._set_setting('age', value)

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        if value >= 0:
            self._gender = value
            self._set_setting('gender', value)

    @property
    def relationship_bit(self):
        return self._relationship_bit

    @relationship_bit.setter
    def relationship_bit(self, value):
        if value >= 0:
            self._relationship_bit = value
            self._set_setting('relationship_bit', value)
            self._inject_relbits()

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, value):
        if value >= 0:
            self._sex = value
            self._set_setting('sex', value)

    @property
    def genitalia(self):
        return self._genitalia

    @genitalia.setter
    def genitalia(self, value):
        if value >= 0:
            self._genitalia = value
            self._set_setting('genitalia', value)

    @property
    def fertility(self):
        return self._fertility

    @fertility.setter
    def fertility(self, value):
        if value >= 0:
            self._fertility = value
            self._set_setting('fertility', value)

    @property
    def sexual_preference(self):
        return self._sexual_preference

    @sexual_preference.setter
    def sexual_preference(self, value):
        if value >= 0:
            self._sexual_preference = value
            self._set_setting('sexual_preference', value)

    @property
    def voice_actor(self):
        return self._voice_actor

    @voice_actor.setter
    def voice_actor(self, value):
        if value >= 0:
            self._voice_actor = value
            self._set_setting('voice_actor', value)

    @property
    def voice_pitch(self):
        return self._voice_pitch

    @voice_pitch.setter
    def voice_pitch(self, value):
        if value >= 0:
            self._voice_pitch = value
            self._set_setting('voice_pitch', value)

    @property
    def voice_effect(self):
        return self._voice_effect

    @voice_effect.setter
    def voice_effect(self, value):
        if value >= 0:
            self._voice_effect = value
            self._set_setting('voice_effect', value)

    def _inject_relbits(self):
        instance_manager = services.get_instance_manager(Types.RELATIONSHIP_BIT)
        family_offspring_rel_bit = instance_manager.get(get_resource_key(RelationshipBit.OFFSPRING, Types.RELATIONSHIP_BIT))
        family_sibling_rel_bit = instance_manager.get(get_resource_key(RelationshipBit.SIBLING, Types.RELATIONSHIP_BIT))
        clone_rel_bit = instance_manager.get(get_resource_key(TuningId.CLONE_RELATIONSHIP_BIT, Types.RELATIONSHIP_BIT))

        affordance_ids = [EAAffordances.CloningMachine.CLONE_SIM_PICKED_CONTINUATION, CMOAffordances.CloningMachine.CLONE_SIM_PICKED_CONTINUATION]

        def inject_to_continuation(tuning, relationship_bits, genealogy=None):
            try:
                new_success_basic_extras = list(tuning.outcome._success_actions.basic_extras)
                new_failure_basic_extras = list(tuning.outcome._failure_actions.basic_extras)

                for index, basic_extra in enumerate(tuning.outcome._success_actions.basic_extras):
                    if hasattr(basic_extra.factory, '_CloneSimInfoSource'):
                        new_tuned_values = tuning.outcome._success_actions.basic_extras[index]._tuned_values.clone_with_overrides(set_genealogy=genealogy, relationship_bits_to_add=tuple(relationship_bits))
                        new_success_basic_extras[index]._tuned_values = new_tuned_values

                for index, basic_extra in enumerate(tuning.outcome._failure_actions.basic_extras):
                    if hasattr(basic_extra.factory, '_CloneSimInfoSource'):
                        new_tuned_values = tuning.outcome._failure_actions.basic_extras[index]._tuned_values.clone_with_overrides(set_genealogy=genealogy, relationship_bits_to_add=tuple(relationship_bits))
                        new_failure_basic_extras[index]._tuned_values = new_tuned_values

                tuning.outcome._success_actions = tuning.outcome._success_actions.clone_with_overrides(basic_extras=tuple(new_success_basic_extras))
                tuning.outcome._failure_actions = tuning.outcome._failure_actions.clone_with_overrides(basic_extras=tuple(new_failure_basic_extras))

                return tuning
            except Exception as e:
                self._log.write(e)

        for id in affordance_ids:
            key = sims4.resources.get_resource_key(id, Types.INTERACTION)
            affordance = services.get_instance_manager(Types.INTERACTION)._tuned_classes.get(key)

            if affordance is not None:
                if self.relationship_bit == RelationshipBit.OFFSPRING:
                    # Put back the tunable from the 'set_genealogy' node to create clones as offsprings.
                    # Replace the sibling relbit with the offspring one.
                    inject_to_continuation(affordance, [family_offspring_rel_bit, clone_rel_bit], genealogy=self._offspring_genealogy)

                elif self.relationship_bit == RelationshipBit.SIBLING:
                    # Remove the tunable from the 'set_genealogy' node to create clones as siblings.
                    # Replace the offspring relbit with the sibling one.
                    inject_to_continuation(affordance, [family_sibling_rel_bit, clone_rel_bit])

                elif self.relationship_bit == RelationshipBit.NONE:
                    # Remove the tunable from the 'set_genealogy' node to create unrelated clones.
                    # Remove the offspring/sibling relbit.
                    inject_to_continuation(affordance, [clone_rel_bit])
