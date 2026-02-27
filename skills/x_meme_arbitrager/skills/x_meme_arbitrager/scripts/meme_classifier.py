import sys
import json
import numpy as np
from datetime import datetime

# Simple embedding-like vectors for meme keywords (pre-defined for no deps)
MEME_VECTORS = {
    'hype': np.array([1, 0.8, 0.9, 0.7]),  # moon, pump, viral, tothemoon
    'fud': np.array([-1, -0.8, -0.9, -0.7]),  # dump, rug, scam, crash
    'neutral': np.array([0, 0, 0, 0])
}
KEYWORDS = {
    'hype': ['moon', 'pump', 'viral', 'tothemoon', 'bullish', 'buy'],
    'fud': ['dump', 'rug', 'scam', 'crash', 'bearish', 'sell'],
}

def classify_meme(data):
    """
    Classifies meme hype using basic vector similarity and engagement weighting.
    Returns hype_level (low/medium/high) and confidence.
    Handles empty data.
    """
    if not data:
        return {"hype_level": "neutral", "confidence": 0.0}
    
    try:
        vectors = []
        weights = []
        for item in data:
            text = item.get('text', '').lower()
            eng = item.get('engagements', 1)
            vec = np.zeros(4)
            for kw in KEYWORDS['hype']:
                if kw in text: vec += MEME_VECTORS['hype']
            for kw in KEYWORDS['fud']:
                if kw in text: vec += MEME_VECTORS['fud']
            if np.linalg.norm(vec) > 0:
                vec /= np.linalg.norm(vec)  # Normalize
            vectors.append(vec)
            weights.append(eng)  # Weight by engagements
        
        if not vectors:
            return {"hype_level": "neutral", "confidence": 0.0}
        
        # Weighted average vector
        weighted_vec = np.average(vectors, axis=0, weights=weights)
        
        # Similarity to classes
        sim_hype = np.dot(weighted_vec, MEME_VECTORS['hype']) / (np.linalg.norm(weighted_vec) * np.linalg.norm(MEME_VECTORS['hype']) or 1)
        sim_fud = np.dot(weighted_vec, MEME_VECTORS['fud']) / (np.linalg.norm(weighted_vec) * np.linalg.norm(MEME_VECTORS['fud']) or 1)
        
        score = sim_hype - sim_fud
        if score > 0.5:
            level = "high"
        elif score > 0:
            level = "medium"
        elif score < -0.5:
            level = "low"
        else:
            level = "neutral"
        
        confidence = abs(score)  # 0-1
        
        return {"hype_level": level, "confidence": float(confidence)}
    
    except Exception as e:
        return {"hype_level": "neutral", "confidence": 0.0, "error": str(e)}

if __name__ == "__main__":
    try:
        input_json = sys.stdin.read().strip()
        data = json.loads(input_json)
        result = classify_meme(data)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"hype_level": "neutral", "confidence": 0.0, "error": str(e)}))
        sys.exit(1)
