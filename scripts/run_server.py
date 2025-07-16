import uvicorn

if __name__ == "__main__":
    print("🚀 Starting SatelliteLLM API server...")
    print("📝 API Documentation will be available at: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 