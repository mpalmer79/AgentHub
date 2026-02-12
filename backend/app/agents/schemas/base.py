from typing import Dict, Any, List, Optional


def create_tool_schema(
    name: str,
    description: str,
    properties: Dict[str, Dict[str, Any]],
    required: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Helper to create consistent tool schemas"""
    schema = {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
        }
    }
    if required:
        schema["input_schema"]["required"] = required
    return schema


def string_prop(description: str) -> Dict[str, str]:
    """Create a string property"""
    return {"type": "string", "description": description}


def integer_prop(description: str) -> Dict[str, str]:
    """Create an integer property"""
    return {"type": "integer", "description": description}


def number_prop(description: str) -> Dict[str, str]:
    """Create a number property"""
    return {"type": "number", "description": description}


def boolean_prop(description: str) -> Dict[str, str]:
    """Create a boolean property"""
    return {"type": "boolean", "description": description}


def array_string_prop(description: str) -> Dict[str, Any]:
    """Create an array of strings property"""
    return {"type": "array", "items": {"type": "string"}, "description": description}
