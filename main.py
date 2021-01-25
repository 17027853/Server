import os
import shutil
import cv2
from flask import Flask,request,send_from_directory,jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['IMAGE_FOLDER'] = os.path.abspath('.')+'\\images\\'
ALLOWED_EXTENSIONS=set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/api/upload',methods=['POST'])
def upload_file():
    if request.method=='POST':
        for k in request.files:
            file = request.files[k]

            image_urls = []
            if file and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                print("image :" + filename + "received from app")
                file = file.save(os.path.join(app.config['IMAGE_FOLDER'],filename))
                print("image saved to images/"+filename)
                path = "images/"+filename
                image_urls.append("images/%s"%filename)

                # delete last result
                dir_path = 'runs/detect/exp'
                try:
                    shutil.rmtree(dir_path)
                except OSError as e:
                    print("Error: %s : %s" % (dir_path, e.strerror))

                # Call the detect.py program
                print("detection on "+filename+" started")
                os.system("python detect.py --weights best.pt --img 416 --conf 0.4 --source images/" + filename)

        #save back to images folder
        img = cv2.imread("runs/detect/exp/" + filename, 1)
        cv2.imwrite("images/"+filename, img)
        print("detection finished and "+filename+"saved")

        #send result back
        return jsonify("images/"+filename)#bewerkte foto

#static
@app.route("/images/<imgname>",methods=['GET'])
def images(imgname):
    return send_from_directory(app.config['IMAGE_FOLDER'],imgname)

if __name__ == "__main__":
    # IMAGE_FOLDER
    if not os.path.exists(app.config['IMAGE_FOLDER']):
        os.mkdir(app.config['IMAGE_FOLDER'])
    app.run(host="192.168.68.115", port=5000, debug=True)