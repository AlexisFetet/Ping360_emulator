#!/usr/bin/env python3

import logging
import os
import pty
import tty
from contextlib import ExitStack
from selectors import EVENT_READ
from selectors import DefaultSelector as Selector
from threading import Thread


class VirtualSerialLink():

    def __init__(self, logging_level=logging.INFO) -> None:
        self.master_files = {}
        self.slave_names = {}
        self.logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
        self.worker = Thread(target=self.run)
        self.worker.daemon = True
        self.configure()
        self.logger.info(f"Created {list(self.slave_names.values())[0]} and {list(self.slave_names.values())[1]}")
        self.worker.start()
        

    def configure(self) -> None:
        for _ in range(2):
            master_fd, slave_fd = pty.openpty()
            tty.setraw(master_fd)
            os.set_blocking(master_fd, False)
            slave_name = os.ttyname(slave_fd)
            self.master_files[master_fd] = open(master_fd, 'r+b', buffering=0)
            self.slave_names[master_fd] = slave_name
            

    def run(self) -> None:

        with Selector() as selector, ExitStack() as stack:
        # Context manage all the master file objects, and add to selector.
            for fd, f in self.master_files.items():
                stack.enter_context(f)
                selector.register(fd, EVENT_READ)

            while True:
                for key, events in selector.select():
                    if not events & EVENT_READ:
                        continue

                    data = self.master_files[key.fileobj].read()
                    print(data)
                    # to the sending file.
                    for fd, f in self.master_files.items():
                        if fd != key.fileobj:
                            f.write(data)


def main():
    VirtualSerialLink()


if __name__ == '__main__':
    main()
