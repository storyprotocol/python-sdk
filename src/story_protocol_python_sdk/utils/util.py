def snake_to_camel(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.

    :param snake_str str: The snake_case string to convert.
    :return str: The camelCase string.
    """
    components = snake_str.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def convert_dict_keys_to_camel_case(snake_dict: dict) -> dict:
    """
    Convert all keys in a dictionary from snake_case to camelCase.

    :param snake_dict dict: The dictionary with snake_case keys.
    :return dict: A new dictionary with camelCase keys.
    """
    return {snake_to_camel(key): value for key, value in snake_dict.items()}
