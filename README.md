# ShutterSpace

A photgraphy portfolio website.

# Front-End Design

I used Instagram, 500px and my old photography website as inspration for my photography portfolio website.

https://instagram.com/

https://500px.com/

https://daniel-carson.format.com/

![adobe](<docs/readme_images/Screenshot 2025-09-26 at 14.08.03 (3)-1.png>)

I've used Adobe colour wheel I took a screenshot of 
my webpage and used the colours from that to come up with a colour palette.


I took a screenshot of my website and you can upload to Adobe colour a choose the colour from within your site. You
can choose colour harmony, from Analogous, complementray and many more.

![website](<docs/readme_images/Screenshot 2025-09-26 at 14.28.44 (3).png>)

## Wireframes

### Homepage Desktop Design
![Homepage Wireframe](docs/readme_images/New%20Wireframe%201.png)
![Desktop Create an account Wireframe](docs/readme_images/New%20Wireframe%204.png)

### Tablet Design
![TabletHomepageWireframe](docs/readme_images/New%20Wireframe%205.png)
![TabletCreateanaccountWireframe](docs/readme_images/New%20Wireframe%203.png)

### Mobile Design
![MobileHomepageWireframe](docs/readme_images/New%20Wireframe%202.png)
![MobileCreateanaccountWireframe](docs/readme_images/New%20Wireframe%206.png)

# Design UI & UX


# Database

My ERD diagram.

![erddiagram](<docs/readme_images/Screenshot 2025-09-26 at 13.38.19 (3).png>)

https://drawsql.app/teams/daniel-carson/diagrams/shutterspace

# Agile Methodology

# User stories

## Testing

Detailed testing documentation can be found [here.](./TESTING.md)

# Resources 

Copilot

Google AI
https://www.google.com/search?q=&sca_esv=8d061dbbff1738e7&sxsrf=AE3TifMDSt1uGQ1V7E2qGOclabDn5poumA%3A1758977381038&source=hp&ei=ZN3XaM6cO-WjkdUP7fvjqQM&iflsig=AOw8s4IAAAAAaNfrdSZxt8ZRKRg-qUPbAypTDRpsgrXv&aep=22&udm=50&ved=0ahUKEwjO3tev_fiPAxXlUaQEHe39ODUQteYPCCU&oq=&gs_lp=Egdnd3Mtd2l6IgBIAFAAWABwAHgAkAEAmAEAoAEAqgEAuAEByAEAmAIAoAIAmAMAkgcAoAcAsgcAuAcAwgcAyAcA&sclient=gws-wiz

Getting Started with Django: Building a Portfolio App.
https://realpython.com/courses/django-portfolio-project/

## Deploy to Heroku (helper)

This project includes a runtime pin (`runtime.txt`) to use Python 3.11 on Heroku and a small helper script to push, run migrations and collectstatic.

Make the helper executable and run it:

```bash
chmod +x bin/deploy.sh
./bin/deploy.sh <heroku-app-name>
```

Alternatively run the commands manually (replace `<app>` with your Heroku app name):

```bash
git push heroku main
heroku run python manage.py migrate --app <app>
heroku run python manage.py collectstatic --noinput --app <app>
heroku restart --app <app>
```