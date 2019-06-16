.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==========================
E2yun Partners Geolocation
==========================
This module extends Partners Geolocation
if partner.country_id.code == 'CN' use Baidu Geolocation
others use Bing Geolocation
replace website google map with baidu map

Requirements
============

You need to install and to start a baidu aip sdk to use this module.
Documentation is available on `Baidu AIP website`_.

You need to install package `baidu-aip`::

    pip install baidu-aip

.. _`Baidu AIP website`: http://ai.baidu.com/docs#/OCR-Python-SDK/top


Configuration
=============


Set the configuration parameter ``baidu_app_id``

Set the configuration parameter ``baidu_app_key``

Set the configuration parameter ``baidu_secret_key``



Bug Tracker
===========



Credits
=======

Contributors
------------

* Joytao <joytao.zhu@e2yun.com>

Maintainer
----------

.. image:: http://www.e2yun.com:8080/logo.png
   :alt: Odoo partner
   :target: http://www.e2yun.com

This module is maintained by the E2yun.


To contribute to this module, please visit http://e2yun.com.
