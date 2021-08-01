import services
import traceback
from m22lib.utils.files import *
from m22lib.utils.localization import LocalizedString
from cloningmachineoverhaul.enums.strings import Strings
from sims4.localization import LocalizationHelperTuning, _create_localized_string
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
from sims4.collections import AttributeDict
from ui.ui_text_input import UiTextInput
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory


class M22TextInputLengthName(HasTunableSingletonFactory, AutoFactoryInit):
    __qualname__ = 'M22TextInputLengthName'

    def build_msg(self, dialog, msg, *additional_tokens):
        msg.max_length = 200
        msg.min_length = 1
        msg.input_too_short_tooltip = _create_localized_string(Strings.SimNameMenu.RENAME_SIM_DIALOG_TOOLTIP, msg.min_length, msg.max_length)


class M22TextInputDialogOkCancel:
    def __init__(self, callback_function, title, text):
        return


def show_rename_sim_dialog(callback_function, title_id, desc_id, first_name, last_name):
    try:
        client = services.client_manager().get_first_client()
        log = M22LogFileManager()

        first_name_input = UiTextInput(sort_order=0, restricted_characters=None, check_profanity=False, height=25)
        first_name_input.default_text = lambda **_: LocalizationHelperTuning.get_raw_text(first_name)
        first_name_input.title = LocalizedString(Strings.SimNameMenu.RENAME_SIM_DIALOG_FIRST_NAME_TITLE).string
        first_name_input.max_length = 100
        first_name_input.initial_value = lambda **_: LocalizationHelperTuning.get_raw_text(first_name)
        first_name_input.length_restriction = M22TextInputLengthName()

        last_name_input = UiTextInput(sort_order=1, restricted_characters=None, check_profanity=False, height=25)
        last_name_input.default_text = lambda **_: LocalizationHelperTuning.get_raw_text(last_name)
        last_name_input.title = LocalizedString(Strings.SimNameMenu.RENAME_SIM_DIALOG_LAST_NAME_TITLE).string
        last_name_input.max_length = 100
        last_name_input.initial_value = lambda **_: LocalizationHelperTuning.get_raw_text(last_name)
        last_name_input.length_restriction = M22TextInputLengthName()

        inputs = AttributeDict({'input_field_0': first_name_input, 'input_field_1': last_name_input})

        dlg = UiDialogTextInputOkCancel.TunableFactory().default(
            client.active_sim,
            text=LocalizedString(desc_id).string,
            title=LocalizedString(title_id).string,
            text_inputs=inputs,
            is_special_dialog=True,
        )

        dlg.add_listener(callback_function)
        dlg.show_dialog()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for call in traceback.format_exception(exc_type, exc_value, exc_traceback):
            log.write(call)
