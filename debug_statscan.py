"""
Debug script to inspect Stats Canada metadata structure for product ID 36100434
"""
from src.services.statscan_api import StatsCanService
import json

# Initialize service
sc_service = StatsCanService()

# Fetch metadata for GDP table
product_id = "36100434"
print(f"Fetching metadata for product ID: {product_id}")
metadata = sc_service.get_cube_metadata(product_id)

if metadata:
    print(f"\nMetadata retrieved successfully")
    print(f"\nTable Title: {metadata.get('cubeTitleEn')}")
    print(f"Frequency: {metadata.get('frequencyCode')}")

    # Inspect dimensions structure
    dimensions = metadata.get("dimension", [])
    print(f"\nDimensions found: {len(dimensions)}")

    for i, dim in enumerate(dimensions):
        dim_name = dim.get("dimensionNameEn", "Unknown")
        members = dim.get("member", [])
        print(f"\nDimension {i}: {dim_name}")
        print(f"  Members count: {len(members)}")

        if members:
            # Show first member structure
            first_member = members[0]
            print(f"  First member keys: {list(first_member.keys())}")
            print(f"  First member sample: {json.dumps(first_member, indent=2)[:300]}...")

    # Check for coordinateToMemberId
    if "object" in metadata:
        obj = metadata["object"]
        if "coordinateToMemberId" in obj:
            coord_map = obj["coordinateToMemberId"]
            print(f"\ncoordinateToMemberId found with {len(coord_map)} entries")
            # Show first few entries
            for i, (coord, vec_id) in enumerate(list(coord_map.items())[:5]):
                print(f"  {coord} -> {vec_id}")

    # Save full metadata to file for inspection
    with open("metadata_36100434.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nFull metadata saved to metadata_36100434.json")

else:
    print(f"Failed to retrieve metadata for product ID: {product_id}")
