from datetime import datetime
from PIL import UnidentifiedImageError
from fastapi import APIRouter, Depends, Form, UploadFile, status, HTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool
from database import get_db
from auth import CurrentUser
from botocore.exceptions import ClientError
from image_utils import delete_background_image, process_background_image, upload_background_image
import models
from schemas import SettingsResponse

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("", response_model=SettingsResponse)
async def get_lan_settings(db: DbSession):
    result = await db.execute(select(models.LanSettings).where(models.LanSettings.id == 1))
    lan_settings = result.scalars().first()

    if not lan_settings:
        default_settings = models.LanSettings(
                        id=1,
                        name="Default LAN Party",
                        lan_date=None,
                        image_file=None
                    )
        db.add(default_settings)
        await db.commit()
        await db.refresh(default_settings)
        return default_settings
    
    return lan_settings 

@router.patch("", response_model=SettingsResponse)
async def update_lan_settings(
    db: DbSession,
    current_user: CurrentUser,
    name: Annotated[str, Form(min_length=3, max_length=50)],
    lan_date: Annotated[datetime | None, Form()] = None,
    file: UploadFile | None = None,
):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not logged in")

    result = await db.execute(select(models.LanSettings).where(models.LanSettings.id == 1))
    lan_settings = result.scalars().first()

    if not lan_settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LAN settings not found")

    old_filename = None

    if file is not None and file.filename:
        image = await file.read()
        try:
            process_bytes, new_filename = await run_in_threadpool(process_background_image, image)
        except UnidentifiedImageError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP)."
            ) from err

        try:
            await upload_background_image(process_bytes, new_filename)
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image to S3. Please try again later."
            ) from e

        old_filename = lan_settings.image_file
        lan_settings.image_file = new_filename

    lan_settings.name = name
    lan_settings.lan_date = lan_date

    await db.commit()
    await db.refresh(lan_settings)

    if(old_filename):   
        try:
            await delete_background_image(old_filename)
        except ClientError:
            pass

    return lan_settings

