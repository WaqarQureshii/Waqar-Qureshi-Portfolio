"""
Dataset configurations for Stats Canada and yfinance data sources.

Defines structured configurations for tables and tickers using dataclasses,
following the same pattern as fred_datasets.py for consistency.

Metadata extracted from archive/v1/config/datasets.py and src/config/constants.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.config.constants import STATSCAN_PRIORITY_TABLES, YFINANCE_TICKERS


# =============================================================================
# STATS CANADA CONFIGURATIONS
# =============================================================================

@dataclass
class StatsCanTableConfig:
    """Configuration for a single Stats Canada table."""

    product_id: str          # "36100434"
    name: str                # "GDP by Industry"
    category: str            # "Economy", "Labour Market", "Housing", "Trade"
    frequency: str           # "monthly", "quarterly", "annual"
    description: Optional[str] = None
    breakdowns: Optional[List[str]] = None  # ["industry", "geography"]
    priority: int = 2        # 1=high priority, 2=normal
    default_vectors: Optional[List[int]] = None  # Default vector IDs to fetch

    @property
    def cache_key(self) -> str:
        """Generate cache key for this table (used by CacheManager)."""
        return self.product_id

    def __repr__(self) -> str:
        return f"StatsCanTable({self.product_id}: {self.name})"


@dataclass
class StatsCanCategory:
    """Category grouping of related Stats Canada tables."""

    name: str
    description: str
    tables: List[StatsCanTableConfig] = field(default_factory=list)

    def get_product_ids(self) -> List[str]:
        """Get list of all product IDs in this category."""
        return [t.product_id for t in self.tables]

    def get_priority_tables(self, priority: int = 1) -> List[StatsCanTableConfig]:
        """Get tables matching priority level."""
        return [t for t in self.tables if t.priority == priority]

    def __repr__(self) -> str:
        return f"StatsCanCategory({self.name}: {len(self.tables)} tables)"


# =============================================================================
# STATS CANADA TABLE DEFINITIONS
# =============================================================================

# Build configurations from archived metadata
# Reference: archive/v1/config/datasets.py

STATSCAN_TABLE_CONFIGS: Dict[str, StatsCanTableConfig] = {
    # Economy - GDP
    "36100434": StatsCanTableConfig(
        product_id="36100434",
        name="GDP by Industry (Monthly)",
        category="Economy",
        frequency="monthly",
        description="Gross Domestic Product by industry at basic prices",
        breakdowns=["industry", "geography"],
        priority=1,
        default_vectors=[
            41690973,  # All industries, seasonally adjusted, chained (2017) dollars
            41691182,  # All industries, unadjusted, chained (2017) dollars
        ]
    ),
    "36100222": StatsCanTableConfig(
        product_id="36100222",
        name="GDP by Expenditure (Quarterly)",
        category="Economy",
        frequency="quarterly",
        description="Gross Domestic Product by expenditure",
        breakdowns=["expenditure_category"],
        priority=1
    ),

    # Economy - Inflation
    "18100004": StatsCanTableConfig(
        product_id="18100004",
        name="Consumer Price Index (Monthly)",
        category="Economy",
        frequency="monthly",
        description="Consumer Price Index and inflation measures",
        breakdowns=["geography", "products_and_product_groups"],
        priority=1
    ),

    # Economy - Interest Rates
    "10100139": StatsCanTableConfig(
        product_id="10100139",
        name="Interest Rates and Bond Yields",
        category="Economy",
        frequency="monthly",
        description="Bank of Canada interest rates and selected yields",
        breakdowns=["rate_type"],
        priority=1
    ),

    # Labour Market - Employment
    "14100287": StatsCanTableConfig(
        product_id="14100287",
        name="Employment by Province (Monthly)",
        category="Labour Market",
        frequency="monthly",
        description="Labour force characteristics by province",
        breakdowns=["geography", "labour_force_characteristics", "sex", "age_group"],
        priority=1
    ),

    # Housing - Housing Starts
    "34100143": StatsCanTableConfig(
        product_id="34100143",
        name="Housing Starts (Monthly)",
        category="Housing",
        frequency="monthly",
        description="New housing construction starts",
        breakdowns=["geography", "dwelling_type"],
        priority=1
    ),

    # Housing - Housing Prices
    "18100205": StatsCanTableConfig(
        product_id="18100205",
        name="New Housing Price Index",
        category="Housing",
        frequency="monthly",
        description="New housing price index by province",
        breakdowns=["geography"],
        priority=1
    ),

    # Trade
    "12100011": StatsCanTableConfig(
        product_id="12100011",
        name="International Merchandise Trade (Monthly)",
        category="Trade",
        frequency="monthly",
        description="Canadian international merchandise trade",
        breakdowns=["trade_direction", "principal_trading_areas"],
        priority=1
    ),
}


# =============================================================================
# STATS CANADA CATEGORY GROUPINGS
# =============================================================================

STATSCAN_CATEGORIES: Dict[str, StatsCanCategory] = {
    "economy": StatsCanCategory(
        name="Economy",
        description="GDP, CPI, interest rates, and economic indicators",
        tables=[
            STATSCAN_TABLE_CONFIGS["36100434"],  # GDP by industry (monthly)
            STATSCAN_TABLE_CONFIGS["36100222"],  # GDP by expenditure (quarterly)
            STATSCAN_TABLE_CONFIGS["18100004"],  # CPI
            STATSCAN_TABLE_CONFIGS["10100139"],  # Interest rates
        ]
    ),

    "labour": StatsCanCategory(
        name="Labour Market",
        description="Employment and labour force statistics",
        tables=[
            STATSCAN_TABLE_CONFIGS["14100287"],  # Employment
        ]
    ),

    "housing": StatsCanCategory(
        name="Housing",
        description="Housing starts and price indices",
        tables=[
            STATSCAN_TABLE_CONFIGS["34100143"],  # Housing starts
            STATSCAN_TABLE_CONFIGS["18100205"],  # Housing prices
        ]
    ),

    "trade": StatsCanCategory(
        name="International Trade",
        description="Import/export merchandise trade",
        tables=[
            STATSCAN_TABLE_CONFIGS["12100011"],  # International trade
        ]
    ),
}


# =============================================================================
# STATS CANADA HELPER FUNCTIONS
# =============================================================================

def get_table_config(product_id: str) -> Optional[StatsCanTableConfig]:
    """
    Get configuration for a specific table.

    Args:
        product_id: 8-digit Product ID (e.g., "36100434")

    Returns:
        StatsCanTableConfig or None if not found

    Example:
        >>> config = get_table_config("36100434")
        >>> print(config.name)  # "GDP by Industry (Monthly)"
    """
    return STATSCAN_TABLE_CONFIGS.get(product_id)


def get_category(category_name: str) -> Optional[StatsCanCategory]:
    """
    Get category by name.

    Args:
        category_name: Category name (e.g., "economy", "labour")

    Returns:
        StatsCanCategory or None if not found

    Example:
        >>> cat = get_category("economy")
        >>> print(len(cat.tables))  # 4
    """
    return STATSCAN_CATEGORIES.get(category_name.lower())


def get_all_product_ids() -> List[str]:
    """
    Get list of all configured product IDs.

    Returns:
        List of product ID strings

    Example:
        >>> pids = get_all_product_ids()
        >>> print(len(pids))  # 8
    """
    return list(STATSCAN_TABLE_CONFIGS.keys())


def get_tables_by_category(category_name: str) -> List[StatsCanTableConfig]:
    """
    Get all tables in a specific category.

    Args:
        category_name: Category name (e.g., "economy", "labour")

    Returns:
        List of StatsCanTableConfig objects

    Example:
        >>> tables = get_tables_by_category("economy")
        >>> for table in tables:
        ...     print(table.name)
    """
    category = get_category(category_name)
    if category:
        return category.tables
    return []


def get_priority_tables(priority: int = 1) -> List[StatsCanTableConfig]:
    """
    Get all high-priority tables across categories.

    Args:
        priority: Priority level (1=high, 2=normal)

    Returns:
        List of StatsCanTableConfig objects matching priority

    Example:
        >>> high_priority = get_priority_tables(priority=1)
        >>> print(len(high_priority))  # 8 (all are priority 1)
    """
    return [
        config for config in STATSCAN_TABLE_CONFIGS.values()
        if config.priority == priority
    ]


def search_tables(query: str) -> List[StatsCanTableConfig]:
    """
    Search tables by name or description (case-insensitive).

    Args:
        query: Search query string

    Returns:
        List of matching StatsCanTableConfig objects

    Example:
        >>> results = search_tables("GDP")
        >>> print(len(results))  # 2 (monthly and quarterly GDP)
    """
    query_lower = query.lower()
    results = []

    for config in STATSCAN_TABLE_CONFIGS.values():
        # Search in name
        if query_lower in config.name.lower():
            results.append(config)
            continue

        # Search in description
        if config.description and query_lower in config.description.lower():
            results.append(config)

    return results


def get_all_categories() -> Dict[str, StatsCanCategory]:
    """
    Get all category groupings.

    Returns:
        Dictionary of {category_name: StatsCanCategory}

    Example:
        >>> categories = get_all_categories()
        >>> for name, cat in categories.items():
        ...     print(f"{name}: {len(cat.tables)} tables")
    """
    return STATSCAN_CATEGORIES


# =============================================================================
# YFINANCE CONFIGURATIONS
# =============================================================================

@dataclass
class YFinanceTickerConfig:
    """Configuration for a single yfinance ticker."""

    ticker: str              # "AAPL", "^GSPC"
    name: str                # "Apple Inc.", "S&P 500"
    category: str            # "index", "stock", "volatility"
    sector: str              # "Technology", "Market"
    interval: str            # "1d" (default interval)
    priority: int = 2        # 1=high priority, 2=normal

    @property
    def cache_key(self) -> str:
        """Generate cache key for this ticker (used by CacheManager)."""
        return self.ticker

    def __repr__(self) -> str:
        return f"YFinanceTicker({self.ticker}: {self.name})"


# =============================================================================
# YFINANCE TICKER DEFINITIONS
# =============================================================================

# Build configurations from constants.py YFINANCE_TICKERS

def _build_yfinance_configs() -> Dict[str, YFinanceTickerConfig]:
    """Build YFinanceTickerConfig objects from constants.py."""
    configs = {}

    for ticker, info in YFINANCE_TICKERS.items():
        configs[ticker] = YFinanceTickerConfig(
            ticker=ticker,
            name=info["name"],
            category=info["category"].lower(),
            sector=info["sector"],
            interval=info["interval"],
            priority=info["priority"]
        )

    return configs


YFINANCE_TICKER_CONFIGS: Dict[str, YFinanceTickerConfig] = _build_yfinance_configs()


# =============================================================================
# YFINANCE CATEGORY GROUPINGS
# =============================================================================

YFINANCE_CATEGORIES: Dict[str, List[YFinanceTickerConfig]] = {
    "indices": [
        YFINANCE_TICKER_CONFIGS["^GSPC"],   # S&P 500
        YFINANCE_TICKER_CONFIGS["^DJI"],    # Dow Jones
        YFINANCE_TICKER_CONFIGS["^IXIC"],   # NASDAQ
    ],

    "volatility": [
        YFINANCE_TICKER_CONFIGS["^VIX"],    # VIX
    ],

    "tech_stocks": [
        YFINANCE_TICKER_CONFIGS["AAPL"],    # Apple
        YFINANCE_TICKER_CONFIGS["MSFT"],    # Microsoft
        YFINANCE_TICKER_CONFIGS["GOOGL"],   # Alphabet
        YFINANCE_TICKER_CONFIGS["AMZN"],    # Amazon
        YFINANCE_TICKER_CONFIGS["NVDA"],    # NVIDIA
        YFINANCE_TICKER_CONFIGS["TSLA"],    # Tesla
    ],
}


# =============================================================================
# YFINANCE HELPER FUNCTIONS
# =============================================================================

def get_ticker_config(ticker: str) -> Optional[YFinanceTickerConfig]:
    """
    Get configuration for a specific ticker.

    Args:
        ticker: Ticker symbol (e.g., "AAPL", "^GSPC")

    Returns:
        YFinanceTickerConfig or None if not found

    Example:
        >>> config = get_ticker_config("AAPL")
        >>> print(config.name)  # "Apple Inc."
    """
    return YFINANCE_TICKER_CONFIGS.get(ticker)


def get_tickers_by_category(category: str) -> List[YFinanceTickerConfig]:
    """
    Get all tickers in a specific category.

    Args:
        category: Category name (e.g., "indices", "tech_stocks", "volatility")

    Returns:
        List of YFinanceTickerConfig objects

    Example:
        >>> tickers = get_tickers_by_category("indices")
        >>> for ticker in tickers:
        ...     print(ticker.name)
    """
    return YFINANCE_CATEGORIES.get(category.lower(), [])


def get_all_tickers() -> List[str]:
    """
    Get list of all configured ticker symbols.

    Returns:
        List of ticker strings

    Example:
        >>> tickers = get_all_tickers()
        >>> print(len(tickers))  # 10
    """
    return list(YFINANCE_TICKER_CONFIGS.keys())


def get_priority_tickers(priority: int = 1) -> List[YFinanceTickerConfig]:
    """
    Get all tickers matching priority level.

    Args:
        priority: Priority level (1=high, 2=normal)

    Returns:
        List of YFinanceTickerConfig objects matching priority

    Example:
        >>> high_priority = get_priority_tickers(priority=1)
        >>> for ticker in high_priority:
        ...     print(ticker.ticker)  # ^GSPC, ^DJI, ^IXIC, ^VIX
    """
    return [
        config for config in YFINANCE_TICKER_CONFIGS.values()
        if config.priority == priority
    ]


def search_tickers(query: str) -> List[YFinanceTickerConfig]:
    """
    Search tickers by symbol or name (case-insensitive).

    Args:
        query: Search query string

    Returns:
        List of matching YFinanceTickerConfig objects

    Example:
        >>> results = search_tickers("apple")
        >>> print(results[0].ticker)  # "AAPL"
    """
    query_lower = query.lower()
    results = []

    for config in YFINANCE_TICKER_CONFIGS.values():
        # Search in ticker symbol
        if query_lower in config.ticker.lower():
            results.append(config)
            continue

        # Search in name
        if query_lower in config.name.lower():
            results.append(config)

    return results


def get_yfinance_category_names() -> List[str]:
    """
    Get list of all yfinance category names.

    Returns:
        List of category name strings

    Example:
        >>> categories = get_yfinance_category_names()
        >>> print(categories)  # ['indices', 'volatility', 'tech_stocks']
    """
    return list(YFINANCE_CATEGORIES.keys())
