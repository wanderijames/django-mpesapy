========
Mpesapy
========

Mpesapy is a simple Django app that has been integrated with M-Pesa API.

Detailed documentation is in the "docs" directory.

Has been tested with Django 3+. Versions prior to 1.1.3 has been tested with Django==1.9.

Checkout the latest code in the repo `wanderijames/django-mpesapy <https://github.com/wanderijames/django-mpesapy>`_.

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

4. Start the development server and visit http://127.0.0.1:8000/admin/ to add a business number with its settings and IPN details. The following is an example::

   .. image:: http://res.cloudinary.com/dqothee9u/image/upload/v1492782379/change_business2_fpxlso.png



Things to remember
-------------------
1. For M-Pesa G2 API they will need to whitelist your server IP.
2. Sometimes the **register_url** doesn't work, so send them the URL to register. Your URL would be something like the following::

    https://host/mpesapy/v2/900900/validate/

    https://host/mpesapy/v2/900900/confirm/
