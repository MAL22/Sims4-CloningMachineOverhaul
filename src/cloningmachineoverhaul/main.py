import sims4.commands
import services
import sims4.log
import sims4.reload
import zone
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantType
from interactions.context import InteractionContext, QueueInsertStrategy, InteractionBucketType
from interactions.priority import Priority
from sims4.localization import LocalizationHelperTuning
from cloningmachineoverhaul.enums.cloning_params import Sex, RelationshipBit, Fertility, FemaleFertility, MaleFertility, \
    Genitalia, VoiceActor
from cloningmachineoverhaul.enums.strings import Strings
from cloningmachineoverhaul.enums.objects import Objects
from cloningmachineoverhaul.enums.interactions import EAAffordances, CMOAffordances
from cloningmachineoverhaul.settings.settings_cloning import CloningSettings
from m22lib.ui.choices_dialog import display_choices
from m22lib.ui.input_dialog import show_rename_sim_dialog
from m22lib.utils.localization import LocalizedString
from m22lib.tunings.tuning_utils import get_tuning
from m22lib.utils.files import M22LogFileManager
from m22lib.utils.injector import injector
from m22lib.exceptions.exception_watcher import error_watcher
from interactions.utils.creation import SimCreationElement
from sims.aging import aging_element
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_spawner import SimSpawner, SimCreator
from sims.sim_info_types import Age, Gender
from sims4.resources import Types, get_resource_key
from sims4.tuning.instance_manager import InstanceManager
from ui.ui_dialog_picker import ObjectPickerRow, UiObjectPicker

MOD_AUTHOR = 'MAL22'
MOD_NAME = 'Cloning Machine Overhaul'
MOD_VER = '2021.02.23-beta'

CLONE_SETTINGS_FILENAME = 'cmo_settings'
LOG_FILENAME_PREFIX = 'CloningMachineOverhaul_log'

with sims4.reload.protected(globals()):
    # _log = sims4.log.Logger(LOG_FILENAME_PREFIX, default_owner='MAL22')
    _loaded = False
    _log = None
    cloning_settings = None
    dna_sim_info = None


@error_watcher()
def load_config():
    global cloning_settings, _log
    _log = M22LogFileManager(LOG_FILENAME_PREFIX, timestamped_filename=False)

    _log.write('{}\'s {} version {} initializing...'.format(MOD_AUTHOR, MOD_NAME, MOD_VER))

    cloning_settings = CloningSettings()

    _log.write('{}\'s {} version {} initialized'.format(MOD_AUTHOR, MOD_NAME, MOD_VER))


@injector(zone.Zone, 'on_loading_screen_animation_finished')
def on_loading_screen_animation_finished(original, self, *args, **kwargs):
    global _loaded
    try:
        if not _loaded:
            load_config()
            _loaded = True
    except Exception as e:
        _log.write(e)
    finally:
        original(self, *args, **kwargs)


@sims4.commands.Command('cmo.reset', command_type=sims4.commands.CommandType.Live)
def reset_cloning_machine_overhaul(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global _loaded
    _loaded = False
    _log.write('Reset issued to: {}'.format(MOD_NAME))
    load_config()
    output('{} has been reset'.format(MOD_NAME))


@sims4.commands.Command('cmo.dna_sample_picker', command_type=sims4.commands.CommandType.Live)
def cmo_dna_sample_picker(sim_id, object_id, _connection=None, *args):
    output = sims4.commands.CheatOutput(_connection)

    object_inst = services.object_manager().get(int(object_id))
    sim_info = services.sim_info_manager().get(int(sim_id))
    sim_inst = sim_info.get_sim_instance()

    def callback(dialog):
        try:
            global dna_sim_info
            dna_sim_info = None
            _log.write(f'Dialog picked result is {dialog.picked_results[0]}')

            if dialog.picked_results:
                dna_sim_info = inv_objs[dialog.picked_results[0]].get_stored_sim_info()
                context = InteractionContext(sim_inst, InteractionContext.SOURCE_SCRIPT, Priority.High, insert_strategy=QueueInsertStrategy.FIRST, bucket=InteractionBucketType.DEFAULT)
                res = sim_inst.push_super_affordance(get_tuning(CMOAffordances.CloningMachine.CLONE_SIM_PICKED_CONTINUATION), object_inst, context)
                _log.write(f'{res.interaction.get_participants(participant_type=ParticipantType.Actor)}')
                _log.write(f'Creating a clone of {dna_sim_info.first_name} {dna_sim_info.last_name}')
        except Exception as e:
            _log.write(f'callback {e}')

    try:
        picker_dialog = UiObjectPicker.TunableFactory().default(
            sim_info,
            text=None,
            title=LocalizedString(Strings.DnaPickerMenu.DNA_PICKER_DIALOG_TITLE).string,
            picker_type=UiObjectPicker.UiObjectPickerObjectPickerType.OBJECT,
            min_selectable=1,
            max_selectable=1
        )
        inv_objs = [sample for sample in sim_inst.inventory_component if sample.definition.id == Objects.DNA_SAMPLE_OBJECT]
        for index, inv_obj in enumerate(inv_objs):
            stored_sim_info = inv_obj.get_stored_sim_info()

            row = ObjectPickerRow(
                option_id=index, icon=None,
                object_id=inv_obj.id, def_id=inv_obj.definition.id,
                row_description=LocalizationHelperTuning.get_raw_text(f'{stored_sim_info.first_name} {stored_sim_info.last_name}'),
            )
            picker_dialog.add_row(row)

        picker_dialog.add_listener(callback)
        picker_dialog.show_dialog()

    except Exception as e:
        _log.write(f'cmo_dna_sample_picker {e}')


@sims4.commands.Command('cmo.dna_picker_status', command_type=sims4.commands.CommandType.Live)
def cmo_dna_picker_status(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    global dna_sim_info
    try:
        output(f'DNA Sim Info: {dna_sim_info.first_name} {dna_sim_info.last_name}' if dna_sim_info is not None else f'No DNA Sim Info')
    except Exception as e:
        output(f'{e}')


@injector(SimCreationElement._CloneSimInfoSource, 'get_sim_infos_and_positions')
def cmo_get_sim_infos_and_positions(original, self, resolver, household):
    global dna_sim_info
    try:
        _log.write(f'{resolver.affordance}')
        if resolver.affordance == get_tuning(EAAffordances.Spellcasters.SPELLS_SELF_CLONE) or resolver.affordance == get_tuning(EAAffordances.CloningMachine.CLONE_SIM_PICKED_CONTINUATION):
            _log.write(f'ea_get_sim_infos_and_positions')
            return original(self, resolver, household)
        _log.write(f'cmo_get_sim_infos_and_positions')

        use_fgl = False
        clone_sim_info = self._create_clone_sim_info(dna_sim_info, resolver, household)
        if clone_sim_info is None:
            return ()
        (position, location) = (None, None)
        spawning_object = self._get_spawning_object(resolver)
        if spawning_object is not None:
            (position, location) = self._get_position_and_location(spawning_object, resolver)
            use_fgl = self.force_fgl or position is None
        return ((clone_sim_info, position, location, use_fgl),)
    except Exception as e:
        _log.write(f'get_sim_infos_and_positions {e}')
        return ()


@injector(SimCreationElement._GenalogySetAsChild, '__call__')
def __cmo_call__(original, self, actor_sim_info, created_sim_info):
    global dna_sim_info
    _log.write(f'__cmo_call__')
    original(self, actor_sim_info, created_sim_info)


@injector(SimCreationElement, '_do_behavior')
def cmo_do_behavior(original, self):

    if dna_sim_info is None:
        _log.write(f'ea_do_behavior')
        return original(self)
    _log.write(f'cmo_do_behavior')

    resolver = self.interaction.get_resolver()
    target_participant = dna_sim_info
    household = self.household_option(self.interaction)
    client_manager = services.client_manager()
    for (sim_info, position, location, use_fgl) in self.sim_info_source.get_sim_infos_and_positions(resolver, household):
        if target_participant is not None:
            self._apply_relationship_bits(target_participant, sim_info)
        single_sim_resolver = SingleSimResolver(sim_info)
        for loot in self.pre_spawn_loot:
            loot.apply_to_resolver(single_sim_resolver)
        self.sim_info_source.do_pre_spawn_behavior(sim_info, resolver, household)
        SimSpawner.spawn_sim(sim_info, position, spawn_action=self.spawn_action, sim_location=location, use_fgl=use_fgl)
        if self.set_summoning_purpose is not None:
            services.current_zone().venue_service.active_venue.summon_npcs((sim_info,), self.set_summoning_purpose)
        if self.set_genealogy is not None and target_participant is not None:
            self.set_genealogy(target_participant, sim_info)
        self.sim_info_source.do_post_spawn_behavior(sim_info, resolver, client_manager)
    return True


@error_watcher()
@injector(SimCreationElement._CloneSimInfoSource, '_create_clone_sim_info')
def create_clone_sim_info(original, self, source_sim_info, resolver, household):
    global cloning_settings
    global dna_sim_info

    if resolver.affordance == get_tuning(EAAffordances.Spellcasters.SPELLS_SELF_CLONE):
        _log.write(f'ea_create_clone_sim_info')
        return original(self, source_sim_info, resolver, household)
    _log.write(f'cmo_create_clone_sim_info')

    sim_creator = SimCreator(
        gender=source_sim_info.gender,
        age=source_sim_info.age,
        first_name=set_first_name(source_sim_info),
        last_name=source_sim_info._base.last_name,
        traits=source_sim_info.trait_tracker.equipped_traits)
    (sim_info_list, _) = SimSpawner.create_sim_infos(
        (sim_creator,),
        household=household,
        account=source_sim_info.account,
        generate_deterministic_sim=True,
        creation_source='cloning',
        skip_adding_to_household=True)
    clone_sim_info = sim_info_list[0]
    source_sim_proto = source_sim_info.save_sim(for_cloning=True)
    clone_sim_id = clone_sim_info.sim_id
    clone_first_name = clone_sim_info._base.first_name
    clone_last_name = clone_sim_info._base.last_name
    clone_breed_name = clone_sim_info._base.breed_name
    clone_first_name_key = clone_sim_info._base.first_name_key
    clone_last_name_key = clone_sim_info._base.last_name_key
    clone_full_name_key = clone_sim_info._base.full_name_key
    clone_breed_name_key = clone_sim_info._base.breed_name_key
    clone_sim_info.load_sim_info(source_sim_proto, is_clone=True, default_lod=SimInfoLODLevel.FULL)
    clone_sim_info.sim_id = clone_sim_id
    clone_sim_info._base.first_name = clone_first_name
    clone_sim_info._base.last_name = clone_last_name
    clone_sim_info._base.breed_name = clone_breed_name
    clone_sim_info._base.first_name_key = clone_first_name_key
    clone_sim_info._base.last_name_key = clone_last_name_key
    clone_sim_info._base.full_name_key = clone_full_name_key
    clone_sim_info._base.breed_name_key = clone_breed_name_key
    clone_sim_info._household_id = household.id
    if not self._try_add_sim_info_to_household(clone_sim_info, resolver, household, skip_household_check=True):
        return
    source_trait_tracker = source_sim_info.trait_tracker
    clone_trait_tracker = clone_sim_info.trait_tracker
    for trait in clone_trait_tracker.personality_traits:
        if not source_trait_tracker.has_trait(trait):
            clone_sim_info.remove_trait(trait)
    for trait in clone_trait_tracker.gender_option_traits:
        if not source_trait_tracker.has_trait(trait):
            clone_sim_info.remove_trait(trait)
    correct_aspiration_trait = clone_sim_info.primary_aspiration.primary_trait
    for trait in tuple(clone_trait_tracker.aspiration_traits):
        if trait is not correct_aspiration_trait:
            clone_sim_info.remove_trait(trait)
    source_sim_info.relationship_tracker.create_relationship(clone_sim_info.sim_id)
    source_sim_info.relationship_tracker.add_relationship_score(clone_sim_info.sim_id, 1)
    self._ensure_parental_lineage_exists(source_sim_info, clone_sim_info)
    services.sim_info_manager().set_default_genealogy(sim_infos=(clone_sim_info,))

    change_gender(clone_sim_info)
    change_sex(clone_sim_info)
    change_fertility(clone_sim_info)
    change_genitalia(clone_sim_info)
    change_age(clone_sim_info)

    def rename_sim_callback(dialog):
        if dialog.accepted:
            _log.write(clone_sim_info)
            clone_sim_info.first_name = dialog.text_input_responses.get('input_field_0')
            clone_sim_info.last_name = dialog.text_input_responses.get('input_field_1')

    show_rename_sim_dialog(
        rename_sim_callback,
        Strings.SimNameMenu.RENAME_SIM_DIALOG_TITLE,
        Strings.SimNameMenu.RENAME_SIM_DIALOG_DESC,
        SimSpawner.get_random_first_name(cloning_settings.gender, clone_sim_info.species),
        clone_sim_info.last_name,
    )

    clone_sim_info.set_default_data()
    clone_sim_info.save_sim()
    household.save_data()
    if not household.is_active_household:
        clone_sim_info.request_lod(SimInfoLODLevel.BASE)
    clone_sim_info.resend_physical_attributes()
    clone_sim_info.relationship_tracker.clean_and_send_remaining_relationship_info()

    return clone_sim_info


@error_watcher()
@sims4.commands.Command('cmo.gender_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_gender_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('gender_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.gender = 0
        elif result == 1:
            cloning_settings.gender = Gender.MALE
        elif result == 2:
            cloning_settings.gender = Gender.FEMALE

    display_choices([Strings.Gender.AUTOMATIC, Strings.Gender.MALE, Strings.Gender.FEMALE], handle_result, text=LocalizedString(Strings.GenderMenu.GENDER_MENU_DESC, get_gender_text()), title=LocalizedString(Strings.GenderMenu.GENDER_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.relbit_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_relbit_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('relbit_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.relationship_bit = RelationshipBit.SIBLING
        elif result == 1:
            cloning_settings.relationship_bit = RelationshipBit.OFFSPRING
        elif result == 2:
            cloning_settings.relationship_bit = RelationshipBit.NONE

    display_choices([Strings.Relbit.SIBLING, Strings.Relbit.OFFSPRING], handle_result, text=LocalizedString(Strings.RelbitMenu.RELBIT_MENU_DESC, get_relbit_text()), title=LocalizedString(Strings.RelbitMenu.RELBIT_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.age_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_age_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('age_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.age = 0
        elif result == 1:
            cloning_settings.age = Age.TODDLER
        elif result == 2:
            cloning_settings.age = Age.CHILD
        elif result == 3:
            cloning_settings.age = Age.TEEN
        elif result == 4:
            cloning_settings.age = Age.YOUNGADULT
        elif result == 5:
            cloning_settings.age = Age.ADULT
        elif result == 6:
            cloning_settings.age = Age.ELDER

    display_choices([Strings.Age.AUTOMATIC, Strings.Age.TODDLER, Strings.Age.CHILD, Strings.Age.TEEN, Strings.Age.YOUNGADULT, Strings.Age.ADULT, Strings.Age.ELDER], handle_result, text=LocalizedString(Strings.AgeMenu.AGE_MENU_DESC, get_age_text()), title=LocalizedString(Strings.AgeMenu.AGE_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.frame_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_sex_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('sex_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.sex = Sex.AUTOMATIC
        elif result == 1:
            cloning_settings.sex = Sex.MALE
        elif result == 2:
            cloning_settings.sex = Sex.FEMALE

    display_choices([Strings.GenericMenu.AUTOMATIC, Strings.Gender.MALE, Strings.Gender.FEMALE], handle_result, text=LocalizedString(Strings.BodySexMenu.BODY_SEX_MENU_DESC, get_sex_text()), title=LocalizedString(Strings.BodySexMenu.BODY_SEX_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.genitalia_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_genitalia_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('sex_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.sex = Sex.AUTOMATIC
        elif result == 1:
            cloning_settings.sex = Sex.MALE
        elif result == 2:
            cloning_settings.sex = Sex.FEMALE

    display_choices([Strings.GenericMenu.AUTOMATIC, Strings.Gender.MALE, Strings.Gender.FEMALE], handle_result, text=LocalizedString(Strings.GenitaliaMenu.GENITALIA_MENU_DESC, get_sex_text()), title=LocalizedString(Strings.GenitaliaMenu.GENITALIA_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.fertility_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_fertility(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('sex_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.sex = Sex.AUTOMATIC
        elif result == 1:
            cloning_settings.sex = Sex.MALE
        elif result == 2:
            cloning_settings.sex = Sex.FEMALE

    display_choices([Strings.Gender.AUTOMATIC, Strings.Gender.MALE, Strings.Gender.FEMALE], handle_result, text=LocalizedString(Strings.FertilityMenu.FERTILITY_MENU_DESC, get_sex_text()), title=LocalizedString(Strings.FertilityMenu.FERTILITY_MENU_TITLE))


@error_watcher()
@sims4.commands.Command('cmo.voiceactor_menu', command_type=sims4.commands.CommandType.Live)
def show_clone_sex_menu(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    def handle_result(result):
        global cloning_settings
        _log.write('voiceactor_menu {}'.format(result if result is not None else 'Cancelled'))
        if result == 0:
            cloning_settings.voice_actor = VoiceActor.AUTOMATIC
        elif result == 1:
            cloning_settings.voice_actor = VoiceActor.MELODIC
        elif result == 2:
            cloning_settings.voice_actor = VoiceActor.SWEET
        elif result == 3:
            cloning_settings.voice_actor = VoiceActor.LILTED
        elif result == 4:
            cloning_settings.voice_actor = VoiceActor.CLEAR
        elif result == 5:
            cloning_settings.voice_actor = VoiceActor.WARM
        elif result == 6:
            cloning_settings.voice_actor = VoiceActor.BRASH


    display_choices([Strings.GenericMenu.AUTOMATIC, Strings.VoiceTypes.VOICE_MELODIC, Strings.VoiceTypes.VOICE_SWEET, Strings.VoiceTypes.VOICE_LILTED, Strings.VoiceTypes.VOICE_CLEAR, Strings.VoiceTypes.VOICE_WARM, Strings.VoiceTypes.VOICE_BRASH],
                    handle_result, text=LocalizedString(Strings.BodySexMenu.BODY_SEX_MENU_DESC, get_sex_text()), title=LocalizedString(Strings.BodySexMenu.BODY_SEX_MENU_TITLE))


def set_first_name(sim_info):
    global cloning_settings
    if cloning_settings.gender == 0 or cloning_settings.gender == sim_info.gender:
        return sim_info._base.first_name
    return SimSpawner.get_random_first_name(cloning_settings.gender, sim_info.species)


@error_watcher()
def change_age(sim_info):
    global cloning_settings
    if cloning_settings.age == 0:
        # Age of source sim is the same as the selected CMO setting; do nothing.
        return
    sim_info.change_age(cloning_settings.age, sim_info.age)
    clone_sim_age_up = aging_element.AgeUp(sim_info)
    clone_sim_age_up.show_age_up_dialog(True)


@error_watcher()
def change_gender(sim_info):
    global cloning_settings
    if cloning_settings.gender == 0 or sim_info.gender == cloning_settings.gender:
        # Gender is the same as the source sim or the selected CMO setting is AUTOMATIC; do nothing.
        return
    # Change to the opposite gender.
    if sim_info.gender == Gender.MALE:
        sim_info.gender = Gender.FEMALE
    else:
        sim_info.gender = Gender.FEMALE


@error_watcher()
def change_sex(sim_info):
    global cloning_settings
    if cloning_settings.sex == Sex.AUTOMATIC:
        # Body sex will be the same as the source sim; do nothing.
        return
    instance_manager = services.get_instance_manager(Types.TRAIT)
    trait_sex_feminine = instance_manager.get(get_resource_key(Sex.FEMALE, Types.TRAIT))
    trait_sex_masculine = instance_manager.get(get_resource_key(Sex.MALE, Types.TRAIT))
    if (cloning_settings.sex == Sex.MALE and sim_info.trait_tracker.has_trait(trait_sex_masculine)) or (cloning_settings.sex == Sex.FEMALE and sim_info.trait_tracker.has_trait(trait_sex_feminine)):
        # Body sex is already set to the selected CMO setting; do nothing.
        return
    if cloning_settings.sex == Sex.MALE:
        # Change to a masculine frame
        sim_info.remove_trait(trait_sex_feminine)
        sim_info.add_trait(trait_sex_masculine)
    else:
        # Change to a feminine frame
        sim_info.remove_trait(trait_sex_masculine)
        sim_info.add_trait(trait_sex_feminine)


"""def change_clothing_pref(sim_info):
    global cloning_settings
    if cloning_settings.clothing_preference = 
    if sim_info.trait_tracker.has_trait(GlobalGenderPreferenceTuning.MALE_CLOTHING_PREFERENCE_TRAIT):
        sim_info.remove_trait(GlobalGenderPreferenceTuning.MALE_CLOTHING_PREFERENCE_TRAIT)
        sim_info.add_trait(GlobalGenderPreferenceTuning.FEMALE_CLOTHING_PREFERENCE_TRAIT)
    elif sim_info.trait_tracker.has_trait(GlobalGenderPreferenceTuning.FEMALE_CLOTHING_PREFERENCE_TRAIT):
        sim_info.remove_trait(GlobalGenderPreferenceTuning.FEMALE_CLOTHING_PREFERENCE_TRAIT)
        sim_info.add_trait(GlobalGenderPreferenceTuning.MALE_CLOTHING_PREFERENCE_TRAIT)"""


@error_watcher()
def change_fertility(sim_info):
    global cloning_settings
    if cloning_settings.fertility == Fertility.AUTOMATIC:
        # Pregnancy options will be the same as the sim; do nothing.
        return

    # Fetch the tuning instances of the fertility related traits.
    instance_manager = services.get_instance_manager(Types.TRAIT)
    trait_pregnancy_canBeImpregnated = instance_manager.get(get_resource_key(FemaleFertility.CAN_BE_IMPREGNATED, Types.TRAIT))
    trait_pregnancy_cannotBeImpregnated = instance_manager.get(get_resource_key(FemaleFertility.CANNOT_BE_IMPREGNATED, Types.TRAIT))
    trait_pregnancy_canImpregnate = instance_manager.get(get_resource_key(MaleFertility.CAN_IMPREGNATE, Types.TRAIT))
    trait_pregnancy_cannotImpregnate = instance_manager.get(get_resource_key(MaleFertility.CANNOT_IMPREGNATE, Types.TRAIT))

    if cloning_settings.fertility == Fertility.CAN_IMPREGNATE:
        # Remove the ability to become pregnant.
        sim_info.remove_trait(trait_pregnancy_canBeImpregnated)
        sim_info.add_trait(trait_pregnancy_cannotBeImpregnated)
        # Add the ability to impregnate.
        sim_info.remove_trait(trait_pregnancy_cannotImpregnate)
        sim_info.add_trait(trait_pregnancy_canImpregnate)

    elif cloning_settings.fertility == Fertility.CAN_BE_IMPREGNATED:
        # Add the ability to become pregnant.
        sim_info.add_trait(trait_pregnancy_canBeImpregnated)
        sim_info.remove_trait(trait_pregnancy_cannotBeImpregnated)
        # Remove the ability to impregnate.
        sim_info.add_trait(trait_pregnancy_cannotImpregnate)
        sim_info.remove_trait(trait_pregnancy_canImpregnate)

    elif cloning_settings.fertility == Fertility.BOTH:
        # Add the ability to both impregnate and become pregnant.
        sim_info.add_trait(trait_pregnancy_canBeImpregnated)
        sim_info.add_trait(trait_pregnancy_canImpregnate)
        sim_info.remove_trait(trait_pregnancy_cannotBeImpregnated)
        sim_info.remove_trait(trait_pregnancy_cannotImpregnate)

    elif cloning_settings.fertility == Fertility.NEITHER:
        # Remove the ability to both impregnate and become pregnant.
        sim_info.remove_trait(trait_pregnancy_canBeImpregnated)
        sim_info.remove_trait(trait_pregnancy_canImpregnate)
        sim_info.add_trait(trait_pregnancy_cannotBeImpregnated)
        sim_info.add_trait(trait_pregnancy_cannotImpregnate)


@error_watcher()
def change_genitalia(sim_info):
    global cloning_settings
    if cloning_settings.genitalia == Genitalia.AUTOMATIC:
        # Genitalia will be the same as the source sim; do nothing.
        return
    instance_manager = services.get_instance_manager(Types.TRAIT)
    trait_toilet_sitting = instance_manager.get(get_resource_key(Genitalia.FEMALE, Types.TRAIT))
    trait_toilet_standing = instance_manager.get(get_resource_key(Genitalia.MALE, Types.TRAIT))
    if (cloning_settings.genitalia == Genitalia.MALE and sim_info.trait_tracker.has_trait(trait_toilet_standing)) or (cloning_settings.genitalia == Genitalia.FEMALE and sim_info.trait_tracker.has_trait(trait_toilet_sitting)):
        # Genitalia is already set to the selected CMO setting; do nothing.
        return
    if cloning_settings.sex == Sex.MALE:
        # Change to a penis.
        sim_info.remove_trait(trait_toilet_sitting)
        sim_info.add_trait(trait_toilet_standing)
    else:
        # Change to a vulva.
        sim_info.remove_trait(trait_toilet_standing)
        sim_info.add_trait(trait_toilet_sitting)


def get_age_text():
    global cloning_settings
    if cloning_settings.age == 0:
        return Strings.Age.AUTOMATIC
    elif cloning_settings.age == Age.BABY:
        return Strings.Age.BABY
    elif cloning_settings.age == Age.TODDLER:
        return Strings.Age.TODDLER
    elif cloning_settings.age == Age.CHILD:
        return Strings.Age.CHILD
    elif cloning_settings.age == Age.TEEN:
        return Strings.Age.TEEN
    elif cloning_settings.age == Age.YOUNGADULT:
        return Strings.Age.YOUNGADULT
    elif cloning_settings.age == Age.ADULT:
        return Strings.Age.ADULT
    elif cloning_settings.age == Age.ELDER:
        return Strings.Age.ELDER


def get_gender_text():
    global cloning_settings
    if cloning_settings.gender == 0:
        return Strings.Gender.AUTOMATIC
    elif cloning_settings.gender == Gender.MALE:
        return Strings.Gender.MALE
    elif cloning_settings.gender == Gender.FEMALE:
        return Strings.Gender.FEMALE


def get_sex_text():
    global cloning_settings
    _log.write(cloning_settings.sex)
    if cloning_settings.sex == 0:
        return Strings.Gender.AUTOMATIC
    elif cloning_settings.sex == Sex.MALE:
        return Strings.Gender.MALE
    elif cloning_settings.sex == Sex.FEMALE:
        return Strings.Gender.FEMALE


def get_fertility_text():
    global cloning_settings
    _log.write(cloning_settings.fertility)
    if cloning_settings.fertility == Fertility.AUTOMATIC:
        return Strings.FertilityMenu.AUTOMATIC
    elif cloning_settings.fertility == Fertility.BOTH:
        return Strings.FertilityMenu.BOTH
    elif cloning_settings.fertility == Fertility.NEITHER:
        return Strings.FertilityMenu.NEITHER
    elif cloning_settings.fertility == Fertility.CAN_BE_IMPREGNATED:
        return Strings.FertilityMenu.CAN_BE_IMPREGNATED
    elif cloning_settings.fertility == Fertility.CAN_IMPREGNATE:
        return Strings.FertilityMenu.CAN_IMPREGNATE


def get_genitalia_text():
    global cloning_settings
    _log.write(cloning_settings.genitalia)
    if cloning_settings.genitalia == Genitalia.AUTOMATIC:
        return Strings.Gender.AUTOMATIC
    elif cloning_settings.genitalia == Genitalia.MALE:
        return Strings.Gender.MALE
    elif cloning_settings.genitalia == Genitalia.FEMALE:
        return Strings.Gender.FEMALE


def get_relbit_text():
    global cloning_settings
    if cloning_settings.relationship_bit == RelationshipBit.NONE:
        return Strings.Relbit.DEFAULT
    elif cloning_settings.relationship_bit == RelationshipBit.OFFSPRING:
        return Strings.Relbit.OFFSPRING
    elif cloning_settings.relationship_bit == RelationshipBit.SIBLING:
        return Strings.Relbit.SIBLING


def get_voice_actor_text():
    global cloning_settings
    return
