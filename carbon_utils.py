"""
Carbon Utilities - EcoCompute AI / GreenGL
Carbon intensity fetching, emissions calculation, and suggestions
"""

import time
import random
from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class CarbonData:
    """Container for carbon-related calculations"""
    carbon_intensity_g_per_kwh: float
    is_mocked: bool
    region: str
    emissions_grams_per_second: float
    emissions_grams_total: float
    suggestion: str


# Configuration
CARBON_INTENSITY_THRESHOLD = 400  # gCO2/kWh - above this is considered "high"
DEFAULT_MOCK_INTENSITY = 650  # Default mocked value
ELECTRICITY_MAPS_API_URL = "https://api.electricitymap.org/v3/carbon-intensity/latest"

# Region-specific mocked carbon intensities (gCO2/kWh) when API is unavailable
REGION_MOCK_INTENSITIES = {
    "US": 450,
    "US-CAL-CISO": 350,
    "GB": 250,
    "DE": 420,
    "FR": 60,
    "JP": 550,
    "CN": 700,
    "IN": 750,
    "AU": 680
}


class CarbonCalculator:
    """Calculate carbon emissions and provide suggestions"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cached_intensity: Optional[float] = None
        self.cache_time: float = 0
        self.cache_duration: float = 300  # 5 minutes cache
        self.job_start_time: Optional[float] = None
        self.total_energy_wh: float = 0.0
        self.last_update_time: float = time.time()
        self.is_mocked = True
        self.region = "Unknown"
    
    def start_job(self):
        """Mark the start of a job for emissions tracking"""
        self.job_start_time = time.time()
        self.total_energy_wh = 0.0
        self.last_update_time = time.time()
    
    def stop_job(self):
        """Mark the end of a job"""
        self.job_start_time = None
    
    def is_job_running(self) -> bool:
        """Check if a job is currently being tracked"""
        return self.job_start_time is not None
    
    def get_runtime_hours(self) -> float:
        """Get the runtime of the current job in hours"""
        if self.job_start_time is None:
            return 0.0
        return (time.time() - self.job_start_time) / 3600.0
    
    def fetch_carbon_intensity(self, zone: str = "US-CAL-CISO") -> float:
        """
        Fetch real-time carbon intensity from Electricity Maps API.
        Falls back to mocked value if API fails.
        """
        # Check cache first (but only if same zone)
        if self.cached_intensity and (time.time() - self.cache_time) < self.cache_duration and self.region == zone:
            return self.cached_intensity
        
        # Try to fetch from API
        if self.api_key:
            try:
                headers = {"auth-token": self.api_key}
                params = {"zone": zone}
                response = requests.get(
                    ELECTRICITY_MAPS_API_URL,
                    headers=headers,
                    params=params,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    intensity = data.get("carbonIntensity", DEFAULT_MOCK_INTENSITY)
                    self.cached_intensity = intensity
                    self.cache_time = time.time()
                    self.is_mocked = False
                    self.region = zone
                    return intensity
            except Exception as e:
                print(f"⚠ Carbon API error: {e}")
        
        # Fall back to mocked value with regional variation
        self.is_mocked = True
        
        # Get region-specific base intensity or use default
        base_intensity = REGION_MOCK_INTENSITIES.get(zone, DEFAULT_MOCK_INTENSITY)
        
        # Add some time-based variation to simulate real-world fluctuations
        time_factor = abs((time.time() % 3600) / 3600)  # 0-1 based on hour
        variation = random.uniform(-50, 50) * time_factor
        mocked_value = max(50, base_intensity + variation)
        
        self.cached_intensity = mocked_value
        self.cache_time = time.time()
        self.region = f"Mocked ({zone})"
        
        return mocked_value
    
    def update_energy_consumption(self, power_watts: float):
        """Update total energy consumption based on current power draw"""
        current_time = time.time()
        if self.job_start_time is not None:
            time_delta_hours = (current_time - self.last_update_time) / 3600.0
            energy_wh = power_watts * time_delta_hours
            self.total_energy_wh += energy_wh
        self.last_update_time = current_time
    
    def calculate_emissions(self, power_watts: float, carbon_intensity: float) -> CarbonData:
        """
        Calculate carbon emissions using the formula:
        carbon_grams = (power_watts / 1000) * carbon_intensity * runtime_hours
        """
        self.update_energy_consumption(power_watts)
        
        # Calculate emissions rate (per second for real-time display)
        # power_watts / 1000 = kW
        # carbon_intensity is in gCO2/kWh
        # Divide by 3600 to get per-second rate
        emissions_per_second = (power_watts / 1000) * carbon_intensity / 3600
        
        # Calculate total emissions for the job
        runtime_hours = self.get_runtime_hours()
        if runtime_hours > 0:
            # Use integrated energy for more accurate calculation
            total_emissions = (self.total_energy_wh / 1000) * carbon_intensity
        else:
            total_emissions = 0.0
        
        # Generate suggestion
        suggestion = self.get_suggestion(carbon_intensity)
        
        return CarbonData(
            carbon_intensity_g_per_kwh=carbon_intensity,
            is_mocked=self.is_mocked,
            region=self.region,
            emissions_grams_per_second=emissions_per_second,
            emissions_grams_total=total_emissions,
            suggestion=suggestion
        )
    
    def get_suggestion(self, carbon_intensity: float) -> str:
        """Generate a suggestion based on current carbon intensity"""
        if carbon_intensity > CARBON_INTENSITY_THRESHOLD:
            return "⚠️ High carbon intensity. Consider deferring the job."
        elif carbon_intensity > CARBON_INTENSITY_THRESHOLD * 0.7:
            return "⚡ Moderate carbon intensity. Proceed with awareness."
        else:
            return "✅ Good time to run heavy workloads."


# Singleton instance
_calculator: Optional[CarbonCalculator] = None


def get_calculator(api_key: Optional[str] = None) -> CarbonCalculator:
    """Get or create the global carbon calculator instance"""
    global _calculator
    if _calculator is None:
        _calculator = CarbonCalculator(api_key)
    return _calculator
