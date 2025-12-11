"""
Debug script to find vector IDs for product ID 36100434
"""
from src.services.statscan_api import StatsCanService

# Initialize service
sc_service = StatsCanService()
product_id = "36100434"

print(f"Looking for vectors for product ID: {product_id}\n")

# Approach 1: Check changed series list
print("=== Approach 1: Changed Series List ===")
changed_series = sc_service.get_changed_series_list()
print(f"Total changed series today: {len(changed_series)}")

# Filter for our product ID
our_series = [s for s in changed_series if str(s.get('productId')) == product_id]
print(f"Changed series for product {product_id}: {len(our_series)}")

if our_series:
    print("\nFirst 5 vectors from changed series:")
    for i, series in enumerate(our_series[:5]):
        print(f"  Vector ID: {series.get('vectorId')} - Coordinate: {series.get('coordinate')}")

# Approach 2: Try known vector IDs
print("\n=== Approach 2: Test Known Vectors ===")
print("Testing known vector IDs from Stats Canada website...")

# These are documented vectors for this table (GDP All industries, seasonally adjusted)
test_vectors = [41690973, 41691182]  # Known vectors for this table

for vec_id in test_vectors:
    info = sc_service.get_series_info_from_vector(vec_id)
    if info:
        print(f"\nVector {vec_id}:")
        print(f"  Title: {info.get('seriesTitleEn', 'N/A')[:80]}...")
        print(f"  Product ID: {info.get('productId')}")
    else:
        print(f"\nVector {vec_id}: Not found or error")

# Approach 3: Test with known vectors
print("\n=== Approach 3: Fetch Data with Known Vectors ===")
try:
    data = sc_service.get_data_from_vectors_latest_n_periods(test_vectors, 3)
    if data:
        print(f"Successfully fetched data for {len(data)} vectors")
        print(f"First vector data points: {len(data[0].get('vectorDataPoint', []))}")
    else:
        print("No data returned")
except Exception as e:
    print(f"Error fetching data: {e}")
