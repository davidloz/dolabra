import logging
from typing import Optional

from mythril.laser.ethereum.state.global_state import GlobalState

from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules.taints import CallValueTaint

log = logging.getLogger(__name__)

class Payable(BaseModule):
    pattern_name = "PAYABLE"

    pre_hooks = ['JUMPI', 'RETURN', 'STOP', 'REVERT', 'INVALID']
    post_hooks = ['CALLVALUE']

    def __init__(self):
        self.payable_functions = set()
        self.non_payable_functions = set()
        super().__init__()

    def _analyze(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> Optional[dict]:
        if prev_state and prev_state.instruction['opcode'] == 'CALLVALUE':
            state.mstate.stack[-1].annotate(CallValueTaint())

        if state.instruction['opcode'] == 'JUMPI' and CallValueTaint() in state.mstate.stack[-2].annotations:
            self.non_payable_functions.add(state.environment.active_function_name)

        elif state.instruction['opcode'] in ['RETURN', 'STOP', 'REVERT', 'INVALID']:
            if state.environment.active_function_name not in self.non_payable_functions:
                self.payable_functions.add(state.environment.active_function_name)
                return {'contract': state.environment.active_account.contract_name,
                        'pattern': self.pattern_name,
                        'function_name': state.environment.active_function_name}

        return None