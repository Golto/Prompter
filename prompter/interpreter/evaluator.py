
from typing import List, Dict, Callable, Any, Optional
from abc import ABC, abstractmethod

from .parsing import Block
from .helper import BlockHelper


class BlockError(Exception):
    """Exception personnalisée pour les erreurs liées aux blocs"""
    pass

class ActionError(Exception):
    """Exception personnalisée pour les erreurs liées aux actions"""
    pass


class ActionContext:
    """Gère le contexte d'exécution des actions"""
    def __init__(self):
        self.used_ids: set[str] = set()
        self.results: Dict[str, str] = {}  # Stocke les résultats par ID

    def register_action_id(self, action_id: str) -> None:
        if action_id in self.used_ids:
            raise ActionError(f"Action ID '{action_id}' already exists")
        self.used_ids.add(action_id)

    def has_result(self, action_id: str) -> bool:
        """Vérifie si un résultat existe pour cet ID"""
        return action_id in self.results

    def store_result(self, action_id: str, result: str) -> None:
        """Stocke le résultat d'une action"""
        self.results[action_id] = result

    def get_result(self, action_id: str) -> str:
        """Récupère le résultat d'une action"""
        return self.results.get(action_id)

    def clear(self) -> None:
        self.used_ids.clear()
        self.results.clear()

    def __repr__(self) -> str:
        ids_str = ", ".join(sorted(self.used_ids)) if self.used_ids else "empty"
        results_str = ", ".join(f"{k}: {v}" for k, v in self.results.items()) if self.results else "empty"
        return f"ActionContext(used_ids=[{ids_str}], results=[{results_str}])"
    
class ActionHandler(ABC):
    """Classe abstraite définissant le contrat pour les handlers d'actions

    ### Example:
    ```py
    class DefaultHandler(ActionHandler):
        def handle(self, content: str, params: Dict[str, str]) -> str:
            return f"WARNING: No default handler registered for action with content: {content}"
    ```
    """
    
    @abstractmethod
    def handle(self, content: str, params: Dict[str, str]) -> str:
        """Traite une action avec son contenu et ses paramètres
        
        Args:
            content: Le contenu à traiter
            params: Les paramètres de l'action
            
        Returns:
            str: Le résultat du traitement
        
        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée
        """
        pass

    def validate_params(self, params: Dict[str, str]) -> None:
        """Valide les paramètres communs à tous les handlers"""
        required_params = {"id"}  # Par exemple
        missing_params = required_params - set(params.keys())
        if missing_params:
            raise ActionError(f"Missing required parameters: {missing_params}")

    def __call__(self, content: str, params: Dict[str, str]) -> str:
        """Permet d'utiliser le handler comme une fonction"""
        self.validate_params(params)
        return self.handle(content, params)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}()>"

class ActionRegistry:
    """Registre des actions disponibles

    ### Example
    ```py
    # Configuration du registre
    registry = ActionRegistry()

    # Exemple de fonction de traitement
    class ImageHandler(Actionhandler):
        def handle(self, content: str, params: Dict[str, str]) -> str:
            return f"Generated image from: {content}"

    registry.register("default", ImageHandler)
    ```
    
    """
    def __init__(self):
        self.actions: Dict[str, ActionHandler] = {}

    def register(self, action_type: str, handler: Any) -> None:
        """Enregistre une nouvelle fonction de traitement pour un type d'action
        
        Args:
            action_type: Le type d'action à enregistrer
            handler: Le handler à utiliser pour ce type d'action
            
        Raises:
            ActionError: Si le handler n'est pas une instance de ActionHandler
        """
        if not isinstance(handler, ActionHandler):
            raise ActionError(
                f"Handler must be an instance of ActionHandler, got {type(handler).__name__}"
            )
        self.actions[action_type] = handler

    def get_handler(self, action_type: str) -> ActionHandler:
        """Récupère le handler pour un type d'action
        
        Args:
            action_type: Le type d'action dont on veut récupérer le handler
            
        Returns:
            ActionHandler: Le handler correspondant au type d'action
            
        Raises:
            ActionError: Si aucun handler n'est enregistré pour ce type d'action
        """
        if action_type not in self.actions:
            raise ActionError(f"No handler registered for action type '{action_type}'")
        return self.actions[action_type]
    
    def __repr__(self) -> str:
        handlers = [f"{k}: {v}" for k, v in self.actions.items()]
        handlers_str = ", ".join(handlers) if handlers else "empty"
        return f"ActionRegistry(handlers=[{handlers_str}])"


class Evaluator:
    """Évalue les blocs et exécute les actions"""
    def __init__(self, registry: ActionRegistry):
        self.registry = registry
        self.context = ActionContext()

    def evaluate_blocks(self, blocks: List[Block]) -> List[Any]:
        """Évalue une liste de blocs
        
        Fait d'abord une passe pour identifier tous les RESULT,
        puis traite les ACTION en tenant compte des RESULT existants
        """
        results = []
        
        # Première passe : traitement des RESULT
        for block in blocks:
            if block.type == "RESULT":
                self._process_result_block(block)
        
        # Deuxième passe : traitement des ACTION
        for block in blocks:
            if block.type == "ACTION":
                try:
                    result = self.evaluate_action(block)
                except Exception as e:
                    error_msg = (
                        f"Error executing action: {str(e)}\n"
                        "> Make sure to use an available `type` parameter."
                    )
                    result = BlockHelper.create_block("ERROR", error_msg)
                if result is not None:  # Si l'action n'a pas été ignorée
                    results.append(result)
                
        return results

    def _process_result_block(self, block: Block) -> None:
        """Traite un bloc RESULT en stockant son contenu"""
        if "id" not in block.params:
            raise BlockError("Result block must have an 'id' parameter")
        
        action_id = block.params["id"]
        self.context.store_result(action_id, block.content)

    def evaluate_action(self, block: Block) -> Optional[str]:
        """Évalue un bloc d'action"""
        if "id" not in block.params:
            raise ActionError("Action block must have an 'id' parameter")

        action_id = block.params["id"]
        
        # Si un résultat existe déjà pour cet ID, on ignore l'action
        if self.context.has_result(action_id):
            return None

        # Vérifie si l'ID est déjà utilisé
        self.context.register_action_id(action_id)
        
        # Récupère et exécute le handler approprié
        action_type = block.params.get("type", "default")
        handler = self.registry.get_handler(action_type)
        
        # Exécute l'action et crée le bloc de résultat

        try:
            result = handler(block.content, block.params)
            self.context.store_result(action_id, result)
        except Exception as e:
            error_msg = f"Error executing action: {str(e)}"
            self.context.store_result(action_id, error_msg)
            result = error_msg
        
        # Crée et retourne le bloc de résultat
        return BlockHelper.create_result(result, action_id)