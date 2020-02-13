

# Flashing Binaries

This script will allow you to both copy over and flash both cb/ec bins across multiple platforms.<br>Using the multiprocessing module each flash is executed simultenously with other instances. 

## Prerequisites

You will need to execute this command in terminal. 

```
$ pip install -r requirements.txt
```

This command will install all the modules needed to allow the script to run.

## Running

Create a folder called *__latest__* to store the bin files within the same directory as the script.
```
ChromeTestLib.py  flashing_binaries.py  latest  README.md  requirements.txt
```
<br>
You can run this script like in the given example.

```
$ python flashing_binaries.py --IP 192.168.1.100 192.168.1.111 192.168.1.222 
```





