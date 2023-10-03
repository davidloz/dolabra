from typing import Optional, List

from mythril.analysis.module.base import DetectionModule, EntryPoint
from mythril.support.support_utils import Singleton
from mythril.exceptions import DetectorNotFoundError

from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules import Payable, StorageCallerCheck, Getter, Setter, Token

MODULES = {
    Getter.pattern_name: Getter,
    Setter.pattern_name: Setter,
    StorageCallerCheck.pattern_name: StorageCallerCheck,
    Token.pattern_name: Token,
    Payable.pattern_name: Payable
}

class ModuleLoader(object, metaclass=Singleton):
    def __init__(self):
        self._modules = []
        self._register_modules()

    def register_module(self, detection_module: BaseModule):
        """Registers a detection module with the module loader"""
        if not isinstance(detection_module, DetectionModule):
            raise ValueError(
                "The passed variable is not a valid detection module")
        self._modules.append(detection_module)

    def get_detection_modules(self,
                              white_list: Optional[List[str]] = None
        ) -> List[BaseModule]:

        result = self._modules[:]

        if white_list:
            available_names = [type(module).__name__ for module in result]

            for name in white_list:
                if name not in available_names:
                    raise DetectorNotFoundError(
                        "Invalid detection module: {}".format(name)
                    )

            result = [
                module for module in result if type(module).__name__ in white_list
            ]

        return result
    
    def set_modules(self, modules: List[BaseModule]) -> None:
        assert modules is not None and len(modules) > 0
        self._modules = modules

    def reset_modules(self) -> None:
        for module in self._modules:
            module.reset()

    def _register_modules(self):
        self._modules.extend(
            [
                StorageCallerCheck(),
                Getter(),
                Setter(),
                Token()
            ]
        )
