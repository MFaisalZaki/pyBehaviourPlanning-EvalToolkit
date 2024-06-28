import os
import json
from collections import defaultdict

def getkeyvalue(data, target_key):
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            result = getkeyvalue(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = getkeyvalue(item, target_key)
            if result is not None:
                return result
    return None

def setkeyvalue(data, target_key, value_to_set):
    """
    Sets the value for a given key within a nested dictionary or list.

    Parameters:
    - data: The nested dictionary or list to search through.
    - target_key: The key for which the value should be set.
    - value_to_set: The value to set for the target key.

    Returns:
    - True if the value was set successfully, False otherwise.
    """
    if isinstance(data, dict):
        if target_key in data:
            data[target_key] = value_to_set
            return True
        for key, value in data.items():
            if setkeyvalue(value, target_key, value_to_set):
                return True
    elif isinstance(data, list):
        for item in data:
            if setkeyvalue(item, target_key, value_to_set):
                return True
    return False
