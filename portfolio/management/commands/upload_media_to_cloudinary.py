from django.core.management.base import BaseCommand
from django.conf import settings
from portfolio.models import Photo
import os

try:
    import cloudinary
    import cloudinary.uploader
except Exception:
    cloudinary = None


class Command(BaseCommand):
    help = ('Upload local media/photos files to Cloudinary and update '
            'Photo.image field.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show actions without uploading')
        parser.add_argument(
            '--path',
            default=os.path.join(settings.MEDIA_ROOT, 'photos'),
            help='Path to local photos folder')

    def handle(self, *args, **options):
        if cloudinary is None:
            self.stderr.write(
                'cloudinary package not available. Install `cloudinary` '
                'and configure CLOUDINARY_URL.')
            return

        photos_path = options['path']
        dry_run = options['dry_run']

        if not os.path.isdir(photos_path):
            self.stderr.write(f'Photos path does not exist: {photos_path}')
            return

        # Map filenames to Photo objects (by basename)
        photos_map = {}
        for p in Photo.objects.all():
            if p.image:
                name = os.path.basename(p.image.name)
                photos_map.setdefault(name, []).append(p)

        uploaded = 0
        for fname in sorted(os.listdir(photos_path)):
            full = os.path.join(photos_path, fname)
            if not os.path.isfile(full):
                continue
            self.stdout.write(f'Found file: {fname}')
            if fname not in photos_map:
                self.stdout.write(self.style.WARNING(
                    f'No Photo record references {fname}; skipping'))
                continue
            if dry_run:
                photo_count = len(photos_map[fname])
                self.stdout.write(self.style.NOTICE(
                    f'Would upload {full} and update {photo_count} Photo(s)'))
                continue

            # Upload to Cloudinary
            try:
                res = cloudinary.uploader.upload(full, resource_type='image')
                url = res.get('secure_url')
                public_id = res.get('public_id')
                self.stdout.write(self.style.SUCCESS(
                    f'Uploaded {fname} to {url}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f'Upload failed for {fname}: {e}'))
                continue

            # Update Photo instances to point to the public_id
            # (Cloudinary storage backend will craft URL)
            for p in photos_map[fname]:
                # store the public_id or full URL depending on your
                # storage backend; here set to public_id
                # If using django-cloudinary-storage, you can store the
                # public_id with folder if needed.
                p.image.name = public_id
                p.save()
                uploaded += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Uploaded and updated {uploaded} Photo(s).'))
