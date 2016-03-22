# Copyright (c) 2016, BRML
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy

from std_msgs.msg import Float64


class FlashRecorder(object):
    def __init__(self):
        """ Flash time stamp recorder class writing time stamps for each
        white flash of the robot's head screen into a .txt file.
        """
        self._sub = None
        self._fp = None

    def start(self, outname):
        """ Set up the flash recorder with the parameters for the recording
        and subscribe to the callback function of the screen flash subscriber.
        :param outname: Filename to write the text file to, without the
        extension.
        :return: Whether the text file was opened successfully.
        """
        try:
            self._fp = open(outname + '.txt', 'w')
        except IOError:
            print "ERROR-start-Problem with opening text file."
            raise
        self._fp.write('# timestamps [s]\n')

        self._sub = rospy.Subscriber('/data/head/flash_white',
                                     Float64, callback=self._add_timestamp)
        return not self._fp.closed

    def _add_timestamp(self, ts):
        """ Flash subscriber callback function """
        self._fp.write('%f\n' % ts.data)

    def stop(self):
        """ Stop recording head screen flash time stamps.
        :return: Whether the text file is open.
        """
        self._sub.unregister()
        self._fp.close()
        return self._fp.closed