import re
import logging
from typing import Optional

from mythril.laser.ethereum.state.global_state import GlobalState
from dolabra.analysis.module.modules.basemodule import BaseModule
from dolabra.analysis.module.modules.taints import PushFourTaint

log = logging.getLogger(__name__)

class Token(BaseModule):
    pattern_name = "TOKEN"

    pre_hooks = ['JUMPDEST']
    post_hooks = ['PUSH4'] 

    def __init__(self):
        self.erc20_signatures = {
            "0x06fdde03": "name()",  
            "0x95d89b41": "symbol()",  
            "0x313ce567": "decimals()",  
            "0x18160ddd": "totalSupply()",  
            "0x70a08231": "balanceOf(address)",  
            "0xa9059cbb": "transfer(address,uint256)",  
            "0x23b872dd": "transferFrom(address,address,uint256)",  
            "0xdd62ed3e": "approve(address,uint256)",  
            "0x8da5cb5b": "allowance(address,address)",  
        }

        self.erc721_signatures = {
            "0x80ac58cd": "supportsInterface(bytes4)",  
            "0x5b5e139f": "balanceOf(address)",  
            "0x6352211e": "ownerOf(uint256)",  
            "0xa22cb465": "safeTransferFrom(address,address,uint256)",  
            "0x42842e0e": "safeTransferFrom(address,address,uint256,bytes)",  
            "0x23b872dd": "transferFrom(address,address,uint256)",  
            "0x018a8e63": "approve(address,uint256)",  
            "0xe985e9c5": "setApprovalForAll(address,bool)",  
            "0x0178f79b": "getApproved(uint256)",  
            "0x4b5d4f24": "isApprovedForAll(address,address)",  
        }

        self.function_signatures = set()
        self.found_erc20_signatures = set()
        self.found_erc721_signatures = set()

        super().__init__()

    def _analyze(self, state: GlobalState, prev_state: Optional[GlobalState] = None) -> Optional[dict]:

        if prev_state and prev_state.instruction['opcode'] == 'PUSH4': 
            function_signature_decimal = state.mstate.stack[-1].value
            function_signature_hex = hex(function_signature_decimal).rstrip("L") #.rjust(8, '0')
            self.function_signatures.add(function_signature_hex)
            state.mstate.stack[-1].annotate(PushFourTaint(function_signature_hex))

        for signature in self.erc20_signatures:
            if signature in self.function_signatures and signature not in self.found_erc20_signatures:
                self.found_erc20_signatures.add(signature)
                self.results.append({
                    'contract': state.environment.active_account.contract_name,
                    'pattern': self.pattern_name,
                    'signature': self.erc20_signatures[signature],
                    'token_type': "ERC20",
                    'function_name': state.environment.active_function_name                    
                    })
                
        for signature in self.erc721_signatures:
            if signature in self.function_signatures and signature not in self.found_erc721_signatures:
                self.found_erc721_signatures.add(signature)
                self.results.append({
                    'contract': state.environment.active_account.contract_name,
                    'pattern': self.pattern_name,
                    'signature': self.erc721_signatures[signature],
                    'token_type': "ERC721",
                    'function_name': state.environment.active_function_name                    
                    })        

        return None
