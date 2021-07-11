from sims4.localization import _create_localized_string


class LocalizedString:
    def __init__(self, string, *args):
        self._params = [_create_localized_string(arg) for arg in args]
        self._string = lambda *_, **__: _create_localized_string(string, *self.params)

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        return

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, value):
        return
