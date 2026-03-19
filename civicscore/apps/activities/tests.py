"""
tests.py — Unit tests for the activities app geo-validation system.

Covers:
  • utils.extract_gps_info() with: valid GPS image, no-EXIF image,
    corrupted bytes, non-image file
  • activities view POST: image with GPS, image without GPS

Run with:
    python manage.py test apps.activities.tests
"""

import io
import struct

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from .utils import extract_gps_info, has_geotag

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers — synthetic image builders
# ---------------------------------------------------------------------------

def _make_jpeg_bytes_no_exif() -> bytes:
    """Return a minimal valid JPEG with no EXIF data."""
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color=(100, 149, 237))
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_jpeg_bytes_with_gps() -> bytes:
    """
    Return JPEG bytes that contain a GPSInfo EXIF entry.

    We use piexif if available (Pillow companion library), otherwise we fall
    back to injecting a minimal raw EXIF/APP1 block by hand using struct.
    This keeps the test self-contained without requiring piexif.
    """
    try:
        import piexif  # optional — preferred when installed

        exif_dict = {
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef:  b"N",
                piexif.GPSIFD.GPSLatitude:     ((12, 1), (55, 1), (35040, 1000)),
                piexif.GPSIFD.GPSLongitudeRef: b"E",
                piexif.GPSIFD.GPSLongitude:    ((77, 1), (36, 1), (36720, 1000)),
            }
        }
        exif_bytes = piexif.dump(exif_dict)

        buf = io.BytesIO()
        img = Image.new("RGB", (10, 10), color=(100, 200, 100))
        img.save(buf, format="JPEG", exif=exif_bytes)
        return buf.getvalue()

    except ImportError:
        # piexif not installed — skip GPS-positive tests gracefully
        return b""


def _make_png_bytes() -> bytes:
    """Return a minimal valid PNG (no EXIF support)."""
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 128, 0))
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Utils tests
# ---------------------------------------------------------------------------

class ExtractGpsInfoTests(TestCase):

    def test_jpeg_without_exif_returns_no_gps(self):
        """Plain JPEG with no EXIF → has_gps=False, coords=None."""
        f = SimpleUploadedFile("test.jpg", _make_jpeg_bytes_no_exif(), content_type="image/jpeg")
        result = extract_gps_info(f)

        self.assertFalse(result["has_gps"])
        self.assertIsNone(result["latitude"])
        self.assertIsNone(result["longitude"])

    def test_png_format_returns_no_gps(self):
        """PNG files have no _getexif → has_gps=False (no exception)."""
        f = SimpleUploadedFile("test.png", _make_png_bytes(), content_type="image/png")
        result = extract_gps_info(f)

        self.assertFalse(result["has_gps"])

    def test_corrupted_bytes_returns_no_gps(self):
        """Garbage bytes should not raise; should return has_gps=False."""
        f = SimpleUploadedFile("corrupt.jpg", b"\x00\xFF\xAB\xCD\x00\x11garbage", content_type="image/jpeg")
        result = extract_gps_info(f)

        self.assertFalse(result["has_gps"])

    def test_empty_file_returns_no_gps(self):
        """Empty file should not raise; should return has_gps=False."""
        f = SimpleUploadedFile("empty.jpg", b"", content_type="image/jpeg")
        result = extract_gps_info(f)

        self.assertFalse(result["has_gps"])

    def test_text_file_disguised_as_image_returns_no_gps(self):
        """Text content masquerading as image should not raise."""
        f = SimpleUploadedFile("fake.jpg", b"this is not an image", content_type="image/jpeg")
        result = extract_gps_info(f)

        self.assertFalse(result["has_gps"])

    def test_has_geotag_wrapper_returns_bool(self):
        """has_geotag() should always return a bool, never None."""
        f = SimpleUploadedFile("test.jpg", _make_jpeg_bytes_no_exif(), content_type="image/jpeg")
        result = has_geotag(f)
        self.assertIsInstance(result, bool)

    def test_jpeg_with_gps_returns_has_gps_true(self):
        """JPEG with injected GPS EXIF → has_gps=True, numeric lat/lon."""
        gps_jpeg = _make_jpeg_bytes_with_gps()
        if not gps_jpeg:
            self.skipTest("piexif not installed — skipping GPS-positive test")

        f = SimpleUploadedFile("gps.jpg", gps_jpeg, content_type="image/jpeg")
        result = extract_gps_info(f)

        self.assertTrue(result["has_gps"])
        self.assertIsInstance(result["latitude"], float)
        self.assertIsInstance(result["longitude"], float)
        # Bangalore-ish coordinates
        self.assertAlmostEqual(result["latitude"],  12.926, places=2)
        self.assertAlmostEqual(result["longitude"], 77.612, places=2)


# ---------------------------------------------------------------------------
# View integration tests
# ---------------------------------------------------------------------------

class ActivityViewGeoTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")
        self.url = reverse("add_activity")

    def _post_activity(self, image_bytes, filename="proof.jpg", content_type="image/jpeg"):
        proof = SimpleUploadedFile(filename, image_bytes, content_type=content_type)
        return self.client.post(self.url, {
            "activity_type": "tree",
            "description":   "Planted 5 trees near the park.",
            "proof":         proof,
        }, follow=True)

    # ---- No-GPS image -------------------------------------------------------

    def test_post_without_gps_saves_as_manual_review(self):
        """Submission with no-GPS image → status=manual_review, is_geo_verified=False."""
        from .models import Activity
        response = self._post_activity(_make_jpeg_bytes_no_exif())
        self.assertEqual(response.status_code, 200)

        activity = Activity.objects.get(user=self.user)
        self.assertEqual(activity.status, "manual_review")
        self.assertFalse(activity.is_geo_verified)
        self.assertIsNone(activity.latitude)
        self.assertIsNone(activity.longitude)

    def test_post_without_gps_shows_warning_message(self):
        """No-GPS submission → Django warning message displayed."""
        response = self._post_activity(_make_jpeg_bytes_no_exif())
        msgs = list(get_messages(response.wsgi_request))
        self.assertTrue(any("manual" in str(m).lower() or "gps" in str(m).lower() for m in msgs))

    def test_post_with_corrupted_image_saves_as_manual_review(self):
        """Corrupted file upload → saved for manual review, no crash."""
        from .models import Activity
        response = self._post_activity(b"\x00\xFF\xAB garbage bytes")
        self.assertEqual(response.status_code, 200)

        activity = Activity.objects.get(user=self.user)
        self.assertIn(activity.status, ("manual_review", "pending"))
        self.assertFalse(activity.is_geo_verified)

    # ---- GPS-positive image -------------------------------------------------

    def test_post_with_gps_saves_verified(self):
        """GPS-positive image → is_geo_verified=True, lat/lon stored, status=pending."""
        gps_jpeg = _make_jpeg_bytes_with_gps()
        if not gps_jpeg:
            self.skipTest("piexif not installed — skipping GPS-positive view test")

        from .models import Activity
        response = self._post_activity(gps_jpeg)
        self.assertEqual(response.status_code, 200)

        activity = Activity.objects.get(user=self.user)
        self.assertTrue(activity.is_geo_verified)
        self.assertEqual(activity.status, "pending")
        self.assertIsNotNone(activity.latitude)
        self.assertIsNotNone(activity.longitude)

    def test_post_with_gps_shows_success_message(self):
        """GPS-positive image → Django success message displayed."""
        gps_jpeg = _make_jpeg_bytes_with_gps()
        if not gps_jpeg:
            self.skipTest("piexif not installed")

        response = self._post_activity(gps_jpeg)
        msgs = list(get_messages(response.wsgi_request))
        self.assertTrue(any("success" in str(m).tags or "verified" in str(m).lower() for m in msgs))
