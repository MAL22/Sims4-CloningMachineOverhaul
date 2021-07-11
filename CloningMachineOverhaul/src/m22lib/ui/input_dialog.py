import services
from m22lib.utils.files import *
from sims4.localization import LocalizationHelperTuning
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
from sims4.collections import AttributeDict
from ui.ui_text_input import UiTextInput
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory


class M22TextInputLengthName(HasTunableSingletonFactory, AutoFactoryInit):
    __qualname__ = 'M22TextInputLengthName'

    def build_msg(self, dialog, msg, *additional_tokens):
        msg.max_length = 200
        msg.min_length = 1
        msg.input_too_short_tooltip = LocalizationHelperTuning.get_raw_text("Names must contain at least one character!")


def show_rename_sim_dialog(callback_function, title, text, first_name, last_name):
    client = services.client_manager().get_first_client()
    log = M22LogFileManager()

    localized_title = lambda **_: LocalizationHelperTuning.get_raw_text(title)
    localized_text = lambda **_: LocalizationHelperTuning.get_raw_text(text)
    localized_first_name = lambda **_: LocalizationHelperTuning.get_raw_text(first_name)
    localized_last_name = lambda **_: LocalizationHelperTuning.get_raw_text(last_name)

    log.write('Creating a sim rename ui...')

    first_name_input = UiTextInput(sort_order=0, restricted_characters=None, check_profanity=False)
    first_name_input.default_text = lambda **_: LocalizationHelperTuning.get_raw_text('First Name')
    first_name_input.title = lambda **_: LocalizationHelperTuning.get_raw_text('First Name')
    first_name_input.max_length = 100
    first_name_input.initial_value = localized_first_name
    first_name_input.length_restriction = M22TextInputLengthName()

    last_name_input = UiTextInput(sort_order=1, restricted_characters=None, check_profanity=False)
    last_name_input.default_text = lambda **_: LocalizationHelperTuning.get_raw_text('Last Name')
    last_name_input.title = lambda **_: LocalizationHelperTuning.get_raw_text('Last Name')
    last_name_input.max_length = 100
    last_name_input.initial_value = localized_last_name
    last_name_input.length_restriction = M22TextInputLengthName()

    inputs = AttributeDict({'input_field_0': first_name_input, 'input_field_1': last_name_input})

    dialog = UiDialogTextInputOkCancel.TunableFactory().default(
        client.active_sim,
        text=localized_text,
        title=localized_title,
        text_inputs=inputs,
        is_special_dialog=True
    )
    dialog.add_listener(callback_function)
    dialog.show_dialog()
