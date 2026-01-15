from PIL import Image
import io
import cloudinary
import cloudinary.uploader
from ..config import settings
from typing import Optional, Dict

# Initialize Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

class ImageOptimizer:
    """
    Advanced image optimization service
    - Auto-resize to optimal dimensions
    - Convert to WebP for better compression
    - Generate thumbnails
    - Upload to Cloudinary
    """
    
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    THUMBNAIL_SIZE = (400, 300)
    QUALITY = 85
    
    @staticmethod
    def optimize_image(image_bytes: bytes, filename: str) -> Dict[str, str]:
        """
        Optimize image and return URLs
        Returns: {
            'original_url': str,
            'optimized_url': str,
            'thumbnail_url': str,
            'width': int,
            'height': int,
            'file_size': int
        }
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Get original dimensions
            original_width, original_height = img.size
            
            # Convert to RGB if necessary (for WebP)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if original_width > ImageOptimizer.MAX_WIDTH or original_height > ImageOptimizer.MAX_HEIGHT:
                img.thumbnail((ImageOptimizer.MAX_WIDTH, ImageOptimizer.MAX_HEIGHT), Image.Resampling.LANCZOS)
            
            # Save optimized version to bytes
            optimized_bytes = io.BytesIO()
            img.save(optimized_bytes, format='WEBP', quality=ImageOptimizer.QUALITY, optimize=True)
            optimized_bytes.seek(0)
            
            # Create thumbnail
            thumb_img = img.copy()
            thumb_img.thumbnail(ImageOptimizer.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            thumb_bytes = io.BytesIO()
            thumb_img.save(thumb_bytes, format='WEBP', quality=80)
            thumb_bytes.seek(0)
            
            # Upload original to Cloudinary
            original_upload = cloudinary.uploader.upload(
                image_bytes,
                folder="kayan_pro/originals",
                public_id=filename.split('.')[0],
                resource_type="image"
            )
            
            # Upload optimized version
            optimized_upload = cloudinary.uploader.upload(
                optimized_bytes.getvalue(),
                folder="kayan_pro/optimized",
                public_id=f"{filename.split('.')[0]}_optimized",
                resource_type="image"
            )
            
            # Upload thumbnail
            thumbnail_upload = cloudinary.uploader.upload(
                thumb_bytes.getvalue(),
                folder="kayan_pro/thumbnails",
                public_id=f"{filename.split('.')[0]}_thumb",
                resource_type="image"
            )
            
            return {
                'original_url': original_upload['secure_url'],
                'optimized_url': optimized_upload['secure_url'],
                'thumbnail_url': thumbnail_upload['secure_url'],
                'width': img.width,
                'height': img.height,
                'file_size': len(optimized_bytes.getvalue())
            }
            
        except Exception as e:
            print(f"Image optimization error: {e}")
            return None
    
    @staticmethod
    def delete_image(public_id: str) -> bool:
        """Delete image from Cloudinary"""
        try:
            cloudinary.uploader.destroy(public_id)
            return True
        except Exception as e:
            print(f"Image deletion error: {e}")
            return False

# Singleton instance
image_optimizer = ImageOptimizer()
