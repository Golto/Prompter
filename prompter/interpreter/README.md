
# Prompter Interpreter

A Python library for parsing and interpreting structured text blocks with custom action handlers. This library provides a robust framework for processing text-based commands, actions, and generating appropriate responses.

## Features

- **Flexible Block Parsing**: Parse structured text blocks with customizable start/end markers
- **Extensible Handler System**: Create custom handlers for different types of actions
- **Built-in Error Handling**: Comprehensive error management with formatted error blocks
- **Context Management**: Track action IDs and prevent duplicates
- **Rich Parameter Support**: Pass parameters to actions through block headers
- **Multiple Block Types**: Support for various block types (ACTION, RESULT, INFO, TEST, etc.)

## Quick Start

### Basic Usage

```python
from prompter.interpreter import Interpreter, ActionHandler
from typing import Dict

# Create a custom handler
class GreetingHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        return f"Hello, {content}!"

# Initialize interpreter
interpreter = Interpreter()
interpreter.register_handler("greet", GreetingHandler())

# Process text with action blocks
text = """
Let's greet someone!
##ACTION_START type=greet id=greeting001
John Doe
##ACTION_END
"""

results = interpreter.interpret(text)
print(results)
# Output:
# ##RESULT_START id=greeting001
# Hello, John Doe!
# ##RESULT_END
```

### Advanced Examples

#### Image Generation Handler

```python
class ImageHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        # Simulate image generation
        image_path = f"images/{params.get('id', 'default')}.png"
        return f"Generated image at {image_path}"

interpreter = Interpreter()
interpreter.register_handler("image", ImageHandler())

text = """
##ACTION_START type=image id=img001
A cat sitting on a windowsill at sunset, digital art style
##ACTION_END
"""

results = interpreter.interpret(text)
```

#### Multiple Handlers and Block Types

```python
# Math operation handler
class MathHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        try:
            result = eval(content)  # Note: eval used for demonstration only
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

# Translation handler
class TranslationHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        target_lang = params.get('lang', 'fr')
        return f"Translated to {target_lang}: {content}"

interpreter = Interpreter()
interpreter.register_handler("math", MathHandler())
interpreter.register_handler("translate", TranslationHandler())

text = """
Let's do some calculations and translations:

##ACTION_START type=math id=calc001
2 + 2 * 3
##ACTION_END

##ACTION_START type=translate id=trans001 lang=es
Hello, world!
##ACTION_END
"""

results = interpreter.interpret(text)
```

## Block Format

Blocks follow this structure:
```
##TYPE_START param1=value1 param2=value2
content
##TYPE_END
```

### Common Block Types

- **ACTION**: Represents an action to be executed
- **RESULT**: Contains the result of an action
- **INFO**: Provides contextual information
- **TEST**: Used for testing purposes
- **CUSTOM**: User-defined block types

### Parameters

Parameters are key-value pairs specified in the block header:
- `id`: Unique identifier for the action (required for ACTION blocks)
- `type`: Action type determining which handler to use
- Custom parameters specific to each handler

## Creating Custom Handlers

```python
from prompter.interpreter import ActionHandler

class CustomHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        # Process content using params
        # Return result as string
        return f"Processed: {content}"

# Register the handler
interpreter = Interpreter()
interpreter.register_handler("custom", CustomHandler())
```

## Error Handling

The system automatically handles and formats errors:

```python
class RiskyHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        raise RuntimeError("Something went wrong")

text = """
##ACTION_START type=risky id=risk001
Dangerous operation
##ACTION_END
"""

# Output will be:
# ##ERROR_START
# Error executing action: Something went wrong
# ##ERROR_END
```

## Context Management

```python
# Clear interpreter context
interpreter.clear_context()

# Access used IDs
print(interpreter.context.used_ids)
```

## BlockHelper Utility

For users looking for a convenient way to create structured blocks, the `BlockHelper` class provides static methods to generate formatted blocks such as `ACTION`, `INFO`, and `RESULT`. These blocks follow the same format used by the interpreter.

### Example Usage

```python
from helper import BlockHelper

# Create an ACTION block
action_block = BlockHelper.create_action(
    content="This is an action block.",
    action_id="example001",
    action_type="greet"
)
print(action_block)
# Output:
# ##ACTION_START id=example001 type=greet
# This is an action block.
# ##ACTION_END

# Create a custom block
custom_block = BlockHelper.create_block(
    block_type="EXAMPLE",
    content="This is an example block.",
    params={"key": "value"}
)
print(custom_block)
# Output:
# ##EXAMPLE_START key=value
# This is an example block.
# ##EXAMPLE_END
```

### Available Methods

- **`create_block(block_type: str, content: str, params: Dict[str, str] = None)`**: Create a generic block.
- **`create_info(content: str)`**: Create an `INFO` block.
- **`create_action(content: str, action_id: str, action_type: str)`**: Create an `ACTION` block.
- **`create_result(content: str, result_id: str)`**: Create a `RESULT` block.

For more details, see the `helper.py` file.