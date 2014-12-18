# SSHConfigFS

`SSHConfigFS` is a FUSE filesystem to build SSH client config files on–the–fly.

If your `~/.ssh/config` is anything like mine, then it's pretty long (and only seems to grow).  Rather than having to continue managing one big file, I wrote this FUSE filesystem to instead build a config "file" dynamically from many smaller logical chunks.

## OS Requirements

### OSX

Python 2.7 and the [osxfuse](https://osxfuse.github.io/) package ([Fuse4X](http://fuse4x.github.com/) also works, but that project is being merged with *osxfuse*).

### Linux

You will need to install fusypy with pip, the alternative python package installer.

#### Ubuntu/Linux Mint
https://github.com/terencehonles/fusepy/issues/30

First install pip:

    sudo apt-get install python-pip

Install wheel package using pip repo:

    sudo pip install wheel

Install fusepy package using pip repo:

    sudo pip install fusepy

OR

Install fusepy package using github sources:

    sudo pip install git+https://github.com/dsoprea/fusepy.git

Setup fusepy with pip wheel:

    sudo pip wheel fusepy

Run the script with python2.7.x:

    python2.7 sshconfigfs.py

PS: you might need to give read access to /etc/fuse.conf:

    sudo chmod 644 /etc/fuse.conf

sshconfigfs needs no admin rights.

## Installation

On OSX, first install [osxfuse](https://osxfuse.github.io/) (if you're using Homebrew it's available with `brew install osxfuse`), then install the python requirements: `pip install -r requirements.txt` installs only *fusepy*.

## Running the filesystem

To start, run the `sshconfigfs.py` script.  There are no arguments, yet, and it will run in the foreground.

The directory `~/.ssh/config.d/` is monitored for changes to its `mtime`.  Whenever one of the files inside `~/.ssh/config.d/` changes, it triggers re-generation of the combined config. 

For a chunk of config to be included in the final output, it must start with a number.  In `~/.ssh/config.d/` I keep several files:

    10_base
    15_tunnels
    20_workhosts
    30_personalhosts

These files are combined in the order they appear above, using shell–style globbing, into a single "file" contained within the FUSE mountpoint `~/.sshconfigfs/` (the combined file is called `config`).

You could create a symbolic link from `~/.ssh/config` to the generated `~/.sshconfigfs/config` file, so `ssh` can find it, or use the `-F` argument to `ssh` to point it directly at the generated file.

To give another example of use, I have a *crontab* entry periodically generating *ssh* `Host…` config chunks—using data from VPS provider's APIs—which are then written to files inside `~/.ssh/config.d/`.  This keeps my config up to date without my having to manually manage a large, somewhat dynamic, list of hosts.

## Run at startup

I use OSX.  To keep `SSHConfigFS` running, I use the included `.plist` file to tell OSX's `launchd` to run the `sshconfigfs.py` script to mount the filesystem.

    mkdir -p ~/Library/LaunchAgents

Edit the `com.markhellewell.SSHConfigFS.plist` file and change the path to the `sshconfigfs.py` script.  Then:

    cp com.markhellewell.SSHConfigFS.plist ~/Library/LaunchAgents/
    launchctl load -w ~/Library/LaunchAgents/com.markhellewell.SSHConfigFS.plist

This will keep the `SSHConfigFS` mounted, as your user, forever.

## TODO

* dæmon mode support (at the moment will only run in the foreground)
* take arguments to configure `configd_dir` etc.
* pie shop?

## License

The BSD License.  See LICENSE.
