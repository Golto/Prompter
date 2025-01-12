from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from pathlib import Path
import re

from .analyzer import Analyzer, Flag
from .template_loader import FlagTemplate, TemplateLoader

class TemplateManager:
    """Manages flag to file templates"""

    def __init__(self):
        loader = TemplateLoader()
        self.templates = loader.templates
        self._template_map = loader._template_map
    
    def get_template(self, flag_name: str, var_name: str) -> Optional[str]:
        """Get template path for a flag"""
        return self._template_map.get((flag_name, var_name))
    

@dataclass
class Dependency:
    """Represents a dependency between prompts"""
    path: str             # Chemin relatif du fichier
    flags: Set[str]       # Liste des flags dans ce fichier
    params: Dict[str, str]  # Paramètres requis
    dependencies: Set[str]  # Chemins des fichiers dont ce fichier dépend


class Linker:
    """Links flags to their source files and manages dependencies"""
    
    def __init__(self):
        self.analyzer = Analyzer()
        self.template_manager = TemplateManager()
        self.dependencies: Dict[str, Dependency] = {}
    
    def get_template_for_flag(self, flag: Flag) -> Optional[str]:
        """
        Get the template path for a flag, without applying parameters
        
        Example:
            For flag "@__symbol__:beginning"
            returns "agents/{agent_name}/beginning.md"
        """
        return self.template_manager.get_template(flag.name, flag.var_name)

    def analyze_dependencies(self, path: str) -> Dependency:
        """
        Analyze dependencies for a file recursively
        """
        if path in self.dependencies:
            return self.dependencies[path]
            
        flags = self.analyzer.list_flags(path)
        deps = set()
        params = {}
        
        for flag in flags:
            # Si c'est un parameter flag, l'ajouter aux paramètres requis
            if flag.name == "parameter":
                params[flag.var_name] = str
                continue
            
            # Sinon, analyser le template du fichier
            template = self.get_template_for_flag(flag)
            if template:
                # Collecter les paramètres du template
                param_matches = re.finditer(r'\{(\w+)\}', template)
                for match in param_matches:
                    param_name = match.group(1)
                    params[param_name] = str
                
                deps.add(template)
                
                # Si le template ne contient pas de paramètres,
                # on peut l'analyser récursivement
                if not re.search(r'\{(\w+)\}', template):
                    child_dep = self.analyze_dependencies(template)
                    params.update(child_dep.params)
        
        dep = Dependency(
            path=path,
            flags={f.var_name for f in flags},
            params=params,
            dependencies=deps
        )
        self.dependencies[path] = dep
        return dep
