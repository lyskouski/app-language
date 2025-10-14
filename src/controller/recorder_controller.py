# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.utils import platform

if platform == 'android':
    from controller.recorder_controller_android import RecorderControllerAndroid as AudioRecorder
elif platform == 'ios':
    from controller.recorder_controller_ios import RecorderControllerIos as AudioRecorder
else:
    from controller.recorder_controller_desktop import RecorderControllerDesktop as AudioRecorder

class RecorderController:
    def __init__(self):
        self.recorder = AudioRecorder()

    def get_initial_status(self, status_label):
        return self.recorder.get_initial_status(status_label)

    def start_recording(self, status_label):
        return self.recorder.start_recording(status_label)

    def stop_recording(self, status_label):
        return self.recorder.stop_recording(status_label)
