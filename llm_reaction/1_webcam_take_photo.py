import cv2
import time
import requests
import base64
import numpy as np
import json

def main():
    # URL of your Flask (Stable Diffusion) server
    url = "http://synthia.tangatory.com"  # adjust to your actual endpoint

    # Initialize webcam
    cap = cv2.VideoCapture(0)  # 0 is the default camera index

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Press 'space' to capture a photo and send to server, or 'q' to quit...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from webcam.")
            break

        cv2.imshow("Webcam Feed", frame)
        key = cv2.waitKey(1) & 0xFF

        # Press space bar (key code 32) to capture and send the image
        if key == 32:
            print("Capturing image and sending to server...")
            response = send_frame_to_server(frame, url)
            print("Server response:", response)

        # Press 'q' to quit
        if key == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

def send_frame_to_server(frame, url):
    """
    Captures the frame, encodes it to JPEG, converts to base64,
    sends the image in a JSON payload as the POST body 
    {"image64": "<base64_string>"} to the server, and returns the server response.
    """
    # Encode the frame as JPEG in memory
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        return "Error: Failed to encode the frame to JPEG."

    # Convert the image to bytes
    image_bytes = encoded_image.tobytes()
    
    # Convert to base64 string (without prefix)
    base64_str = base64.b64encode(image_bytes).decode('utf-8')

    # Prepare the JSON payload
    payload = {"image_b64": base64_str}
    headers = {"Content-Type": "application/json"}

    try:
        # Send POST request with JSON data as the body
        response = requests.post(url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        return f"Error sending request: {e}"

    if response.status_code != 200:
        return f"Server returned status code: {response.status_code}, response: {response.text}"
    
    try:
        return response.json()
    except Exception as e:
        return f"Error parsing JSON: {e}, raw response: {response.text}"

if __name__ == "__main__":
    main()
