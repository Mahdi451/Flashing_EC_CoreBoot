import multiprocessing
import tarfile, glob, shlex
import os, sys, time, argparse

from functools import partial
from collections import defaultdict
from scapy.all import srp, Ether, ARP, conf
from ChromeTestLib import ChromeTestLib

cwd = os.getcwd()
bin_location = cwd + "/latest"
test = ChromeTestLib()
parser = argparse.ArgumentParser()
parser.add_argument('--IP',dest='ip',nargs='?',type=str,metavar=('IP_list.txt'),default='IPs.txt',help='list of IPs to flash')
args = parser.parse_args()

with open(("%s/%s" % (cwd,args.ip))) as f:
    ip_list=list()
    ip_lines=f.readlines()
    for ip in ip_lines:
        ip_list.append(ip.rstrip())
    f.close()

def createFolders(absFolderPath):
    try:
        os.makedirs(absFolderPath)
        return True
    except IOError as err:
        print ("I/O error({0}): {1}".format(err))
        sys.exit(1)
    except OSError as e:
        print ("Exception found!!!")
        print (e)
        sys.exit(1)

def find_and_return_latest_binaries(binaries_folder_location):
    d = dict()
    try:
        files_array = os.listdir(binaries_folder_location)
    except OSError as e:
        print (e)
        return False
    if not files_array or len(files_array) > 2:  #it should have max 2 files inside.
        return False
    for file in files_array:
        if file.endswith(".bin"):
            file_path = os.path.join(binaries_folder_location, file)
            file_size = os.path.getsize(file_path)
            #print()
            if 400000 < file_size < 600000:
                # print ("file size: %d bytes"%os.path.getsize(file_path))
                # print ("ec file path is: ", file_path)
                abs_ec_image_path = file_path
                d["ec"] = abs_ec_image_path
            if 15000000 < file_size:
                # print ("file size: %d bytes"%os.path.getsize(file_path))
                # print ("cb file path is: ", file_path)
                abs_cb_image_path = file_path
                d["cb"] = abs_cb_image_path
    if not d:
        print ("cb/ec images are not copied to binaries folder.")
        return False
    else:
        return d

def FlashBinaries(dut_ip, email, cwd, cbImageSrc = "", ecImageSrc = ""):
    flashDict = dict()
    flashing_status = "FAIL"
    cbFlashStatus = False
    ecFlashStatus = False
    if test.check_if_remote_system_is_live(dut_ip):
        print("DUT IP: %s is live.\n" % dut_ip)
        test.adding_to_results(("DUT IP: %s - LIVE." % dut_ip),cwd)
        before_flash=test.check_bin_version(cwd,dut_ip) 

        if cbImageSrc:
            cbImageDest = "/tmp/autoflashCB.bin"
            copy_cb = test.copy_file_from_host_to_dut(cbImageSrc, cbImageDest, dut_ip, cwd="")
            cbCmd = "flashrom -p host -w " + cbImageDest
            cbFlashStatus = test.run_command_to_check_non_zero_exit_status(cwd, cbCmd, dut_ip)
            if cbFlashStatus:
                print("DUT IP: %s [CB Flash Successful]\n" % dut_ip)
            if not cbFlashStatus:
                print("DUT IP: %s [CB Flash Unsuccessful]\n" % dut_ip)

        if ecImageSrc:
            ecImageDest = "/tmp/autoflashEC.bin"
            copy_ec = test.copy_file_from_host_to_dut(ecImageSrc, ecImageDest, dut_ip, cwd="")
            ecCmd = "flashrom -p ec -w " + ecImageDest
            ecFlashStatus = test.run_command_to_check_non_zero_exit_status(cwd, ecCmd, dut_ip)
            if ecFlashStatus:
                print("DUT IP: %s [EC Flash Successful]\n" % dut_ip)
            if not ecFlashStatus:
                print("DUT IP: %s [EC Flash Unsuccessful]\n" % dut_ip)

        if cbFlashStatus and ecFlashStatus:
            """ this is required for the reboot part of flash """
            test.run_async_command("sleep 2; reboot > /dev/null 2>&1", dut_ip)
            print("Pinging DUT IP: %s\n" % dut_ip)
            time.sleep(3)
            for i in range(60):
                if test.check_if_remote_system_is_live(dut_ip):
                    time.sleep(2)
                    flashing_status = "PASS"
                    flashDict[dut_ip] = flashing_status
                    after_flash=test.check_bin_version(cwd,dut_ip) 
                    test.comparing_versions(before_flash, after_flash, dut_ip)
                    test.storing_results(before_flash, after_flash, dut_ip, cwd)
                    print("DUT IP: %s is back online.\n" % dut_ip)
                    return flashDict
                time.sleep(2)
            flashDict[dut_ip] = flashing_status
            resultDict.update(flashDict)
            return flashDict
            
        else:
            flashDict[dut_ip] = flashing_status
            resultDict.update(flashDict)
            after_flash=test.check_bin_version(cwd,dut_ip) 
            test.comparing_versions(before_flash, after_flash, dut_ip)
            test.storing_results(before_flash, after_flash, dut_ip, cwd)
            return flashDict

    else:
        print("DUT IP: %s is not live.\n" % dut_ip)
        test.adding_to_results(("DUT IP: %s - NOT LIVE." % dut_ip),cwd)
    flashDict[dut_ip] = flashing_status
    resultDict.update(flashDict)
    return flashDict   



if __name__ == "__main__":
    email=input("Please enter an E-mail: ")
    # email='results.cssdesk@gmail.com'
    t1=time.perf_counter()
    flash_ec = flash_cb = False
    resultDict = dict()

    #Check if destination folder exist else exit
    if not os.path.isdir(bin_location):
        print("Binaries folder doesn't exist. Creating one. Copy binaries into folder named latest and rerun flashing script!")
        createFolders(bin_location)
        sys.exit(1)

    binaryDict = find_and_return_latest_binaries(bin_location)

    if binaryDict:
        if not "ec" in binaryDict:
            binaryDict["ec"] = ""
        if not "cb" in binaryDict:
            binaryDict["cb"] = ""
    else:
        print("Binaries are not available. Copy binaries into folder named latest and rerun flashing script!")
        sys.exit(1)

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        resultDict = pool.map(partial(FlashBinaries, email = email, cwd = cwd,
            cbImageSrc = binaryDict["cb"], ecImageSrc = binaryDict["ec"]), ip_list)
    
    print("\n************************************************************************")
    print(resultDict) 
    test.adding_to_results(resultDict, cwd)
    test.mailing_results(cwd, email)
    t2=time.perf_counter()
    tot=t2-t1
    minutes=tot/60
    seconds=tot%60
    print("\nExecution Time: %dm %ds" % (minutes,seconds))      

