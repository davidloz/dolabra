import logging
from typing import Optional

from mythril.laser.ethereum.state.global_state import GlobalState

from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules.taints import DupOneTaint, PushOneTaint, DupTwoTaint, SwapOneTaint, StorageSaveTaint, CalldataLoadTaint, CalldataSizeTaint

log = logging.getLogger(__name__)

state_changers = ['CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL', 'SELFDESTRUCT', 'CREATE', 'CREATE2']
tx_or_block_access = ['ORIGIN', 'GASPRICE', 'COINBASE', 'TIMESTAMP', 'NUMBER', 'DIFFICULTY', 'GASLIMIT', 'GAS']

class Setter(BaseModule):
    pattern_name = "SETTER"

    pre_hooks = state_changers
    post_hooks = ['DUP1', 'PUSH1', 'DUP2', 'SWAP1', 'SSTORE', 'CALLDATALOAD', 'CALLDATASIZE'] 

    def __init__(self):
        self.already_storage_tainted_sign = []
        self.function_black_list = []
        super().__init__()

    def _analyze(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> Optional[dict]:
        current_function = state.environment.active_function_name

        # (4) The function does not change the state
        if state.instruction['opcode'] in state_changers:
            self.function_black_list.append(current_function)

        # (5) no accesses to tx and block variables
        if prev_state and prev_state.instruction['opcode'] in tx_or_block_access:
            self.function_black_list.append(current_function)

        if prev_state and prev_state.instruction['opcode'] == 'DUP1':
            state.mstate.stack[-1].annotate(DupOneTaint())

        elif prev_state and prev_state.instruction['opcode'] == 'PUSH1':
            if len(state.mstate.stack) > 1 and DupOneTaint() in state.mstate.stack[-2].annotations:
                state.mstate.stack[-2].annotate(PushOneTaint())

        elif prev_state and prev_state.instruction['opcode'] == 'DUP2' and {DupOneTaint(), PushOneTaint()}.issubset(state.mstate.stack[-1].annotations):
            state.mstate.stack[-1].annotate(DupTwoTaint())

        elif prev_state and prev_state.instruction['opcode'] == 'SWAP1' and {DupOneTaint(), PushOneTaint(), DupTwoTaint()}.issubset(state.mstate.stack[-1].annotations):
            state.mstate.stack[-1].annotate(SwapOneTaint())

         # (3) The value depends on the calldata
        elif prev_state and prev_state.instruction['opcode'] == 'CALLDATALOAD':
            state.mstate.stack[-1].annotate(CalldataLoadTaint())            

        elif prev_state and prev_state.instruction['opcode'] == 'CALLDATASIZE':
            for stack_index in range(len(state.mstate.stack)):
                    if CalldataLoadTaint() in state.mstate.stack[stack_index].annotations:
                        state.mstate.stack[stack_index].annotate(CalldataSizeTaint())
                        self.function_black_list.append(current_function)        

        # (1) There is a write to storage
        elif prev_state and prev_state.instruction['opcode'] == 'SSTORE':
            if current_function not in self.function_black_list:             
                if len(state.mstate.stack) >= 1:                    
                    # loop through the stack to find the DUP1 element, there can be mulitple PUSH1s setting the indexes
                    for stack_index in range(len(state.mstate.stack)):                                        
                        if {DupOneTaint(), PushOneTaint(), DupTwoTaint(), SwapOneTaint()}.issubset(state.mstate.stack[stack_index].annotations) and current_function not in self.already_storage_tainted_sign:                        
                            state.mstate.stack[stack_index].annotate(StorageSaveTaint())
                            self.already_storage_tainted_sign.append(current_function)
                            return {'contract': state.environment.active_account.contract_name, 'pattern': self.pattern_name, 'function_name': current_function}             

        return None
