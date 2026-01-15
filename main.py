import io
from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import utils

app = FastAPI()

@app.post("/api/encode")
async def encode(file: UploadFile, secret_text: str = Form()):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    # read image to ram
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")

    new_image = image.copy()
    encoded_image = utils.encode(new_image, secret_text)

    # return it as file
    output_buffer = io.BytesIO()
    encoded_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return StreamingResponse(output_buffer, media_type="image/png")

@app.post("/api/decode")
async def decode(file: UploadFile):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    hidden_message = utils.decode(image)
    return {"hidden_message": hidden_message}
