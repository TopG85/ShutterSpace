from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
import os
from portfolio.models import Profile, Photo


class Command(BaseCommand):
    help = 'Upload local MEDIA files to default storage (e.g. Cloudinary) and update model fields'

    def handle(self, *args, **options):
        """
        Safe media migration:
        - If no cloud storage is detected (DEFAULT_FILE_STORAGE doesn't mention 'cloud' and
          CLOUDINARY_URL isn't set), the command prints a warning and exits (safe for Heroku).
        - For each Profile.avatar and Photo.image:
          * Try reading the file from disk under MEDIA_ROOT and re-save it (uploads to configured storage).
          * If the file isn't present on disk, attempt to open it through the model field storage and re-save.
          * Each item is wrapped in try/except so one failure doesn't abort the whole run.
        """
        default_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', '') or ''
        has_cloud_env = 'CLOUDINARY_URL' in os.environ

        # If we don't detect cloud storage, do a safe skip (so it won't crash on Heroku)
        if 'cloud' not in default_storage.lower() and not has_cloud_env:
            self.stdout.write(self.style.WARNING(
                'Cloud storage not detected. This command is intended to be run locally with a cloud '
                'DEFAULT_FILE_STORAGE (e.g. django-cloudinary-storage) or with CLOUDINARY_URL set. '
                'Skipping migration.'
            ))
            return

        media_root = getattr(settings, 'MEDIA_ROOT', '') or ''

        def safe_username(obj):
            try:
                return obj.user.username
            except Exception:
                return getattr(obj.user, 'id', 'unknown')

        # Migrate avatars
        for profile in Profile.objects.all():
            try:
                field = getattr(profile, 'avatar', None)
                if not field:
                    continue
                name = getattr(field, 'name', '') or ''
                if not name:
                    continue

                local_path = os.path.join(media_root, name) if media_root else None

                if local_path and os.path.exists(local_path):
                    try:
                        with open(local_path, 'rb') as f:
                            profile.avatar.save(os.path.basename(name), File(f), save=True)
                        self.stdout.write(self.style.SUCCESS(
                            f'Uploaded avatar for {safe_username(profile)} from disk: {name}'
                        ))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'Failed to upload avatar for {safe_username(profile)} from disk ({name}): {e}'
                        ))
                else:
                    # Fallback: try opening from the field storage (may be remote)
                    try:
                        with profile.avatar.open('rb') as f:
                            profile.avatar.save(os.path.basename(name), File(f), save=True)
                        self.stdout.write(self.style.SUCCESS(
                            f'Uploaded avatar for {safe_username(profile)} from storage: {name}'
                        ))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'Could not open avatar for {safe_username(profile)} ({name}): {e}'
                        ))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Unexpected error migrating avatar for profile {profile.pk}: {e}'))

        # Migrate photos
        for photo in Photo.objects.all():
            try:
                field = getattr(photo, 'image', None)
                if not field:
                    continue
                name = getattr(field, 'name', '') or ''
                if not name:
                    continue

                local_path = os.path.join(media_root, name) if media_root else None

                if local_path and os.path.exists(local_path):
                    try:
                        with open(local_path, 'rb') as f:
                            photo.image.save(os.path.basename(name), File(f), save=True)
                        self.stdout.write(self.style.SUCCESS(f'Uploaded photo {photo.id} from disk: {name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to upload photo {photo.id} from disk ({name}): {e}'))
                else:
                    try:
                        with photo.image.open('rb') as f:
                            photo.image.save(os.path.basename(name), File(f), save=True)
                        self.stdout.write(self.style.SUCCESS(f'Uploaded photo {photo.id} from storage: {name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Could not open photo {photo.id} ({name}): {e}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Unexpected error migrating photo {photo.pk}: {e}'))

        self.stdout.write(self.style.SUCCESS('Media migration complete.'))