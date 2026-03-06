from flask import Flask, render_template, request
import os
import cv2

app = Flask(__name__, static_folder="static")

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        return "No file uploaded"

    file = request.files['file']

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    image = cv2.imread(filepath) # OPEN IMAGE WITH OPENCV
    height, width = image.shape[:2]

    # crop middle part where rail usually exists
    image = image[int(height*0.4):int(height*0.7), :]

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(7,7),0)

    edges = cv2.Canny(blur,120,250)
    edges = cv2.Canny(gray, 80, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # FIND CRACK CONTOURS

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area > 150 and area < 2000:

            x,y,w,h = cv2.boundingRect(cnt)

            aspect_ratio = w/h if h!=0 else 0

            if aspect_ratio > 3 or aspect_ratio < 0.3:

                cv2.drawContours(image,[cnt],-1,(0,0,255),2)

    cv2.imwrite("static/output.jpg", image) # SAVE OUTPUT IMAGE

    return render_template("index.html",
                       result="Crack Detection Complete",
                       output_image="static/output.jpg")


if __name__ == "__main__":
    app.run(debug=True)