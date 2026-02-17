import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_text_file(content: str, filename: str) -> str:
    result = cloudinary.uploader.upload(
        content,
        public_id=filename,
        resource_type="raw"
    )
    return result["secure_url"]
