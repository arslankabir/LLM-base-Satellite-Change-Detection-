# 🔐 Google Earth Engine Authentication Guide

## **Google Earth Engine DOESN'T Use API Keys!**

Unlike other satellite data sources, Google Earth Engine uses **OAuth2 authentication** instead of API keys. This is actually better because it's more secure and doesn't require you to manage API keys.

## **Authentication Process:**

### **Step 1: Sign Up (FREE)**
1. Go to: https://signup.earthengine.google.com/
2. Sign up with your Google account
3. Wait for approval (usually 24-48 hours)
4. You'll receive an email when approved

### **Step 2: Install the API**
```bash
pip install earthengine-api
```

### **Step 3: Authenticate**
```bash
earthengine authenticate
```

This will:
- Open your browser
- Ask you to log in to your Google account
- Request permission to access Earth Engine
- Generate authentication tokens automatically

### **Step 4: Verify Authentication**
```python
import ee
ee.Initialize()
print("✅ Google Earth Engine authenticated!")
```

## **What Happens During Authentication:**

When you run `earthengine authenticate`:

1. **Browser opens** to Google's OAuth page
2. **You log in** with your Google account
3. **Google asks permission** to access Earth Engine
4. **Authentication tokens** are saved locally
5. **No API keys needed** - tokens are managed automatically

## **Authentication Files Location:**

The authentication tokens are stored in:
- **Windows**: `C:\Users\YourUsername\.config\earthengine\credentials`
- **Linux/Mac**: `~/.config/earthengine/credentials`

## **No API Key Management Needed!**

Unlike other services where you need to:
- Generate API keys
- Store them securely
- Rotate them regularly
- Worry about key exposure

Google Earth Engine handles all of this automatically with OAuth2.

## **Quick Setup Script:**

I created `setup_google_earth_engine.py` that handles the entire setup:

```bash
python setup_google_earth_engine.py
```

This script will:
1. Install required packages
2. Check if you're authenticated
3. Guide you through authentication if needed
4. Test the setup

## **Example Usage After Authentication:**

```python
import ee

# Initialize (uses stored authentication)
ee.Initialize()

# Get Sentinel-2 imagery (no API key needed!)
sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
image = sentinel2.filterBounds(roi).filterDate('2023-01-01', '2023-12-31').first()

# Download imagery
python download_google_earth_engine.py --source sentinel2 --bbox -74.1 40.7 -73.9 40.9 --start-date 2023-01-01 --end-date 2023-12-31
```

## **Why This is Better Than API Keys:**

- ✅ **More secure** - OAuth2 is industry standard
- ✅ **No key management** - tokens handled automatically
- ✅ **No key rotation** - Google manages token refresh
- ✅ **No key exposure risk** - tokens stored securely
- ✅ **User-specific** - tied to your Google account

## **Troubleshooting:**

If authentication fails:
1. Make sure you're approved for Earth Engine
2. Check your internet connection
3. Try running `earthengine authenticate` again
4. Clear browser cookies if needed

## **Next Steps:**

1. **Sign up**: https://signup.earthengine.google.com/
2. **Wait for approval** (check email)
3. **Run setup**: `python setup_google_earth_engine.py`
4. **Authenticate**: `earthengine authenticate`
5. **Download data**: Use the download scripts

No API keys needed - just your Google account and OAuth2 authentication! 