"""
EcoCompute AI / GreenGL - Main Application
Flask backend for GPU monitoring and carbon emissions tracking
"""

import os
import time
import json
import csv
from io import StringIO
from datetime import datetime
from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS

from gpu_monitor import get_monitor
from carbon_utils import get_calculator

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Get optional API key from environment
CARBON_API_KEY = os.environ.get("ELECTRICITY_MAPS_API_KEY")

# Initialize components
gpu_monitor = get_monitor()
carbon_calc = get_calculator(CARBON_API_KEY)

# Historical data storage (in-memory for simplicity, use database in production)
historical_data = []
MAX_HISTORY_POINTS = 1000


@app.route("/")
def index():
    """Serve the main dashboard"""
    return render_template("dashboard.html")


@app.route("/metrics")
def metrics():
    """API endpoint returning all current metrics as JSON"""
    # Get region from query param or use default
    region = request.args.get('region', 'US-CAL-CISO')
    
    # Get GPU metrics
    gpu_metrics = gpu_monitor.get_metrics()
    
    # Get carbon intensity
    carbon_intensity = carbon_calc.fetch_carbon_intensity(zone=region)
    
    # Calculate emissions
    carbon_data = carbon_calc.calculate_emissions(
        gpu_metrics.power_watts,
        carbon_intensity
    )
    
    # Build response
    response = {
        "timestamp": time.time(),
        "gpu": {
            "name": gpu_metrics.gpu_name,
            "power_watts": round(gpu_metrics.power_watts, 2),
            "temperature_celsius": round(gpu_metrics.temperature_celsius, 1),
            "utilization_percent": round(gpu_metrics.utilization_percent, 1),
            "memory_used_mb": round(gpu_metrics.memory_used_mb, 0),
            "memory_total_mb": round(gpu_metrics.memory_total_mb, 0),
            "memory_percent": round(
                (gpu_metrics.memory_used_mb / gpu_metrics.memory_total_mb) * 100, 1
            ),
            "is_simulated": gpu_metrics.is_simulated
        },
        "carbon": {
            "intensity_g_per_kwh": round(carbon_data.carbon_intensity_g_per_kwh, 1),
            "is_mocked": carbon_data.is_mocked,
            "region": carbon_data.region,
            "emissions_g_per_second": round(carbon_data.emissions_grams_per_second, 6),
            "emissions_g_per_minute": round(carbon_data.emissions_grams_per_second * 60, 4),
            "emissions_total_g": round(carbon_data.emissions_grams_total, 4),
            "suggestion": carbon_data.suggestion
        },
        "job": {
            "running": carbon_calc.is_job_running(),
            "runtime_seconds": round(carbon_calc.get_runtime_hours() * 3600, 1)
        }
    }
    
    # Store in historical data
    if len(historical_data) >= MAX_HISTORY_POINTS:
        historical_data.pop(0)
    historical_data.append(response)
    
    return jsonify(response)


@app.route("/job/start", methods=["POST"])
def start_job():
    """Start a simulated heavy job"""
    gpu_monitor.set_job_running(True)
    carbon_calc.start_job()
    return jsonify({"status": "started", "message": "Heavy job simulation started"})


@app.route("/job/stop", methods=["POST"])
def stop_job():
    """Stop the simulated job"""
    gpu_monitor.set_job_running(False)
    
    # Get final emissions before stopping
    final_emissions = carbon_calc.total_energy_wh
    runtime = carbon_calc.get_runtime_hours()
    
    carbon_calc.stop_job()
    
    return jsonify({
        "status": "stopped",
        "message": "Job simulation stopped",
        "summary": {
            "runtime_hours": round(runtime, 4),
            "total_energy_wh": round(final_emissions, 4)
        }
    })


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "gpu_mode": "simulated" if gpu_monitor.simulated else "real",
        "carbon_api": "connected" if not carbon_calc.is_mocked else "mocked"
    })


@app.route("/history")
def get_history():
    """Get historical metrics data"""
    # Optional query params for filtering
    limit = request.args.get('limit', type=int, default=100)
    start_time = request.args.get('start_time', type=float)
    end_time = request.args.get('end_time', type=float)
    
    filtered_data = historical_data
    
    # Apply time filters
    if start_time:
        filtered_data = [d for d in filtered_data if d['timestamp'] >= start_time]
    if end_time:
        filtered_data = [d for d in filtered_data if d['timestamp'] <= end_time]
    
    # Apply limit
    filtered_data = filtered_data[-limit:]
    
    return jsonify({
        "count": len(filtered_data),
        "data": filtered_data
    })


@app.route("/history/stats")
def history_stats():
    """Get statistical summary of historical data"""
    if not historical_data:
        return jsonify({"error": "No historical data available"}), 404
    
    # Calculate statistics
    power_values = [d['gpu']['power_watts'] for d in historical_data]
    emissions_values = [d['carbon']['emissions_total_g'] for d in historical_data]
    utilization_values = [d['gpu']['utilization_percent'] for d in historical_data]
    
    stats = {
        "total_records": len(historical_data),
        "time_range": {
            "start": historical_data[0]['timestamp'],
            "end": historical_data[-1]['timestamp'],
            "duration_seconds": historical_data[-1]['timestamp'] - historical_data[0]['timestamp']
        },
        "power": {
            "min": min(power_values),
            "max": max(power_values),
            "avg": sum(power_values) / len(power_values)
        },
        "emissions": {
            "min": min(emissions_values),
            "max": max(emissions_values),
            "current": emissions_values[-1]
        },
        "utilization": {
            "min": min(utilization_values),
            "max": max(utilization_values),
            "avg": sum(utilization_values) / len(utilization_values)
        }
    }
    
    return jsonify(stats)


@app.route("/export/sessions")
def export_sessions():
    """Export session data as CSV"""
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        'Timestamp',
        'GPU Name',
        'Power (W)',
        'Temperature (°C)',
        'Utilization (%)',
        'Memory Used (MB)',
        'Carbon Intensity (gCO2/kWh)',
        'Total Emissions (g)',
        'Region',
        'Job Running'
    ])
    
    # Write data rows
    for record in historical_data:
        writer.writerow([
            datetime.fromtimestamp(record['timestamp']).isoformat(),
            record['gpu']['name'],
            record['gpu']['power_watts'],
            record['gpu']['temperature_celsius'],
            record['gpu']['utilization_percent'],
            record['gpu']['memory_used_mb'],
            record['carbon']['intensity_g_per_kwh'],
            record['carbon']['emissions_total_g'],
            record['carbon']['region'],
            record['job']['running']
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=ecocompute-export-{int(time.time())}.csv'}
    )


@app.route("/region/<region_code>", methods=["POST"])
def update_region(region_code):
    """Update the carbon intensity region"""
    # Map region codes to Electricity Maps zones
    region_map = {
        "US": "US",
        "GB": "GB",
        "DE": "DE",
        "FR": "FR",
        "JP": "JP",
        "CN": "CN",
        "IN": "IN",
        "AU": "AU",
        "auto": "US-CAL-CISO"
    }
    
    zone = region_map.get(region_code, "US-CAL-CISO")
    
    # Clear cache to force new fetch
    carbon_calc.cached_intensity = None
    carbon_calc.cache_time = 0
    
    return jsonify({
        "status": "success",
        "region_code": region_code,
        "zone": zone,
        "message": f"Region updated to {region_code}"
    })


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("  🌱 EcoCompute AI / GreenGL")
    print("  GPU Power & Carbon Emissions Monitor")
    print("="*60)
    print(f"\n  GPU Mode: {'Simulated' if gpu_monitor.simulated else 'Real NVML'}")
    print(f"  Carbon API: {'API Key Set' if CARBON_API_KEY else 'Mocked Values'}")
    print(f"\n  Dashboard: http://localhost:5000")
    print(f"  Metrics API: http://localhost:5000/metrics")
    print("\n" + "="*60 + "\n")
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        gpu_monitor.shutdown()


if __name__ == "__main__":
    main()
