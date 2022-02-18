#!/usr/bin/python3
"""
For Linux usage only

Usage example:
    sudo python3 task1.py -i 0.01 'ping -c 4 ya.ru'

"""

from time import sleep
from datetime import datetime
from os import path, listdir
from csv import writer
from argparse import ArgumentParser, RawTextHelpFormatter
import signal
import sys
from psutil import Popen


OUTPUT_FILE = path.join(
        path.dirname(path.abspath(__file__)),
        'process_statistics.csv')

def main():
    """
    1. Run process via psutil.Popen
    2. Open/create csv file
    3. Get resource usage info from process, /proc/<pid>/fd/
    4. Write info to csv
    5. Wait process stops
    
    """

    parser = ArgumentParser(
        usage="sudo task1.py [-h] [-i INTERVAL] command",
        description=(f"Example: sudo python3 {sys.argv[0]} -i 0.01 'ping -c 4 ya.ru'\n\n"
                     f"(Linux version)\nThe script starts the command/program "
                     f"and writes resources used by the process info to {OUTPUT_FILE}"),
        epilog=(f"CSV file {OUTPUT_FILE} columns:\n"
                "    1. time (hours:minutes:seconds:microseconds)\n"
                "    2. cpu usage (%)\n"
                "    3. resident set size (bytes)\n"
                "    4. virtual memory size (bytes)\n"
                "    5. number of used file descriptors\n"),
        formatter_class=RawTextHelpFormatter)

    parser.add_argument("command", type=str)

    parser.add_argument("-i", "--interval", \
                        default=1.0, \
                        type=float, \
                        help='interval default value = 1')

    args = parser.parse_args()

    process = Popen(args.command.split())

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda _sig_no, _stack_frame: (process.terminate(), sys.exit(-1)))

    with open(OUTPUT_FILE, 'w') as output_file:

        csvwriter = writer(output_file, delimiter=' ')

        while process.is_running() and process.status() in ['running', 'sleeping']:

            try:
                # psutil.open_file() can't show pipes and sockets, only files
                # So it's easiest to see all descriptors in /proc/<pid>/fd/
                fd_num = len(listdir('/proc/'+str(process.pid)+'/fd/'))

                csvwriter.writerow(
                    [
                        datetime.now().strftime("%T:%f"),
                        process.cpu_percent(),
                        process.memory_info().rss,
                        process.memory_info().vms,
                        fd_num,
                    ])

            except PermissionError:
                print("You have no permissions, try sudo \n\n{PermissionError}")

            sleep(args.interval)

    process.wait()

if __name__ == '__main__':
    main()
