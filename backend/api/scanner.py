import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from scanner.models import ScannerResponse
from scanner.scanner import (
    ScannerTimeoutError,
    WebsiteUnavailableError,
    scan_website,
)


logger = logging.getLogger(__name__)

router = APIRouter(tags=["scanner"])


class ScanRequest(BaseModel):
    url: HttpUrl


@router.post(
    "/scan",
    response_model=ScannerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid URL"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Website unavailable"},
        status.HTTP_504_GATEWAY_TIMEOUT: {"description": "Website timeout"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Unexpected error"},
    },
)
def scan(request: ScanRequest) -> ScannerResponse:
    try:
        return scan_website(str(request.url))
    except ValueError as exc:
        logger.warning("Invalid scanner request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL",
        ) from exc
    except WebsiteUnavailableError as exc:
        logger.warning("Website unavailable during scan: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Website Unavailable",
        ) from exc
    except ScannerTimeoutError as exc:
        logger.warning("Website timeout during scan: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected scanner API error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected Error",
        ) from exc
