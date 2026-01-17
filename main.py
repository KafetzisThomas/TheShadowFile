import io
import base64
from fastapi import FastAPI, Request, UploadFile, Form, HTTPException
from fastapi.templating import Jinja2Templates
from PIL import Image
import cli

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", include_in_schema=False)
@app.get("/encode", include_in_schema=False)
async def encode_form(request: Request):
    return templates.TemplateResponse(request, "encode.html", {"title": "Embed Secret"})


@app.get("/decode", include_in_schema=False)
async def decode_form(request: Request):
    return templates.TemplateResponse(request, "decode.html", {"title": "Extract Secret"})


@app.post("/api/encode")
async def encode(request: Request, file: UploadFile, secret_text: str = Form()):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    # read image to ram
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    encoded_image = cli.encode(image, secret_text)

    # return it as file
    output_buffer = io.BytesIO()
    encoded_image.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    # convert to base64 for display
    image_str = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

    return templates.TemplateResponse(
        request, "encode.html", {"title": "Embed Secret", "encoded_image": image_str, "secret_text": secret_text},
    )


@app.post("/api/decode")
async def decode(request: Request, file: UploadFile):
    content = await file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    hidden_message = cli.decode(image)
    return templates.TemplateResponse(
        request, "decode.html", {"title": "Extract Secret", "hidden_message": hidden_message},
    )
