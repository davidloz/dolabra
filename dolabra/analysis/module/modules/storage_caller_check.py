import logging
from typing import Optional
from mythril.laser.ethereum.state.global_state import GlobalState
from mythril.laser.smt.bitvec import BitVec

from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules.taints import (
    PushFourTaint,
    PushTwoTaint,
    EqualTaint,
    CallerTaint,
    JumpiTaint,
    StorageLoadTaint
)

log = logging.getLogger(__name__) 

essential_operations = ['SSTORE', 'CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL']

class StorageCallerCheck(BaseModule):
    pattern_name = "STORAGE_CALLER_CHECK"

    pre_hooks = ['JUMPI']
    post_hooks = ['CALLER', 'SLOAD', 'PUSH4', 'EQ', 'PUSH2'] + essential_operations

    def __init__(self):
        self.function_signatures = set()
        self.functions_containing_auth = set()
        super().__init__()
    
    def _annotate_function_start(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> bool:
        if prev_state and prev_state.instruction['opcode'] == 'PUSH4':            
            function_signature = state.mstate.stack[-1].value
            self.function_signatures.add(function_signature)
            state.mstate.stack[-1].annotate(PushFourTaint(function_signature))
        elif prev_state and prev_state.instruction['opcode'] == 'EQ' and PushFourTaint(prev_state.mstate.stack[-1].value) in (state.mstate.stack[-1].annotations):
            state.mstate.stack[-1].annotate(EqualTaint())   
        elif prev_state and prev_state.instruction['opcode'] == 'PUSH2' and len(state.mstate.stack) > 1 and EqualTaint() in (state.mstate.stack[-2].annotations):
            state.mstate.stack[-2].annotate(PushTwoTaint())
        if state.instruction['opcode'] == 'JUMPI' and PushTwoTaint() in (state.mstate.stack[-2].annotations) :
            state.mstate.stack[-2].annotate(JumpiTaint())
    
    def _analyze(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> Optional[dict]:
        self._annotate_function_start(state, prev_state)
        if prev_state and prev_state.instruction['opcode'] not in essential_operations:
            if prev_state and prev_state.instruction['opcode'] == 'SLOAD' and prev_state.mstate.stack[-1].symbolic is False:
                index = prev_state.mstate.stack[-1].value
                if index <= 0xFF:
                    # Restrict memorizing storage keys that result from some sort of hashing
                    # by checking if the index is less than 256.
                    state.mstate.stack[-1].annotate(StorageLoadTaint(index))
            elif prev_state and prev_state.instruction['opcode'] == 'CALLER':
                state.mstate.stack[-1].annotate(CallerTaint())
            elif prev_state and prev_state.instruction['opcode'] == 'EQ' and \
                (CallerTaint() in state.mstate.stack[-1].annotations and self._has_annotation(state.mstate.stack[-1], StorageLoadTaint)):
                state.mstate.stack[-1].annotate(EqualTaint()) 
                            
            elif state.instruction['opcode'] == 'JUMPI' and EqualTaint() in state.mstate.stack[-2].annotations:
                active_function = state.environment.active_function_name
                if active_function not in self.functions_containing_auth:
                    self.functions_containing_auth.add(active_function)
                    return {'contract': state.environment.active_account.contract_name, 'pattern': self.pattern_name, 'function_name': active_function}
            
        return None
