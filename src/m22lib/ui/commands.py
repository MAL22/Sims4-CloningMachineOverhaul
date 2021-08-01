import sims4
from m22lib.ui.input_dialog import show_rename_sim_dialog
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target


@sims4.commands.Command('m22.test_input_dialog', command_type=sims4.commands.CommandType.Live)
def test_display_input_dialog(opt_sim: OptionalTargetParam = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output('Banana')

    def input_dialog_callback(dialog):
        output('input_dialog_callback')

    try:
        show_rename_sim_dialog(input_dialog_callback, 'title', 'text', 'Jim', 'Pickens')
    except Exception as e:
        output(e)
