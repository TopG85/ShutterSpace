Heroku deploy checklist

1) Prepare requirements for Heroku (the repo contains `requirements.heroku.txt`):

   ./bin/heroku_prepare.sh

2) Push to Heroku (replace <app-name> if needed):

   git push heroku main

3) Run migrations and collectstatic on the dyno:

   heroku run python manage.py migrate --app <app-name>
   heroku run python manage.py collectstatic --noinput --app <app-name>

4) If collectstatic reports errors, fetch logs while it's running:

   heroku logs --tail --app <app-name>

5) Verify the staticfiles folder exists on the dyno:

   heroku run ls -la /app/staticfiles --app <app-name>

6) Check DISABLE_COLLECTSTATIC (must be blank or 0):

   heroku config:get DISABLE_COLLECTSTATIC --app <app-name>

7) If you plan to persist user uploads, configure Cloudinary (recommended) or S3:

   - Add `CLOUDINARY_URL` as a Heroku config var.
   - Ensure `django-cloudinary-storage==0.3.0` and `cloudinary==1.36.0` are present in requirements.

If you prefer I can open and update `requirements.txt` directly instead of using the helper script; just tell me which approach you prefer.
