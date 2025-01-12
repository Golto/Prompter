from typing import List, Dict, Any, Optional, Callable
from .parsing import Parser
from .evaluator import Evaluator, ActionRegistry, ActionHandler


class DefaultHandler(ActionHandler):
    def handle(self, content: str, params: Dict[str, str]) -> str:
        """Handler par défaut qui renvoie un warning"""
        return f"WARNING: No default handler registered for action with content: {content}"

class Interpreter:
    """Interprète des textes contenant des blocs d'action et génère des résultats.

    Cette classe combine un Parser pour analyser le texte et un Evaluator pour 
    exécuter les actions détectées.

    ## Attributes:
        parser: Parser utilisé pour détecter les blocs dans le texte
        registry: Registre contenant les handlers disponibles
        evaluator: Evaluateur qui exécute les actions

    ## Examples:
    #### Texte d'entrée :

            >>> text = '''
            ... Création d'une image de chat
            ... ##ACTION_START type=image id=img001
            ... Generate cat image at sunset
            ... ##ACTION_END
            ... '''

    #### Configuration du handler :
           >>> class ImageHandler(ActionHandler):
           ...     def handle(self, content: str, params: Dict[str, str]) -> str:
           ...         # Génération d'image
           ...         return f"Generated image at `{image_path}`"
           
           >>> interpreter = Interpreter()
           >>> interpreter.register_handler("image", ImageHandler())


    #### Configuration - Méthode alternative (registre externe) :

            >>> interpreter = Interpreter()
            >>> interpreter.register_handler("image", ImageHandler())

    #### Interprétation :
            >>> results = interpreter.interpret(text)
            >>> print(results)
            [
                ##RESULT_START id=img001
                Generated image at `images/cat.png`
                ##RESULT_END
            ]

    #### Réinitialisation :
            >>> interpreter.clear_context()  # Efface les IDs utilisés
    """
    
    def __init__(self, registry: Optional[ActionRegistry] = None):
        self.parser = Parser()
        self.registry = registry or ActionRegistry()
        
        # Si aucun registre n'est fourni, on enregistre le handler par défaut
        if not registry:
            self.registry.register("default", DefaultHandler())
            
        self.evaluator = Evaluator(self.registry)
    
    def register_handler(self, action_type: str, handler: ActionHandler) -> None:
        """Enregistre un nouveau handler dans le registre"""
        self.registry.register(action_type, handler)
    
    def interpret(self, text: str) -> List[Any]:
        """Interprète un texte complet"""
        blocks = self.parser.parse(text)
        return self.evaluator.evaluate_blocks(blocks)
    
    def clear_context(self) -> None:
        """Réinitialise le contexte d'exécution"""
        self.evaluator.context.clear()
    
    def __repr__(self) -> str:
        return f"Interpreter(registry={self.registry})"