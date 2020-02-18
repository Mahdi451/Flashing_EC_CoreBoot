# Flashing Binaries

This script will allow you to both copy over and flash both cb/ec bins on multiple devices simultaneously. 


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

After that insert the IPs you would like to flash into *__IPs.txt__* and you are ready to run the script!

```
$ python flashing_binaries.py
```




