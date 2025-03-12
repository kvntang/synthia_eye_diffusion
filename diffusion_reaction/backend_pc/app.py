from flask import Flask, request, jsonify
import base64
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_image():
    try:
        # 1. Get the file from the request
        image_file = request.files['image']
        image_binary = image_file.read()

        # 2. Convert to Base64
        image_b64 = base64.b64encode(image_binary).decode('utf-8')

        # 3. Prepare payload (must match Automatic1111 JSON structure)
        api_request_body = {
            "prompt": "a forest scene",
            "init_images": [image_b64],  # list of base64 strings
            "steps": 50,
            "cfg_scale": 9,
            "denoising_strength": 0.6,
            "width": 512,
            "height": 512
        }

        # 4. POST with JSON
        response = requests.post(
            "http://127.0.0.1:7860/sdapi/v1/img2img",
            json=api_request_body
        )
        
        response_data = response.json()

        # 5. Handle response
        if response_data and 'images' in response_data and len(response_data['images']) > 0:
            generated_image = response_data['images'][0]
            return jsonify({
                "status": "success",
                "image": generated_image
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Error generating image: {response.text}"
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
