from flask import Flask, render_template, request
from engine import run_engine
import requests
import os
import random
import string

app = Flask(__name__, template_folder='.')

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


configurations = {
    "1": {
        "file_path": "C:/Users/Charlie/Desktop/comfyui/tele/change_outfit.json",
        "target_node_id": "978",
        "seed": "949"
    },
    "2": {
        "file_path": "C:/Users/Charlie/Desktop/comfyui/tele/make_nsfw.json",
        "target_node_id": "903",
        "seed": "64"
    },
    "3": {
        "file_path": "C:/Users/Charlie/Desktop/comfyui/tele/creative.json",
        "target_node_id": "1000",
        "seed": "878"
    }
}


def generate_random_filename(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_option', methods=['GET', 'POST'])
def run_option():

    if request.method == 'POST':
        
        xurl = request.form.get('url')
        xfile = request.files['file']

        if xurl:
            response = requests.get(xurl, verify=False)
            if response.status_code == 200:
                extension = xurl.split(".")[-1]
                filename = generate_random_filename() + "." + extension
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                with open(filepath, "wb") as file:
                    file.write(response.content)
        else:
            filename = generate_random_filename() + "_" + xfile.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            xfile.save(filepath)    
        

    user_prompt = request.form['user_prompt']
    selected_option = request.form['option']

    if selected_option in configurations:
        config = configurations[selected_option]
        file_path = config["file_path"]
        target_node_id = config["target_node_id"]
        seed = config["seed"]
        encoded_images, elapsed_time = run_engine(file_path, target_node_id, filename, user_prompt, seed)

        
        return render_template('index.html', encoded_images=encoded_images, elapsed_time=elapsed_time)
    else:
        return "Invalid option."




if __name__ == '__main__':
    app.run(debug=True)
