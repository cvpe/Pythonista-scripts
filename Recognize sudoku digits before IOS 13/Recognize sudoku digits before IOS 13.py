import io
import os

import photos
import ui
from objc_util import ObjCClass, ObjCInstance, ns, nsurl

MODEL_FILENAME = "MNIST.mlmodel"
# MODEL_FILENAME = 'MNISTClassifier.mlmodel'
# MODEL_FILENAME = 'OCR.mlmodel'
# MODEL_FILENAME = 'Alphanum_28x28.mlmodel'

# Use a local path for caching the model file
MODEL_PATH = os.path.join(os.path.expanduser("~/Documents/"), MODEL_FILENAME)

# Declare/import ObjC classes:
MLModel = ObjCClass("MLModel")
VNCoreMLModel = ObjCClass("VNCoreMLModel")
VNCoreMLRequest = ObjCClass("VNCoreMLRequest")
VNImageRequestHandler = ObjCClass("VNImageRequestHandler")


def pil2ui(imgIn):
    with io.BytesIO() as bIO:
        imgIn.save(bIO, "PNG")
        imgOut = ui.Image.from_data(bIO.getvalue())
    del bIO
    return imgOut


def load_model():
    global vn_model
    ml_model_url = nsurl(MODEL_PATH)
    # Compile the model:
    c_model_url = MLModel.compileModelAtURL_error_(ml_model_url, None)
    # Load model from the compiled model file:
    ml_model = MLModel.modelWithContentsOfURL_error_(c_model_url, None)
    # Create a VNCoreMLModel from the MLModel for use with the Vision framework:
    vn_model = VNCoreMLModel.modelForMLModel_error_(ml_model, None)
    return vn_model


def _classify_img_data(img_data):
    global vn_model
    # Create and perform the recognition request:
    req = VNCoreMLRequest.alloc().initWithModel_(vn_model).autorelease()
    handler = (
        VNImageRequestHandler.alloc()
        .initWithData_options_(img_data, None)
        .autorelease()
    )
    success = handler.performRequests_error_([req], None)
    if success:
        best_result = req.results()[0]
        label = str(best_result.identifier())
        confidence = best_result.confidence()
        return {"label": label, "confidence": confidence}
    else:
        return None


def classify_image(img):
    buffer = io.BytesIO()
    img.save(buffer, "JPEG")
    img_data = ns(buffer.getvalue())
    return _classify_img_data(img_data)


def classify_asset(asset):
    mv = ui.View()
    mv.background_color = "white"
    im = ui.ImageView()
    pil_image = asset.get_image()
    print(pil_image.size)

    ui_image = asset.get_ui_image()
    n_squares = 9
    d_grid = 15  # % around the digit
    wim, him = pil_image.size
    ws, hs = ui.get_screen_size()
    if (ws / hs) < (wim / him):
        h = ws * him / wim
        im.frame = (0, (hs - h) / 2, ws, h)
    else:
        w = hs * wim / him
        im.frame = ((ws - w) / 2, 0, w, hs)
    print(wim, him, ws, hs)
    mv.add_subview(im)
    wi = im.width
    hi = im.height
    im.image = ui_image
    im.content_mode = 1  # 1
    mv.frame = (0, 0, ws, hs)
    mv.present("fullscreen")
    dx = wim / n_squares
    dy = him / n_squares
    d = dx * d_grid / 100
    dl = int((wi / n_squares) * d_grid / 100)
    for ix in range(n_squares):
        x = ix * dx
        for iy in range(n_squares):
            y = iy * dy
            pil_char = pil_image.crop(
                (int(x + d), int(y + d), int(x + dx - d), int(y + dy - d))
            )
            button = ui.Button()
            button.frame = (
                int(ix * wi / n_squares) + dl,
                int(iy * hi / n_squares) + dl,
                int(wi / n_squares) - 2 * dl,
                int(hi / n_squares) - 2 * dl,
            )
            button.border_width = 1
            button.border_color = "red"
            button.tint_color = "red"
            ObjCInstance(button).button().contentHorizontalAlignment = 1  # left
            button.background_image = pil2ui(pil_char)
            im.add_subview(button)
            button.title = classify_image(pil_char)["label"]


def main():
    global vn_model
    vn_model = load_model()
    all_assets = photos.get_assets()
    asset = photos.pick_asset(assets=all_assets)
    if asset is None:
        return
    classify_asset(asset)


if __name__ == "__main__":
    main()
