# Import OpenCV
import cv2
# Importamos todo lo necesario
import os
from flask import Flask, render_template, request, jsonify
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import uuid
from datetime import datetime
from os import remove
import base64
import json

# Resoluciones 
# HD 640x360 
# HD 1280x720 
# HD 1920x1080 
# HD 2560x1440 

# Define haar cascade classifier for face detection
face_classifier = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')


# instancia del objeto Flask
app = Flask(__name__)
# Carpeta de subida
app.config['UPLOAD_FOLDER'] = './frames'

@app.route("/")
def upload_file():
 # renderiamos la plantilla "formulario.html"
 return render_template('formulario.html')

@app.route("/faceDetection", methods=['POST'])
def faceDetection():
 if request.method == 'POST':
    try:
        view = request.form['view']
    except:
        view = None
    
    # obtenemos el archivo del input "archivo"
    f = request.files['archivo']
    filename = secure_filename(f.filename)
    img_Id = str(uuid.uuid4())
    img_Path = "%s.png" % (img_Id)
    # Guardamos el archivo en el directorio "Archivos PDF"
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], img_Path))
    # Retornamos una respuesta satisfactoria

    # Read webcam video
    img = cv2.imread('frames/' + img_Path)
    img_Original = cv2.imread('frames/' + img_Path)

    # fetching the dimensions
    wid = img.shape[1]
    hgt = img.shape[0]
    resolucion_Original = str(wid) + "x" + str(hgt)
    # displaying the dimensions
    print("  - Resolucion Img: %s" % (resolucion_Original))

    # Convert image to gray scale OpenCV
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect face using haar cascade classifier
    faces_coordinates = face_classifier.detectMultiScale(gray_img)

    time_now = datetime.now()
    current_date = time_now.strftime("%Y-%m-%d")
    current_time = time_now.strftime("%H:%M:%S")

    faces_Data = []
    img_delete = []
    face_Count = 0
    #img_Id = uuid.uuid4()
    path_Img_Original = "img/frame _processed/frame_original/Original.png" 
    path_Img_Process = "img/frame _processed/frame_out/%s.png" % (img_Id)
    img_delete.append(path_Img_Process)
    img_delete.append("frames/%s.png" % (img_Id))

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces_coordinates:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)

        #
        face_Count += 1
        face_Id = str(uuid.uuid4())
        path_face = "img/frame _processed/faces/%s.png" % (face_Id)
        img_delete.append(path_face)
        face_Coordinate = {}
        face_Coordinate["id"] = face_Count
        face_Coordinate["face"] = {
            "face_Id": face_Id,
            "face_Coordinate" : {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h)
            }
        }
        face_Coordinate["frame"] = {
            "id": str(img_Id),
            "date": str(current_date),
            "time": str(current_time)
            }

        faces_Data.append(face_Coordinate)


        #Recortar una imagen
        imageOut = img_Original[
            (y - 10):(y + 118),
            (x - 10):(x + 118)
            ]
        # Saving the image
        cv2.imwrite( path_face, imageOut)
        

        b64_Face = None
        with open(path_face, "rb") as img_file:
            b64_Face = base64.b64encode(img_file.read())

        face_Coordinate["box_face"] = b64_Face.decode()

        # Using cv2.putText() method
        # font
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.4
        color = (255, 0, 0)
        thickness = 1
        org = (x, y)
        Text_FaceId = "Face: %s" % (face_Count)

        cv2.putText(img,  Text_FaceId, org, font, fontScale, color, thickness, cv2.LINE_AA)
        print("  - procesando Face: %s" % (face_Count))


    #cv2.imshow('Face Detector', img)

    # Saving the image
    cv2.imwrite( path_Img_Original, img_Original)
    cv2.imwrite( path_Img_Process, img)


    # show output image
    #cv2.imshow('image', img)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()


    b64_string = None
    with open(path_Img_Process, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
    #print(b64_string)

    #
    ResponseData = {}
    ResponseData["faces_Data"] = faces_Data
    ResponseData["frame_Process"] = b64_string.decode()

    #
    for element in img_delete:
        print("remove file: %s" % (element))
        remove(element)

    print("Result:")
    #print(ResponseData)

    with open('data_result/data.json', 'w') as f:
        json.dump(ResponseData, f)





    if (view == "json"):
        return jsonify(ResponseData)
    else:
        return "<img src='data:image/png;base64," + b64_string.decode() + "' alt='Red dot' /> <br> <img src='data:image/png;base64," + ResponseData["faces_Data"][0]["box_face"] + "' alt='Red dot' /> <img src='data:image/png;base64," + ResponseData["faces_Data"][1]["box_face"] + "' alt='Red dot' />"
    

if __name__ == '__main__':
 # Iniciamos la aplica
  app.run(debug=True)