__author__ = 'Altertech, https://www.altertech.com/'
__copyright__ = 'Copyright (C) 2012-2020 Altertech'
__license__ = 'Apache License 2.0'
__version__ = '0.0.1'

import eva.pluginapi as pa
import sqlalchemy as sa
import threading

from neotasker import g

sql = sa.text

from types import SimpleNamespace
db_lock = threading.RLock()
flags = SimpleNamespace(ready=False, db=None)

ro_fields = []
rw_fields = []

logger = pa.get_logger()


# undocummented thread-local, don't use in own plugins
def get_db():
    with db_lock:
        if not g.has('userdb'):
            g.x_userinfo_db = flags.db.connect()
        else:
            try:
                g.x_userinfo_db.execute('select 1')
            except:
                try:
                    g.userdb.close()
                except:
                    pass
                g.x_userinfo_db = flags.db.connect()
        return g.x_userinfo_db


def init(config, **kwargs):
    for f in [x.strip() for x in config.get('ro', '').split(',')]:
        ro_fields.append(f)
    for f in [x.strip() for x in config.get('rw', '').split(',')]:
        rw_fields.append(f)
    from eva.core import create_db_engine, format_db_uri
    # undocummented internal function, don't use in own plugins
    db = format_db_uri(config['db'])
    flags.db = create_db_engine(db)
    logger.debug('userinfo plugin loaded')
    logger.debug(f'userinfo.db = {db}')
    logger.debug(f'userinfo.ro_fields = {", ".join(ro_fields)}')
    logger.debug(f'userinfo.rw_fields = {", ".join(rw_fields)}')
    pa.register_apix(APIFuncs(), sys_api=True)
    flags.ready = True


def before_start(**kwargs):
    dbconn = get_db()
    meta = sa.MetaData()
    t_userinfo = sa.Table('userinfo', meta,
                          sa.Column('u', sa.String(128), primary_key=True),
                          sa.Column('utp', sa.String(32), primary_key=True),
                          sa.Column('name', sa.String(256), primary_key=True),
                          sa.Column('value', sa.String(256)))
    try:
        meta.create_all(dbconn)
    except:
        pa.log_traceback()
        logger.error('unable to create userinfo table in db')


class APIFuncs(pa.APIX):

    @pa.api_log_d
    def get_field(self, **kwargs):
        k, u, utp, name = pa.parse_function_params(kwargs, 'kupn', 'S..S')
        if u is not None:
            if not pa.key_check(k, master=True):
                raise pa.AccessDenied(
                    'getting info for the specified user requires master key')
        else:
            u = pa.get_aci('u')
            utp = pa.get_aci('utp')
        if name not in ro_fields and name not in rw_fields:
            raise pa.ResourceNotFound(f'field {name}')
        if u is None:
            raise pa.AccessDenied('user not logged in')
        if utp is None:
            utp = ''
        dbconn = get_db()
        r = dbconn.execute(sql('select value from userinfo where '
                               'u=:u and utp=:utp and name=:name'),
                           u=u,
                           utp=utp,
                           name=name)
        d = r.fetchone()
        return {name: d.value if d else ''}

    @pa.api_log_i
    def set_field(self, **kwargs):
        k, u, utp, name, value = pa.parse_function_params(
            kwargs, 'kupnv', 'S..SSS')
        if u is not None:
            if not pa.key_check(k, master=True):
                raise pa.AccessDenied(
                    'setting info for the specified user requires master key')
        else:
            u = pa.get_aci('u')
            utp = pa.get_aci('utp')
        if u is None:
            raise pa.AccessDenied('user not logged in')
        if utp is None:
            utp = ''
        if name in ro_fields:
            if not pa.key_check(k, master=True):
                raise pa.AccessDenied(
                    f'field {name} is read-only, master is required to set')
        elif name not in rw_fields:
            raise pa.ResourceNotFound(f'field {name}')
        dbconn = get_db()
        r = dbconn.execute(sql('select value from userinfo where '
                               'u=:u and utp=:utp and name=:name'),
                           u=u,
                           utp=utp,
                           name=name)
        d = r.fetchone()
        if d is None:
            dbconn.execute(sql('insert into userinfo(u, utp, name, value) '
                               'values (:u, :utp, :name, :value)'),
                           u=u,
                           utp=utp,
                           name=name,
                           value=value)
        else:
            dbconn.execute(sql('update userinfo set value=:value where '
                               'u=:u and utp=:utp and name=:name'),
                           u=u,
                           utp=utp,
                           name=name,
                           value=value)
        return True