from typing import Dict, Any, Optional, List
from .linker import Linker
from .analyzer import Analyzer

class PromptBuildError(Exception):
    """Custom error for prompt building failures"""
    pass

class PromptBuilder:
    """Builds complete prompts by recursively replacing flags
    ### Example
    ```py
    builder = PromptBuilder()

    try:
        # Construction d'un prompt système pour l'agent tinia
        prompt = builder.build("system_prompt", agent_name="tinia", temp_debug="test")
        print(prompt)
        
    except PromptBuildError as e:
        print("Error building prompt:")
        print(e)
    ```
    """
    
    def __init__(self):
        self.analyzer = Analyzer()
        self.linker = Linker()
    
    def build(self, template_name: str, **kwargs) -> str:
        """
        Build a complete prompt from a template name
        
        Args:
            template_name: Name of the template to build (e.g. "system-prompt")
            **kwargs: Parameters required by the template (e.g. agent_name="tinia")
            
        Returns:
            str: The complete prompt with all flags replaced
            
        Raises:
            PromptBuildError: If a flag cannot be resolved or a parameter is missing
        """
        # Chercher le template initial dans le linker
        template = self.linker.template_manager.get_template("symbol", template_name)
        if not template:
            raise PromptBuildError(f"Template not found: {template_name}")
            
        # Analyser les dépendances pour vérifier les paramètres requis
        dep = self.linker.analyze_dependencies(template)
        
        # Vérifier que tous les paramètres requis sont fournis
        missing_params = set(dep.params.keys()) - set(kwargs.keys())
        if missing_params:
            raise PromptBuildError(
                f"Missing required parameters for template '{template_name}': {missing_params}"
            )
        
        try:
            # Construire le prompt récursivement
            return self._build_recursive(template, kwargs, [template])
        except PromptBuildError as e:
            # Propager l'erreur en ajoutant le contexte
            raise PromptBuildError(
                f"Error building template '{template_name}': {str(e)}"
            ) from e
    
    def _build_recursive(self, path: str, params: Dict[str, Any], 
                        build_stack: List[str]) -> str:
        """
        Recursively build a prompt by replacing all flags
        
        Args:
            path: Path to the current prompt file
            params: Parameters available for replacement
            build_stack: Stack of templates being processed (for error context)
            
        Raises:
            PromptBuildError: With detailed context if something goes wrong
        """
        # Charger le contenu
        content = self.analyzer.loader.read_prompt(path)
        if content is None:
            build_path = " -> ".join(build_stack)
            raise PromptBuildError(
                f"File not found: {path}\n"
                f"Build path: {build_path}"
            )
        
        # Trouver tous les flags
        flags = self.analyzer.list_flags(path)
        
        # Remplacer chaque flag
        for flag in flags:
            if flag.name == "parameter":
                # Flag de paramètre direct
                if flag.var_name not in params:
                    build_path = " -> ".join(build_stack)
                    raise PromptBuildError(
                        f"Missing parameter '{flag.var_name}' "
                        f"at line {flag.line_number} in {path}\n"
                        f"Build path: {build_path}"
                    )
                replacement = str(params[flag.var_name])
            
            else:
                # Flag qui pointe vers un autre fichier
                template = self.linker.get_template_for_flag(flag)
                if template is None:
                    build_path = " -> ".join(build_stack)
                    raise PromptBuildError(
                        f"Undefined flag '{flag.full_match}' "
                        f"at line {flag.line_number} in {path}\n"
                        f"Build path: {build_path}"
                    )
                
                try:
                    # Résoudre le template avec les paramètres
                    resolved_path = template.format(**params)
                except KeyError as e:
                    build_path = " -> ".join(build_stack)
                    raise PromptBuildError(
                        f"Missing parameter '{e.args[0]}' for template '{template}' "
                        f"at line {flag.line_number} in {path}\n"
                        f"Build path: {build_path}"
                    )
                
                # Éviter les boucles infinies
                if resolved_path in build_stack:
                    cycle = " -> ".join(build_stack[build_stack.index(resolved_path):])
                    raise PromptBuildError(f"Circular dependency detected: {cycle}")
                
                # Construction récursive
                replacement = self._build_recursive(
                    resolved_path, 
                    params,
                    build_stack + [resolved_path]
                )
            
            # Remplacer le flag dans le contenu
            content = content.replace(flag.full_match, replacement)
        
        return content