import datetime
import services
import os
import ui.ui_dialog_service
from m22lib.utils.injector import injector
from m22lib.utils.localization import LocalizedString
from m22lib.utils.files import M22LogFileManager
from sims4.localization import LocalizationHelperTuning, _create_localized_string
from ui.ui_dialog import ButtonType, UiDialog, UiDialogResponse

_log = M22LogFileManager('m22lib', timestamped_filename=False)


class UiDialogChoices(UiDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choice_responses = list()

    def _get_responses_gen(self):
        # yield old values:
        super_results = list(super()._get_responses_gen())
        for result in super_results:
            yield result
        # yield our choices:
        for response in self._choice_responses:
            yield response


shown_choices_dlg = None


@injector(ui.ui_dialog_service.UiDialogService, "dialog_respond")
def display_choices_dialog_respond_hook(original, self, *args, **kwargs):
    try:
        dialog = self._active_dialogs.get(args[0], None)

        global shown_choices_dlg
        if shown_choices_dlg != None:
            dlg = shown_choices_dlg
            shown_choices_dlg = None
            dlg.respond(args[1])
            return True

        # regular handling of other ui:
        result = original(self, *args, **kwargs)
        return result
    except Exception as e:
        _log.write(e)


def display_choices(choices, choice_callback, text: LocalizedString = None, title: LocalizedString = None):
    # create ui:
    client = services.client_manager().get_first_client()

    try:
        dlg = UiDialogChoices.TunableFactory().default(client.active_sim, text=text.string, title=title.string)

        labels = [lambda choice=choice: _create_localized_string(choice) for choice in choices]
        for idx, choice in enumerate(choices):
            dlg._choice_responses.append(UiDialogResponse(dialog_response_id=idx, text=labels[idx], ui_request=UiDialogResponse.UiDialogUiRequest.NO_REQUEST))

        # default cancel choice:
        dlg._choice_responses.append(UiDialogResponse(dialog_response_id=ButtonType.DIALOG_RESPONSE_CANCEL, text=lambda **_: LocalizationHelperTuning.get_raw_text("Cancel"), ui_request=UiDialogResponse.UiDialogUiRequest.NO_REQUEST))
    except Exception as e:
        _log.write(e)

    # response handler calling the choice_callback of the user:
    def choice_response_callback(dialog):
        try:
            if dialog.accepted:
                try:
                    # choice_callback(choices[ui.response - dlg.CHOICES_LOWEST_ID])
                    choice_callback(dialog.response)
                except IndexError:
                    choice_callback(None)
            else:
                choice_callback(None)
        except Exception as e:
            _log.write(e)

    # show ui:
    dlg.add_listener(choice_response_callback)
    # shown_choices_dlg = dlg
    dlg_service = services.ui_dialog_service()
    dlg_service._active_dialogs[dlg.dialog_id] = dlg
    dlg.show_dialog()
