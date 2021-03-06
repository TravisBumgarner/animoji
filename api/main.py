import uuid
import os

from flask import Flask, send_file, request, jsonify, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import imageio
from flask_cors import CORS


app = Flask(__name__, static_folder="dist/")
CORS(app)


def text_to_image(text, width, height, foreground_color, background_color, font_size):
    image = Image.new("RGB", (width, height), color=background_color)
    font = ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
    d = ImageDraw.Draw(image)
    d.text((0, 0), text, font=font, fill=foreground_color)
    return image


@app.route("/ok")
def ok():
    return "Server is running!"


@app.route("/images/<filename>")
def images(filename):
    return send_from_directory("images", filename)


@app.route("/process", methods=["post", "get"])
def process():
    data = request.get_json()
    print(data)
    frames = data["frames"]
    width = int(data["width"])
    height = int(data["height"])
    font_size = int(data["font_size"])
    frame_rate = int(data["frame_rate"])
    foreground_color = data["foreground_color"]
    background_color = data["background_color"]

    images = [
        text_to_image(
            text=frame,
            width=width,
            height=height,
            foreground_color=foreground_color,
            background_color=background_color,
            font_size=font_size,
        )
        for frame in frames
    ]
    params = {"duration": (1 / frame_rate)}
    filename = f"{uuid.uuid4().hex[:12].lower()}.gif"
    file_path = f"./images/{filename}"
    file_url = f"http://localhost:5000/images/{filename}"

    imageio.mimsave(file_path, images, **params)
    return jsonify({"url": file_url})


@app.route("/", defaults={"path": ""})
@app.route("/static/<path:path>")
def serve(path):
    print(os.listdir(app.static_folder))
    if path != "" and os.path.exists(app.static_folder + path):
        print("sending app")
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")
