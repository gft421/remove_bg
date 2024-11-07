from flask import Flask, request, render_template
from PIL import Image
import io
import base64
from rembg import remove

app = Flask(__name__)

# Max file size (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Function to check allowed file extensions
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to remove the background from the image and make it sticker-like
def remove_background(image_file):
    """Removes the background from an image, leaving only the object/person."""
    # Read the image file into a byte stream
    image_bytes = image_file.read()
    
    try:
        # Open the image and ensure it's valid
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verifies if the image is valid
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

    # Remove background using rembg
    result = remove(image_bytes)
    return Image.open(io.BytesIO(result)).convert("RGBA")  # Keep transparency

# Route for the homepage (GET and POST methods)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if a file was uploaded
        file = request.files.get("image")
        
        if file and allowed_file(file.filename):
            # Check the file size
            if len(file.read()) > MAX_FILE_SIZE:
                return "File size exceeds the limit of 5 MB.", 400
            file.seek(0)  # Reset file pointer after size check
            
            result_image = remove_background(file)
            if result_image:
                img_bytes = img_to_bytes(result_image)
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                return render_template("index.html", img_data=img_base64)
            else:
                return "Failed to process image", 400
        else:
            return "Invalid file type or no file uploaded", 400
    return render_template("index.html")

# Function to convert an image to bytes for sending as a response
def img_to_bytes(img):
    """Converts an Image object to bytes, ensuring it has a transparent background."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")  # Save as PNG to retain transparency
    return buf.getvalue()

if __name__ == "__main__":
    app.run(debug=True)
