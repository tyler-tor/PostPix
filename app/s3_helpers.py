"""Image upload helpers (validation + S3).

Uploads are checked before they reach S3:
  * size is capped by MAX_CONTENT_LENGTH in config (Flask returns 413),
  * the file must be a real JPEG/PNG/WEBP/GIF (opened with Pillow, so a
    renamed .exe or HTML file is rejected even if it is called photo.jpg),
  * the stored file name and Content-Type come from the detected format,
    never from what the browser claimed.

Then (P24) every upload is re-encoded with Pillow instead of stored as sent:
  * posts: a WebP no wider than 1080 px (and 1350 px tall) plus a 400 px
    WebP thumbnail for grids. Phone photos are often 3-8 MB; the explore grid
    would otherwise download them at full size to draw 300 px tiles.
  * profile pictures: one 320 px WebP.
  * rotation from the camera (EXIF) is applied, and all metadata, including
    GPS location, is dropped because the re-encoded file does not carry it.
  * files are cached for a year (their names are random and never reused).
"""
import io
import os
import uuid

import boto3
from PIL import Image, ImageOps, UnidentifiedImageError

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

# Sizes: (max width, max height) in pixels. Images are only ever shrunk.
MAIN_SIZE = (1080, 1350)
THUMB_SIZE = (400, 400)
AVATAR_SIZE = (320, 320)
CACHE_CONTROL = 'public, max-age=31536000, immutable'

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


def get_unique_filename(ext, suffix=''):
    """Random, non-guessable key like 'uploads/3f2a...9c.jpg'."""
    return f'{UPLOAD_PREFIX}{uuid.uuid4().hex}{suffix}.{ext}'


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
            ExtraArgs={'ContentType': content_type, 'CacheControl': CACHE_CONTROL}
        )
    except Exception as e:
        # Log the real reason server-side; don't leak AWS details to clients.
        print(f'S3 upload failed: {e!r}')
        return {'errors': 'upload failed'}
    return {'url': f'{S3_LOCATION}{key}'}


def _encode_webp(image, size, quality):
    """Shrink a copy of `image` to fit inside `size` and return (bytes, width, height)."""
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)  # keeps the ratio, never enlarges
    buffer = io.BytesIO()
    copy.save(buffer, 'WEBP', quality=quality, method=4)
    buffer.seek(0)
    return buffer, copy.width, copy.height


def make_variants(file, kind):
    """Decode the upload once and return {name: (BytesIO, width, height)}."""
    file.stream.seek(0)
    with Image.open(file.stream) as img:
        img = ImageOps.exif_transpose(img)  # apply the camera's rotation
        img.load()
        # WebP needs RGB(A); palette/greyscale/CMYK images are converted.
        img = img.convert('RGBA' if img.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if kind == 'avatar':
            return {'main': _encode_webp(img, AVATAR_SIZE, 82)}
        return {'main': _encode_webp(img, MAIN_SIZE, 82),
                'thumb': _encode_webp(img, THUMB_SIZE, 78)}


def process_and_upload_image(file, kind='post'):
    """Validate an uploaded image, resize it and send it to S3.

    kind: 'post' (main + thumbnail) or 'avatar' (one small image).
    Returns {'url', 'thumbUrl', 'width', 'height'} on success (thumbUrl is
    None for avatars), {'errors': ..., 'status': code} on failure.
    """
    if not file or not file.filename:
        return {'errors': 'image required', 'status': 400}
    if not allowed_file(file.filename):
        return {'errors': 'file type not permitted (use jpg, png, webp or gif)', 'status': 400}
    try:
        validate_image(file)
        variants = make_variants(file, kind)
    except (InvalidImage, OSError, Image.DecompressionBombError) as e:
        return {'errors': str(e) if isinstance(e, InvalidImage) else 'file is not a valid image', 'status': 400}

    name = get_unique_filename('webp')
    main, width, height = variants['main']
    result = upload_file_to_s3(main, name, 'image/webp')
    if 'url' not in result:
        result['status'] = 502
        return result
    out = {'url': result['url'], 'thumbUrl': None, 'width': width, 'height': height}
    if 'thumb' in variants:
        thumb = upload_file_to_s3(variants['thumb'][0], name.replace('.webp', '_thumb.webp'), 'image/webp')
        if 'url' not in thumb:
            thumb['status'] = 502
            return thumb
        out['thumbUrl'] = thumb['url']
    return out
