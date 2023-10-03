import logging
from typing import Text

from mythril.ethereum.evmcontract import EVMContract

from dolabra.contract_loaders.file_loader import FileLoader

log = logging.getLogger(__name__)

class RuntimeLoader(FileLoader):
    def __init__(self, path: Text) -> None:
        super().__init__(path)

    def contract(self) -> EVMContract:        
        try:
            with open(self._file_path, 'rb') as contract_bin:
                bytecode = contract_bin.read().decode()
        except IOError as e:
            log.error('Failed to open contract binary file: %s', e)
            raise IOError('Failed to open contract binary file')
        return EVMContract(code=bytecode)

    @classmethod
    def create(cls, **options):
        return cls(options.get('path'))

