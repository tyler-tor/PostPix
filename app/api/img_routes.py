from flask import Blueprint, request
from flask_login import login_required
from app.s3_helpers import process_and_upload_image

img_routes = Blueprint('img', __name__)


@img_routes.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """Upload one image (form field "image") and return its public URL."""
    if "image" not in request.files:
        return {"errors": ["image required"]}, 400

    result = process_and_upload_image(request.files["image"])
    if "url" not in result:
        return {"errors": [result["errors"]]}, result.get("status", 400)
    return {"url": result["url"]}
