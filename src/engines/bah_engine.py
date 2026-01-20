import json
import os
from typing import Dict, Tuple, List


class BAHFetcher:
    """
    Simplified BAH lookup engine using official 2026 DoD data.
    Uses duty station names instead of zip codes.
    No caching, no web search - just clean lookups from verified data.
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.data_file = os.path.join(self.data_dir, 'bah_2026_real.json')
        self.bah_data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load the official 2026 BAH data."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    return data.get('locations', {})
            except Exception as e:
                print(f"Error loading BAH data: {e}")
                return {}
        return {}
    
    def get_all_locations(self) -> List[str]:
        """Get sorted list of all duty station names."""
        return sorted(list(self.bah_data.keys()))
    
    def get_rate(self, location: str, rank: str, has_dependents: bool) -> Tuple[float, str]:
        """
        Get BAH rate for a duty station.
        
        Args:
            location: Duty station name (e.g., "SAN DIEGO, CA")
            rank: Military rank (e.g., "E-6", "O-3")
            has_dependents: Whether service member has dependents
            
        Returns:
            Tuple of (rate, source) where source is always "official_2026"
        """
        dep_key = "with_dep" if has_dependents else "no_dep"
        
        # Check if location exists
        if location not in self.bah_data:
            print(f"⚠️ Location '{location}' not found in database")
            return 0.0, "not_found"
        
        location_data = self.bah_data[location]
        
        # Check if rank exists for this location
        if rank not in location_data:
            print(f"⚠️ Rank '{rank}' not found for {location}")
            return 0.0, "not_found"
        
        rank_data = location_data[rank]
        
        # Get the rate
        rate = rank_data.get(dep_key, 0)
        
        if rate > 0:
            return float(rate), "official_2026"
        else:
            return 0.0, "not_found"
    
    def get_location_info(self, location: str) -> Dict:
        """Get all ranks and rates for a location."""
        return self.bah_data.get(location, {})


# Global instance for easy import
bah_fetcher = BAHFetcher()
