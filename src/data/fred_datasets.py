"""
FRED Dataset Configurations and Definitions.

Provides structured access to FRED economic series with grouping by category,
metadata, and helper functions for series selection.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from src.config.constants import FRED_SERIES


@dataclass
class FredSeriesConfig:
    """Configuration for a single FRED series."""

    series_id: str
    name: str
    category: str
    frequency: str
    description: Optional[str] = None
    units: Optional[str] = None
    seasonal_adjustment: Optional[str] = None
    priority: int = 2

    @property
    def cache_key(self) -> str:
        """Generate cache key for this series."""
        return self.series_id

    def __repr__(self) -> str:
        return f"FredSeries({self.series_id}: {self.name})"


@dataclass
class FredCategory:
    """Category grouping of related FRED series."""

    name: str
    description: str
    series: List[FredSeriesConfig] = field(default_factory=list)

    def get_series_ids(self) -> List[str]:
        """Get list of all series IDs in this category."""
        return [s.series_id for s in self.series]

    def get_priority_series(self, priority: int = 1) -> List[FredSeriesConfig]:
        """Get series matching priority level."""
        return [s for s in self.series if s.priority == priority]


# =============================================================================
# BUILD SERIES CONFIGS FROM CONSTANTS
# =============================================================================

def _build_series_configs() -> Dict[str, FredSeriesConfig]:
    """Build FredSeriesConfig objects from constants."""
    configs = {}
    for series_id, metadata in FRED_SERIES.items():
        configs[series_id] = FredSeriesConfig(
            series_id=series_id,
            name=metadata["name"],
            category=metadata["category"],
            frequency=metadata["frequency"],
            priority=metadata.get("priority", 2)
        )
    return configs


FRED_SERIES_CONFIGS = _build_series_configs()


# =============================================================================
# CATEGORY GROUPINGS
# =============================================================================

CATEGORIES: Dict[str, FredCategory] = {
    "interest_rates": FredCategory(
        name="Interest Rates",
        description="Treasury yields and interest rate indicators",
        series=[
            FRED_SERIES_CONFIGS["DGS2"],
            FRED_SERIES_CONFIGS["DGS5"],
            FRED_SERIES_CONFIGS["DGS10"],
            FRED_SERIES_CONFIGS["DGS30"],
            FRED_SERIES_CONFIGS["TB3MS"],
        ]
    ),

    "inflation": FredCategory(
        name="Inflation",
        description="Consumer price indices and inflation measures",
        series=[
            FRED_SERIES_CONFIGS["CPIAUCSL"],
            FRED_SERIES_CONFIGS["CPILFESL"],
        ]
    ),

    "gdp": FredCategory(
        name="GDP",
        description="Gross Domestic Product measures",
        series=[
            FRED_SERIES_CONFIGS["GDP"],
            FRED_SERIES_CONFIGS["GDPC1"],
        ]
    ),

    "labor": FredCategory(
        name="Labor Market",
        description="Employment and unemployment statistics",
        series=[
            FRED_SERIES_CONFIGS["UNRATE"],
            FRED_SERIES_CONFIGS["PAYEMS"],
        ]
    ),

    "housing": FredCategory(
        name="Housing",
        description="Housing market indicators",
        series=[
            FRED_SERIES_CONFIGS["HOUST"],
            FRED_SERIES_CONFIGS["CSUSHPISA"],
        ]
    ),

    "debt": FredCategory(
        name="Debt",
        description="Public and household debt measures",
        series=[
            FRED_SERIES_CONFIGS["GFDEBTN"],
            FRED_SERIES_CONFIGS["TDSP"],
        ]
    ),

    "money_supply": FredCategory(
        name="Money Supply",
        description="Monetary aggregates and liquidity measures",
        series=[
            FRED_SERIES_CONFIGS["M2SL"],
        ]
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_series_config(series_id: str) -> Optional[FredSeriesConfig]:
    """
    Get configuration for a specific series.

    Args:
        series_id: FRED series identifier

    Returns:
        FredSeriesConfig or None if not found

    Example:
        >>> config = get_series_config("DGS10")
        >>> print(config.name)
        "10-Year Treasury..."
    """
    return FRED_SERIES_CONFIGS.get(series_id)


def get_category(category_name: str) -> Optional[FredCategory]:
    """
    Get category by name.

    Args:
        category_name: Category identifier (e.g., "interest_rates")

    Returns:
        FredCategory or None if not found

    Example:
        >>> category = get_category("interest_rates")
        >>> print(category.get_series_ids())
        ["DGS2", "DGS5", "DGS10", "DGS30"]
    """
    return CATEGORIES.get(category_name)


def get_all_series_ids() -> List[str]:
    """
    Get list of all configured FRED series IDs.

    Returns:
        List of series IDs

    Example:
        >>> ids = get_all_series_ids()
        >>> print(len(ids))
        15
    """
    return list(FRED_SERIES_CONFIGS.keys())


def get_series_by_category(category_name: str) -> List[FredSeriesConfig]:
    """
    Get all series in a category.

    Args:
        category_name: Category identifier

    Returns:
        List of FredSeriesConfig objects

    Example:
        >>> housing_series = get_series_by_category("housing")
        >>> for series in housing_series:
        >>>     print(series.name)
    """
    category = CATEGORIES.get(category_name)
    return category.series if category else []


def get_priority_series(priority: int = 1) -> List[FredSeriesConfig]:
    """
    Get all high-priority series across categories.

    Args:
        priority: Priority level (1 = highest)

    Returns:
        List of FredSeriesConfig objects matching priority

    Example:
        >>> high_priority = get_priority_series(priority=1)
        >>> print([s.series_id for s in high_priority])
    """
    return [s for s in FRED_SERIES_CONFIGS.values() if s.priority == priority]


def search_series(query: str) -> List[FredSeriesConfig]:
    """
    Search series by name or description.

    Args:
        query: Search term (case-insensitive)

    Returns:
        List of matching FredSeriesConfig objects

    Example:
        >>> results = search_series("treasury")
        >>> for series in results:
        >>>     print(series.name)
    """
    query_lower = query.lower()
    return [
        s for s in FRED_SERIES_CONFIGS.values()
        if query_lower in s.name.lower() or
           (s.description and query_lower in s.description.lower())
    ]


def get_all_categories() -> Dict[str, FredCategory]:
    """
    Get all category groupings.

    Returns:
        Dictionary of category_name -> FredCategory

    Example:
        >>> categories = get_all_categories()
        >>> for cat_id, cat in categories.items():
        >>>     print(f"{cat.name}: {len(cat.series)} series")
    """
    return CATEGORIES
