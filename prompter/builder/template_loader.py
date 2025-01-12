
from pathlib import Path
import yaml
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class FlagTemplate:
    """Template for a flag mapping"""
    flag_name: str
    var_name: str
    template: str

class TemplateLoader:
    """Loads and manages template configurations"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_path = self.base_path / "config" / "templates.yaml"
        self.templates = self._load_templates()
        self._template_map = self._build_template_map()
    
    def _load_templates(self) -> List[FlagTemplate]:
        """Load templates from YAML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Template configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        return [
            FlagTemplate(**template_data)
            for template_data in config['templates']
        ]
    
    def _build_template_map(self) -> Dict[Tuple[str, str], str]:
        """Build index for quick template access"""
        return {
            (t.flag_name, t.var_name): t.template 
            for t in self.templates
        }
    
    def get_template(self, flag_name: str, var_name: str) -> str:
        """Get template path for given flag and variable names"""
        key = (flag_name, var_name)
        if key not in self._template_map:
            raise KeyError(f"No template found for flag '{flag_name}' and variable '{var_name}'")
        return self._template_map[key]