import os
from flask import Flask, render_template, request
from PIL import Image
import imagehash
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DUPLICATES_FOLDER = 'duplicates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DUPLICATES_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    duplicates = []
    if request.method == 'POST':
        files = request.files.getlist('images')
        uploaded_paths = []

        # Save uploaded images
        for f in files:
            path = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(path)
            uploaded_paths.append(path)

        # Detect duplicates/similar images
        hashes = {}
        for path in uploaded_paths:
            try:
                img = Image.open(path)
                img_hash = imagehash.phash(img)

                found_dup = False
                for h in hashes:
                    if abs(img_hash - h) <= 5:  # similarity threshold
                        duplicates.append(os.path.basename(path))
                        shutil.move(path, DUPLICATES_FOLDER)
                        found_dup = True
                        break

                if not found_dup:
                    hashes[img_hash] = path

            except Exception as e:
                print("Error processing", path, e)

    return render_template('index.html', duplicates=duplicates)

if __name__ == '__main__':
    app.run(debug=True)
