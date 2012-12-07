#!/usr/bin/env python
# FUSE filesystem to build SSH config file dynamically.
# Mark Hellewell <mark.hellewell@gmail.com>
import glob
import logging
import os
from stat import S_IFDIR, S_IFREG
#from sys import argv, exit
import threading
from time import sleep, time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

# TODO is there a "file" type object belonging to FUSE?  Would be
# better to extend that.

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SSHConfigFS(LoggingMixIn, Operations):
    """Builds ssh's config file dynamically.
    """

    def __init__(self, ssh_dir, configd_dir):
        self.now = time()
        self.ssh_dir = ssh_dir
        self.configd_dir = configd_dir

        # generate config
        self.config = ''
        for conf_file in glob.iglob("{}/[0-9]*".format(self.configd_dir)):
            try:
                self.config += file(conf_file, 'r').read()
                print "{} was included".format(conf_file)
            except IOError:
                print "IOError while tring to read {}: skipping!".format(conf_file)
                continue
        self.config_size = len(self.config)

    def init(self, arg):
        # start the self.configd_dir watcher
        t = threading.Thread(target=self.dir_watcher)
        t.start()

    def getattr(self, path, fh=None):
        try:
            # TODO the nlink value needs to be calculated based on
            # size of generated content, or an error is generated
            # saying too much data was read!
            # TODO use 'defaultdict' to avoid all the st_ repitition?
            fattr = {
                '/': dict(st_mode=(S_IFDIR | 0550),
                          st_uid=os.getuid(), # or user requested
                          st_gid=os.getgid(),
                          st_nlink=2,
                          st_ctime=self.now,
                          st_mtime=self.now,
                          st_atime=self.now),
                '/config': dict(st_mode=(S_IFREG | 0440),
                                st_uid=os.getuid(), # or user requested
                                st_gid=os.getgid(),
                                st_size=self.config_size,
                                st_nlink=2,
                                st_ctime=self.now,
                                st_mtime=self.now,
                                st_atime=self.now),
                }[path]
            return fattr
        except KeyError:
            return dict()

    def read(self, path, size, offset, fh):
        if path == '/config':
            return self.config

    def readdir(self, path, fh):
        return ['.', '..', 'config',]

    def dir_watcher(self):
        """Monitors the configd_dir for changes, rebuilding the config
        when required."""
        # TODO
        while True:
            #print self.config_size
            sleep(10)
        return

    # def destroy(self, path):
    #     pass


if __name__ == '__main__':
    # TODO should take arguments for: user, config.d location, and?

    # TODO maybe better to default to using mountpoint of
    # ~/.sshconfigfs ?
    ssh_dir = os.path.join(os.path.expanduser('~'), '.ssh')

    # directory containing ssh config chunks
    configd_dir = os.path.join(ssh_dir, 'config.d')
    if not os.path.exists(configd_dir):
        os.mkdir(configd_dir)

    # where our filesystem will be mounted
    mountpoint = os.path.join(ssh_dir, '.sshconfigfs')
    if not os.path.exists(mountpoint):
        os.mkdir(mountpoint)

    fuse = FUSE(SSHConfigFS(ssh_dir, configd_dir), mountpoint, foreground=True)
