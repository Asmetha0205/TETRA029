"""
Custom Exceptions for the Demand & Trend Intelligence Engine.

Provides specific exception types for error handling in demand analysis,
trend calculation, and industry intelligence generation.
"""


class DemandEngineError(Exception):
    """Base exception for all Demand & Trend Intelligence Engine errors."""
    pass


class EmptyDatasetError(DemandEngineError):
    """Raised when the input dataset is empty."""
    pass


class InvalidInputError(DemandEngineError):
    """Raised when input data is invalid or malformed."""
    pass


class MissingHistoricalDataError(DemandEngineError):
    """Raised when required historical data is not available."""
    pass


class CorruptSnapshotError(DemandEngineError):
    """Raised when a snapshot file is corrupted or unreadable."""
    pass


class SnapshotStorageError(DemandEngineError):
    """Raised when snapshot storage operations fail."""
    pass


class NegativeGrowthError(DemandEngineError):
    """Raised when growth calculations produce unexpected negative values."""
    pass


class MissingTechnologyError(DemandEngineError):
    """Raised when a required technology is not found in the dataset."""
    pass


class InvalidRankingError(DemandEngineError):
    """Raised when ranking calculations produce invalid results."""
    pass


class ConfigurationError(DemandEngineError):
    """Raised when configuration parameters are invalid."""
    pass


class WeightSumError(ConfigurationError):
    """Raised when configured weights do not sum to approximately 1.0."""
    pass


class ThresholdConflictError(ConfigurationError):
    """Raised when threshold values conflict (e.g., min > max)."""
    pass


class ReportGenerationError(DemandEngineError):
    """Raised when report generation fails."""
    pass


class ExportError(DemandEngineError):
    """Raised when exporting reports or data fails."""
    pass


class ValidationError(DemandEngineError):
    """Raised when data validation fails."""
    pass
