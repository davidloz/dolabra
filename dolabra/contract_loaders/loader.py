from enum import Enum

from dolabra.contract_loaders.contract_loader import ContractLoader
from dolabra.contract_loaders.binary_loader import BinaryLoader
from dolabra.contract_loaders.runtime_loader import RuntimeLoader
from dolabra.contract_loaders.solidity_loader import SolidityLoader
from dolabra.contract_loaders.jsonrpc_loader import JsonRpcLoader

class LoaderType(Enum):
    BINARY = 1
    SOLIDITY = 2
    JSON_RPC = 3
    RUNTIME = 4

class Loader():
    def get_contract(loader_type: LoaderType, **options) -> ContractLoader:
        switcher = {
            LoaderType.BINARY:   BinaryLoader.create,
            LoaderType.RUNTIME:  RuntimeLoader.create,
            LoaderType.SOLIDITY: SolidityLoader.create,
            LoaderType.JSON_RPC: JsonRpcLoader.create
        }
        if loader_type not in switcher:
            raise NotImplementedError('This loader has not been implemented yet')
        return switcher.get(loader_type)(**options)
