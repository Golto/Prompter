"""


## Examples

#### Example: ACTION
>>> BlockHelper.create_action("This is a block.", action_id="example001")

```plaintext
##ACTION_START id=example001
This is a block.
##ACTION_END
```

#### Example: custom block
```py
BlockHelper.create_block(
    block_type="EXAMPLE",
    content="This is an example block.",
    params={
        "is_a_test": True
    }
)
```

```plaintext
##EXAMPLE_START is_a_test=True
This is an example block.
##EXAMPLE_END
```
"""


from typing import Dict



class BlockHelper:
    """
    Utility class for creating formatted blocks with specific types and parameters.

    This class provides static methods to generate structured text blocks following a consistent format, 
    such as ACTION, INFO, and RESULT blocks. These blocks are defined with start and end markers 
    and can include additional parameters.

    Example block format:
        ##BLOCK_TYPE_START param1=value1 param2=value2
        Content of the block.
        ##BLOCK_TYPE_END

    Methods:
        create_block(block_type: str, content: str, params: Dict[str, str] = None) -> str
            Creates a generic block with the specified type, content, and optional parameters.

        create_info(content: str) -> str
            Creates an INFO block containing the provided content.

        create_action(content: str, action_id: str) -> str
            Creates an ACTION block containing the provided content and an action ID.

        create_result(content: str, result_id: str) -> str
            Creates a RESULT block containing the provided content and a result ID.

    Examples:
        Example: Creating an ACTION block
        >>> BlockHelper.create_action("This is a block.", action_id="example001")
        ##ACTION_START id=example001
        This is a block.
        ##ACTION_END

        Example: Creating a custom block
        >>> BlockHelper.create_block(
                block_type="EXAMPLE",
                content="This is an example block.",
                params={
                    "is_a_test": True
                }
            )
        ##EXAMPLE_START is_a_test=True
        This is an example block.
        ##EXAMPLE_END
    """

    @staticmethod
    def create_block(block_type: str, content: str, params: Dict[str, str] = None) -> str:
        params_str = " ".join([f"{k}={v}" for k, v in (params or {}).items()])
        params_part = f" {params_str}" if params_str else ""
        
        return (
            f"##{block_type}_START{params_part}\n"
            f"{content}\n"
            f"##{block_type}_END"
        ).strip()

    @staticmethod
    def create_info(content: str) -> str:
        return BlockHelper.create_block("INFO", content)

    @staticmethod
    def create_action(content: str, action_id: str, action_type: str) -> str:
        return BlockHelper.create_block("ACTION", content, {"id": action_id, "type": action_type})

    @staticmethod
    def create_result(content: str, result_id: str) -> str:
        return BlockHelper.create_block("RESULT", content, {"id": result_id})