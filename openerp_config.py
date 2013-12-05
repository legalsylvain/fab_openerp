# -*- coding: utf-8 -*-

################################################################################
# Configuration file for fab deployment. 
# Here there is public common parameters ; 
# If there is parameters with '***' value, please redefine in a config private file
################################################################################

DEPLOYMENT_TYPE = 'production'

### Server Configuration ###
SERVER_HOSTNAME = '***'
ADMIN_USER = '***'
ADMIN_GROUP = '***'

### Mail Configuration ###
MAIL_MAILHUB = '***'
MAIL_AUTH_USER = '***'
MAIL_AUTH_PASS = '***'
MAIL_AUTH_METHOD = '***'

### Database configuration ###
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_OPENERP_USER = '***'
DB_OPENERP_PWD = '***'

### OpenERP Configuration (System) ###
SYSTEM_USER_OPENERP = '***'
OPENERP_SERVICE_NAME = 'openerp'
OPENERP_DIRECTORY = '/opt/openerp/'
OPENERP_BIN_DIRECTORY = OPENERP_DIRECTORY + 'ocb-server/bin/'
OPENERP_SCRIPT_NAME = 'openerp-server'
OPENERP_SCRIPT_DIRECTORY = OPENERP_DIRECTORY + 'ocb-server/'
OPENERP_SCRIPT_PATH = OPENERP_SCRIPT_DIRECTORY + OPENERP_SCRIPT_NAME

### OpenERP Configuration (network) ###
URL_OPENERP = '***'
EMAIL_ADMIN = '***'
OPENERP_XML_RPC_IP = 'localhost'
OPENERP_XML_RPC_PORT = '8069'
OPENERP_NET_RPC_IP = 'localhost'
OPENERP_NET_RPC_PORT = '8070'

### OpenERP Configuration (Repositories) ###
OPENERP_REPOSITORIES = [
    {'name':'***', 'url':'***', 'rev':'***', 'addons_folder': None,},
    {'name':'***', 'url':'***', 'rev':'***', 'addons_folder': '***',},
]

### OpenERP Databases ###
OPENERP_DATABASES = ['***', '***']

### OpenERP Configuration (Backup folder) ###
OPENERP_BACKUP_PATH = '***'
OPENERP_BACKUP_MAIL = '***'
OPENERP_BACKUP_MAX_DAY = '***'
OPENERP_BACKUP_GROUP = '***'
OPENERP_BACKUP_TIMESPEC = '***'
SYSTEM_BACKUP_USER = '***'
SYSTEM_BACKUP_PWD = '***'

### OpenERP logs ###
OPENERP_LOG_FOLDER = '/var/log/openerp/'
OPENERP_NORMAL_LOG_PATH =       OPENERP_LOG_FOLDER + 'openerp-syslog.log'
OPENERP_NORMAL_LOG_PATH_ALL =   OPENERP_LOG_FOLDER + '*.log'
OPENERP_ERROR_LOG_PATH =        OPENERP_LOG_FOLDER + 'openerp-syslog.err'
OPENERP_ERROR_LOG_PATH_ALL =    OPENERP_LOG_FOLDER + '*.err'

### OpenERP Configuration (Miscelleaneous) ###
OPENERP_ADMIN_PWD = '***'

### Packages configuration ###
PACKAGES_TO_UNINSTALL = [
    '',
]
PACKAGES_TO_INSTALL = [
    'byobu', 'di', 'bzr', 'vim', 'nano', 'python-pip',
    'postgresql-9.1', 'apache2', 'proftpd', 'ssmtp', 
    'python2.7', 'python-dateutil', 'python-feedparser', 'python-gdata', 'python-ldap', 'python-libxslt1',
    'python-lxml', 'python-mako', 'python-openid', 'python-psycopg2', 'python-pybabel', 'python-pychart',
    'python-pydot', 'python-pyparsing', 'python-reportlab', 'python-simplejson', 'python-tz', 'python-vatnumber',
    'python-vobject', 'python-webdav', 'python-werkzeug', 'python-xlwt', 'python-yaml', 'python-zsi', 'python-unittest2',
    'docutils-common', 'docutils-doc', 'python-docutils', 'python-jinja2', 'python-mock', 'python-psutil',
    'python-pygments', 'python-roman',  'python-fpconst', 'python-soappy', 
    'python-cairo', 
]
PIP_PACKAGES_TO_INSTALL = [
    'cairosvg',
]
