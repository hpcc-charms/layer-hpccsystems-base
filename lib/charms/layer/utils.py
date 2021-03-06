#!/usr/bin/env python3
import os
import sys
import platform
import re
from subprocess import check_call, check_output
from pathlib import Path

IP_FILE_PATTERN =re.compile("^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*(;)?\s*$")
IP4_PATTERN =re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

class SSHKey(object):
    """
    This is helper class to manage SSH keys and related files
    """
    def __init__(self, user, group, home):
       self.user  = user
       self.group = group
       self.home  = home
   
    def key_dir(self):
       return Path(self.home + '/.ssh')

    def has_key(self):
        return self.ssh_pri_key().exists()

    def generate_key(self):
        sshDir = self.key_dir()
        if not sshDir.exists():
            host.mkdir(sshDir, owner=self.user, group=self.group, perms=0o755)
        priKeyFile = self.private_key()
        (sshDir + '/config').write_lines([
                'Host *',
                '    StrictHostKeyChecking no'
        ], append=True)
        check_call(['ssh-keygen', '-t', 'rsa', '-P', '', '-f', priKeyFile])
        host.chownr(sshDir, self.user, self.group)
        os.chmod(sshDir + '/rd_rsa', 0o600)
        os.chmod(sshDir + '/rd_rsa.pub', 0o644)
        with open(sshDir + '/rd_rsa.pub', 'r') as pubKeyFile:
           pubKey = pubKeyFile.read().replace('\n','')
        self.process_authorized_keys(pubKey)


    def install_key(self, priKey, pubKey):
        sshDir = self.key_dir()
        if not sshDir.exists():
            host.mkdir(sshDir, owner=self.user, group=self.group, perms=0o755)
        elif  pubKey in open(sshDir + '/id_rsa.pub').read():
            return
        Path(sshDir + '/id_rsa').write_text(priKey, append=False)
        Path(sshDir + '/id_rsa.pub').write_text(pubKey, append=False)
        os.chmod(sshDir + '/rd_rsa', 0o600)
        os.chmod(sshDir + '/rd_rsa.pub', 0o644)
        self.process_authorized_keys(pubKey)
          
    def process_authorized_keys(self, pubKey):
        authFile = self.key_dir() + '/authorized_keys'
        if authFile.exists():
            if pubKey in open(authFile).read():
                return
        Path(authFile).write_text(pubKey, append=False)
        os.chmod(authFile, 0o644)

    def pubic_key(self):
        return  self.key_dir() + '/id_rsa.pub'

    def private_key(self):
        return  self.key_dir() + '/id_rsa'


def package_extension():
     # will deal with other linux distro later
     return platform.linux_distribution()[2] + "_amd64.deb" 

# get dali ip with configgen -env /etc/HPCCSystems/environmen.xml -listall | grep DaliServer | cut -d',' -f2
