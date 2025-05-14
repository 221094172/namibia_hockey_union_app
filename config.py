import os

# Flask configuration
SECRET_KEY = os.environ.get("SESSION_SECRET", "namibia_hockey_secret_key")
DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

# Admin configuration
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "aadmin@gmai.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
ADMIN_SECRET_CODE = os.environ.get("ADMIN_SECRET_CODE", "admin")  # This is used to verify admin registration

# Upload directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
TEAM_LOGOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'team_logos')
PLAYER_PHOTOS_FOLDER = os.path.join(UPLOAD_FOLDER, 'player_photos')

# Ensure upload folders exist
for folder in [UPLOAD_FOLDER, TEAM_LOGOS_FOLDER, PLAYER_PHOTOS_FOLDER]:
    os.makedirs(folder, exist_ok=True)