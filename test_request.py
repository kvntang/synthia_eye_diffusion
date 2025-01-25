import requests
import base64
import os

def main():
    # 1. URL of your Flask server
    url = "http://127.0.0.1:3000"

    # 2. Path to the local image you want to send
    image_path = "test_image.jpg"

    # 3. Open the image file in binary mode
    with open(image_path, "rb") as img_file:
        # Prepare multipart form-data (the key "image" must match your Flask code)
        files = {
            "image": img_file
        }

        # 4. Send a POST request with the image
        response = requests.post(url, files=files)

    # 5. Check the server response
    print("Status Code:", response.status_code)

    try:
        response_data = response.json()
        print("Response JSON:", response_data)
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw Response:", response.text)
        return

    # 6. If successful, extract the base64 image from the response and save it
    if response_data.get("status") == "success":
        base64_image_str = response_data.get("image", "")

        # In case there's a data URL prefix, remove it
        if base64_image_str.startswith("data:image"):
            # Split on the comma to remove "data:image/png;base64,"
            base64_image_str = base64_image_str.split(",", 1)[1]

        # Decode the base64 string to raw image bytes
        image_bytes = base64.b64decode(base64_image_str)

        # 7. Write the bytes to a new file (e.g., output.png)
        output_filename = "output.png"
        with open(output_filename, "wb") as out_file:
            out_file.write(image_bytes)
        
        print(f"Saved response image to {os.path.abspath(output_filename)}")

    else:
        error_msg = response_data.get("message", "Unknown error.")
        print("Error from server:", error_msg)

if __name__ == "__main__":
    main()
