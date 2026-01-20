"""
BAH Data Ingestion Script
Reads 2026 BAH Rate Excel files and generates bah_2026_real.json
"""
import pandas as pd
import json
import re
from pathlib import Path


def normalize_rank(raw_rank: str) -> str:
    """
    Convert CSV rank format to app format.
    E01 -> E-1, W02 -> W-2, O03E -> O-3E
    """
    if not raw_rank or raw_rank == 'MHA':
        return None
    
    # Handle special cases
    if raw_rank == 'MHA_NAME':
        return None
    
    # Extract letter prefix (E, W, O)
    match = re.match(r'^([EWO])(\d+)([A-Z]*)$', raw_rank)
    if match:
        prefix = match.group(1)
        number = match.group(2).lstrip('0')  # Remove leading zeros
        suffix = match.group(3)
        return f"{prefix}-{number}{suffix}"
    
    return raw_rank


def ingest_bah_data():
    """
    Main ingestion function.
    Reads both Excel files and creates master JSON.
    """
    project_root = Path(__file__).parent.parent
    with_file = project_root / "2026 BAH Rates - With.xlsx"
    without_file = project_root / "2026 BAH Rates - Without.xlsx"
    
    print(f"📂 Reading: {with_file.name}")
    df_with = pd.read_excel(with_file, header=1)  # Skip first row, use row 2 as header
    print(f"   Columns: {list(df_with.columns[:5])}...")  # Show first 5 columns
    print(f"   Shape: {df_with.shape}")
    
    print(f"📂 Reading: {without_file.name}")
    df_without = pd.read_excel(without_file, header=1)  # Skip first row, use row 2 as header
    print(f"   Columns: {list(df_without.columns[:5])}...")
    print(f"   Shape: {df_without.shape}")
    
    # Master dictionary
    bah_data = {
        "description": "2026 BAH (Basic Allowance for Housing) rates - OFFICIAL DoD DATA",
        "year": 2026,
        "data_source": "Official DoD 2026 BAH Rates (DFAS)",
        "note": "Complete dataset - all duty stations, all ranks",
        "locations": {}
    }
    
    print(f"\n🔄 Processing {len(df_with)} locations...")
    
    # Process WITH dependents
    for idx, row in df_with.iterrows():
        location = row.get('MHA_NAME', '').strip()
        if not location or location == 'MHA_NAME':
            continue
        
        if location not in bah_data["locations"]:
            bah_data["locations"][location] = {}
        
        # Process all rank columns
        for col in df_with.columns:
            if col == 'MHA' or col == 'MHA_NAME':
                continue
            
            normalized_rank = normalize_rank(col)
            if not normalized_rank:
                continue
            
            rate = row.get(col)
            if pd.notna(rate):
                if normalized_rank not in bah_data["locations"][location]:
                    bah_data["locations"][location][normalized_rank] = {}
                
                bah_data["locations"][location][normalized_rank]["with_dep"] = int(rate)
    
    # Process WITHOUT dependents
    for idx, row in df_without.iterrows():
        location = row.get('MHA_NAME', '').strip()
        if not location or location == 'MHA_NAME':
            continue
        
        if location not in bah_data["locations"]:
            bah_data["locations"][location] = {}
        
        # Process all rank columns
        for col in df_without.columns:
            if col == 'MHA' or col == 'MHA_NAME':
                continue
            
            normalized_rank = normalize_rank(col)
            if not normalized_rank:
                continue
            
            rate = row.get(col)
            if pd.notna(rate):
                if normalized_rank not in bah_data["locations"][location]:
                    bah_data["locations"][location][normalized_rank] = {}
                
                bah_data["locations"][location][normalized_rank]["no_dep"] = int(rate)
    
    # Save to JSON
    output_path = project_root / "src" / "data" / "bah_2026_real.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(bah_data, f, indent=2)
    
    print(f"\n✅ SUCCESS!")
    print(f"📊 Locations processed: {len(bah_data['locations'])}")
    print(f"💾 Saved to: {output_path}")
    
    # Show sample
    sample_location = list(bah_data["locations"].keys())[0]
    sample_ranks = list(bah_data["locations"][sample_location].keys())[:3]
    print(f"\n📝 Sample data for '{sample_location}':")
    for rank in sample_ranks:
        data = bah_data["locations"][sample_location][rank]
        print(f"  {rank}: ${data.get('with_dep', 0)} (with) / ${data.get('no_dep', 0)} (without)")


if __name__ == "__main__":
    ingest_bah_data()
