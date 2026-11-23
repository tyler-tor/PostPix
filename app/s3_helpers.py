"""Image upload helpers (validation + S3).

Uploads are checked before they reach S3:
  * size is capped by MAX_CONTENT_LENGTH in config (Flask returns 413),
  * the file must be a real JPEG/PNG/WEBP/GIF (opened with Pillow, so a
    renamed .exe or HTML file is rejected even if it is called photo.jpg),
  * the stored file name and Content-Type come from the detected format,
    never from what the browser claimed.
"""
import os
import uuid

import boto3
from PIL import Image, UnidentifiedImageError

# With no S3_KEY/S3_SECRET set, boto3 falls back to its normal credential
# chain (e.g. an EC2 IAM role), which is the plan for production (P37).
s3 = boto3.client(
   "s3",
   aws_access_key_id=os.environ.get("S3_KEY"),
   aws_secret_access_key=os.environ.get("S3_SECRET")
)

# Pillow format name -> (file extension, Content-Type)
IMAGE_FORMATS = {
    'JPEG': ('jpg', 'image/jpeg'),
    'PNG': ('png', 'image/png'),
    'WEBP': ('webp', 'image/webp'),
    'GIF': ('gif', 'image/gif'),
}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# Refuse absurd pixel counts (decompression bombs: tiny file, huge image).
Image.MAX_IMAGE_PIXELS = 50_000_000

UPLOAD_PREFIX = 'uploads/'
BUCKET_NAME = os.environ.get('S3_BUCKET')
# Public base URL for uploaded files. Set S3_PUBLIC_URL_BASE to your CloudFront
# URL later (P37); default is the bucket's HTTPS URL.
S3_LOCATION = os.environ.get('S3_PUBLIC_URL_BASE') or f'https://{BUCKET_NAME}.s3.amazonaws.com/'
if not S3_LOCATION.endswith('/'):
    S3_LOCATION += '/'


class InvalidImage(ValueError):
    pass


def allowed_file(filename):
    """Quick first check on the name. The real check is validate_image()."""
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file):
    """Open the upload with Pillow and return (extension, content_type).

    Raises InvalidImage if it is not a supported, uncorrupted image.
    Leaves the stream at position 0 so it can be uploaded afterwards.
    """
    try:
        file.stream.seek(0)
        with Image.open(file.stream) as img:
            fmt = img.format
            img.verify()  # checks the file is not truncated/corrupt
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError) as e:
        raise InvalidImage('file is not a valid image') from e
    finally:
        file.stream.seek(0)
    if fmt not in IMAGE_FORMATS:
        raise InvalidImage('only JPEG, PNG, WEBP and GIF images are allowed')
    return IMAGE_FORMATS[fmt]


def get_unique_filename(ext):
    """Random, non-guessable key like 'uploads/3f2a...9c.jpg'."""
    return f'{UPLOAD_PREFIX}{uuid.uuid4().hex}.{ext}'


def upload_file_to_s3(file, key, content_type):
    """Upload to S3 without an ACL.

    New buckets have ACLs disabled ("Bucket owner enforced"), so passing
    ACL='public-read' makes the upload fail. Public read access should come
    from a bucket policy or CloudFront (P37) instead.
    """
    if not BUCKET_NAME:
        return {'errors': 'S3 is not configured (S3_BUCKET is empty)'}
    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            key,
            ExtraArgs={'ContentType': content_type}
        )
    except Exception as e:
        # Log the real reason server-side; don't leak AWS details to clients.
        print(f'S3 upload failed: {e!r}')
        return {'errors': 'upload failed'}
    return {'url': f'{S3_LOCATION}{key}'}


def process_and_upload_image(file):
    """Validate an uploaded image and send it to S3.

    Returns {'url': ...} on success, {'errors': ..., 'status': code} on failure.
    """
    if not file or not file.filename:
        return {'errors': 'image required', 'status': 400}
    if not allowed_file(file.filename):
        return {'errors': 'file type not permitted (use jpg, png, webp or gif)', 'status': 400}
    try:
        ext, content_type = validate_image(file)
    except InvalidImage as e:
        return {'errors': str(e), 'status': 400}
    result = upload_file_to_s3(file, get_unique_filename(ext), content_type)
    if 'url' not in result:
        result['status'] = 502
    return result
