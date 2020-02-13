# Flashing Binaries

This script will allow you to both copy over and flash both cb/ec bins across multiple platforms.<br>Using the multiprocessing module each flash is executed simultenously with other instances. 

## Prerequisites

You will need to execute this command in terminal. 

```
$ pip install -r requirements.txt
```

This command will install all the modules needed to allow this script to run.

## Running

Create a folder called *__latest__* to store the bin files within the same directory as the script.
```
ChromeTestLib.py  flashing_binaries.py  IPs.txt  latest  README.md  requirements.txt
```
<br>
Insert list of IPs into *__IPs.txt__* and run scipt in this format.

```
$ python flashing_binaries.py --IP IPs.txt 
```





