# -*- coding: utf-8 -*-
#  See LICENSE file for full copyright and licensing details.

""" Models registries redis.

"""
from collections import Mapping
from contextlib import closing
import logging
import odoo
from odoo.tools import (assertion_report, config)

from odoo.modules.registry import Registry

def is_redis_session_store_activated():
    return config.get('enable_redis')


try:
    import redis
    from . import RedisLRU

except ImportError:
    if is_redis_session_store_activated():
        raise ImportError('Please install package python-redis: apt-get install python-redis')


_logger = logging.getLogger(__name__)


class RegistryRedis(Mapping):
    #models.BaseModel._param_lock = _param_lock
    def init(self, db_name):
        self.models = {}  # model name/model instance mapping
        self._sql_error = {}
        self._init = True
        self._init_parent = {}
        self._assertion_report = assertion_report.assertion_report()
        self._fields_by_model = None

        # modules fully loaded (maintained during init phase by `loading` module)
        self._init_modules = set()

        self.db_name = db_name
        self._db = odoo.sql_db.db_connect(db_name)

        # special cursor for test mode; None means "normal" mode
        self.test_cr = None

        # Indicates that the registry is
        self.ready = False

        # Inter-process signaling:
        # The `base_registry_signaling` sequence indicates the whole registry
        # must be reloaded.
        # The `base_cache_signaling sequence` indicates all caches must be
        # invalidated (i.e. cleared).
        self.registry_sequence = None
        self.cache_sequence = None

        # self.cache = LRU(8192)
        r = redis.StrictRedis.from_url(odoo.tools.config['ormcache_redis_url'])
        self.cache = RedisLRU.RedisLRU(r, db_name)

        # Flag indicating if at least one model cache has been cleared.
        # Useful only in a multi-process context.
        self.cache_cleared = False

        with closing(self.cursor()) as cr:
            has_unaccent = odoo.modules.db.has_unaccent(cr)
            if odoo.tools.config['unaccent'] and not has_unaccent:
                _logger.warning("The option --unaccent was given but no unaccent() function was found in database.")
            self.has_unaccent = odoo.tools.config['unaccent'] and has_unaccent


    Registry.init = init

    @classmethod
    def delete(cls, db_name):
        """ Delete the registry linked to a given database. """
        with cls._lock:
            if db_name in cls.registries:
                cls.registries[db_name].clear_caches()
                del cls.registries[db_name]

    Registry.delete = delete