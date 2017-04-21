========
Mpesapy
========

Mpesapy is a simple Django app that has been integrated with M-Pesa API.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "mpesapy" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'mpesapy',
    )

2. Include the mpesapy URLconf in your project urls.py like this::

    url(r'^mpesapy/', include('mpesapy.urls')),

3. Run `python manage.py migrate` to create the mpesapy models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to see some of the M-Pesa transactions that have been pushed to you by Safaricom (you'll need the Admin app enabled).