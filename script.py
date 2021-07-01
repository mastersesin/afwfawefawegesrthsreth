import os
import time
import threading

import paramiko

SCRIPT_CONTENT = """
rm -rf run.sh
sudo apt-get update
sudo mkfs -t xfs /dev/nvme2n1
sudo mkdir -p /tmp1
sudo mount /dev/nvme2n1 /tmp1
sudo mkdir /tmp1/tmp1
sudo mkdir /mnt/ramdisk1
sudo apt install -y libsodium-dev cmake g++ git
sudo mount -t tmpfs -o size=110G tmpfs /mnt/ramdisk1/
sudo chown -R ubuntu.ubuntu /tmp1
cd /tmp1
git clone https://github.com/mastersesin/afwfawefawegesrthsreth.git
cd afwfawefawegesrthsreth
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt
mkdir uploading
git checkout new
"""
PEM_PATH = 'pem'
run_file = open('run', 'r')
list_thread = []


def worker(paramiko_ssh_key, paramiko_connect_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(paramiko_connect_ip, username='ubuntu', key_filename=os.path.join(PEM_PATH, paramiko_ssh_key))
    ssh.exec_command("echo '{}' >> run.sh".format(SCRIPT_CONTENT))
    ssh.exec_command("chmod 777 run.sh")
    (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command('./run.sh')
    for content in ssh_stdout.readlines():
        print(content.rstrip())
    ssh.exec_command(
        'tmux new-session -d -s "myTempSession1" /tmp1/afwfawefawegesrthsreth/chia_plot -t /tmp1/tmp1/ -d /tmp1/ -2 /mnt/ramdisk1/ -n -1 -r 70 -p a59e33b8108631810978bb60e9150ff9b4f38ad2e76776d8491acb7e7dacb906f9fff90ee6dcff9ca56d54ea20702f92 -f ad1b159147734d8a817e776e02ef0ced0ff61db9d6695c24bf7147a6622082c9ab59620697e9c434accdf3ab76bd1393')
    ssh.exec_command(
        'tmux new-session -d -s "myTempSession2" python3 /tmp1/afwfawefawegesrthsreth/worker.py')
    print('done 1')


for line in run_file:
    index, pem_name, ip = line.rstrip().split(' ')
    new_thread = threading.Thread(target=worker, args=[pem_name, ip])
    new_thread.start()
    list_thread.append(new_thread)
    print('sllep1')
    time.sleep(1)

for thread in list_thread:
    thread.join()

print('done 2')
