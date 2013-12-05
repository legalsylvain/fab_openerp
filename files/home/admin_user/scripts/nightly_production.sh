#!/bin/sh
# -*- coding: utf-8 -*-

### Entete du mail a envoyer en fin de tache
aFichier="/home/%(ADMIN_USER)s/mail.txt"
echo "To:%(OPENERP_BACKUP_MAIL)s" > $aFichier
echo "From:%(EMAIL_ADMIN)s" >> $aFichier
echo "Subject: Sauvegarde sur le serveur %(SERVER_HOSTNAME)s" >> $aFichier
echo "MIME-Version: 1.0" >> $aFichier
aMailPart='my_boundary'
echo "Content-Type: multipart/mixed; boundary=\"-$aMailPart\"" >> $aFichier
 echo "---$aMailPart" >> $aFichier
 echo "Content-Type: text/plain" >> $aFichier
 echo "Content-Disposition: inline" >> $aFichier
echo "\n\nDebut d'execution du script : "$(date +%%D-%%Hh%%Mm%%Ss) >> $aFichier

### creation du repertoire de backup
aNomRepertoire="backup_%(SERVER_HOSTNAME)s__"$(date +%%Y-%%m-%%d_%%H-%%M-%%S)
aRepertoireArchive="%(OPENERP_BACKUP_PATH)s"$aNomRepertoire
mkdir -m 755 $aRepertoireArchive

######################################
### Backup OpenERP
######################################

### Arrêt de production
sudo service apache2 stop > /dev/null
sudo service openerp stop > /dev/null

### Sauvegarde des bases de donnees OpenERP
%(command_pg_dump_lines)s

### Reprise de production
sudo service apache2 start > /dev/null
sudo service openerp start > /dev/null

### Deplacement des dump
%(command_move_lines)s
chmod 755 -R $aRepertoireArchive
chown %(ADMIN_USER)s -R $aRepertoireArchive
chgrp %(OPENERP_BACKUP_GROUP)s -R $aRepertoireArchive

### Purge des anciens repertoires
find %(OPENERP_BACKUP_PATH)s -maxdepth 1 -mindepth 1 -atime +%(OPENERP_BACKUP_MAX_DAY)s -exec rm -r {} \;

### Envoi sur serveur distant
cd $aRepertoireArchive
echo "\n*** RETOUR D'EXPORT FTP sur %(EXTERNAL_BACKUP_HOST)s ***" >> $aFichier
ftp -i -n %(EXTERNAL_BACKUP_HOST)s %(EXTERNAL_BACKUP_PORT)s  << END_SCRIPT >> $aFichier
quote USER %(EXTERNAL_BACKUP_LOGIN)s
quote PASS %(EXTERNAL_BACKUP_PASSWORD)s
pwd
bin
quote CWD %(EXTERNAL_BACKUP_ROOT_FOLDER)s
quote MKD $aNomRepertoire
quote CWD $aNomRepertoire
%(command_put_ftp_lines)s
quit
END_SCRIPT

### recapitulatif mail 

echo "\n*** ETAT DES SAUVEGARDES ***" >> $aFichier
du -h --max-depth=1 %(OPENERP_BACKUP_PATH)s | sort -hr >> $aFichier
echo "\n*** ETAT DU SERVEUR ***" >> $aFichier
di -h --type ext3,ext4 >> $aFichier
echo "\n*** SERVEUR ***" >> $aFichier
hostname >> $aFichier
echo "\nFin d'execution du script : "$(date +%%D-%%Hh%%Mm%%Ss) >> $aFichier

### piece jointe mail 
echo "---$aMailPart" >> $aFichier
echo "Content-Type: text/plain" >> $aFichier
echo "Content-Transfer-Encoding: base64" >> $aFichier
echo "Content-Disposition: attachment; filename=\%(OPENERP_ERROR_LOG_NAME)s\"" >> $aFichier
sudo sed -i -e "s/#012/\n/g" %(OPENERP_ERROR_LOG_PATH)s
base64 %(OPENERP_ERROR_LOG_PATH)s >> $aFichier

### Envoi du mail
sudo sendmail %(OPENERP_BACKUP_MAIL)s < $aFichier


