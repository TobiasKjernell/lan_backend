import uuid
from io import BytesIO
from PIL import Image, ImageOps
import boto3
from starlette.concurrency import run_in_threadpool
from config import settings

def _get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(settings.s3_access_key_id.get_secret_value() if settings.s3_access_key_id else None),
        aws_secret_access_key=(settings.s3_secret_access_key.get_secret_value() if settings.s3_secret_access_key else None),
        endpoint_url=settings.s3_endpoint_url
    )

def process_background_image(content: bytes) -> tuple[bytes, str]:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        
        filename = f"{uuid.uuid4().hex}.jpg"
        
        output = BytesIO()

        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)
    
    return output.read(), filename

def _upload_to_s3(file_content: bytes, filename: str) -> str:
    s3_client = _get_s3_client()
    s3_client.upload_fileobj(
        BytesIO(file_content),
        settings.s3_bucket_name,
        filename,
        ExtraArgs={"ContentType": "image/jpeg"}
    )

def _delete_from_s3(filename: str) -> None:
    s3_client = _get_s3_client()
    s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=filename)   


##Async fixes for S3 operations
async def upload_background_image(file_bytes: bytes, filename: str) -> None:
    filename = f"background_pics/{filename}"
    await run_in_threadpool(_upload_to_s3, file_bytes, filename)


async def delete_background_image(filename: str | None) -> None:
    if filename is None:
        return
    key = f"background_pics/{filename}"
    await run_in_threadpool(_delete_from_s3, key)
