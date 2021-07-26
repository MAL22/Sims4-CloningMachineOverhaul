import traceback
import inspect
import sys
from m22lib.utils.files import M22LogFileManager
from functools import wraps


def error_watcher(default_value=None, error_callback=None, log: M22LogFileManager = None):

    def build_exc_msg(func, exc):
        msg = 'Exception encountered: {}: {}'

        if not inspect.isbuiltin(func):
            method_name = '{}.{}'.format(inspect.getmodule(func).__name__, func.__name__)
            method_signature = inspect.signature(func)
            annotation = method_signature.return_annotation

            method_details = '{} ({}) -> {} :: {}'.format(
                method_name,
                method_signature,
                annotation if annotation != inspect.Signature.empty else None,
                repr(exc)
            )

            msg = msg.format(method_details, exc)
        else:
            msg = msg.format(func, exc)

        return msg

    def _function_watcher_wrapper(func):

        @wraps(func)
        def _internal_wrapper(*args, **kwargs):
            nonlocal log
            if log is None:
                log = M22LogFileManager()
            value = default_value

            try:
                value = func(*args, **kwargs)
            except Exception as exc:
                (_, _, exc_traceback) = sys.exc_info()

                log.write('{}'.format(build_exc_msg(func, exc)))
                if error_callback and callable(error_callback):
                    log.write('{}'.format(error_callback(*args, **kwargs)))
                log.write('Traceback:\n{}'.format(''.join(traceback.format_tb(exc_traceback))))

            finally:
                return value

        return _internal_wrapper

    return _function_watcher_wrapper
