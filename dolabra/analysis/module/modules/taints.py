from typing import Optional

class PushOneTaint:
    """ Class to be used as annotation for PUSH1 elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'PushOneTaint'):
        return isinstance(other, PushOneTaint)        
    
class PushTwoTaint:
    """ Class to be used as annotation for PUSH2 elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'PushTwoTaint'):
        return isinstance(other, PushTwoTaint) 
    
class PushFourTaint:
    """ Class to be used as annotation for PUSH4 elements. """

    def __init__(self, function_signature: Optional[int] = None):
        self.function_signature = function_signature

    def __hash__(self):
        return hash(type(self))
    
    def __eq__(self, other: 'PushFourTaint'):
        return isinstance(other, PushFourTaint) and self.function_signature == other.function_signature
    
class DupOneTaint:
    """ Class to be used as annotation for DUP1 elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'DupOneTaint'):
        return isinstance(other, DupOneTaint)
    
class DupTwoTaint:
    """ Class to be used as annotation for DUP2 elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'DupTwoTaint'):
        return isinstance(other, DupTwoTaint)
    
class CallValueTaint:
    """ Class to be used as annotation for CALLVALUE elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'CallValueTaint'):
        return isinstance(other, CallValueTaint)  

class IsZeroTaint:
    """ Class to be used as annotation for ISZERO elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'IsZeroTaint'):
        return isinstance(other, IsZeroTaint)       

class SwapOneTaint:
    """ Class to be used as annotation for SWAP1 elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'SwapOneTaint'):
        return isinstance(other, SwapOneTaint)   
    
class StorageLoadTaint:
    """ Class to be used as annotation for SLOAD elements. """

    def __init__(self, storage_address: Optional[int] = None):
        self.storage_address = storage_address

    def __hash__(self):
        return hash((type(self), self.storage_address))

    def __eq__(self, other: 'StorageLoadTaint'):
        return isinstance(other, StorageLoadTaint) and self.storage_address == other.storage_address
    
class StorageSaveTaint:
    """ Class to be used as annotation for SSTORE elements. """

    def __init__(self, storage_address: Optional[int] = None):
        self.storage_address = storage_address

    def __hash__(self):
        return hash((type(self), self.storage_address))

    def __eq__(self, other: 'StorageSaveTaint'):
        return isinstance(other, StorageSaveTaint) and self.storage_address == other.storage_address
    
class EqualTaint:
    """ Class to be used as annotation for EQ elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'EqualTaint'):
        return isinstance(other, EqualTaint)  
    
class CalldataLoadTaint:
    """ Class to be used as annotation for CALLDATALOAD elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'CalldataLoadTaint'):
        return isinstance(other, CalldataLoadTaint)
    
class CalldataSizeTaint:
    """ Class to be used as annotation for CalldataSizeTaint elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'CalldataSizeTaint'):
        return isinstance(other, CalldataSizeTaint)    
    
class CallerTaint:
    """ Class to be used as annotation for CALLER elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'CallerTaint'):
        return isinstance(other, CallerTaint)
    
class JumpiTaint:
    """ Class to be used as annotation for JUMPI elements. """

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other: 'JumpiTaint'):
        return isinstance(other, JumpiTaint)