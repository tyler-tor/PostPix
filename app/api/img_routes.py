from flask import Blueprint, request
from flask_login import current_user, login_required
from app.s3_helpers import process_and_upload_image

img_routes = Blueprint('img', __name__)


@img_routes.route('/upload', methods=['POST'])
@login_required
def upload_image():
    """Upload one image (form field "image"), resize it, return its public URLs."""
    if "image" not in request.files:
        return {"errors": ["image required"]}, 400

    kind = 'avatar' if request.form.get('kind') == 'avatar' else 'post'
    result = process_and_upload_image(request.files["image"], kind, demo=current_user.is_demo)
    if "url" not in result:
        return {"errors": [result["errors"]]}, result.get("status", 400)
    return {"url": result["url"], "thumbUrl": result["thumbUrl"],
            "width": result["width"], "height": result["height"]}
