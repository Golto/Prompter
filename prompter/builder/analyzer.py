
from typing import List
from dataclasses import dataclass
import re
from .loader import Loader

@dataclass
class Flag:
    """
    Represents a flag in a prompt file.
    - Format: `@__[flag_name]__:[var_name]`
    - Example: `@__symbol__:beginning`
    """
    name: str          # Le nom du flag (ex: "symbol" dans @__symbol__:beginning)
    var_name: str      # Le nom de la variable (ex: "beginning" dans @__symbol__:beginning)
    line_number: int   # La ligne où le flag a été trouvé
    full_match: str    # Le flag complet (@__symbol__:beginning)

class Analyzer:
    """Analyze prompt files to find flags

### Example
    ```py
    analyzer = Analyzer()
    flags = analyzer.list_flags("agents/main.md")

    for flag in flags:
        print(f"Line {flag.line_number}: {flag.full_match}")
        print(f"  Flag name: {flag.name}")
        print(f"  Var name: {flag.var_name}\\n")
    ```
    """

    FLAG_PATTERN = r'@__(\w+)__:(\w+)'

    def __init__(self):
        self.loader = Loader()

    def list_flags(self, path: str) -> List[Flag]:
        """
        Find all flags in a file
        
        Args:
            path: Path relative to the prompts directory (ex: "agents/main.md")
            
        Returns:
            List[Flag]: List of all flags found in the file
        """
        flags = []
        
        # Load file content
        content = self.loader.read_prompt(path)
        if content is None:
            return flags
            
        # Parse content line by line to keep track of line numbers
        for line_num, line in enumerate(content.splitlines(), 1):
            # Find all matches in current line
            matches = re.finditer(self.FLAG_PATTERN, line)
            
            for match in matches:
                flags.append(Flag(
                    name=match.group(1),       # First capture group (flag_name)
                    var_name=match.group(2),   # Second capture group (var_name)
                    line_number=line_num,
                    full_match=match.group(0)  # Complete match
                ))
        
        return flags