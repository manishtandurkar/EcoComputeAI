"""
GPU Monitor Module - EcoCompute AI / GreenGL
Handles GPU telemetry via NVML with automatic fallback to simulation
"""

import time
import math
import random
from dataclasses import dataclass
from typing import Optional

# Try to import nvidia-ml-py (imported as pynvml), set flag if unavailable
try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


@dataclass
class GPUMetrics:
    """Container for GPU telemetry data"""
    power_watts: float
    temperature_celsius: float
    memory_used_mb: float
    memory_total_mb: float
    utilization_percent: float
    gpu_name: str
    is_simulated: bool


class GPUMonitor:
    """Monitor GPU metrics using NVML or simulation fallback"""
    
    def __init__(self):
        self.nvml_initialized = False
        self.handle = None
        self.simulated = False
        self.job_running = False
        self._sim_start_time = time.time()
        
        # Simulation parameters
        self._sim_base_power = 15.0  # Idle power in watts
        self._sim_max_power = 250.0  # Max power under load
        self._sim_base_temp = 35.0   # Idle temperature
        self._sim_max_temp = 85.0    # Max temperature under load
        self._sim_memory_total = 8192.0  # 8GB simulated VRAM
        
        self._initialize()
    
    def _initialize(self):
        """Initialize NVML or fall back to simulation"""
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    self.nvml_initialized = True
                    print("✓ NVML initialized - Real GPU detected")
                    return
            except Exception as e:
                print(f"⚠ NVML initialization failed: {e}")
        
        self.simulated = True
        print("⚠ No GPU detected - Running in simulation mode")
    
    def set_job_running(self, running: bool):
        """Set whether a heavy job is running (for simulation)"""
        self.job_running = running
        if running:
            self._sim_start_time = time.time()
    
    def _get_simulation_metrics(self) -> GPUMetrics:
        """Generate simulated GPU metrics"""
        elapsed = time.time() - self._sim_start_time
        
        # Base oscillation for idle state (breathing pattern)
        idle_wave = math.sin(elapsed * 0.5) * 0.1 + 1.0
        
        if self.job_running:
            # Ramp up to heavy load with some noise
            ramp = min(1.0, (time.time() - self._sim_start_time) / 3.0)  # 3 second ramp
            load_factor = ramp * (0.7 + random.uniform(0, 0.3))  # 70-100% load
            
            power = self._sim_base_power + (self._sim_max_power - self._sim_base_power) * load_factor
            temp = self._sim_base_temp + (self._sim_max_temp - self._sim_base_temp) * load_factor * 0.8
            utilization = load_factor * 100
            memory_used = self._sim_memory_total * (0.3 + load_factor * 0.6)
        else:
            # Idle state with slight variations
            power = self._sim_base_power * idle_wave + random.uniform(-2, 2)
            temp = self._sim_base_temp + random.uniform(-1, 3)
            utilization = random.uniform(0, 8)
            memory_used = self._sim_memory_total * 0.15 + random.uniform(0, 200)
        
        return GPUMetrics(
            power_watts=max(5.0, power),
            temperature_celsius=max(25.0, temp),
            memory_used_mb=memory_used,
            memory_total_mb=self._sim_memory_total,
            utilization_percent=min(100, max(0, utilization)),
            gpu_name="Simulated GPU (Demo Mode)",
            is_simulated=True
        )
    
    def _get_real_metrics(self) -> GPUMetrics:
        """Get real GPU metrics via NVML"""
        try:
            # Power usage
            power_mw = pynvml.nvmlDeviceGetPowerUsage(self.handle)
            power_watts = power_mw / 1000.0
            
            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            
            # Memory
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            memory_used_mb = mem_info.used / (1024 * 1024)
            memory_total_mb = mem_info.total / (1024 * 1024)
            
            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            utilization = util.gpu
            
            # GPU Name
            name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            return GPUMetrics(
                power_watts=power_watts,
                temperature_celsius=float(temp),
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                utilization_percent=float(utilization),
                gpu_name=name,
                is_simulated=False
            )
        except Exception as e:
            print(f"⚠ Error reading GPU metrics: {e}")
            # Fall back to simulation on error
            self.simulated = True
            return self._get_simulation_metrics()
    
    def get_metrics(self) -> GPUMetrics:
        """Get current GPU metrics (real or simulated)"""
        if self.simulated or not self.nvml_initialized:
            return self._get_simulation_metrics()
        return self._get_real_metrics()
    
    def shutdown(self):
        """Clean up NVML resources"""
        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# Singleton instance
_monitor: Optional[GPUMonitor] = None


def get_monitor() -> GPUMonitor:
    """Get or create the global GPU monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = GPUMonitor()
    return _monitor
