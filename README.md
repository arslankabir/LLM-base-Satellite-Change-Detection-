# 🛰️ LLM-based Satellite Change Detection

A powerful AI-driven platform for detecting and analyzing changes in satellite imagery, with specialized capabilities for conflict zone monitoring. Combines computer vision, geospatial analysis, and large language models to provide actionable insights from satellite data.

## 🌟 Key Features

### **Core Analysis**
- **High-resolution satellite imagery processing** (10m resolution GeoTIFF)
- **Advanced change detection** using NDVI and NDBI satellite indices
- **AI-powered natural language summaries** using local Llama 3.2 model
- **Professional-grade analysis** with confidence scoring
- **Web interface** for easy image upload and analysis

### **Satellite Data Integration**
- **Google Earth Engine integration** for high-quality satellite data
- **Automatic data download** for any geographic region
- **Multiple satellite sources** (Sentinel-2, Landsat)
- **High-resolution GeoTIFF export** to Google Drive
- **Cloud cover filtering** for optimal image quality

### **Advanced Capabilities**
- **Multi-temporal analysis** (2023, 2024, 2025 data)
- **Geographic region targeting** (Gaza Strip case study included)
- **Professional reporting** with detailed statistics
- **RESTful API** for integration with other systems
- **Comprehensive testing suite** for validation

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Activate virtual environment
llmenv\Scripts\activate  # Windows
source llmenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
GEE_PROJECT_ID=your_gee_project_id
```

### 3. Start Services
```bash
# Start Ollama service (if not running)
ollama serve

# Start SatelliteLLM server
python main.py
```

### 4. Access the System
- **Web Interface**: `http://localhost:8000/static/frontend.html`
- **API Documentation**: `http://localhost:8000/docs`
- **API Endpoint**: `http://localhost:8000/generate-summary`

## 📡 API Usage

### Generate Change Summary

**Endpoint:** `POST /generate-summary`

**Request:**
- `before_image`: GeoTIFF/PNG/JPG file (before period)
- `after_image`: GeoTIFF/PNG/JPG file (after period)

**Response:**
```json
{
    "summary": "Satellite analysis indicates minimal environmental changes, with no significant loss or gain of vegetation cover (0.00% loss/gain). Urban development changes are also negligible, with no observed growth or decline.",
    "confidence": 0.95,
    "map_overlay_url": null
}
```

## 🛠️ Technical Architecture

### **Change Detection Engine (`change_detector.py`)**
- **NDVI Analysis**: Normalized Difference Vegetation Index for vegetation changes
- **NDBI Analysis**: Normalized Difference Built-up Index for urban development
- **Multi-format Support**: GeoTIFF, PNG, JPG processing
- **Professional Algorithms**: Threshold-based detection with configurable parameters

### **AI Integration (`gpt_summary.py`)**
- **Local LLM**: Ollama + Llama 3.2 for privacy and speed
- **Specialized Prompts**: Geospatial context optimization
- **Confidence Scoring**: Reliability assessment for each analysis
- **Fallback System**: Rule-based summaries when LLM unavailable

### **Satellite Data Pipeline**
- **Google Earth Engine**: High-quality satellite data access
- **Multi-source Support**: Sentinel-2 (10m), Landsat (30m)
- **Quality Filtering**: Cloud cover, date range, resolution optimization
- **Export System**: High-resolution GeoTIFF to Google Drive

## 📁 Project Structure

```
LLM-based-Satellite-Change-Detection/
├── main.py                          # FastAPI backend server
├── change_detector.py               # Core change detection engine
├── gpt_summary.py                   # AI summary generation
├── frontend.html                    # Web interface
├── requirements.txt                 # Python dependencies
├── .env                            # Environment configuration
│
├── 📥 Data Download Scripts
│   ├── download_gaza_strip_data.py      # Gaza Strip satellite data
│   ├── download_gaza_2025.py            # 2025 Gaza Strip data
│   ├── download_gaza_2025_high_res.py   # High-res 2025 data
│   └── gee_setup.py                     # Google Earth Engine setup
│
├── 🧪 Testing Scripts
│   ├── test_high_res_gaza.py            # High-res Gaza analysis
│   ├── test_gaza_analysis.py            # Standard Gaza analysis
│   └── test_system.py                   # General system testing
│
├── 📊 Data Directories
│   ├── gaza_high_res/                   # High-resolution GeoTIFF files
│   ├── gaza_strip_data/                 # Standard resolution data
│   └── sample_data/                     # Sample images for testing
│
└── 📚 Documentation
    ├── README.md                        # This file
    └── troubleshooting.md               # Common issues and solutions
```

## 🌍 Satellite Data Download

### **Gaza Strip Analysis (Case Study)**
```bash
# Download high-resolution 2023-2024 comparison
python download_gaza_strip_data.py

# Download 2025 data (current year)
python download_gaza_2025_high_res.py

# Test analysis with downloaded data
python test_high_res_gaza.py
```

### **Custom Region Download**
```bash
# Download for specific coordinates
python download_gaza_strip_data.py --year 2024 --max-cloud-cover 15

# Download timeline analysis (2023-2025)
python download_gaza_2025.py --timeline
```

### **High-Resolution Export**
```bash
# Export full-resolution GeoTIFF to Google Drive
python download_gaza_2025_high_res.py

# Files will be available in Google Drive folder: Gaza_Strip_High_Res_2025
```

## 🔧 Configuration

### **Environment Variables**
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Google Earth Engine
GEE_PROJECT_ID=your_gee_project_id

# API Configuration
API_HOST=localhost
API_PORT=8000
```

### **Google Earth Engine Setup**
1. **Install GEE Python API**:
   ```bash
   pip install earthengine-api
   ```

2. **Authenticate**:
   ```bash
   earthengine authenticate
   ```

3. **Set Project ID** in `.env` file

## 🧪 Testing and Validation

### **System Testing**
```bash
# Test with sample data
python test_system.py

# Test Gaza Strip analysis
python test_gaza_analysis.py

# Test high-resolution analysis
python test_high_res_gaza.py
```

### **Quality Assurance**
- **Multi-resolution testing**: Thumbnail vs GeoTIFF comparison
- **Confidence scoring**: Reliability assessment for each analysis
- **Error handling**: Robust fallback systems
- **Performance optimization**: Efficient processing for large files

## 📊 Analysis Results

### **Change Detection Metrics**
- **Vegetation Changes**: Loss/gain percentages using NDVI
- **Urban Development**: Growth/decline using NDBI
- **Total Change Percentage**: Overall environmental impact
- **Confidence Score**: Analysis reliability (0.0-1.0)

### **Output Formats**
- **JSON Reports**: Structured data for integration
- **Natural Language Summaries**: Human-readable insights
- **GeoTIFF Overlays**: Visual change maps (planned)
- **Professional Reports**: Export-ready documentation

## 🌟 Advanced Features

### **Multi-Temporal Analysis**
- **Timeline Analysis**: 2023 → 2024 → 2025 progression
- **Seasonal Comparison**: Same period across years
- **Change Trajectory**: Environmental trend analysis

### **Geographic Targeting**
- **Region-Specific Analysis**: Gaza Strip case study
- **Custom Coordinates**: Any geographic area
- **Multi-Scale Analysis**: Local to regional coverage

### **Professional Integration**
- **RESTful API**: Easy integration with existing systems
- **Web Interface**: User-friendly analysis platform
- **Batch Processing**: Multiple image pair analysis
- **Export Capabilities**: Google Drive integration

## 🔍 Troubleshooting

### **Common Issues**

1. **Ollama Connection Error**:
   ```bash
   # Start Ollama service
   ollama serve
   
   # Check model availability
   ollama list
   ```

2. **Google Earth Engine Authentication**:
   ```bash
   # Re-authenticate
   earthengine authenticate
   
   # Check project access
   python -c "import ee; ee.Initialize()"
   ```

3. **Large File Processing**:
   - Use high-resolution script for GeoTIFF files
   - Increase timeout for large uploads
   - Check available memory

### **Performance Optimization**
- **Use GeoTIFF format** for best analysis quality
- **Optimize cloud cover** (≤20% recommended)
- **Select appropriate resolution** (10m for detailed analysis)
- **Monitor system resources** during processing

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests** for new functionality
4. **Submit a pull request**

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Earth Engine** for satellite data access
- **Ollama** for local LLM capabilities
- **Sentinel-2** and **Landsat** for satellite imagery
- **FastAPI** for robust API framework
- **LangChain** for AI integration

## 📞 Support

For support and questions:
- **Issues**: GitHub Issues
- **Documentation**: This README and inline code comments
- **Examples**: Test scripts in the project

---

**SatelliteLLM**: Transforming satellite imagery into actionable environmental intelligence through the power of AI. 