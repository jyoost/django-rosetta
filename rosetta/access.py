from django.conf import settings
from rosetta.conf import settings as rosetta_settings

from django.utils import importlib


def can_translate(user):
    return get_access_control_function()(user)


def get_access_control_function():
    """
    Return a predicate for determining if a user can access the Rosetta views
    """
    fn_path = getattr(settings, 'ROSETTA_ACCESS_CONTROL_FUNCTION', None)
    if fn_path is None:
        return is_superuser_staff_or_in_translators_group
    # Dynamically load a permissions function
    perm_module, perm_func = fn_path.rsplit('.', 1)
    perm_module = importlib.import_module(perm_module)
    return getattr(perm_module, perm_func)


# Default access control test
def is_superuser_staff_or_in_translators_group(user):
    if not getattr(settings, 'ROSETTA_REQUIRES_AUTH', True):
        return True
    if not user.is_authenticated():
        return False
    elif user.is_superuser and user.is_staff:
        return True
    else:
        return user.groups.filter(name='translators').exists()


def can_translate_language(user, langid):
    if not rosetta_settings.ROSETTA_LANGUAGE_GROUPS:
        return can_translate(user)
    elif not user.is_authenticated():
        return False
    elif user.is_superuser and user.is_staff:
        return True
    else:
        return user.groups.filter(name='translators-%s' % langid).exists()
