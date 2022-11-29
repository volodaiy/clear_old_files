# This script archives files older than 3 days and then deletes the source. It also removes .gz files older than 90 days.
# Skips symlinks and their parent.

# You need to add a directory to the "dir_dict" dictionary

import os
import tarfile
import datetime

dir_dict = {
'catalogd': '/var/log/catalogd/',
'atop': '/var/log/atop/'
}


def modification_date(filename):
    t = os.path.getmtime(filename)
    return (datetime.date.today() - datetime.date.fromtimestamp(t)).days


def search_link_file(dir, link_path):
    for search_link in os.listdir(dir):
        if not os.path.isdir(os.path.join(dir, search_link)):
            if os.path.islink(dir + search_link):
                link_path.append(os.readlink(dir + search_link))
    return link_path


def create_arch(dir, files):
    log_write_clear = open('/var/tmp/clearlog_' + str(datetime.date.today()) + '.txt', 'a+')
    with tarfile.open(dir + files + '.gz', 'w:gz') as tar:
        tar.add(os.path.join(dir + files))
        log_write_clear.write('gzip: ' + dir + files + '\n')
    log_write_clear.close()


def clear_oldfiles(dir, files):
    log_write_clear = open('/var/tmp/clearlog_' + str(datetime.date.today()) + '.txt', 'a+')
    if os.path.isfile(dir + files):
        os.remove(dir + files)
        log_write_clear.write('clear: ' + dir + files + '\n')
    log_write_clear.close()


def proc_del_oldfiles(dir_dict):
    for dir in dir_dict.values():
        link_path = []
        try:
            search_link_file(dir, link_path)
            for files in os.listdir(dir):
                if not os.path.isdir(os.path.join(dir, files)):
                    if files not in link_path:
                        if not os.path.islink(dir + files):
                            if not files.endswith('.gz'):
                                if modification_date(dir + files) >= 3:
                                    create_arch(dir, files)
                                    clear_oldfiles(dir, files)
                            else:
                                if modification_date(dir + files) >= 90:
                                    clear_oldfiles(dir, files)
        except Exception as er:
            print(er)
            continue


proc_del_oldfiles(dir_dict)
