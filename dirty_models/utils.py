import re


def underscore_to_camel(string):
    """
    Converts the underscored string to camel case.
    """
    return re.sub('_([a-z])', lambda x: x.group(1).upper(), string)
