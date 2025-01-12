"""
prompter.interpreter
==================

A powerful and flexible interpreter system for processing structured text blocks with custom action handlers.

This module provides a complete framework for parsing, interpreting, and executing text blocks containing 
structured commands and actions. It's designed to be extensible through custom action handlers while 
maintaining a consistent block format.

Key Components
-------------
- Interpreter: Main class that combines parsing and evaluation capabilities
- ActionHandler: Base class for implementing custom action handlers
- ActionRegistry: Registry system for managing available handlers
- BlockHelper: Utility class for creating properly formatted blocks

Block Format
-----------
Blocks follow this structure:
```
##TYPE_START param1=value1 param2=value2
content
##TYPE_END
```

Common block types include:
- ACTION: Represents an action to be executed
- RESULT: Contains the result of an action
- INFO: Provides contextual information
- TEST: Used for testing purposes
- CUSTOM: User-defined block types

Basic Usage
----------
```python
from prompter.interpreter import Interpreter, ActionRegistry, ActionHandler

# Create interpreter
interpreter = Interpreter()

# Define custom handler
class MyHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        return f"Processed: {content}"

# Register handler
interpreter.register_handler("my_action", MyHandler())

# Process text
results = interpreter.interpret('''
    ##ACTION_START type=my_action id=action001
    Some content to process
    ##ACTION_END
''')
```

Action Handling
-------------
The system supports:
- Multiple action types through different handlers
- Parameter passing to actions
- Error handling and result formatting
- Action context management
- Unique action IDs to prevent duplicates

Error Handling
------------
The system provides structured error handling:
- Missing handler errors
- Runtime execution errors
- Parameter validation errors
All errors are returned in a standardized block format:

```
##ERROR_START
Error message and details
##ERROR_END
```

Classes
-------
Interpreter
    Main class that orchestrates parsing and evaluation of blocks.

ActionHandler
    Base class for implementing custom action handlers.
    Methods:
        handle(content: str, params: Dict[str, str]) -> str

ActionRegistry
    Registry system for managing action handlers.
    Methods:
        register(action_type: str, handler: ActionHandler)
        get_handler(action_type: str) -> ActionHandler

BlockHelper
    Utility class for creating formatted blocks.
    Methods:
        create_block(block_type: str, content: str, params: Dict)
        create_action(content: str, action_id: str, action_type: str)
        create_result(content: str, action_id: str)

See Also
--------
- prompter.interpreter.parsing : Detailed parsing functionality
- prompter.interpreter.evaluator : Action evaluation system
- prompter.interpreter.helper : Block creation utilities

Notes
-----
- Action IDs must be unique within a single interpretation context
- Handlers should be thread-safe if used in concurrent environments
- Custom block types can be implemented through the handler system
"""
from .interpreter import Interpreter
from .evaluator import ActionHandler, ActionRegistry
from .helper import BlockHelper