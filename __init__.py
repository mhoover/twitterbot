import ConfigParser
import os
import pytz

from datetime import datetime


def update_args(args):
    cfg = ConfigParser.ConfigParser()
    cfg.read('config.cfg')

    args['keys'] = [os.getenv(key) for key in args['keys']]
    args['date'] = datetime.strftime(datetime.now(pytz.utc), format='%Y-%m-%d')
    if not args['directory']:
        args['directory'] = cfg.get('parameters', 'directory')

    return args
