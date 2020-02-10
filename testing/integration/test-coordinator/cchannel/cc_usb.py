"""
Communication Channel Via Usb
********************************
 
:module: cc_usb
 
:synopsis: Usb communication channel
 
.. currentmodule:: cc_usb
 
:Copyright: Copyright (c) 2010-2019 Robert Bosch GmbH
    This program and the accompanying materials are made available under the
    terms of the Eclipse Public License 2.0 which is available at
    http://www.eclipse.org/legal/epl-2.0.
    
    SPDX-License-Identifier: EPL-2.0

.. warning: Still under test
"""

import serial
import cc_uart
import message

class CCUsb(cc_uart.CCUart):
    
    def __init__(self, serialPort):
        super(CCUsb, self).__init__(serialPort, baudrate=9600)

    def _cc_send(self, msg):
        rawPacket = msg.serialize()
        crc = self._calculate_crc32(rawPacket)

        rawPacket.insert(0, ((crc >> 8) & 0xFF))
        rawPacket.insert(1, (crc & 0xFF))
        self._send_using_slip(rawPacket)

    def _send_using_slip(self, rawPacket):
        SLIP_rawPacket=[]
        SLIP_rawPacket.append(self.START)
    
        for aByte in rawPacket:
            if aByte == self.START:
                SLIP_rawPacket.append(self.ESC)
                SLIP_rawPacket.append(self.ESC_START)
            elif aByte == self.ESC:
                SLIP_rawPacket.append(self.ESC)
                SLIP_rawPacket.append(self.ESC_ESC)
            else:
                SLIP_rawPacket.append(aByte)
        self.serial.write(bytearray(SLIP_rawPacket))
        self.serial.flushOutput()
        return
    
    #################### todo TO DELETE IF NOT NEEDED ANYMORE #######################

    def CCwaitAfterReboot(self, retry_count, reboot_time):
        import logging
        import time

        self.CCclose()
        for i in range(retry_count):
            try:
                time.sleep(reboot_time)
                self.CCopen()
                break
            except (serial.SerialException, serial.serialutil.SerialTimeoutException):
                self.logger.debug("Unable to connect to USB port after reboot."+"Retrying after "+reboot_time+" seconds")