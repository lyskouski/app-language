# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import time

from android import activity
from android.permissions import request_permissions, Permission, check_permission
from jnius import autoclass
from kivy.app import App

class RecorderControllerAndroid():
    is_available = False

    def __init__(self):
        try:
            self.MediaRecorder = autoclass('android.media.MediaRecorder')
            self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
            activity.bind(on_activity_result=self._on_permission_result)
            self.is_available = True
        except ImportError as e:
            print(f"Android audio not available: {e}")
            self.is_available = False

    def _on_permission_result(self, request_code = 200, permissions = None, grant_results = None):
        try:
            if check_permission(Permission.RECORD_AUDIO):
                self.is_available = True
            else:
                self.is_available = False
                request_permissions([Permission.RECORD_AUDIO])
        except Exception as e:
            print(f"Error handling permission result: {e}")

    def get_initial_status(self, status_label):
        self._on_permission_result()
        if self.is_available:
            status_label.text = "Audio recording is ready"
        else:
            status_label.text = "[!] Audio recording is not available"
        return self.is_available

    def start_recording(self, status_label):
        if not self.is_available:
            status_label.text = "[!] Audio recording is not available"
            return False
        app = App.get_running_app()
        recorded_file = app.get_with_home_dir(f'tmp_{int(time.time())}.3gp')
        try:
            self.media_recorder = self.MediaRecorder()
            self.media_recorder.setAudioSource(self.AudioSource.MIC)
            self.media_recorder.setOutputFormat(self.OutputFormat.THREE_GPP)
            self.media_recorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
            self.media_recorder.setOutputFile(recorded_file)
            self.media_recorder.prepare()
            self.media_recorder.start()
        except Exception as e:
            status_label.text = f"[!] Recording failed: {e}"
            return None
        return recorded_file

    def stop_recording(self, status_label):
        try:
            self.media_recorder.stop()
            self.media_recorder.release()
            self.media_recorder = None
        except Exception as e:
            status_label.text = f"[!] Error stopping Android recording: {e}"
            return False
        return True
