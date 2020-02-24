import re, os, platform
import subprocess, paramiko
from smtplib import SMTP

global cmd_output

class ChromeTestLib(object):

    def check_if_remote_system_is_live(self, dut_ip):
        host = dut_ip
        try:
            response=subprocess.call(('ping -c 1 %s;' % host),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        except:
            return False
        if response == 0:
            return True
        else:
            return False

    def comparing_versions(self,before_flash, after_flash, dut_ip):
        if ((before_flash[0] == after_flash[0]) and (before_flash[1] == after_flash[1])):
            print("DUT IP: %s  No changes were made to CB or EC.\n" % dut_ip)
        elif ((before_flash[0] != after_flash[0]) and (before_flash[1] == after_flash[1])):
            print("DUT IP: %s  Changes were made to CB but not EC.\n" % dut_ip)
        elif ((before_flash[0] == after_flash[0]) and (before_flash[1] != after_flash[1])):
            print("DUT IP: %s  Changes were made to EC but not CB.\n" % dut_ip)

    def storing_results(self, before_flash, after_flash, dut_ip, cwd):
        with open('%s/flash_info.txt' % cwd, 'a') as f:
            str1='\n'.join(before_flash)
            str2='\n'.join(after_flash)
            f.write("\nDUT IP: %s" % dut_ip)
            f.write("\n---------------------")
            f.write("\nPrevious Versions:\n%s" % str1)
            f.write("\n---------------------")
            f.write("\nCurrent Versions:\n%s" % str2)
            f.write("\n\n")
            f.close()
    
    def adding_to_results(self, input, cwd):
        with open('%s/flash_info.txt' % cwd, 'a') as f:
            f.write("\n")
            f.write(str(input)) 
            f.close()

    def mailing_results(self, cwd, email):
        os.system("mail -s \"CB/EC Flash Results\" %s < %s/flash_info.txt" % (email,cwd))
        os.remove("%s/flash_info.txt" % cwd)

    def check_bin_version(self, cwd, dut_ip):
        global cmd_output
        cmd1='crossystem | grep fwid | awk \'{print $1,$2,$3}\''
        cmd2='ectool version | awk \'NR==1,NR==2{print $1,$2,$3}\''

        self.run_command_to_check_non_zero_exit_status(cwd=cwd, command=cmd1, dut_ip=dut_ip)
        cb_ver = cmd_output
        self.run_command_to_check_non_zero_exit_status(cwd=cwd, command=cmd2, dut_ip=dut_ip)
        ec_ver = cmd_output

        return cb_ver, ec_ver

    def copy_file_from_host_to_dut(self, src, dst, dut_ip, cwd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(dut_ip, username='root', password='test0000')

        sftp = client.open_sftp()
        sftp.put(src, dst)		
        sftp.close()

        if self.run_command_to_check_non_zero_exit_status(cwd="", command="", dut_ip=dut_ip):	
            print ("DUT IP: %s [Image Copy Successful]\n" % dut_ip)	
            return True
        else:
            print ("DUT IP: %s [Image Copy Unsuccessful]\n" % dut_ip)	
            return False

    def run_command_to_check_non_zero_exit_status(self, cwd, command, dut_ip, username = "root", password = "test0000"):
        global cmd_output
        if self.check_if_remote_system_is_live(dut_ip):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(dut_ip, username=username, password=password)
                stdin, stdout, stderr = client.exec_command(command)
                command_exit_status = stdout.channel.recv_exit_status()
                out = stdout.read().decode('utf-8').strip("\n")
                """ print ('This is error = %s' % stderr.read()) """
                client.close()
                cmd_output = out
                if command_exit_status == 0:
                    if "Skip jumping to RO" in out:
                        # print("[[EC was not flashed properly and must be completed using Servo]]")
                        msg="EC was not flashed properly."
                        self.adding_to_results(("DUT IP: %s\n%s\n" % (dut_ip,msg)), cwd)
                        return False
                    return True
                elif "flashrom" in command:
                    # print("[[This is flashrom related command and flash status can be decided" 
                    # + "\nbased on flashing only as verification fails most of the time]]")
                    if "Erasing and writing flash chip" in out:
                        return True
                    else:
                        # print("[[Failed to write to flash chip]]")
                        msg="CB was not flashed properly"
                        self.adding_to_results(("DUT IP: %s\n%s\n" % (dut_ip,msg)), cwd)
                        return False
            except paramiko.ssh_exception.NoValidConnectionsError as error:
                print("Failed to connect to host '%s' with error: %s" % (dut_ip, error))
            except paramiko.AuthenticationException as error:
                print("Failed to authenticate dut '%s' with error: %s" % (dut_ip, error))
            except EOFError:
                print ("Failed EOFError")
        return False


    def run_async_command(self, command, dut_ip, username="root", password="test0000"):
        if self.check_if_remote_system_is_live(dut_ip):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(dut_ip, username=username, password=password)
                stdin, stdout, stderr = client.exec_command(command)
                client.close()
                return True              
            except paramiko.ssh_exception.NoValidConnectionsError as error:
                print("Failed to connect to host '%s' with error: %s" % (dut_ip, error))
            except paramiko.AuthenticationException as error:
                print("Failed to authenticate dut '%s' with error: %s" % (dut_ip, error))
            except EOFError:
                print ("Failed EOFError")
        return False



    """ def check_if_system_is_a_chrome_os_system(self, ip):
        chromeos_detection_cmd = "cat /etc/lsb-release | grep -i chromeos_release_name"
        output = self.run_command_to_check_non_zero_exit_status(chromeos_detection_cmd, ip)
        if output:
            print (output)
            chrome_os_check = re.findall("chrome os|chromium os", output, re.I)
        else:
            return False
        if chrome_os_check:
            return True
        else:
            return False """


    """ def search_and_copy_file_from_dut(self, ip, filename):
        if self.check_if_remote_system_is_live(ip):
            if self.check_if_system_is_a_chrome_os_system(ip):
                print ("Deleting existing generate_log file if any.")
                log_file_path = "/tmp/" + ip + "_generate_log.tgz"
                if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                    self.run_command_to_check_non_zero_exit_status("rm -rf " + log_file_path, ip)
                cmd = "generate_logs --output=" + log_file_path
                generate_log_status = self.run_command_to_check_non_zero_exit_status(cmd, ip)
                print ("generate_log_status is:", generate_log_status)
                if generate_log_status == False:
                    print ("log generation failed")
                    return False
                else:
                    print ("log generated successfuly")
                    if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                        return log_file_path
            else:
                print ("remote system is not a chromeos device")
        else:
            print ("DUT %s is not up" % ip)

        return False """


    """ def collect_chromeos_dut_logs(self, ip):
        if self.check_if_remote_system_is_live(ip):
            if self.check_if_system_is_a_chrome_os_system(ip):
                print ("Deleting existing generate_log file if any.")
                log_file_path = "/tmp/" + ip + "_generate_log.tgz"
                if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                    self.run_command_to_check_non_zero_exit_status("rm -rf " + log_file_path, ip)
                cmd = "generate_logs --output=" + log_file_path
                generate_log_status = self.run_command_to_check_non_zero_exit_status(cmd, ip)
                print ("generate_log_status is:", generate_log_status)
                if generate_log_status == False:
                    print ("log generation failed")
                    return False
                else:
                    print ("log generated successfuly")
                    if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                        return log_file_path
            else:
                print ("remote system is not a chromeos device")
        else:
            print ("DUT %s is not up" % ip)
        return False """


    """ def copy_file_from_dut_to_host(self, src, dst, dut_ip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(dut_ip, username='root', password='test0000')

        sftp = client.open_sftp()
        sftp.get(src, dst)
        sftp.close()

        if os.path.isfile(dst):
            print ("--> File copy successful.")
            return True
        else:
            print ("--> File copy unsuccessful.")
            return False """
