"""
Dataset configurations mapping friendly names to Statistics Canada Product IDs (PIDs)
and other metadata for easy data access.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TableConfig:
    """Configuration for a specific data table"""
    pid: str  # Product ID (e.g., "36100434")
    friendly_name: str
    description: str
    frequency: str  # "monthly", "quarterly", "annual"
    breakdowns: Optional[List[str]] = None  # Available geographic or categorical breakdowns
    update_priority: int = 1  # 1=high, 2=medium, 3=low (for batch updates)


@dataclass
class DatasetConfig:
    """Configuration for a logical dataset (may contain multiple tables)"""
    name: str
    category: str
    description: str
    tables: List[TableConfig]


# =============================================================================
# DATASET DEFINITIONS
# =============================================================================

DATASETS = {
    # =========================================================================
    # ECONOMY DATASETS
    # =========================================================================
    "gdp": DatasetConfig(
        name="GDP",
        category="Economy",
        description="Gross Domestic Product by industry and expenditure",
        tables=[
            TableConfig(
                pid="36100434",
                friendly_name="gdp_monthly",
                description="GDP by industry at basic prices (monthly)",
                frequency="monthly",
                breakdowns=["industry", "geography"],
                update_priority=1
            ),
            TableConfig(
                pid="36100222",
                friendly_name="gdp_quarterly_expenditure",
                description="GDP by expenditure (quarterly)",
                frequency="quarterly",
                breakdowns=["expenditure_category"],
                update_priority=1
            )
        ]
    ),
    
    "cpi": DatasetConfig(
        name="Consumer Price Index",
        category="Economy",
        description="Consumer Price Index and inflation measures",
        tables=[
            TableConfig(
                pid="18100004",
                friendly_name="cpi_monthly",
                description="Consumer Price Index (monthly)",
                frequency="monthly",
                breakdowns=["geography", "products_and_product_groups"],
                update_priority=1
            )
        ]
    ),
    
    "interest_rates": DatasetConfig(
        name="Interest Rates",
        category="Economy",
        description="Bank of Canada interest rates and bond yields",
        tables=[
            TableConfig(
                pid="10100139",
                friendly_name="bank_rates",
                description="Selected interest rates and yields",
                frequency="monthly",
                breakdowns=["rate_type"],
                update_priority=1
            )
        ]
    ),
    
    # =========================================================================
    # LABOUR MARKET DATASETS
    # =========================================================================
    "employment": DatasetConfig(
        name="Employment",
        category="Labour Market",
        description="Labour force survey employment statistics",
        tables=[
            TableConfig(
                pid="14100287",
                friendly_name="employment_monthly",
                description="Labour force characteristics by province (monthly)",
                frequency="monthly",
                breakdowns=["geography", "labour_force_characteristics", "sex", "age_group"],
                update_priority=1
            ),
            TableConfig(
                pid="14100355",
                friendly_name="employment_industry",
                description="Employment by industry (monthly)",
                frequency="monthly",
                breakdowns=["geography", "industry", "sex"],
                update_priority=2
            )
        ]
    ),
    
    "unemployment": DatasetConfig(
        name="Unemployment",
        category="Labour Market",
        description="Unemployment rates and characteristics",
        tables=[
            TableConfig(
                pid="14100017",
                friendly_name="unemployment_duration",
                description="Unemployment by duration",
                frequency="monthly",
                breakdowns=["geography", "duration", "sex", "age_group"],
                update_priority=2
            )
        ]
    ),
    
    "wages": DatasetConfig(
        name="Wages",
        category="Labour Market",
        description="Average hourly and weekly earnings",
        tables=[
            TableConfig(
                pid="14100063",
                friendly_name="average_earnings",
                description="Average hourly and weekly earnings",
                frequency="monthly",
                breakdowns=["geography", "industry", "earnings_type"],
                update_priority=2
            )
        ]
    ),
    
    # =========================================================================
    # HOUSING DATASETS
    # =========================================================================
    "housing_starts": DatasetConfig(
        name="Housing Starts",
        category="Housing",
        description="New housing construction starts",
        tables=[
            TableConfig(
                pid="34100143",
                friendly_name="housing_starts_monthly",
                description="Housing starts (monthly)",
                frequency="monthly",
                breakdowns=["geography", "dwelling_type"],
                update_priority=1
            )
        ]
    ),
    
    "housing_prices": DatasetConfig(
        name="Housing Prices",
        category="Housing",
        description="New and resale housing price indices",
        tables=[
            TableConfig(
                pid="18100205",
                friendly_name="new_housing_price_index",
                description="New Housing Price Index",
                frequency="monthly",
                breakdowns=["geography"],
                update_priority=1
            )
        ]
    ),
    
    # =========================================================================
    # TRADE DATASETS
    # =========================================================================
    "international_trade": DatasetConfig(
        name="International Trade",
        category="Trade",
        description="Canadian international merchandise trade",
        tables=[
            TableConfig(
                pid="12100011",
                friendly_name="trade_monthly",
                description="International merchandise trade (monthly)",
                frequency="monthly",
                breakdowns=["trade_direction", "principal_trading_areas"],
                update_priority=1
            )
        ]
    ),
    
    # =========================================================================
    # DEMOGRAPHICS DATASETS
    # =========================================================================
    "population": DatasetConfig(
        name="Population",
        category="Demographics",
        description="Population estimates and projections",
        tables=[
            TableConfig(
                pid="17100005",
                friendly_name="population_quarterly",
                description="Population estimates (quarterly)",
                frequency="quarterly",
                breakdowns=["geography", "age_group", "sex"],
                update_priority=2
            )
        ]
    ),
    
    # =========================================================================
    # BUSINESS DATASETS
    # =========================================================================
    "retail_trade": DatasetConfig(
        name="Retail Trade",
        category="Business",
        description="Retail trade sales by industry",
        tables=[
            TableConfig(
                pid="20100008",
                friendly_name="retail_sales_monthly",
                description="Retail trade sales by province and territory",
                frequency="monthly",
                breakdowns=["geography", "industry"],
                update_priority=2
            )
        ]
    ),
    
    "manufacturing": DatasetConfig(
        name="Manufacturing",
        category="Business",
        description="Manufacturing sales and inventories",
        tables=[
            TableConfig(
                pid="16100047",
                friendly_name="manufacturing_sales",
                description="Manufacturing sales by industry",
                frequency="monthly",
                breakdowns=["geography", "industry"],
                update_priority=2
            )
        ]
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dataset_by_friendly_name(friendly_name: str) -> Optional[tuple]:
    """
    Get dataset and table config by table's friendly name.
    
    Returns:
        tuple: (dataset_key, dataset_config, table_config) or None if not found
    """
    for dataset_key, dataset in DATASETS.items():
        for table in dataset.tables:
            if table.friendly_name == friendly_name:
                return dataset_key, dataset, table
    return None


def get_table_by_pid(pid: str) -> Optional[tuple]:
    """
    Get dataset and table config by Product ID.
    
    Returns:
        tuple: (dataset_key, dataset_config, table_config) or None if not found
    """
    for dataset_key, dataset in DATASETS.items():
        for table in dataset.tables:
            if table.pid == pid:
                return dataset_key, dataset, table
    return None


def get_all_pids() -> List[str]:
    """Get list of all Product IDs across all datasets."""
    pids = []
    for dataset in DATASETS.values():
        for table in dataset.tables:
            pids.append(table.pid)
    return pids


def get_datasets_by_category(category: str) -> dict:
    """Get all datasets in a specific category."""
    return {
        key: dataset 
        for key, dataset in DATASETS.items() 
        if dataset.category == category
    }


def get_all_categories() -> List[str]:
    """Get list of all unique categories."""
    return sorted(list(set(dataset.category for dataset in DATASETS.values())))


if __name__ == "__main__":
    # Test the configuration
    print("Available Categories:")
    for cat in get_all_categories():
        print(f"  - {cat}")
    
    print(f"\nTotal Datasets: {len(DATASETS)}")
    print(f"Total Tables: {len(get_all_pids())}")
    
    print("\nSample Dataset (GDP):")
    gdp = DATASETS["gdp"]
    print(f"  Name: {gdp.name}")
    print(f"  Category: {gdp.category}")
    print(f"  Tables: {len(gdp.tables)}")
    for table in gdp.tables:
        print(f"    - {table.friendly_name} (PID: {table.pid})")