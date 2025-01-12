import os
from pathlib import Path
from typing import Optional

class Loader:
    """Load prompt files from the prompts directory

### Example:
    ```py
    loader = Loader()

    # Lire un prompt
    content = loader.read_prompt("agents/main.md")
    if content:
        print("Content of agents/main.md:")
        print(content)
    else:
        print("File not found")

    # Obtenir le chemin absolu d'un prompt
    path = loader.get_prompt_path("agents/tinia/beginning.md")
    print(f"\\nPath to beginning.md: {path}")
    ```
    """
    
    def __init__(self):
        # Get the directory where loader.py is located
        self.module_dir = Path(__file__).parent
        # The prompts directory is a sibling of loader.py
        self.prompts_dir = self.module_dir / "prompts"
        
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompts directory not found at {self.prompts_dir}"
            )
    
    def get_prompt_path(self, relative_path: str) -> Path:
        """
        Convert a relative path to an absolute path in the prompts directory
        
        Args:
            relative_path: Path relative to the prompts directory
                         (e.g. "agents/main.md" or "user/input.md")
        
        Returns:
            Path: Absolute path to the prompt file
        """
        return self.prompts_dir / relative_path
    
    def read_prompt(self, relative_path: str) -> Optional[str]:
        """
        Read a prompt file's content
        
        Args:
            relative_path: Path relative to the prompts directory
                         (e.g. "agents/main.md" or "user/input.md")
        
        Returns:
            str: Content of the prompt file
            None: If file doesn't exist
        """
        prompt_path = self.get_prompt_path(relative_path)
        
        if not prompt_path.exists():
            return None
            
        return prompt_path.read_text(encoding='utf-8')