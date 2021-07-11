import sims4
from server_commands.argument_helpers import get_optional_target, OptionalTargetParam


@sims4.commands.Command('cmo.print_voice_info', command_type=sims4.commands.CommandType.Live)
def display_fam_types(opt_sim: OptionalTargetParam = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim = get_optional_target(opt_sim, _connection)
    output('Pitch: {}'.format(str(sim.sim_info._base.voice_pitch)))
    output('Actor: {}'.format(str(sim.sim_info._base.voice_actor)))
    output('Effect: {}'.format(str(sim.sim_info._base.voice_effect)))


@sims4.commands.Command('cmo.display_relbits', command_type=sims4.commands.CommandType.Live)
def display_relbits(opt_sim: OptionalTargetParam = None, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    sim = get_optional_target(opt_sim, _connection)
    output('displaying relationship bits of {} {}:'.format(sim.sim_info.first_name, sim.sim_info.last_name))
    for bit in sim.sim_info.relationship_tracker.get_all_bits():
        output('bit: {}'.format(str(bit)))
