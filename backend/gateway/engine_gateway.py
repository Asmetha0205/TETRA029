"""
Base Engine Gateway Abstraction for CurricuAlign AI.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEngineGateway(ABC):
    """
    Abstract Base Class for all Engine Gateways.
    Ensures a standard facade interface across subsystems.
    """

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the friendly name of the engine."""
        pass

    @abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """Perform health check on the underlying engine."""
        pass
