import time
import logging
from typing import Optional

# laser imports
from mythril.laser.ethereum import svm
from mythril.laser.ethereum.state.world_state import WorldState
from mythril.laser.ethereum.strategy.extensions.bounded_loops import BoundedLoopsStrategy
from mythril.laser.plugin.loader import LaserPluginLoader

from mythril.laser.plugin.plugins import (
    MutationPrunerBuilder,
    DependencyPrunerBuilder,
    CoveragePluginBuilder,
    InstructionProfilerBuilder,
)

import mythril.laser.ethereum.state.account

from dolabra.analysis.module.modules.loader import ModuleLoader
from dolabra.logger.log_manager import setup_logger
from dolabra.contract_loaders.file_loader import FileLoader
from dolabra.contract_loaders.jsonrpc_loader import JsonRpcLoader
from dolabra.contract_loaders.binary_loader import BinaryLoader
from dolabra.contract_loaders.runtime_loader import RuntimeLoader

from dolabra.constants import TIMEOUT, MAX_DEPTH, BOUNDED_LOOPS_LIMIT

setup_logger()
log = logging.getLogger(__name__)

class SymbolicWrapper:
    white_list=[]
    
    def __init__(self, contract, module_loader: Optional[ModuleLoader] = ModuleLoader()):
        self.contract = contract
        self.module_loader = module_loader

    def _process_contract(self):
        contract = self.contract
        bytecode = None
        runtime = None
        contract_address = None
        dyn_loader = None

        if contract is not None:
            if isinstance(contract, FileLoader):
                bytecode = contract.contract().creation_disassembly.bytecode
            elif isinstance(contract, RuntimeLoader):
                contract_address = "0"
                runtime = contract.contract().disassembly
            elif isinstance(contract, JsonRpcLoader):
                contract_address = contract.address
                dyn_loader = contract.dyn_loader
            else:
                raise ValueError('Invalid type for contract parameter')

        return bytecode, runtime, contract_address, dyn_loader


    
    def _initialize_laser(self, timeout, max_depth, creation_code, runtime_code, target_address, dyn_loader):
        world_state = WorldState()

        if creation_code and not runtime_code and not target_address:
            log.info('Initializing symbolic execution of creation code')
            laser = svm.LaserEVM(
                execution_timeout=timeout,
                max_depth=max_depth,
                requires_statespace=False)

        elif runtime_code and not creation_code:
            assert target_address
            log.info('Initializing symbolic execution of runtime code')
            account = mythril.laser.ethereum.state.account.Account(
                "0",
                runtime_code,
                contract_name="MAIN",
                balances=world_state.balances,
                concrete_storage=False)
            world_state.put_account(account)
            laser = svm.LaserEVM(
                execution_timeout=timeout,
                max_depth=max_depth,
                requires_statespace=False)

        elif target_address and not runtime_code and not creation_code:
            assert dyn_loader is not None, "Dynamic Loader has not been provided"
            log.info('Initializing symbolic execution of an existing contract')
            world_state.accounts_exist_or_load(target_address, dyn_loader)
            laser = svm.LaserEVM(
                dynamic_loader=dyn_loader,
                execution_timeout=timeout,
                max_depth=max_depth,
                requires_statespace=False)

        else:
            raise ValueError('Exactly one of creation_code, runtime_code and target_address needs to be provided')

        return laser, world_state


    
    def _register_hooks_and_load_plugins(self, laser, bounded_loops_limit):
        log.info('Registering hooks and loading plugins...')     

        for module in self.module_loader.get_detection_modules(self.white_list):
            for hook in module.pre_hooks:
                laser.register_hooks('pre', {hook: [module.execute]})
            for hook in module.post_hooks:
                laser.register_hooks('post', {hook: [module.execute]})    

        # Load laser plugins
        laser.extend_strategy(BoundedLoopsStrategy,
                              loop_bound=bounded_loops_limit)
        plugin_loader = LaserPluginLoader()
        plugin_loader.load(CoveragePluginBuilder())
        plugin_loader.load(MutationPrunerBuilder())
        plugin_loader.load(InstructionProfilerBuilder())
        plugin_loader.load(DependencyPrunerBuilder())
        plugin_loader.instrument_virtual_machine(laser, None)

    def _run_symbolic_execution(self, laser, creation_code, target_address, world_state=None):
        log.info('Starting symbolic execution...')
        start_time = time.time()
        laser.sym_exec(creation_code=creation_code,
                       contract_name='Unknown',
                       world_state=world_state,
                       target_address=int(target_address, 16) if target_address else None)
        log.info(
            'Symbolic execution finished in %.2f seconds.',
            time.time() - start_time)

        report = []
        for module in self.module_loader.get_detection_modules(self.white_list):
            report.append(module.results)

        return report    


    
    def run_analysis(self):
        log.info('Processing the contract and preparing for analysis...')
        bytecode, runtime, contract_address, dyn_loader = self._process_contract()

        laser, world_state = self._initialize_laser(
            timeout=TIMEOUT,
            max_depth=MAX_DEPTH,
            creation_code=bytecode,
            runtime_code=runtime,
            target_address=contract_address,
	    dyn_loader=dyn_loader)

        self._register_hooks_and_load_plugins(laser, bounded_loops_limit=BOUNDED_LOOPS_LIMIT)

        report = self._run_symbolic_execution(
            laser,
            creation_code=bytecode,
            target_address=contract_address,
            world_state=world_state)

        return report
