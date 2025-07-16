from typing import Dict, Any, Tuple
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm():
    """Get the best available LLM with fallback options"""
    models_to_try = [
        "llama3.2:3b",      # Latest and most efficient
        "llama3:latest",    # Good balance
        "deepseek-r1:8b",   # Large reasoning model
        "deepseek-r1:1.5b", # Smaller reasoning model
        "deepseek-coder:1.3b" # Code-specialized
    ]
    
    for model_name in models_to_try:
        try:
            print(f"🔄 Trying model: {model_name}")
            llm = Ollama(model=model_name)
            # Test the model with a simple query
            test_response = llm.invoke("Hello")
            print(f"✅ Successfully connected to {model_name}")
            return llm
        except Exception as e:
            print(f"❌ {model_name} not available: {e}")
            continue
    
    print("⚠️ No LLM models available, falling back to rule-based summaries")
    return None

def create_satellite_prompt():
    """Create a specialized prompt for satellite change analysis optimized for Llama 3.2"""
    template = """
    You are a satellite imagery change detection expert specializing in conflict zones. Analyze the following satellite change detection data and generate a professional summary.

    {change_data}

    Please provide a summary that includes:
    1. A brief overview of the analysis results, focusing on significant changes
    2. Specific findings about vegetation changes
    3. Specific findings about urban development changes
    4. Pixel-level changes and their significance
    5. Environmental implications and potential causes (consider conflict-related damage)
    6. Data quality assessment

    The summary should be concise, professional, and include percentages where appropriate. Pay special attention to pixel-level changes which may indicate localized damage.
    """
    
    return PromptTemplate(
        input_variables=["change_data"],
        template=template
    )

def generate_summary(change_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Generate a natural language summary using an LLM, or fallback to rule-based summary.
    If pixel_change_percentage >= 10%, explicitly mention war/conflict in the summary.
    """
    pixel_change = change_data.get('pixel_change_percentage', 0.0)
    conflict_damage_detected = pixel_change >= 10.0
    # Compose a warning for major conflict damage
    conflict_warning = "\n\n⚠️ **ALERT:** The detected changes are consistent with widespread war-related destruction in Gaza during this period. Immediate humanitarian and environmental assessment is recommended.\n" if conflict_damage_detected else ""

    llm = get_llm()
    
    if llm is None:
        # Fallback to rule-based summary
        summary = generate_rule_based_summary(change_data)
        if conflict_damage_detected:
            summary += conflict_warning
    
    try:
        # Format change data for LLM
        formatted_data = format_change_data(change_data)
        
        # Create prompt and chain
        prompt = create_satellite_prompt()
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate summary
        result = chain.invoke({"change_data": formatted_data})
        
        # Extract text from result (invoke returns a dict with 'text' key)
        summary_text = result.get('text', str(result)).strip()
        
        # Calculate confidence based on data quality
        confidence = calculate_confidence(change_data)
        
        return summary_text, confidence
        
    except Exception as e:
        print(f"LLM generation failed: {e}")
        # Fallback to rule-based summary
        return generate_rule_based_summary(change_data)

def format_change_data(change_data: Dict[str, Any]) -> str:
    """Format change detection data into a string for LLM input."""
    analysis_type = change_data.get("analysis_type", "unknown")
    
    if analysis_type == "satellite_indices":
        # Format satellite indices data
        veg_changes = change_data.get("vegetation_changes", {})
        urban_changes = change_data.get("urban_changes", {})
        
        formatted = f"""
        Analysis Type: Satellite Indices (NDVI/NDBI)
        Total Change Percentage (combined): {change_data.get('total_change_percentage', 0):.2f}%
        Pixel-level Spectral Change: {change_data.get('pixel_change_percentage', 0):.2f}%
        
        Vegetation Changes (NDVI):
        - Loss: {veg_changes.get('loss_percentage', 0):.2f}%
        - Gain: {veg_changes.get('gain_percentage', 0):.2f}%
        - Net Change: {veg_changes.get('net_change', 0):.2f}%
        - Mean NDVI Change: {veg_changes.get('mean_ndvi_change', 0):.3f}
        
        Urban Changes (NDBI):
        - Growth: {urban_changes.get('growth_percentage', 0):.2f}%
        - Decline: {urban_changes.get('decline_percentage', 0):.2f}%
        - Net Change: {urban_changes.get('net_change', 0):.2f}%
        - Mean NDBI Change: {urban_changes.get('mean_ndbi_change', 0):.3f}
        """
    else:
        # Format RGB-based data
        channel_changes = change_data.get("channel_changes", {})
        formatted = f"""
        Analysis Type: RGB-based Analysis
        Total Change Percentage (pixel-level): {change_data.get('total_change_percentage', 0):.2f}%
        Pixel-level Spectral Change: {change_data.get('pixel_change_percentage', 0):.2f}%
        Change Type: {change_data.get('change_type', 'unknown')}
        
        Channel Changes:
        - Red Channel: {channel_changes.get('red', 0):.2f}%
        - Green Channel: {channel_changes.get('green', 0):.2f}%
        - Blue Channel: {channel_changes.get('blue', 0):.2f}%
        """
    
    return formatted

def calculate_confidence(change_data: Dict[str, Any]) -> float:
    """Calculate confidence score based on data quality and change magnitude"""
    analysis_type = change_data.get("analysis_type", "unknown")
    
    if analysis_type == "satellite_indices":
        # Higher confidence for satellite indices
        total_change = change_data.get("total_change_percentage", 0)
        
        if total_change < 1.0:
            return 0.95  # High confidence for minimal changes
        elif total_change < 5.0:
            return 0.90  # High confidence for moderate changes
        elif total_change < 15.0:
            return 0.85  # Good confidence for significant changes
        else:
            return 0.80  # Moderate confidence for major changes
    else:
        # Lower confidence for RGB-based analysis
        total_change = change_data.get("total_change_percentage", 0)
        
        if total_change < 1.0:
            return 0.85
        elif total_change < 5.0:
            return 0.75
        else:
            return 0.65

def generate_rule_based_summary(change_data: Dict[str, Any]) -> Tuple[str, float]:
    """
    Fallback rule-based summary generation.
    Returns a tuple of (summary, confidence_score).
    """
    # Extract key metrics
    total_change = change_data.get('total_change_percentage', 0)
    change_type = change_data.get('change_type', 'unknown')
    analysis_type = change_data.get('analysis_type', 'unknown')
    
    # Generate summary based on the data
    if analysis_type == "satellite_indices":
        veg_changes = change_data.get("vegetation_changes", {})
        urban_changes = change_data.get("urban_changes", {})
        
        summary = f"Satellite analysis detected {total_change:.1f}% total change. "
        
        if veg_changes:
            net_veg = veg_changes.get('net_change', 0)
            if net_veg < -1.0:
                summary += f"Vegetation loss of {abs(net_veg):.1f}% detected. "
            elif net_veg > 1.0:
                summary += f"Vegetation growth of {net_veg:.1f}% detected. "
        
        if urban_changes:
            net_urban = urban_changes.get('net_change', 0)
            if net_urban > 1.0:
                summary += f"Urban expansion of {net_urban:.1f}% detected. "
            elif net_urban < -1.0:
                summary += f"Urban decline of {abs(net_urban):.1f}% detected. "
    else:
        # RGB-based analysis
        if total_change < 1.0:
            summary = f"Minimal changes detected ({total_change:.1f}% total change). "
        elif total_change < 5.0:
            summary = f"Moderate changes detected ({total_change:.1f}% total change). "
        else:
            summary = f"Significant changes detected ({total_change:.1f}% total change). "
        
        channel_changes = change_data.get("channel_changes", {})
        if change_type == "vegetation":
            summary += f"Changes appear to be primarily vegetation-related, with {channel_changes.get('green', 0):.1f}% change in green channel. "
        elif change_type == "urban":
            summary += f"Changes appear to be primarily urban-related, with {channel_changes.get('red', 0):.1f}% change in red channel. "
        else:
            summary += f"Changes are distributed across color channels (R: {channel_changes.get('red', 0):.1f}%, G: {channel_changes.get('green', 0):.1f}%, B: {channel_changes.get('blue', 0):.1f}%). "
    
    # Calculate confidence
    confidence = calculate_confidence(change_data)
    
    return summary.strip(), confidence 