'''

'''
from functools import wraps


def injector(target_object, target_function_name):

    def inject(target_function, new_function):
        @wraps(target_function)
        def _inject(*args, **kwargs):
            return new_function(target_function, *args, **kwargs)
        return _inject

    def _inject_to(new_function):
        target_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, inject(target_function, new_function))
        return new_function
    return _inject_to
