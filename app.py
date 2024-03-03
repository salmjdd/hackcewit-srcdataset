from flask import Flask, render_template, request, jsonify
from firebase_admin import credentials, storage, initialize_app

import cv2
import numpy as np
import base64
from io import BytesIO
from matplotlib import pyplot as plt

app = Flask(__name__)

cred = credentials.Certificate("hackimagedb-firebase-adminsdk-ap594-bf0afe0c08.json")
initialize_app(cred, {'storageBucket': 'hackimagedb.appspot.com'})

bucket = storage.bucket()
global img_path


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Received POST request data:", request.form)
        global img_path
        img_path = request.form['image_selection']
        current_index = int(request.form.get('current_index', 0))
        image_paths = list_files_in_bucket('hackimagedb.appspot.com', img_path)

        if current_index < len(image_paths) - 1:
            current_index += 1

        next_image_path = image_paths[current_index]
        print(next_image_path)

        blob = bucket.blob(next_image_path)
        image_stream = blob.download_as_bytes()

        image_np = np.frombuffer(image_stream, np.uint8)

        image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        _, jpeg_image = cv2.imencode('.jpg', image_cv)

        jpeg_base64 = base64.b64encode(jpeg_image).decode('utf-8')

        next_index = current_index + 1

        hist = cv2.calcHist([image_cv], [0], None, [256], [0, 256])

        plt.figure()
        plt.title("Histogram")
        plt.xlabel("Pixel intensity")
        plt.ylabel("Frequency")
        plt.plot(hist)
        plt.xlim([0, 256])
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        histogram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return render_template('index.html', image_data=jpeg_base64, histogram_data=histogram_base64,
                               current_index=next_index)
    else:
        return render_template('index.html', image_data=None, current_index=0)


@app.route('/next', methods=['POST'])
def on_mouse_clicked():
    current_index = int(request.form.get('current_index', 0))
    image_paths = list_files_in_bucket('hackimagedb.appspot.com', img_path)

    if current_index < len(image_paths) - 1:
        current_index += 1

    next_image_path = image_paths[current_index]
    print(next_image_path)

    blob = bucket.blob(next_image_path)
    image_stream = blob.download_as_bytes()

    image_np = np.frombuffer(image_stream, np.uint8)

    image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    _, jpeg_image = cv2.imencode('.jpg', image_cv)

    jpeg_base64 = base64.b64encode(jpeg_image).decode('utf-8')

    next_index = current_index + 1

    hist = cv2.calcHist([image_cv], [0], None, [256], [0, 256])

    plt.figure()
    plt.title("Histogram")
    plt.xlabel("Pixel intensity")
    plt.ylabel("Frequency")
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    histogram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render_template('index.html', image_data=jpeg_base64, histogram_data=histogram_base64,
                           current_index=next_index)


@app.route('/prev', methods=['POST'])
def on_prev_clicked():
    current_index = int(request.form.get('current_index', 0))
    image_paths = list_files_in_bucket('hackimagedb.appspot.com', img_path)

    current_index -= 1

    next_image_path = image_paths[current_index]
    print(next_image_path)

    blob = bucket.blob(next_image_path)
    image_stream = blob.download_as_bytes()

    image_np = np.frombuffer(image_stream, np.uint8)

    image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    _, jpeg_image = cv2.imencode('.jpg', image_cv)

    jpeg_base64 = base64.b64encode(jpeg_image).decode('utf-8')

    next_index = current_index - 1

    hist = cv2.calcHist([image_cv], [0], None, [256], [0, 256])

    plt.figure()
    plt.title("Histogram")
    plt.xlabel("Pixel intensity")
    plt.ylabel("Frequency")
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    histogram_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render_template('index.html', image_data=jpeg_base64, histogram_data=histogram_base64,
                           current_index=next_index)


def list_files_in_bucket(bucket_name, directory_path):
    """List all files in a specific directory in Firebase Storage."""
    blob_list = bucket.list_blobs(prefix=directory_path)
    file_paths = []
    for blob in blob_list:
        file_paths.append(blob.name)
    return file_paths
