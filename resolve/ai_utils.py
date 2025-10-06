import requests
import json
from django.conf import settings


def check_content_safety(text):
    """
    Check if the content is safe and legitimate.
    Returns 'LEGITIMATE' or 'FALSE_OR_ABUSIVE'
    
    In a real implementation, this would call an AI moderation API.
    For now, this is a placeholder that simulates the API call.
    """
    
    # Placeholder implementation - in production, replace with actual AI API
    # Example API call structure:
    """
    api_key = getattr(settings, 'AI_MODERATION_API_KEY', None)
    if not api_key:
        return 'LEGITIMATE'  # Default to allowing if no API key
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'text': text,
        'model': 'moderation-latest'  # Example model name
    }
    
    try:
        response = requests.post(
            'https://api.example.com/moderate',  # Replace with actual API endpoint
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('classification', 'LEGITIMATE')
        else:
            return 'LEGITIMATE'  # Default to allowing on API errors
            
    except requests.RequestException:
        return 'LEGITIMATE'  # Default to allowing on network errors
    """
    
    # Simple keyword-based moderation for demo purposes
    abusive_keywords = [
        'spam', 'fake', 'scam', 'hate', 'abuse', 'harassment',
        'threat', 'violence', 'illegal', 'fraud'
    ]
    
    text_lower = text.lower()
    for keyword in abusive_keywords:
        if keyword in text_lower:
            return 'FALSE_OR_ABUSIVE'
    
    # Check for very short or nonsensical content
    if len(text.strip()) < 10:
        return 'FALSE_OR_ABUSIVE'
    
    return 'LEGITIMATE'
