# TINO Photography Site

## Folder Structure
```
photography_site/
├── app.py                   ← Run this to start the site
├── requirements.txt         ← Python packages
├── README.md
├── instance/
│   └── bookings.db          ← Database (auto-created)
├── templates/
│   ├── base.html            ← Master layout (nav + footer)
│   ├── index.html           ← Home page
│   ├── portfolio.html       ← Portfolio with filters
│   ├── services.html        ← Services & pricing
│   ├── about.html           ← About page
│   ├── contact.html         ← Booking form
│   └── admin.html           ← View all bookings
└── static/
    ├── css/
    │   └── style.css        ← All styles
    ├── js/                  ← (empty, JS is inline)
    └── images/              ← PUT YOUR PHOTOS HERE
```

## Setup (do this once)
1. Open terminal in the photography_site folder
2. Run: pip install -r requirements.txt
3. Run: python app.py
4. Open browser: http://127.0.0.1:5000

## Adding Your Photos
Just drop your .jpg files into static/images/
Make sure the filenames match exactly:
  crypt.jpg, bedroom1.jpg, dylanpark.jpg, tinoroom.jpg,
  streetview.jpg, dylancar.jpg, chinafood.jpg, cecilstreet.jpg,
  monbrand1.jpg, monbrand2.jpg, timbboots.jpg, flowers.jpg,
  churchwindow.jpg, churchscript.jpg, churchentry.jpg,
  churchfront.jpg, me&dylan.jpg, restuarant.jpg

## Email Setup (iCloud)
1. Go to appleid.apple.com
2. Sign in > Security > App-Specific Passwords > Generate
3. Name it "Photography Site"
4. Before running app.py, set the password:
   Windows: set MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   Mac/Linux: export MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
5. Then run: python app.py

## Admin Dashboard
Go to: http://127.0.0.1:5000/admin
See all enquiries, mark as read/replied, click reply to email them.

## Pages
/ ............. Home
/portfolio .... All photos with category filters
/services ..... Services & pricing
/about ........ About you
/contact ...... Booking form
/admin ........ Your bookings dashboard
