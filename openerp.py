# -*- coding: utf-8 -*-

## Generic packages
from fabric.api import *
from fabtools.vagrant import vagrant

## Librairies
from fabtools import service
from fabtools import deb
from fabtools import files
from fabtools import utils
from fabtools import require
from fabtools import cron
from datetime import datetime
from fabric.operations import run

## Import role
from openerp_config import *
from openerp_config_private import *

### specific config file
if DEPLOYMENT_TYPE == 'production':
    from openerp_config_production_private import *
elif DEPLOYMENT_TYPE =='test': 
    from openerp_config_test_private import *
else: 
    assert("problem !")

@task
def test():
    _require_nightly_production_script()
    
@task
def install():
    '''This task's goal is to install all the packages required for running 
OpenERP on a Debian and getting OpenERP sources by launchpad / github'''
    ## Install packages and locales
    _require_packages_locales()

    ## Install Apache, enable modules and disable default website
    _require_configured_apache()
    
    ## Install Postgres and create user
    _require_postgres_and_user()
    
    ## Create openerp user in linux
    _require_openerp_user()
    
    ## Get or update sources from launchpad
    _require_openerp_sources()

    ## Creating config.conf file for OpenERP
    _require_openerp_config_file()
    
    ## Creating openerp service
    _require_openerp_service()
    
    ## Install ssl certificate
    _require_certificate_deployment()

    ## Creating openerp apache site
    _require_openerp_website()
    
    ## Managing openerp logs by syslog 
    _require_configured_openerp_log()
    
    ## Nightly Script  
    if DEPLOYMENT_TYPE == 'production': 
        _require_nightly_production_script()
    elif DEPLOYMENT_TYPE == 'test': 
        _require_nightly_test_script()
    
    ## Configure ftp server
    _require_configured_ftp_server()

    ## Managing mail system
    _require_sendmail()
    
    ## Deploy specific files
    _required_specific_files()
    
    # Reloading services
    _require_services_stopped()
    _require_services_started()

@task
def update():
    '''This task's goal is to update all system librairies and code sources
    and to update databases'''
    # TODO : 
    ## Arrêter le serveur, service, & co.
    ## Lancer le backup.
    ## récupérer les sources
    ## Faire un update all des X databases avec un stop-after-init et worker = 1; 
    ## Lancer un 2ème backup.
    ##
#    if TEST_ENV: require.apache.enabled('openerp_test')
#    else: require.apache.disabled('openerp_test')
#    if not TEST_ENV: require.apache.enabled('openerp_production')
#    else: require.apache.disabled('openerp_production')
#    require.service.stopped('apache2')
#    require.service.stopped(OPENERP_SERVICE_NAME)
#    _backup_databases('pre_migration')
#    _require_openerp_sources()
#    _update_databases()
    _backup_databases('post_migration')
#    require.service.started(OPENERP_SERVICE_NAME)
#    require.service.started('apache2')

def _require_services_stopped():
    ## Stopping apache2, postgresql, Openerp service
    require.service.stopped('apache2')
    require.service.stopped(OPENERP_SERVICE_NAME)

def _require_services_started():
    ## starting apache2, postgresql, Openerp service
    require.service.started('apache2')
    require.service.started(OPENERP_SERVICE_NAME)

def _require_sendmail():
    params = {
        'MAIL_AUTH_USER' : MAIL_AUTH_USER,
        'MAIL_MAILHUB' : MAIL_MAILHUB,
        'ADMIN_USER' : ADMIN_USER,
    }
    require.files.template_file(
        path = '/etc/ssmtp/revaliases',
        template_source = 'files/etc/ssmtp/revaliases',
        context=params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='755', use_sudo = True,)
    params = {
        'EMAIL_ADMIN' : EMAIL_ADMIN,
        'MAIL_MAILHUB' : MAIL_MAILHUB,
        'SERVER_HOSTNAME' : SERVER_HOSTNAME,
        'MAIL_AUTH_USER' : MAIL_AUTH_USER,
        'MAIL_AUTH_PASS' : MAIL_AUTH_PASS,
        'MAIL_AUTH_METHOD' : MAIL_AUTH_METHOD,
    }
    require.files.template_file(
        path = '/etc/ssmtp/ssmtp.conf',
        template_source = 'files/etc/ssmtp/ssmtp.conf',
        context=params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='755', use_sudo = True,)

def _required_specific_files():
    require.files.template_file(
        path = '/usr/bin/wkhtmltopdf.sh',
        template_source = 'files/usr/bin/wkhtmltopdf.sh',
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='755', use_sudo = True,
    )

def _require_packages_locales():
    require.system.default_locale('fr_FR.UTF-8')
    ## Update system packages
    deb.update_index()
    deb.upgrade()
    
    ## Uninstall non required packages
    for package in PACKAGES_TO_UNINSTALL:
        require.deb.nopackage(package)
    
    ## Install required packages
    for package in PACKAGES_TO_INSTALL:
        require.deb.package(package)
    
    for pip_package in PIP_PACKAGES_TO_INSTALL:
        utils.run_as_root('pip install %s' %(pip_package))
    ## Update system packages
    utils.run_as_root('apt-get autoremove -y')
    deb.update_index()
    deb.upgrade()

def _require_configured_apache():
    ## Param apache2
    utils.run_as_root('a2enmod proxy_http proxy ssl rewrite')
    require.apache.disabled('default')
    require.apache.disabled('default-ssl')

def _require_postgres_and_user():
    ## Installs and configure our PostgreSQL server
    require.postgres.server()
    require.postgres.user(
        DB_OPENERP_USER,
        password=DB_OPENERP_PWD,
        createdb=True,
        createrole=True,
        login=True,
        connection_limit=20
    )

def _require_nightly_production_script():
    '''Create a script to backup openerp databases and plan execution 
    '''
    require.group(OPENERP_BACKUP_GROUP)
    require.directory(
        OPENERP_BACKUP_PATH, 
        owner=ADMIN_USER, group=OPENERP_BACKUP_GROUP, mode='755', use_sudo=True
    )
    command_pg_dump_lines , command_move_lines, command_put_ftp_lines = '', '', ''
    for database in OPENERP_DATABASES:
        command_pg_dump_lines += 'su - postgres -c "pg_dump --format=c %s --file=/tmp/postgres_%s.dump"\n' %(database, database)
        command_move_lines += 'mv /tmp/postgres_%s.dump $aRepertoireArchive' %(database)
        command_put_ftp_lines += 'put postgres_%s.dump' %(database)
    params = {
        'EMAIL_ADMIN' : EMAIL_ADMIN,
        'SERVER_HOSTNAME' : SERVER_HOSTNAME,
        'OPENERP_BACKUP_PATH' : OPENERP_BACKUP_PATH,
        'OPENERP_BACKUP_MAX_DAY' : OPENERP_BACKUP_MAX_DAY,
        'OPENERP_BACKUP_MAIL' : OPENERP_BACKUP_MAIL,
        'ADMIN_USER' : ADMIN_USER,
        'OPENERP_BACKUP_GROUP' : OPENERP_BACKUP_GROUP,
        'command_pg_dump_lines' : command_pg_dump_lines,
        'command_move_lines' : command_move_lines,
        'command_put_ftp_lines' : command_put_ftp_lines,
        'EXTERNAL_BACKUP_HOST' : EXTERNAL_BACKUP_HOST,
        'EXTERNAL_BACKUP_PORT' : EXTERNAL_BACKUP_PORT,
        'EXTERNAL_BACKUP_LOGIN' : EXTERNAL_BACKUP_LOGIN,
        'EXTERNAL_BACKUP_PASSWORD' : EXTERNAL_BACKUP_PASSWORD,
        'EXTERNAL_BACKUP_ROOT_FOLDER' : EXTERNAL_BACKUP_ROOT_FOLDER,
        'OPENERP_ERROR_LOG_NAME' : OPENERP_ERROR_LOG_NAME,
        'OPENERP_ERROR_LOG_PATH' : OPENERP_ERROR_LOG_PATH,
    }
    require.directory('/home/' + ADMIN_USER +'/scripts/',  mode='755', use_sudo=True)
    require.files.template_file(
        path = '/home/' + ADMIN_USER +'/scripts/nightly_production.sh',
        template_source = 'files/home/admin_user/scripts/nightly_production.sh',
        context = params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='755', use_sudo = True,
    )
    cron.add_task('nightly_production', OPENERP_BACKUP_TIMESPEC, 'root', '/home/' + ADMIN_USER +'/scripts/nightly_production.sh')
    
    require.user(SYSTEM_BACKUP_USER,
        password=SYSTEM_BACKUP_PWD,
        group=OPENERP_BACKUP_GROUP, 
        create_group=False,
        home=OPENERP_BACKUP_PATH,
        )

def _require_configured_ftp_server():
    require.files.template_file(
        path = '/etc/proftpd/conf.d/proftpd.conf',
        template_source = 'files/etc/proftpd/conf.d/proftpd.conf',
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='755', use_sudo = True,
    )
    require.service.restarted('proftpd')

def _backup_databases(suffix):
    for database in OPENERP_DATABASES:
        name =  database + '_' \
            + datetime.now().strftime('%Y_%m_%d__%H_%M_%S') + '_' \
            + suffix
        utils.run_as_root('su postgres -c "pg_dump --format=c %s --file=%s"' %(database, '/tmp/' + name))
        # move OPENERP_BACKUP_PATH

def _require_certificate_deployment():
    ## Deploying certificate
    require.file(
        path='/etc/ssl/certs/openerp.crt',
        source='files/etc/ssl/certs/openerp.crt',
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
    require.file(
        path='/etc/ssl/certs/openerp.pem',
        source='files/etc/ssl/certs/openerp.pem',
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
    require.file(
        path='/etc/ssl/private/openerp.key',
        source='files/etc/ssl/private/openerp.key',
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )

def _update_databases():
    for database in OPENERP_DATABASES:
        run("python %s -c %sconfig.conf --database=%s --stop-after-init --worker=1" 
            %(OPENERP_SCRIPT_PATH, OPENERP_DIRECTORY, database))

def _require_openerp_user():
    # Require a user without shell access
    require.user(SYSTEM_USER_OPENERP, create_home=False, shell='/bin/false')

def _require_openerp_sources():
    '''get or update a repository, if required'''

    ## Getting sources of OpenERP
    require.directory(OPENERP_DIRECTORY, use_sudo=True)
    for params in OPENERP_REPOSITORIES:
        path = OPENERP_DIRECTORY + params['name']
        if params['url'][:3] == 'lp:':
            if not files.is_dir(path): 
                print "-> Checkout new directory '%s' at revision '%s'" %(path, params['rev'])
                utils.run_as_root('bzr checkout --lightweight --quiet %s %s --revision=%s' %(params['url'], path, params['rev']))
            else: 
                print "-> Update directory '%s' at revision '%s'" %(path, params['rev'])
                utils.run_as_root('bzr update --quiet %s --revision=%s' %(path, params['rev']))
        else:
            assert False

def _require_openerp_config_file():
    ## Creating config.conf file for OpenERP
    addons_path_openerp = ''
    for params in OPENERP_REPOSITORIES:
        if params['addons_folder']: 
            addons_path_openerp += OPENERP_DIRECTORY + params['name'] + params['addons_folder'] + ','
    
    addons_path_openerp = addons_path_openerp[:-1]
    params = {
        'OPENERP_ADMIN_PWD' : OPENERP_ADMIN_PWD,
        'DB_HOST' : DB_HOST,
        'DB_PORT' : DB_PORT,
        'DB_OPENERP_USER' : DB_OPENERP_USER,
        'DB_OPENERP_PWD' : DB_OPENERP_PWD,
        'OPENERP_BIN_DIRECTORY' : OPENERP_BIN_DIRECTORY,
        'addons_path_openerp' : addons_path_openerp,
        'OPENERP_XML_RPC_IP' : OPENERP_XML_RPC_IP,
        'OPENERP_XML_RPC_PORT' : OPENERP_XML_RPC_PORT,
        'OPENERP_NET_RPC_IP' : OPENERP_NET_RPC_IP,
        'OPENERP_NET_RPC_PORT' : OPENERP_NET_RPC_PORT,
    }
    require.files.template_file(
        path = OPENERP_DIRECTORY + 'config.conf',
        template_source = 'files/opt/openerp/config.conf',
        context = params,
       owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
    
def _require_openerp_service():
    ## Creating openerp service
    params = {
        'OPENERP_DIRECTORY' : OPENERP_DIRECTORY,
        'SYSTEM_USER_OPENERP' : SYSTEM_USER_OPENERP, 
        'OPENERP_SCRIPT_NAME' : OPENERP_SCRIPT_NAME,
        'OPENERP_SCRIPT_DIRECTORY' : OPENERP_SCRIPT_DIRECTORY,
    }
    require.files.template_file(
        path = '/etc/init.d/%s' %(OPENERP_SERVICE_NAME),
        template_source = 'files/etc/init.d/openerp',
        context = params,
        owner=SYSTEM_USER_OPENERP, group=SYSTEM_USER_OPENERP,
        mode='755', use_sudo = True,
    )

    utils.run_as_root('update-rc.d %s defaults' %(OPENERP_SERVICE_NAME))

def _require_openerp_website():
    params = {
        'URL_OPENERP' : URL_OPENERP,
        'EMAIL_ADMIN' : EMAIL_ADMIN, 
        'OPENERP_XML_RPC_IP' : OPENERP_XML_RPC_IP,
        'OPENERP_XML_RPC_PORT' : OPENERP_XML_RPC_PORT,
    }
    require.files.template_file(
        path = '/etc/apache2/sites-available/openerp.conf',
        template_source = 'files/etc/apache2/sites-available/openerp.conf',
        context = params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
    ## Enabling OpenERP Web Site
    require.apache.enabled('openerp')

def _require_configured_openerp_log():
    ## Managing openerp logs by syslog 
    require.directory(OPENERP_LOG_FOLDER, use_sudo=True)
    params = {
        'OPENERP_NORMAL_LOG_PATH' : OPENERP_NORMAL_LOG_PATH,
        'OPENERP_ERROR_LOG_PATH' : OPENERP_ERROR_LOG_PATH,
    }
    require.files.template_file(
        path = '/etc/rsyslog.d/20-openerp.conf',
        template_source = 'files/etc/rsyslog.d/20-openerp.conf',
        context = params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
    require.service.restarted('rsyslog')

    ## Rotation of OpenERP's log
    params = {
        'OPENERP_NORMAL_LOG_PATH_ALL' : OPENERP_NORMAL_LOG_PATH_ALL,
        'OPENERP_ERROR_LOG_PATH_ALL' : OPENERP_ERROR_LOG_PATH_ALL,
    }
    require.files.template_file(
        path = '/etc/logrotate.d/openerp.conf',
        template_source = 'files/etc/logrotate.d/openerp.conf',
        context = params,
        owner=ADMIN_USER, group=ADMIN_GROUP, mode='644', use_sudo = True,
    )
