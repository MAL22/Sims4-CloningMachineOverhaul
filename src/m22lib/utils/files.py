import inspect
import sys
import sims4.commands
import os
import sims4.log
import sims4.reload
import pathlib
from datetime import datetime
from server_commands.argument_helpers import get_tunable_instance
from sims4.resources import Types
if not hasattr(sys.modules[__name__], '__file__'):
    __file__ = inspect.getfile(inspect.currentframe())

with sims4.reload.protected(globals()):
    _log = sims4.log.Logger('m22_file_utils', default_owner='MAL22')


def generate_timestamped_filename(prefix: str) -> str:
    return '{}_{}'.format(prefix, generate_timestamp(False, False))


@sims4.commands.Command('m22.dir', command_type=sims4.commands.CommandType.Live)
def cmd_current_directory(_connection=None) -> str:
    output = sims4.commands.CheatOutput(_connection)
    output(str(get_current_directory()))
    output(str(__file__))
    output(os.path.dirname(__file__))


def get_current_directory() -> str:
    split_path = str(__file__).split('\\')
    return os.path.join(split_path[0], os.sep, *split_path[:len(split_path) - 4])


def generate_timestamp(append_brackets: bool = True, include_time: bool = True) -> str:
    if include_time:
        time_format = '%Y-%m-%d %H:%M:%S'
    else:
        time_format = '%Y-%m-%d'

    if not append_brackets:
        return '{}'.format(str(datetime.now().strftime(time_format)))
    return '[{}]'.format(str(datetime.now().strftime(time_format)))


class M22FileManager:
    def __init__(self, filename: str = 'output', file_extension: str = 'log', timestamped_filename: bool = False):
        if timestamped_filename:
            self.partial_filename = generate_timestamped_filename(filename)
        else:
            self.partial_filename = filename
        self.file_extension = '.' + file_extension
        self.full_filename = self.partial_filename + self.file_extension

    def read(self):
        try:
            with open(os.path.join(get_current_directory(), self.full_filename), 'r') as file:
                return file.readlines()
        except IOError as e:
            self.clear()
            return []

    def append(self, line):
        with open(os.path.join(get_current_directory(), self.full_filename), 'a') as file:
            file.write(line + '\n')

    def write(self, line):
        with open(os.path.join(get_current_directory(), self.full_filename), 'w') as file:
            file.write(line + '\n')

    def clear(self):
        open(os.path.join(get_current_directory(), self.full_filename), 'w').close()


class M22TraitsFileManager(M22FileManager):
    def __init__(self, filename: str, file_extension: str = 'cfg', log_filename: str = 'output'):
        super().__init__(filename, file_extension, False)
        self.log = M22LogFileManager(log_filename)

    def read(self):
        lines = super().read()
        traits = []
        for idx, line in enumerate(lines):
            line = line.rstrip()
            if len(line) > 0 and line[0] != '#':
                trait = get_tunable_instance(sims4.resources.Types.TRAIT, line)
                if trait is not None:
                    traits.append(trait)
                else:
                    self.log.write('Line {}: Invalid trait'.format(idx))
        self.log.write('{}: {} trait{} loaded'.format(self.full_filename, len(lines), 's' if len(lines) > 1 else ''))
        return traits


class M22ConfigFileManager(M22FileManager):
    def __init__(self, filename: str, file_extension: str = 'cfg', log_filename: str = 'output'):
        super().__init__(filename, file_extension, False)
        self.log = M22LogFileManager(log_filename, timestamped_filename=False)

    def read(self):
        lines = super().read()
        if lines is None:
            self.log.write('{} is empty or does not exist'.format(self.full_filename))
            return None
        parameters = {}
        for idx, line in enumerate(lines):
            line = line.rstrip()
            if len(line) > 0 and line[0] != '#':
                parameter = line.split('=', 1)
                parameters[parameter[0]] = int(parameter[1])
                self.log.append('\t#{}\tParam: {}\tValue: {}'.format(idx, parameter[0], parameter[1]), False)
        self.log.write('{}: {} parameter{} loaded'.format(self.full_filename, len(parameters), 's' if len(parameters) > 1 else ''))
        return parameters

    def save(self, parameters: dict):
        try:
            super().clear()
            for idx, parameter in enumerate(parameters.items()):
                super().append('{}={}'.format(parameter[0], parameter[1]))
                self.log.append('\t#{}\n\t\tParam: {}\n\t\tValue: {}'.format(idx, parameter[0], parameter[1]), False)
            self.log.write('{}: {} parameter{} saved'.format(self.full_filename, len(parameters), 's' if len(parameters) > 1 else ''))
        except IOError as e:
            self.log.write(e)


class M22LogFileManager(M22FileManager):
    def __init__(self, filename: str = 'output', file_extension: str = 'log', timestamped_filename: bool = False):
        super().__init__(filename, file_extension, timestamped_filename)

    def write(self, line: str, show_timestamp: bool = True):
        try:
            super().append('{} {}'.format(generate_timestamp() if show_timestamp else '', line))
        except IOError as e:
            pass

    def append(self, line: str, show_timestamp: bool = True):
        try:
            super().append('{} {}'.format(generate_timestamp() if show_timestamp else '', line))
        except IOError as e:
            pass
