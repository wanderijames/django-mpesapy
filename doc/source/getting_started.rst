.. _getting_started:


***************
Getting started
***************

.. _introduction:

Introduction
============

M-Pesa is a mobile money transfer system widely used in Kenya. It is a product of Safaricom. It was launched on
March 6, 2007. By may 2014 it had deposit value of KES 87,686,000,000.00 and transfers of KES 79,676,000,000.00.
They have public API's to be used by its merchants. Curently they support C2C, C2B, B2C and B2B mode of payments. In C2B they have 'Pay Bill' and
'Lipa na Mpesa'. The user/customer is required to enter both the 'business number' and his/her 'account number' while using the former and
only the 'business nmber' in the latter.
This Django app will consume the C2B, B2C and B2B API's. This version  will expose the firt one.

.. _installing_app:

Intalling Django-mpesapy
========================

You can install the app using::

  > pip install django-mpesapy

Open your :file:`settings.py` and add 'mpesapy' in the installed apps like this::

  INSTALLED_APPS = (
        ...
        'mpesapy',
    )
While in the same file define the following::

  MPESA_BUY_USER = "put_your_buy_goods_user_here"
  MPESA_BUY_PASS = "put_your_buy_goods_password_here"
  MPESA_PAYBILL_USER = "put_your_paybill_user_here"
  MPESA_PAYBILL_PASS = "put_paybill_password_here"


Include the mpesapy URLconf in your project urls.py like this::

  url(r'^mpesa/', include('mpesapy.urls',namespace='mpesa')),

Now run the following to create the necessary tables/models::

  > python manage.py migrate

.. _ipn_request:

IPN Request Form
================

This form should be used if the merchant already have a Paybill/Buy goods business number and wishes to have
instant payment notification (IPN) enabled. Take note of the business number, company address/contacts and technical 
contacts since they will be used in the form.

.. _paybill_ipn_request:

Pay Bill IPN Request Form
-------------------------

In the 'User Name' section put the 'MPESA_PAYBILL_USER' value defined earlier.
In the 'Password' section put the 'MPESA_PAYBILL_PASS' value defined earlier.
'URL for IPN Transactions' in both the test and production environment should be put to::

  https://your_server//mpesa/c2b_bill


.. _buy_goods_ipn_request:

Buy Goods IPN Request Form
--------------------------

In the 'User Name' section put the 'MPESA_BUY_USER' value defined earlier.
In the 'Password' section put the 'MPESA_BUY_PASS' value defined earlier.
'URL for IPN Transactions' in both the test and production environment should be put to::

  https://your_server//mpesa/c2b_bill


