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

import cv2
import cv_bridge

import rospy

from sensor_msgs.msg import Image

from baxter_data_acquisition.srv import CameraTrigger


class CameraRecorder(object):
    def __init__(self):
        """ Camera recorder class writing color ROS image messages recorded
        with the head camera of the baxter robot into a .avi video file and
        timestamps for each image frame into an accompanying .txt file.
        """
        self._clip = None
        self._sub = None
        self._fp = None

        self._camera = ""
        self.camera = '/cameras/head_camera/image'

    def start(self, outname, fps, imgsize):
        """ Set up the camera recorder with the parameters for the recording
        and subscribe to the callback function of the baxter head camera.
        :param outname: Filename to write the video and text file to, without
        the extension.
        :param fps: Frames per second for video file.
        :param imgsize: Size (width, height) of images to write into video
        file.
        :return: Whether the video- and text file were opened successfully.
        """
        # try:
        #     self._fp = open(outname + '.txt', 'w')
        # except IOError:
        #     rospy.logfatal("start - Problem with opening text file.")
        #     raise
        # self._fp.write('# timestamps [s]\n')

        self._clip = cv2.VideoWriter(outname + '.avi',
                                     fourcc=cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'),
                                     fps=fps,
                                     frameSize=imgsize,
                                     isColor=True)
        if not self._clip.isOpened():
            rospy.logfatal("start - Problem with opening VideoWriter.")
            raise IOError('Problem with opening VideoWriter!')
        self._sub = rospy.Subscriber(self.camera,
                                     Image, callback=self._add_image)
        return self._clip.isOpened()  # and not self._fp.closed

    def _add_image(self, imgmsg):
        """ Camera subscriber callback function """
        # ts = rospy.get_time()
        # self._fp.write('%f\n' % ts)
        # self._fp.flush()

        try:
            img = cv_bridge.CvBridge().imgmsg_to_cv2(imgmsg, 'bgr8')
        except cv_bridge.CvBridgeError:
            rospy.logfatal('add_image - Problem with ROS image message conversion.')
            raise
        try:
            self._clip.write(img)
        except Exception:
            rospy.logfatal('add_image - Recording frame failed.')
            raise

    def stop(self):
        """ Stop recording data from the head camera.
        :return: Whether the video- and text file are open.
        """
        if self._sub is not None:
            rospy.loginfo('unregistering ...')
            self._sub.unregister()
            rospy.loginfo('unregistered')
        rospy.loginfo('releasing video clip ...')
        self._clip.release()
        rospy.loginfo('released.')  # closing text file ...')
        # self._fp.close()
        # rospy.loginfo('closed')
        return self._clip.isOpened()  # or self._fp.closed

    @property
    def camera(self):
        """ String identifying the camera to record images from.
        :return: Camera name.
        """
        return self._camera

    @camera.setter
    def camera(self, camera):
        self._camera = camera


class CameraClient(object):
    def __init__(self):
        self._service_name = 'camera_service'

    def start(self, outname, fps, imgsize):
        """ Start camera recorder hosted on camera recorder server.
        :param outname: Filename to write the video and text file to, without
        the extension.
        :param fps: Frames per second for video file.
        :param imgsize: Size (width, height) of images to write into video
        file.
        :return: (bool success, string message)
        """
        rospy.logdebug("Waiting for camera recorder server.")
        rospy.wait_for_service(self._service_name)
        try:
            trigger = rospy.ServiceProxy(self._service_name, CameraTrigger)
            resp = trigger(on=True, outname=outname, fps=fps, size=imgsize)
            return resp.success, resp.message
        except rospy.ServiceException as e:
            rospy.logerr('Service call failed: %s' % e)

    def stop(self):
        """ Stop camera recorder hosted on camera recorder server.
        :return: (bool success, string message)
        """
        rospy.wait_for_service(self._service_name)
        try:
            trigger = rospy.ServiceProxy(self._service_name, CameraTrigger)
            resp = trigger(on=False)
            return resp.success, resp.message
        except rospy.ServiceException as e:
            rospy.logerr('Service call failed: %s' % e)
