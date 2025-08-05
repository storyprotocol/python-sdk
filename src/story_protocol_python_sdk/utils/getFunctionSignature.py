from typing import Any, Dict, List


def get_function_signature(
    abi: List[Dict[str, Any]],
    method_name: str,
) -> str:
    """
    Gets the function signature from an ABI for a given method name.

    Args:
        abi: The contract ABI as a list of dictionaries
        method_name: The name of the method to get the signature for

    Returns:
        The function signature in standard format (e.g. "methodName(uint256,address)")
    """

    # Filter functions by name and type
    functions = [
        item
        for item in abi
        if item.get("type") == "function" and item.get("name") == method_name
    ]

    if len(functions) == 0:
        raise ValueError(f"Method {method_name} not found in ABI.")

    # Get the target function
    func = functions[0]

    def get_type_string(input_param: Dict[str, Any]) -> str:
        """
        Recursively get the type string for a parameter.

        Args:
            input_param: The ABI parameter as a dictionary

        Returns:
            The type string representation
        """
        param_type = input_param["type"]

        if param_type.startswith("tuple"):
            components = input_param.get("components", [])
            if components:
                component_types = ",".join(get_type_string(comp) for comp in components)
                return f"({component_types})"
            else:
                return "()"  # Empty tuple
        return param_type

    # Build the function signature
    inputs = ",".join(
        get_type_string(input_param) for input_param in func.get("inputs", [])
    )
    return f"{method_name}({inputs})"
