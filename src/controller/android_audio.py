# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

from kivy.utils import platform
from kivy.event import EventDispatcher

class AndroidAudioRecorder(EventDispatcher):
    def __init__(self):
        super().__init__()
        self.media_recorder = None
        self.is_recording = False
        self.output_file = None
        self.has_permissions = False
        self.permission_callback = None
        self.pending_recording_args = None

        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission, check_permission
                from jnius import autoclass, PythonJavaClass, java_method

                self.MediaRecorder = autoclass('android.media.MediaRecorder')
                self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
                self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
                self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

                self.request_permissions = request_permissions
                self.Permission = Permission
                self.check_permission = check_permission

                # Set up permission callback handler
                self._setup_permission_callback()

                self.available = True
                print("Android audio recording initialized successfully")

            except ImportError as e:
                print(f"Android audio not available: {e}")
                self.available = False
        else:
            self.available = False

    def _setup_permission_callback(self):
        try:
            from android import activity

            # Bind to the permission result event
            activity.bind(on_activity_result=self._on_permission_result)
            print("Permission callback handler set up")

        except Exception as e:
            print(f"Could not set up permission callback: {e}")

    def _on_permission_result(self, request_code, permissions, grant_results):
        try:
            if self.Permission.RECORD_AUDIO in permissions:
                index = permissions.index(self.Permission.RECORD_AUDIO)
                if index < len(grant_results) and grant_results[index]:
                    print("RECORD_AUDIO permission granted")
                    self.has_permissions = True

                    # If we have pending recording, start it now
                    if self.pending_recording_args:
                        output_file, max_duration = self.pending_recording_args
                        self.pending_recording_args = None
                        self._start_recording_internal(output_file, max_duration)

                    # Call user callback if set
                    if self.permission_callback:
                        self.permission_callback(True)
                else:
                    print("RECORD_AUDIO permission denied")
                    self.has_permissions = False

                    # Call user callback if set
                    if self.permission_callback:
                        self.permission_callback(False)

        except Exception as e:
            print(f"Error handling permission result: {e}")

    def check_and_request_permissions(self, callback=None):
        if not self.available:
            if callback:
                callback(False)
            return False

        try:
            # Check if we already have permission
            if self.check_permission(self.Permission.RECORD_AUDIO):
                self.has_permissions = True
                if callback:
                    callback(True)
                return True

            # Store callback for later
            self.permission_callback = callback

            # Request permission - result will come via callback
            self.request_permissions([self.Permission.RECORD_AUDIO])
            print("Permission requested, waiting for user response...")
            return True  # Request was made, but permission not yet granted

        except Exception as e:
            print(f"Permission request failed: {e}")
            if callback:
                callback(False)
            return False

    def start_recording(self, output_file_path, max_duration=30, callback=None):
        if not self.available:
            if callback:
                callback(False, "Android audio recording not available")
            return False

        # If we already have permissions, start recording immediately
        if self.has_permissions:
            return self._start_recording_internal(output_file_path, max_duration, callback)

        # Store recording parameters for after permission is granted
        self.pending_recording_args = (output_file_path, max_duration)

        # Request permissions with callback
        def permission_callback(granted):
            if granted:
                # Permission granted, start recording
                result = self._start_recording_internal(output_file_path, max_duration, callback)
                if not result and callback:
                    callback(False, "Failed to start recording after permission granted")
            else:
                # Permission denied
                self.pending_recording_args = None
                if callback:
                    callback(False, "RECORD_AUDIO permission denied by user")

        return self.check_and_request_permissions(permission_callback)

    def _start_recording_internal(self, output_file_path, max_duration=30, callback=None):
        try:
            self.output_file = output_file_path

            # Initialize MediaRecorder
            self.media_recorder = self.MediaRecorder()
            self.media_recorder.setAudioSource(self.AudioSource.MIC)
            self.media_recorder.setOutputFormat(self.OutputFormat.THREE_GPP)
            self.media_recorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
            self.media_recorder.setOutputFile(output_file_path)

            # Prepare and start recording
            self.media_recorder.prepare()
            self.media_recorder.start()

            self.is_recording = True
            print(f"Started Android recording to: {output_file_path}")

            if callback:
                callback(True, f"Recording started: {output_file_path}")
            return True

        except Exception as e:
            error_msg = f"Failed to start Android recording: {e}"
            print(error_msg)
            self.is_recording = False
            if callback:
                callback(False, error_msg)
            return False

    def stop_recording(self, callback=None):
        if not self.is_recording or not self.media_recorder:
            if callback:
                callback(False, "No active recording to stop")
            return False

        try:
            self.media_recorder.stop()
            self.media_recorder.release()
            self.media_recorder = None
            self.is_recording = False

            success_msg = "Android recording stopped successfully"
            print(success_msg)

            if callback:
                callback(True, success_msg)
            return True

        except Exception as e:
            error_msg = f"Error stopping Android recording: {e}"
            print(error_msg)
            self.is_recording = False

            if callback:
                callback(False, error_msg)
            return False

    def is_available(self):
        return self.available and platform == 'android'

    def has_recording_permission(self):
        return self.has_permissions

    def cancel_pending_recording(self):
        self.pending_recording_args = None
        self.permission_callback = None
