import websocket
import uuid
import json
import urllib.request
import urllib.parse
from PIL import Image
import time
import base64
import random
import string
import os


#server URL
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images


#Cgetting random seed
def generate_random_numbers(length=13):
    snumbers = string.digits
    return ''.join(random.choice(snumbers) for _ in range(length))


#output folder
output_folder = "C:/Users/Charlie/Desktop/comfyui/tele/downloads"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def run_engine(file_path, target_node_id, filename, user_prompt, seed):


    #Timer Start
    start_time = time.time()


    #Load Image
    image_path = "C:/Users/Charlie/Desktop/comfyui/tele/uploads/" + filename




    #Loading prompt
    with open(file_path, "r") as json_file:
        json_data = json_file.read()
    prompt = json.loads(json_data)


    
    xseed = str(seed)  

    #Changing the original Prompt
    prompt["133"]["inputs"]["image"] = image_path
    prompt["999"]["inputs"]["Text"] = user_prompt
    prompt[xseed]["inputs"]["seed"] = generate_random_numbers()


    #websocket and start process
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))

    #getting processed image by node_id (outfit:978, nsfw:903, creative:1000)
    images = get_images(ws, prompt)



        
        
    #getting images
    encoded_images = []
    for node_id in images:
        if node_id == target_node_id:
            for image_data in images[node_id]:
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                encoded_images.append(encoded_image)



    #Timer end
    end_time = time.time()
    elapsed_time = end_time - start_time
    

    return encoded_images, elapsed_time




    # for node_id in images:
    #     if node_id == target_node_id:
    #         for image_data in images[node_id]:
    #             image = Image.open(io.BytesIO(image_data))
    #             image.show()

    #Timer end


