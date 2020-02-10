"""
Auxiliary Interface
**************************
 
:module: test_auxiliary_interface
 
:synopsis: Entry point to the integration test framework
 
.. currentmodule:: integration_test
 
:Copyright: Copyright (c) 2010-2019 Robert Bosch GmbH
    This program and the accompanying materials are made available under the
    terms of the Eclipse Public License 2.0 which is available at
    http://www.eclipse.org/legal/epl-2.0.
    
    SPDX-License-Identifier: EPL-2.0

.. warning:: Still under test
"""
import logging

# Import based on the caller
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "cchannel"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "test_auxiliaries"))
# Import the framework modules
import test_auxiliary_interface
import cchannel_interface
import message


class ExampleAuxiliary(test_auxiliary_interface.AuxiliaryInterface):
    """ Example of an auxiliary implementation
    """
    def _create_auxiliary_instance(self):
        logging.info("Create auxiliary instance")
        # Create an instance (e.g. flash it) -> Placeholder
        # Enable the communication with it
        logging.info("Enable channel")
        self.channel.cc_open()
        # Pingpong
        return_code = self._send_and_wait_ack(message.Message(), 10, 2)
        # Return output
        return return_code


    def _delete_auxiliary_instance(self):
        logging.info("Delete auxiliary instance")
        # Close the communication with it
        self.channel.cc_close()
        return True

    def _run_command(self, unused_parameter, command_message):
        logging.info("Send test request: {}".format(command_message))
        return self._send_and_wait_ack(command_message, 10, 2)

    def _abort_command(self):
        logging.info("Send abort request")
        # Try a soft abort
        msg = message.Message(message.MessageType.COMMAND, message.MessageCommandType.ABORT) # TODO verify if this generation can happened somewhere else
        result = self._send_and_wait_ack(msg, 10, 2)
        # If not successful, do hard reset
        if result is False:
            self._delete_auxiliary_instance()
            self._create_auxiliary_instance()

    def _receive_message(self, timeout_in_s):
        # Read message on the channel
        received_message = self.channel.cc_receive(timeout_in_s)
        if received_message != None:
            # Send ack
            self.channel._cc_send(received_message.generate_ack_message(message.MessageAckType.ACK))
        # Return message
        return received_message

    def _send_and_wait_ack(self, message_to_send, timeout, tries):
        """ Send via the channel a message and wait for an acknowledgement.

        :param message_to_send: Message you want to send out
        :type message_to_send: message.Message
         
        :param timeout: Time in ms to wait for one try
        :type timeout: integer

        :param tries: Number of tries to send the message
        :type tries: integer
         
        :returns: True - Ack, False - Nack
        """
        number_of_tries = 0
        result = False
        while number_of_tries < tries:
            logging.info("Run send try n:" + str(number_of_tries))
            # Send the message
            self.channel.cc_send(message_to_send, timeout)
            # Wait until we get something back
            received_message = self.channel.cc_receive(timeout)
            # Check the outcome
            if received_message is None:
                continue # Next try will occure
            else:
                if message_to_send.check_if_ack_message_is_matching(received_message):
                    logging.info("{} sent".format(message_to_send))
                    result = True
                    break
                else:
                    logging.warning("Received {} not matching {}!".format(received_message, message_to_send))
                    continue # A NACK got received # TODO later on we should have "not supported" and ignore it than.
            # Increase number of tries
            number_of_tries += 1
        return result



############### Test code ############
# Done via test_interface.py



