from pathlib import PurePosixPath

from django.core.files.storage import Storage


class CloudinaryMediaStorage(Storage):
    """Django storage backend for persistent image uploads on Heroku."""

    @staticmethod
    def _split_name(name):
        path = PurePosixPath(name)
        return str(path.with_suffix("")), path.suffix.lstrip(".") or None

    def _save(self, name, content):
        import cloudinary.uploader

        public_id, _ = self._split_name(name.replace("\\", "/"))
        if hasattr(content, "seek"):
            content.seek(0)
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
            unique_filename=False,
        )
        image_format = result.get("format")
        return (
            f"{result['public_id']}.{image_format}"
            if image_format
            else result["public_id"]
        )

    def delete(self, name):
        import cloudinary.uploader

        if not name:
            return
        public_id, _ = self._split_name(name)
        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
            invalidate=True,
        )

    def exists(self, name):
        # Upload names include UUIDs, so collisions are not expected.
        return False

    def url(self, name):
        import cloudinary.utils

        public_id, image_format = self._split_name(name)
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            format=image_format,
            resource_type="image",
            secure=True,
            fetch_format="auto",
            quality="auto",
        )
        return url

