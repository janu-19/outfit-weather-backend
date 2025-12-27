"""
Cloudinary configuration for image storage
"""
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Try to get credentials from CLOUDINARY_URL first, then individual variables
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    # Parse CLOUDINARY_URL format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    try:
        parsed = urlparse(CLOUDINARY_URL)
        API_KEY = parsed.username
        API_SECRET = parsed.password
        CLOUD_NAME = parsed.hostname
    except Exception as e:
        raise ValueError(f"Invalid CLOUDINARY_URL format. Expected: cloudinary://API_KEY:API_SECRET@CLOUD_NAME. Error: {str(e)}")
else:
    # Fall back to individual environment variables
    CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    API_KEY = os.getenv("CLOUDINARY_API_KEY")
    API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Validate credentials
if not all([CLOUD_NAME, API_KEY, API_SECRET]):
    missing = []
    if not CLOUD_NAME:
        missing.append("CLOUDINARY_CLOUD_NAME or CLOUDINARY_URL")
    if not API_KEY:
        missing.append("CLOUDINARY_API_KEY or CLOUDINARY_URL")
    if not API_SECRET:
        missing.append("CLOUDINARY_API_SECRET or CLOUDINARY_URL")
    raise ValueError(
        f"Missing Cloudinary credentials. "
        f"Either set CLOUDINARY_URL or set {', '.join(missing)} in .env file"
    )

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)


def upload_image_to_cloudinary(file_bytes, folder="wardrobe"):
    """
    Upload image to Cloudinary and return secure URL
    
    Args:
        file_bytes: Image file bytes
        folder: Cloudinary folder name (default: "wardrobe")
    
    Returns:
        dict with secure_url and public_id
    """
    # Validate credentials are set
    if not all([CLOUD_NAME, API_KEY, API_SECRET]):
        raise ValueError("Cloudinary credentials not configured. Please check your .env file.")
    
    try:
        # Use unsigned upload if credentials might be invalid
        # This is more forgiving for testing
        result = cloudinary.uploader.upload(
            file_bytes,
            folder=folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True
        )
        return {
            "secure_url": result["secure_url"],
            "public_id": result["public_id"],
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height")
        }
    except cloudinary.exceptions.Error as e:
        error_msg = str(e)
        if "Invalid Signature" in error_msg:
            raise ValueError(
                "Cloudinary signature error. Please verify your CLOUDINARY_API_SECRET in .env file. "
                "Make sure there are no extra spaces or quotes around the value."
            )
        raise Exception(f"Cloudinary upload failed: {error_msg}")
    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {str(e)}")

