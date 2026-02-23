import os
import io
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_markdown(content: str, filename: str) -> str:
    # Convert string to file-like object
    file_obj = io.BytesIO(content.encode("utf-8"))

    result = cloudinary.uploader.upload(
        file_obj,
        public_id=filename,
        resource_type="raw",
        overwrite=True
    )

    return result["secure_url"]