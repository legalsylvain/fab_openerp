#!/bin/sh
# -*- coding: utf-8 -*-

### Entete du mail a envoyer en fin de tache
aFichier="/home/%(ADMIN_USER)s/mail.txt"
echo "Subject: Script nocturne sur serveur de production\n" > $aFichier
echo "Debut d'execution du script : "$(date +%%D-%%Hh%%Mm%%Ss) >> $aFichier

### creation du repertoire de backup
aRepertoireArchive="%(OPENERP_BACKUP_PATH)sbackup_$(date +%%Y-%%m-%%d_%%H-%%M-%%S)/"
mkdir -m 755 $aRepertoireArchive

######################################
### Backup OpenERP
######################################

### Arrêt de production
service apache2 stop > /dev/null
service openerp stop > /dev/null

### Sauvegarde des bases de donnees OpenERP
%(command_pg_dump_lines)s

### Reprise de production
service apache2 start > /dev/null
service openerp start > /dev/null

### Deplacement des dump
%(command_move_lines)s
chmod 755 -R $aRepertoireArchive
chown %(ADMIN_USER)s -R $aRepertoireArchive
chgrp %(OPENERP_BACKUP_GROUP)s -R $aRepertoireArchive


### Purge des anciens repertoires
find %(OPENERP_BACKUP_PATH)s -maxdepth 1 -mindepth 1 -atime +%(OPENERP_BACKUP_MAX_DAY)s -exec rm -r {} \;

### Envoi d'un mail
echo "Fin d'execution du script : "$(date +%%D-%%Hh%%Mm%%Ss) >> $aFichier
echo "\n*** ETAT DES SAUVEGARDES ***" >> $aFichier
du -h --max-depth=1 %(OPENERP_BACKUP_PATH)s >> $aFichier
echo "\n*** ETAT DU SERVEUR ***" >> $aFichier
di -h --type ext3,ext4 >> $aFichier
echo "\n*** SERVEUR ***" >> $aFichier
hostname >> $aFichier
sendmail %(OPENERP_BACKUP_MAIL)s < $aFichier


