import numpy as np
from PIL import Image
from PIL import ImageStat

def extract_features(image: Image.Image):
    """
    Extract lightweight image features without TensorFlow.
    Uses color histograms, texture features, and image statistics.
    """
    # Convert to RGB and resize for consistency
    image = image.convert("RGB")
    image = image.resize((224, 224))
    
    img_array = np.array(image)
    
    # Feature vector to store all features
    features = []
    
    # 1. Color Histogram Features (RGB channels)
    for channel in range(3):  # R, G, B
        hist = np.histogram(img_array[:, :, channel], bins=32, range=(0, 256))[0]
        hist = hist / hist.sum()  # Normalize
        features.extend(hist)
    
    # 2. Image Statistics (mean, std for each channel)
    stats = ImageStat.Stat(image)
    for stat in [stats.mean, stats.stddev]:
        features.extend(stat)
    
    # 3. Dominant Colors (simplified - using color bins)
    # Reshape to get all pixels
    pixels = img_array.reshape(-1, 3)
    # Get dominant color by finding most common color bin
    bins = np.linspace(0, 256, 9)  # 8 bins per channel
    for channel in range(3):
        hist, _ = np.histogram(pixels[:, channel], bins=bins)
        features.extend(hist / len(pixels))  # Normalized histogram
    
    # 4. Texture Features (edge detection approximation using gradients)
    gray = image.convert("L")
    gray_array = np.array(gray)
    
    # Horizontal and vertical gradients
    h_gradient = np.diff(gray_array, axis=1)
    v_gradient = np.diff(gray_array, axis=0)
    
    # Gradient statistics
    features.append(np.mean(np.abs(h_gradient)))
    features.append(np.mean(np.abs(v_gradient)))
    features.append(np.std(h_gradient))
    features.append(np.std(v_gradient))
    
    # 5. Brightness and Contrast
    features.append(np.mean(gray_array))
    features.append(np.std(gray_array))
    
    # 6. Aspect ratio and size (normalized)
    width, height = image.size
    features.append(width / max(width, height))
    features.append(height / max(width, height))
    
    return np.array(features, dtype=np.float32)
