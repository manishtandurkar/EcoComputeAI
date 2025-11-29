# 🌱 EcoCompute AI / GreenGL

**Real-time GPU Power & Carbon Emissions Monitor**

A comprehensive web application that monitors GPU power usage, calculates carbon emissions, and provides actionable insights through a beautiful, responsive dashboard with real-time charts and analytics.

## ✨ Features

### 🎨 Modern UI/UX
- **Dark/Light Theme Toggle**: Switch between themes with smooth animations
- **Glassmorphism Design**: Modern frosted glass aesthetic with backdrop blur
- **Responsive Layout**: Mobile-first design with touch-friendly controls
- **Real-time Animations**: Smooth transitions and animated charts

### 📊 Real-time Monitoring
- **GPU Telemetry**: Power usage (W), temperature (°C), memory usage, utilization %
- **Automatic Fallback**: Works with or without NVIDIA GPU (simulation mode)
- **Live Charts**: Power, utilization, and emissions history with Chart.js
- **Auto-refresh**: Updates every second with smooth animations

### 🌍 Carbon Tracking
- **Multi-region Support**: Select from 8+ regions worldwide
- **Carbon Intensity**: Real-time grid data or region-specific mocked values
- **CO₂ Equivalents**: Trees needed, driving miles, LED hours, phone charges
- **Smart Suggestions**: Recommendations based on grid carbon intensity

### 🔔 Alerts & Notifications
- **Sound Alerts**: Audio notifications for high carbon events
- **Browser Notifications**: Desktop notifications for critical alerts
- **Visual Warnings**: Color-coded indicators for carbon intensity levels
- **Alert Cooldown**: Prevents notification spam

### 📈 Session Tracking
- **Local Storage**: Automatic session history tracking
- **Session Statistics**: Duration, emissions, average power per session
- **Historical View**: Review past sessions with detailed metrics
- **Clear History**: Easy data management

### 💾 Data Export
- **CSV Export**: Download session data for analysis
- **Historical API**: RESTful API for programmatic access
- **Statistics Endpoint**: Aggregate stats and summaries
- **Time-based Filtering**: Query specific time ranges

### 🚀 Advanced Features
- **Job Simulation**: Test with simulated GPU workloads
- **Real-time Charts**: 30-point rolling history for all metrics
- **Memory Visualization**: Progress bars for GPU memory usage
- **Performance Optimized**: Efficient updates and rendering

## 🚀 Quick Start

### Option 1: Easy Launch (Windows)
Double-click `start.ps1` - it will automatically check dependencies and start the server!

### Option 2: Interactive Setup
```bash
python run.py
```
This script will check your environment, install dependencies if needed, and launch the server.

### Option 3: Manual Setup

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run the Application
```bash
python app.py
```

#### 3. Open Dashboard
Navigate to: **http://localhost:5000**

The dashboard will automatically start monitoring and displaying real-time metrics!

> 💡 **First time?** Check out [QUICKSTART.md](QUICKSTART.md) for a detailed walkthrough!

## 🔧 Configuration

### Optional: Real Carbon Intensity Data

To use real carbon intensity data from [Electricity Maps](https://www.electricitymaps.com/):

1. Sign up for a free API key
2. Set the environment variable:

```bash
# Windows PowerShell
$env:ELECTRICITY_MAPS_API_KEY = "your-api-key"

# Windows CMD
set ELECTRICITY_MAPS_API_KEY=your-api-key

# Linux/Mac
export ELECTRICITY_MAPS_API_KEY=your-api-key
```

3. Run the app normally

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard (HTML) |
| `/metrics` | GET | Current metrics (JSON) |
| `/metrics?region=US` | GET | Metrics for specific region |
| `/job/start` | POST | Start simulated heavy job |
| `/job/stop` | POST | Stop simulated job |
| `/health` | GET | Health check status |
| `/history` | GET | Historical metrics data |
| `/history?limit=50` | GET | Limited historical data |
| `/history/stats` | GET | Statistical summary |
| `/export/sessions` | GET | Export CSV file |
| `/region/<code>` | POST | Update carbon region |

### Supported Regions
- `US` - United States
- `GB` - United Kingdom
- `DE` - Germany
- `FR` - France
- `JP` - Japan
- `CN` - China
- `IN` - India
- `AU` - Australia
- `auto` - Auto-detect (default)

## Sample `/metrics` Response

```json
{
  "timestamp": 1732896000.0,
  "gpu": {
    "name": "Simulated GPU (Demo Mode)",
    "power_watts": 15.5,
    "temperature_celsius": 35.2,
    "utilization_percent": 3.5,
    "memory_used_mb": 1229,
    "memory_total_mb": 8192,
    "memory_percent": 15.0,
    "is_simulated": true
  },
  "carbon": {
    "intensity_g_per_kwh": 650.0,
    "is_mocked": true,
    "region": "Mocked (US Average)",
    "emissions_g_per_second": 0.0028,
    "emissions_g_per_minute": 0.168,
    "emissions_total_g": 0.0,
    "suggestion": "⚠️ High carbon intensity. Consider deferring the job."
  },
  "job": {
    "running": false,
    "runtime_seconds": 0.0
  }
}
```

## Carbon Calculation Formula

```
carbon_grams = (power_watts / 1000) × carbon_intensity_g_per_kwh × runtime_hours
```

## 📖 Usage Guide

### Dashboard Overview

1. **Theme Toggle** (🌙/☀️): Switch between dark and light modes
2. **Region Selector**: Choose your carbon intensity region
3. **Start Job**: Begin a simulated GPU workload
4. **Stop Job**: End the simulation and record session
5. **Export CSV**: Download all session data
6. **Clear History**: Remove stored session records

### Understanding Metrics

**Power Draw**: Real-time GPU power consumption in watts
**Temperature**: GPU core temperature in Celsius
**Utilization**: GPU compute utilization percentage
**Memory**: VRAM usage and capacity

**Carbon Intensity**: Grid carbon emissions (gCO₂/kWh)
- Green: < 280 (Good time to run workloads)
- Yellow: 280-400 (Moderate)
- Red: > 400 (High - consider deferring)

### CO₂ Equivalents Explained

- **Trees Needed**: Trees required to absorb this CO₂ in one year (21kg/tree/year)
- **Miles Driven**: Equivalent miles in an average car (404g CO₂/mile)
- **LED Hours**: Hours of 10W LED bulb operation
- **Phone Charges**: Number of smartphone charges (15Wh each)

### Notifications

The app will alert you when:
- Carbon intensity exceeds 400 gCO₂/kWh (Warning)
- Carbon intensity exceeds 600 gCO₂/kWh (Critical)
- Sound alerts can be toggled in the configuration

### Session History

All job sessions are automatically tracked with:
- Start/end timestamps
- Total duration
- Average power consumption
- Total CO₂ emissions
- Region used

Data persists in browser localStorage and can be exported to CSV.

## 🎨 Customization

### Modify Alert Thresholds

Edit `templates/dashboard.html` configuration:

```javascript
const CONFIG = {
    updateInterval: 1000,           // Update frequency (ms)
    chartMaxPoints: 30,              // Chart history length
    highCarbonThreshold: 400,        // Warning threshold (gCO₂/kWh)
    criticalCarbonThreshold: 600,    // Critical threshold
    alertCooldown: 30000,            // Alert cooldown (ms)
    soundEnabled: true               // Enable sound alerts
};
```

### Add Custom Regions

Edit `carbon_utils.py`:

```python
REGION_MOCK_INTENSITIES = {
    "US": 450,
    "YOUR-REGION": 300,  # Add your region
    # ... more regions
}
```

## 📂 Project Structure

```
PitchIt/
├── app.py              # Flask backend + REST API
├── gpu_monitor.py      # GPU telemetry (NVML + simulation)
├── carbon_utils.py     # Carbon intensity & emissions calc
├── templates/
│   └── dashboard.html  # Frontend dashboard
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🖥️ GPU Mode

- **Real Mode**: If NVIDIA GPU is detected and pynvml works, real telemetry is used
- **Simulation Mode**: If no GPU or pynvml fails, realistic simulated data is generated

The app automatically detects and falls back gracefully, making it perfect for:
- Development without GPU hardware
- Demonstrations and presentations
- Testing and debugging

## 🌐 Browser Support

Tested and optimized for:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

### Required Browser Features
- LocalStorage (session history)
- Canvas API (charts)
- Notifications API (alerts)
- Web Audio API (sound alerts)

## 🔒 Privacy & Data

- All session history stored locally in your browser
- No data sent to external servers (except optional Electricity Maps API)
- Historical data stored in-memory on server (resets on restart)
- CSV exports contain only your session data

## 🐛 Troubleshooting

**Charts not appearing?**
- Ensure JavaScript is enabled
- Check browser console for errors
- Clear browser cache

**High memory usage?**
- Historical data limited to 1000 points
- Chart history limited to 30 points
- Clear session history periodically

**Notifications not working?**
- Grant notification permissions in browser
- Check browser notification settings
- Some browsers block notifications in HTTP (use HTTPS)

**API errors?**
- Check Electricity Maps API key
- Verify environment variable is set
- App will automatically fall back to mocked data

## 🚀 Production Deployment

For production use:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Add persistent storage:**
   - Replace in-memory historical data with database (SQLite, PostgreSQL)
   - Implement session management with Redis

3. **Enable HTTPS:**
   - Required for browser notifications
   - Use nginx or similar reverse proxy

4. **Set up monitoring:**
   - Application logs
   - Error tracking (Sentry, etc.)
   - Uptime monitoring

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional CO₂ equivalent calculations
- More chart types and visualizations
- Database integration for persistent history
- User authentication and multi-user support
- GPU compute task optimization suggestions
- Integration with cloud GPU providers

## 📄 License

MIT License - Feel free to use and modify for your needs!

## 🙏 Credits

Built with:
- Flask (Python web framework)
- Chart.js (beautiful charts)
- pynvml (NVIDIA GPU monitoring)
- Electricity Maps API (carbon intensity data)

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with 🌱 for a greener computing future**
