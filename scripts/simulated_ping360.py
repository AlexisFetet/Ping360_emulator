#!/usr/bin/env python3

import logging
import os, time

from brping import PingDevice, PingMessage, PingParser, definitions, Ping360

from virtual_serial_link import VirtualSerialLink
# socat -d -d pty,raw,echo=0 pty,raw,echo=0


class SimulatedPing360(PingDevice):

    def __init__(self, serial_port = '/dev/pts/4'):
        super().__init__()

        self.logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])        
        self._mode = 0
        self._gain_setting = 0
        self._angle = 0
        self._transmit_duration = 0
        self._sample_period = 0
        self._transmit_frequency = 0
        self._number_of_samples = 200
        self._transmit = 0
        self._reserved = 0
        self.serial_port = serial_port
        self.configure()
        self.worker()

    def worker(self) -> None:
        while 1:
            incoming_message: PingMessage = self.read()
            if incoming_message:
                if hasattr(incoming_message, 'requested_id'):
                    if incoming_message.requested_id == definitions.COMMON_PROTOCOL_VERSION:
                        self.answer_protocol_request(incoming_message)
                    if incoming_message.requested_id == definitions.PING360_DEVICE_DATA:
                        self.answer_device_information_request(incoming_message)


    def configure(self) -> None:
        self.connect_serial(self.serial_port)


    def answer_protocol_request(self, request: PingMessage):
        answer = PingMessage(definitions.COMMON_PROTOCOL_VERSION)
        answer.pack_msg_data()
        self.write(answer.msg_data)

    def answer_device_information_request(self, request: PingMessage):
        answer = PingMessage(definitions.PING360_DEVICE_DATA)
        answer.mode = self._mode
        answer.gain_setting = self._gain_setting
        answer.angle = self._angle
        answer.transmit_duration = self._transmit_duration
        answer.sample_period = self._sample_period
        answer.transmit_frequency = self._transmit_frequency
        answer.number_of_samples = self._number_of_samples
        answer.data_length = self._number_of_samples
        answer.data = self.get_data()
        answer.pack_msg_data()
        self.write(answer.msg_data)

    def get_data(self):
        return bytearray([255]*self._number_of_samples)



def main():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

    SimulatedPing360()


if __name__ == '__main__':
    main()
