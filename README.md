
# Flashing Binaries


## Getting Started

This script will allow you to both copy over and flash both cb/ec bins 
across multiple platforms.<br>Using the multiprocessing module each flash 
is executed simultenously with other instances. 

## Prerequisites

You will need to execute this command in terminal. 

```
$ pip install -r requirements.txt
```

This command will install all the modules needed to allow the script to run.

## Running

Before running the script you will need to store the cb/ec bins within 
a folder called *__latest__*<br>located in the same directory as the script

You can run this script by inputting the following into terminal.

```
$ python flashing_binaries.py --IP IP1 IP2 IP3 ... IP*
```

The IPs should be listed like in the given example.

```
$ python flashing_binaries.py --IP 192.168.1.100 192.168.1.111 192.168.1.222 
```





