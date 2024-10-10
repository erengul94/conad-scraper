import argparse
import distutils.util
import os


class EnvArgumentParser(argparse.ArgumentParser):
    """ This class enables usage of environment variables instead of parameters.
    dest or metavar names from add_argument() will be accepted as capital
    environment variables.

    Parameter resolution is done in this order:
    - command line parameter
    - environment variable with capital dest of add_argument()
    - environment variable with capital metavar of add_argument()
    - default value given in add_argument()
    """
    def _add_action(self, action):
        value = None
        if action.dest:
            value = os.environ.get(action.dest.upper())
            if not value and action.metavar:
                value = os.environ.get(action.metavar.upper())
        if value is not None:
            t = action.type
            if not t and action.default is not None:
                t = type(action.default)
            if t == bool:
                if value == '':
                    value = 'False'
                t = distutils.util.strtobool
            if t is None or not t:
                t = str
            if action.option_strings:
                action.required = False
            else:
                action.nargs = '?'
            if value == 'None':
                action.default = None
            elif action.nargs in ('+', '*') or isinstance(action.nargs, int) and action.nargs >= 1:
                action.default = [t(v) for v in value.split(',')]
            else:
                action.default = t(value)

        return super(EnvArgumentParser, self)._add_action(action)

