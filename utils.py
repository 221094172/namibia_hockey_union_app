import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from io import BytesIO

# Maximum dimension sizes for different image types
MAX_LOGO_SIZE = (300, 300)  # Team logos
MAX_PLAYER_PHOTO_SIZE = (400, 500)  # Player photos
MAX_PROFILE_PIC_SIZE = (200, 200)  # User profile pictures

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_optimized_image(file, upload_folder, image_type='logo'):
    """
    Save and optimize an uploaded image.
    
    Args:
        file: The uploaded file object
        upload_folder: The folder where the image should be saved
        image_type: Type of image ('logo', 'player', 'profile')
        
    Returns:
        The path to the saved image or None if saving failed
    """
    if file and allowed_file(file.filename):
        # Generate a unique filename using UUID
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        
        # Ensure the upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Full path to save the file
        file_path = os.path.join(upload_folder, filename)
        
        try:
            # Open the image with PIL
            img = Image.open(file)
            
            # Convert to RGB if it's in RGBA mode (to avoid issues with JPEG)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Determine the max size based on image type
            if image_type == 'logo':
                max_size = MAX_LOGO_SIZE
            elif image_type == 'player':
                max_size = MAX_PLAYER_PHOTO_SIZE
            elif image_type == 'profile':
                max_size = MAX_PROFILE_PIC_SIZE
            else:
                max_size = MAX_LOGO_SIZE  # Default
            
            # Resize the image while maintaining aspect ratio
            img.thumbnail(max_size)
            
            # Save the optimized image
            img.save(file_path, optimize=True, quality=85)
            
            # Return the path for database storage (with leading slash for URL)
            return '/' + file_path
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    return None

def delete_image(image_path):
    """
    Delete an image file if it exists.
    
    Args:
        image_path: Path to the image file (with leading slash)
        
    Returns:
        True if deletion was successful, False otherwise
    """
    if image_path and image_path.startswith('/'):
        # Remove the leading slash for file system path
        file_path = image_path[1:]
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error deleting image: {e}")
    
    return False