import os
import time
import threading

import paramiko

SCRIPT_CONTENT = """
sudo pkill python3
sudo pkill chia_plot
rm -rf run.sh
sudo apt-get update
sudo mkfs -t xfs /dev/nvme2n1
sudo mkdir -p /tmp1
sudo mount /dev/nvme2n1 /tmp1
sudo mkdir /mnt/ramdisk1
sudo rm -rf /mnt/ramdisk1/*
sudo apt install -y libsodium-dev cmake g++ git
sudo mount -t tmpfs -o size=110G tmpfs /mnt/ramdisk1/
cd /tmp1
sudo rm -rf *
sudo mkdir /tmp1/tmp1
git clone https://github.com/mastersesin/afwfawefawegesrthsreth.git
cd afwfawefawegesrthsreth
sudo apt-get install -y python3-pip
pip3 install -r requirements.txt
mkdir uploading
git checkout new
sudo chown -R ubuntu.ubuntu /tmp1
"""
PEM_PATH = 'pem'
run_file = open('sshfile', 'r')
list_thread = []


def worker(paramiko_ssh_key, paramiko_connect_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(paramiko_connect_ip, username='ubuntu', key_filename=os.path.join(PEM_PATH, paramiko_ssh_key))
    ssh.exec_command("echo '{}' >> run.sh".format(SCRIPT_CONTENT))
    ssh.exec_command("chmod 777 run.sh")
    (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command('./run.sh')
    for content in ssh_stdout.readlines():
        content.rstrip()
    ssh.exec_command(
        'tmux new-session -d -s "myTempSession1" /tmp1/afwfawefawegesrthsreth/chia_plot -t /tmp1/tmp1/ -d /tmp1/ -2 /mnt/ramdisk1/ -n -1 -r 32 -p a94a9f827a062a24d8f8c2201f9113fd8428da53deded15d501d8c94ed59e7d700b44bdc7e0e42a1501426fccca005b6 -f ac99a1d74615b16d12189e2b82a51e0640ca1aa38c55a5841f78c58ac448972555585c8295c181a0eaf6a6d9bf5f5d2d')
    ssh.exec_command(
        'tmux new-session -d -s "myTempSession2" python3 /tmp1/afwfawefawegesrthsreth/worker.py')
    print('done {}'.format(paramiko_connect_ip))


for line in run_file:
    index, pem_name, ip = line.rstrip().split(' ')
    new_thread = threading.Thread(target=worker, args=[pem_name, ip])
    new_thread.start()
    list_thread.append(new_thread)
    print('sleep 1')
    time.sleep(1)

for thread in list_thread:
    thread.join()

print('done 2')
