import os
import time
import threading

import paramiko

SERVICE_D = """
[Unit]
Description="Upload 2 service"

[Service]
User=ubuntu
WorkingDirectory=/tmp2/afwfawefawegesrthsreth/
Environment=/tmp2/afwfawefawegesrthsreth/venv/
ExecStart=/tmp2/afwfawefawegesrthsreth/venv/bin/python3 worker.py

[Install]
WantedBy=multi-user.target
"""
SCRIPT_CONTENT = """
sudo pkill -9 chiaplot
rm -rf run.sh
sudo apt-get update
sudo mkfs -t xfs /dev/nvme0n1
sudo mkdir -p /tmp2
sudo mount /dev/nvme0n1 /tmp2
sudo mkdir /mnt/ramdisk2
sudo rm -rf /mnt/ramdisk2/*
sudo apt install -y libsodium-dev cmake g++ git ifstat
sudo mount -t tmpfs -o size=110G tmpfs /mnt/ramdisk2/
cd /tmp2
sudo mkdir /tmp2/tmp2
sudo chown -R ubuntu.ubuntu /tmp2
mv /tmp2/afwfawefawegesrthsreth/uploading /tmp2/
rm -rf afwfawefawegesrthsreth
git clone https://github.com/mastersesin/afwfawefawegesrthsreth.git
cd afwfawefawegesrthsreth
mkdir uploading
git checkout cheat
sudo apt-get install -y python3-pip
sudo pip3 install virtualenv
chmod 777 chiaplot
virtualenv venv
venv/bin/pip install -r requirements.txt
"""

SCRIPT_CHECK = """
pidof python3 &
pidof chiaplot &
ifstat -i ens3 1s 1 | awk 'NR==3 {print $2}'
"""
PEM_PATH = 'pem'
run_file = open('sshfile', 'r')
list_thread = []


def worker(paramiko_ssh_key, paramiko_connect_ip, command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(paramiko_connect_ip, username='ubuntu', key_filename=os.path.join(PEM_PATH, paramiko_ssh_key))
    except paramiko.ssh_exception.AuthenticationException as e:
        print(e, paramiko_connect_ip, paramiko_ssh_key)
        return
    if command == '1':
        ssh.exec_command("echo '{}' >> run.sh".format(SCRIPT_CONTENT))
        ssh.exec_command("chmod 777 run.sh")
        (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command('./run.sh')
        for content in ssh_stdout.readlines():
            print(content.rstrip())
        ssh.exec_command("sudo systemctl stop upload")
        ssh.exec_command(
            "sudo rm -rf /etc/systemd/system/upload2.service".format(SERVICE_D))
        ssh.exec_command(
            "echo '{}' | sudo tee /etc/systemd/system/upload2.service".format(SERVICE_D))
        ssh.exec_command("sudo systemctl start upload2")
        print('done {}'.format(paramiko_connect_ip))
    elif command == '2':
        ssh.exec_command("sudo pkill chiaplot")
        ssh.exec_command("sudo rm -rf /mnt/ramdisk1/*")
        ssh.exec_command(
            'tmux new-session -d -s "myTempSession10" /tmp1/afwfawefawegesrthsreth/chiaplot -t /tmp1/tmp1/ -d /tmp1/ -2 /mnt/ramdisk1/ -n -1 -r 32 -p a94a9f827a062a24d8f8c2201f9113fd8428da53deded15d501d8c94ed59e7d700b44bdc7e0e42a1501426fccca005b6 -f ac99a1d74615b16d12189e2b82a51e0640ca1aa38c55a5841f78c58ac448972555585c8295c181a0eaf6a6d9bf5f5d2d')
    elif command == '3':
        ssh.exec_command("sudo systemctl restart upload")
        ssh.exec_command("mv /tmp1/afwfawefawegesrthsreth/uploading/* /tmp1")
    else:
        (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command("{}".format(SCRIPT_CHECK))
        for content in ssh_stdout.readlines():
            print(content.rstrip())
        print('1 {} {} \n'.format(paramiko_ssh_key, paramiko_connect_ip))


command = input('1 run 2 plot_chia 3 restart_upload 4 check')

for line in run_file:
    index, pem_name, ip = line.rstrip().split()
    new_thread = threading.Thread(target=worker, args=[pem_name, ip, command])
    new_thread.start()
    list_thread.append(new_thread)
    time.sleep(0.1)

for thread in list_thread:
    thread.join()

print('done 2')
