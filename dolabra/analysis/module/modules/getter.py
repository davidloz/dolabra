import logging
from typing import Optional

from mythril.laser.ethereum.state.global_state import GlobalState

from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules.taints import PushOneTaint, DupOneTaint, StorageLoadTaint, CalldataLoadTaint, CalldataSizeTaint

log = logging.getLogger(__name__)

state_changers = ['SSTORE', 'CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL', 'SELFDESTRUCT', 'CREATE', 'CREATE2']
tx_or_block_access = ['ORIGIN', 'GASPRICE', 'COINBASE', 'TIMESTAMP', 'NUMBER', 'DIFFICULTY', 'GASLIMIT', 'GAS']

class Getter(BaseModule):
    pattern_name = "GETTER"    

    pre_hooks = ['RETURN'] + state_changers
    post_hooks = ['PUSH1', 'DUP1', 'SLOAD', 'CALLDATALOAD', 'SHA3', 'CALLDATASIZE'] + tx_or_block_access

    def __init__(self):
        self.already_storage_tainted_sign = []
        self.function_black_list = []
        super().__init__()

    def _analyze(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> Optional[dict]:
        current_function = state.environment.active_function_name
        # (2) the value is read from storage
        if prev_state and prev_state.instruction['opcode'] == 'PUSH1':
            state.mstate.stack[-1].annotate(PushOneTaint())

        elif prev_state and prev_state.instruction['opcode'] == 'DUP1' and PushOneTaint() in state.mstate.stack[-1].annotations:
            state.mstate.stack[-1].annotate(DupOneTaint())

        elif prev_state and prev_state.instruction['opcode'] == 'SLOAD':            
            if len(state.mstate.stack) >= 1:                
                # loop through the stack to find the DUP1 element, there can be mulitple PUSH1s setting the indexes
                for stack_index in range(len(state.mstate.stack)):
                    if DupOneTaint() in state.mstate.stack[stack_index].annotations and current_function not in self.already_storage_tainted_sign:                        
                        if CalldataSizeTaint() in state.mstate.stack[stack_index].annotations and current_function in self.function_black_list:
                            self.function_black_list.remove(current_function)
                        if current_function not in self.function_black_list:
                            state.mstate.stack[stack_index].annotate(StorageLoadTaint())
                            self.already_storage_tainted_sign.append(current_function)
                            
        # (3) The argument list is either empty, or the argument is used to compute the position of the storage slot
        elif prev_state and prev_state.instruction['opcode'] == 'CALLDATALOAD':
            state.mstate.stack[-1].annotate(CalldataLoadTaint())            

        elif prev_state and prev_state.instruction['opcode'] == 'CALLDATASIZE':
            for stack_index in range(len(state.mstate.stack)):
                    if CalldataLoadTaint() in state.mstate.stack[stack_index].annotations:
                        state.mstate.stack[stack_index].annotate(CalldataSizeTaint())
                        self.function_black_list.append(current_function)

        # (4) The function does not change the state
        if state.instruction['opcode'] in state_changers:
            self.function_black_list.append(current_function)

        # (5) no accesses to tx and block variables
        if prev_state and prev_state.instruction['opcode'] in tx_or_block_access:
            self.function_black_list.append(current_function)

        # (1) it is a function returning a value, this should be the last opcode in the function
        if state.instruction['opcode'] == 'RETURN':
            if current_function not in self.function_black_list: 
                 for stack_index in range(len(state.mstate.stack)):
                    if StorageLoadTaint() in state.mstate.stack[stack_index].annotations:                                                                           
                        return {'contract': state.environment.active_account.contract_name, 'pattern': self.pattern_name, 'function_name': current_function}                        

        return None
