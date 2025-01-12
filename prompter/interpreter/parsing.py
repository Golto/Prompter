import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Block:
    type: str
    content: str
    params: Dict[str, str]
    start_pos: int
    end_pos: int

class Parser:
    def __init__(self):
        # Regex modifiée pour ne capturer que les vrais paramètres
        self.block_pattern = re.compile(
            r'^##(\w+)_START(?:\s+((?:\w+=\S+\s*)+))?\s*$(.*?)^##\1_END$',
            re.MULTILINE | re.DOTALL
        )
        
    def _parse_params(self, params_str: str) -> Dict[str, str]:
        """Parse les paramètres d'un bloc (ex: id=img001)"""
        if not params_str:
            return {}
            
        params = {}
        for param in params_str.split():
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        return params

    def parse(self, text: str) -> List[Block]:
        """Parse le texte et retourne une liste de blocs"""
        blocks = []
        last_end = 0
        
        # Trouver tous les blocs
        for match in self.block_pattern.finditer(text):
            start = match.start()
            
            # Ajouter le texte qui précède comme bloc TEXT
            if start > last_end:
                text_content = text[last_end:start].strip()
                if text_content:
                    blocks.append(Block(
                        type="TEXT",
                        content=text_content,
                        params={},
                        start_pos=last_end,
                        end_pos=start
                    ))
            
            # Parser le bloc trouvé
            block_type = match.group(1)
            params_str = match.group(2) or ""
            content = match.group(3).strip()

            blocks.append(Block(
                type=block_type,
                content=content,
                params=self._parse_params(params_str),
                start_pos=start,
                end_pos=match.end()
            ))
            
            last_end = match.end()
        
        # Ajouter le texte restant comme bloc TEXT
        if last_end < len(text):
            remaining_text = text[last_end:].strip()
            if remaining_text:
                blocks.append(Block(
                    type="TEXT",
                    content=remaining_text,
                    params={},
                    start_pos=last_end,
                    end_pos=len(text)
                ))
        
        return blocks