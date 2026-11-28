"""Registers the custom operators with Cosmic Ray (they appear as hc/<OperatorName>)."""
from .operators import HcActionSwap, HcLimitShift, HcStatusSwap

_OPERATORS = {op.__name__: op for op in (HcStatusSwap, HcActionSwap, HcLimitShift)}


class HcProvider:
    def __iter__(self):
        return iter(_OPERATORS)

    def __getitem__(self, name):
        return _OPERATORS[name]
