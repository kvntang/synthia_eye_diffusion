import cv2
import time
import requests
import base64
import numpy as np

def main():
    # 1. URL of your Flask / Stable Diffusion server
    url = "http://app.unaliu.com"  # <-- adjust to your actual endpoint

    # 2. Initialize webcam
    cap = cv2.VideoCapture(0)  # 0 is the default camera index

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Snapshot interval control
    last_capture_time = time.time()
    capture_interval = 10  # seconds

    # Variables to store the last snapshot and the Stable Diffusion image
    last_snapshot = None
    stable_diff_img = None

    print("Press 'q' to quit the webcam feed...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from webcam.")
            break

        current_time = time.time()
        # How many seconds remain until next capture
        time_remaining = int(capture_interval - (current_time - last_capture_time))
        if time_remaining < 0:
            time_remaining = 0

        # Check if it's time for a new snapshot
        if current_time - last_capture_time >= capture_interval:
            # Store the snapshot from the live feed
            last_snapshot = frame.copy()

            # Send it to the server
            stable_diff_img = send_frame_to_server(frame, url)

            # Reset the timer
            last_capture_time = current_time

        # --- LEFT SIDE: Combine live feed + faint snapshot overlay ---
        if last_snapshot is not None:
            # Resize the snapshot to match the current frame size
            snapshot_resized = cv2.resize(last_snapshot, (frame.shape[1], frame.shape[0]))
            # Blend: 50% live feed, 50% snapshot
            left_display = cv2.addWeighted(frame, 0.5, snapshot_resized, 0.5, 0)
        else:
            # If no snapshot yet, just use the live feed
            left_display = frame

        # Draw the countdown timer text on top of the left display
        cv2.putText(
            left_display,
            f"Next capture in: {time_remaining}s",
            (10, 30),  # (x, y) position
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,             # font scale
            (255, 255, 255), # color (white)
            2                # thickness
        )

        # --- RIGHT SIDE: If we have a Stable Diffusion image, display it ---
        if stable_diff_img is not None:
            # Resize to match the height of the left display
            h1, w1 = left_display.shape[:2]
            h2, w2 = stable_diff_img.shape[:2]

            if h1 != h2:
                stable_diff_img_resized = cv2.resize(stable_diff_img, (w1, h1))
            else:
                stable_diff_img_resized = stable_diff_img

            # Combine side by side
            combined = np.hstack([left_display, stable_diff_img_resized])
            cv2.imshow("Webcam + Stable Diffusion", combined)
        else:
            # Otherwise just show the left display
            cv2.imshow("Webcam + Stable Diffusion", left_display)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


def send_frame_to_server(frame, url):
    """
    Sends a single frame to the server, receives the processed image (base64),
    decodes it, and returns it as an OpenCV image (numpy array).
    """
    # Encode the frame as JPEG in memory
    success, encoded_image = cv2.imencode('.jpg', frame)
    if not success:
        print("Failed to encode the frame to JPEG.")
        return None

    # Convert to bytes for requests
    image_bytes = encoded_image.tobytes()

    # Prepare multipart form-data
    files = {"image": ("frame.jpg", image_bytes, "image/jpeg")}

    try:
        # Send POST request
        response = requests.post(url, files=files)
    except Exception as e:
        print("Error sending request:", e)
        return None

    if response.status_code != 200:
        print("Server returned status code:", response.status_code)
        print("Server response:", response.text)
        return None

    # Parse JSON response
    try:
        response_data = response.json()
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw response:", response.text)
        return None

    # Check if the server indicates success
    if response_data.get("status") == "success":
        base64_image_str = response_data.get("image", "")
        # Remove data URL prefix if present
        if base64_image_str.startswith("data:image"):
            base64_image_str = base64_image_str.split(",", 1)[1]

        # Decode base64 to raw bytes
        try:
            decoded_bytes = base64.b64decode(base64_image_str)
        except Exception as e:
            print("Failed to base64-decode image:", e)
            return None

        # Convert the decoded bytes to a numpy array (for OpenCV)
        nparr = np.frombuffer(decoded_bytes, np.uint8)
        processed_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if processed_img is None:
            print("OpenCV failed to decode the server response image.")
            return None

        return processed_img
    else:
        error_msg = response_data.get("message", "Unknown error.")
        print("Error from server:", error_msg)
        return None


if __name__ == "__main__":
    main()
