"""
utils.py — GPS / EXIF extraction utilities for the activities app.

Provides:
    extract_gps_info(image_file)  →  dict with has_gps, latitude, longitude
    has_geotag(image_file)        →  bool (thin wrapper)

Works directly with Django's in-memory uploaded file objects
(InMemoryUploadedFile / TemporaryUploadedFile). Never relies on
a filesystem path so it is safe with any Django FILE_UPLOAD_HANDLERS.
"""

import io
import logging

from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

# EXIF tag IDs we care about
_EXIF_GPS_TAG_ID = 34853   # GPSInfo


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _to_decimal_degrees(dms_values, ref: str) -> float | None:
    """
    Convert GPS DMS (degrees / minutes / seconds) rational tuples
    to a signed decimal-degree float.

    Args:
        dms_values: Sequence of three IFDRational / tuple values
                    representing degrees, minutes, seconds.
        ref:        Cardinal direction character — 'N', 'S', 'E', or 'W'.

    Returns:
        Decimal degrees as a float, or None if conversion fails.
    """
    try:
        degrees = float(dms_values[0])
        minutes = float(dms_values[1])
        seconds = float(dms_values[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if ref in ("S", "W"):
            decimal = -decimal

        return round(decimal, 7)

    except (IndexError, TypeError, ZeroDivisionError, ValueError) as exc:
        logger.debug("DMS-to-decimal conversion failed: %s", exc)
        return None


def _parse_gps_tags(raw_gps: dict) -> dict:
    """
    Parse the raw GPSInfo IFD dict returned by Pillow into human-readable
    key → value pairs, then extract lat/lon.

    Args:
        raw_gps: Dict keyed by numeric EXIF tag IDs for the GPS IFD.

    Returns:
        Dict with keys: has_gps (bool), latitude (float|None),
        longitude (float|None).
    """
    # Remap numeric keys → named keys (e.g. 2 → "GPSLatitude")
    named: dict = {}
    for tag_id, value in raw_gps.items():
        tag_name = GPSTAGS.get(tag_id, tag_id)
        named[tag_name] = value

    latitude   = _to_decimal_degrees(
        named.get("GPSLatitude"),
        named.get("GPSLatitudeRef", "N"),
    )
    longitude  = _to_decimal_degrees(
        named.get("GPSLongitude"),
        named.get("GPSLongitudeRef", "E"),
    )

    has_gps = latitude is not None and longitude is not None

    return {
        "has_gps":   has_gps,
        "latitude":  latitude,
        "longitude": longitude,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_gps_info(image_file) -> dict:
    """
    Extract GPS coordinates from an image's EXIF metadata.

    Accepts any file-like object, including Django's
    InMemoryUploadedFile and TemporaryUploadedFile.  The file pointer
    is reset to the beginning before reading so it works correctly
    even if Django has already partially consumed it.

    Args:
        image_file: A file-like object (Django uploaded file or BytesIO).

    Returns:
        A dict:
        {
            "has_gps":   bool,          # True if valid GPS data was found
            "latitude":  float | None,  # Decimal degrees (+ N, - S)
            "longitude": float | None,  # Decimal degrees (+ E, - W)
        }
    """
    _no_gps = {"has_gps": False, "latitude": None, "longitude": None}

    try:
        # Always seek to the start — Django may have already read the file
        image_file.seek(0)

        # Read the raw bytes so Pillow never touches the filesystem
        raw_bytes = image_file.read()
        image_file.seek(0)   # reset again in case the caller still needs it

        image = Image.open(io.BytesIO(raw_bytes))

    except UnidentifiedImageError:
        logger.warning(
            "extract_gps_info: could not identify image format for '%s'.",
            getattr(image_file, "name", "<unknown>"),
        )
        return _no_gps

    except OSError as exc:
        logger.warning(
            "extract_gps_info: OS error while opening image '%s': %s",
            getattr(image_file, "name", "<unknown>"),
            exc,
        )
        return _no_gps

    # ---- Extract EXIF data -------------------------------------------------
    try:
        exif_data = image._getexif()   # Returns None if no EXIF
    except AttributeError:
        # Formats like PNG / GIF do not support _getexif
        logger.debug(
            "extract_gps_info: format '%s' has no _getexif method.",
            image.format,
        )
        return _no_gps
    except Exception as exc:          # noqa: BLE001 — broad, intentional
        logger.warning("extract_gps_info: failed to read EXIF data: %s", exc)
        return _no_gps

    if not exif_data:
        logger.debug(
            "extract_gps_info: image '%s' has EXIF support but no EXIF data.",
            getattr(image_file, "name", "<unknown>"),
        )
        return _no_gps

    # ---- Look for GPSInfo IFD ----------------------------------------------
    raw_gps = exif_data.get(_EXIF_GPS_TAG_ID)

    if not raw_gps:
        logger.debug(
            "extract_gps_info: no GPSInfo tag in EXIF for '%s'.",
            getattr(image_file, "name", "<unknown>"),
        )
        return _no_gps

    return _parse_gps_tags(raw_gps)


def has_geotag(image_file) -> bool:
    """
    Convenience wrapper — returns True if the image contains
    valid GPS latitude and longitude EXIF data, False otherwise.

    All exceptions are handled internally; this function never raises.

    Args:
        image_file: A file-like object (Django uploaded file or BytesIO).

    Returns:
        bool
    """
    return extract_gps_info(image_file)["has_gps"]
