# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import time
import threading

from android import activity
from android.permissions import request_permissions, Permission, check_permission
from jnius import autoclass
from kivy.app import App

class RecorderControllerAndroid():
    is_available = False

    def __init__(self):
        self._lock = threading.Lock()
        self.media_recorder = None
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
                # Request permission, but don't loop requests from callbacks.
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
            return None
        app = App.get_running_app()
        recorded_file = app.get_with_home_dir(f'tmp_{int(time.time())}.3gp')
        with self._lock:
            if self.media_recorder is not None:
                status_label.text = "[!] Recording is already in progress"
                return None
            try:
                recorder = self.MediaRecorder()
                recorder.setAudioSource(self.AudioSource.MIC)
                recorder.setOutputFormat(self.OutputFormat.THREE_GPP)
                recorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
                recorder.setOutputFile(recorded_file)
                recorder.prepare()
                recorder.start()
                self.media_recorder = recorder
            except Exception as e:
                self.media_recorder = None
                status_label.text = f"[!] Recording failed: {e}"
                return None
        return recorded_file

    def stop_recording(self, status_label):
        with self._lock:
            recorder = self.media_recorder
            self.media_recorder = None

        if recorder is None:
            status_label.text = "[!] No active recording to stop"
            return False

        try:
            recorder.stop()
            recorder.release()
            return True
        except Exception as e:
            try:
                recorder.release()
            except Exception:
                pass
            status_label.text = f"[!] Error stopping Android recording: {e}"
            return False
