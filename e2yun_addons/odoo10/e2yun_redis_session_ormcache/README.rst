=================================
Redis Session and ormchache Store
=================================



This module allows you to use a Redis database to manage sessions and ormchache,
instead of classic filesystem storage. for Open Source Odoo Cluster Implementation.


Requirements
============

You need to install and to start a Redis server to use this module.
Documentation is available on `Redis website`_.

You need to install package `redis`::

    pip install redis

.. _`Redis website`: http://redis.io/topics/quickstart 


Usage
=====

To use Redis, install this module

        1.prepare more than two servers, one is the master ,the others are slave(s)
		2.copy the files to the odoo server directory, and replace the old files;
		3.modify the master odoo.conf file:
            please add `enable_redis = True` option
			session_redis_url=redis://@redis_session-ip:6379/0
			ormcache_redis_url=redis://@redis_ormcache-ip:6379/0      ;strongly recommand the redis instance used in ormchace is not previous one
			max_cron_threads = x                             ;(x>1)
		4.modify all the slave(s) odoo.conf file:
            please add `enable_redis = True` option
			session_redis_url=redis://@redis_session-ip:6379/0       ;same as master
			ormcache_redis_url=redis://@redis_ormcache-ip:6379/0     ;same as master
			max_cron_threads = 0
		5.use a nfs directory as data directory for master and slave(s) server(mount as a folder).
		  odoo.conf:
		       data_dir = data   ==> a nfs directory

Bug Tracker
===========


GDPR / EU Privacy
=================

This addons does not collect any data and does not set any browser cookies.

Credits
=======

Contributors
------------

* Joytao

Maintainer
----------

This module is maintained by e2yun.
You are welcome to contribute.