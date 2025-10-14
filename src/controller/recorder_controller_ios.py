# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import os
import time

try:
    from pyobjus import autoclass, objc_str
    HAS_IOS_AUDIO = True
except ImportError:
    print("Warning: iOS audio libraries not available")
    HAS_IOS_AUDIO = False
    autoclass = None
    objc_str = None

from kivy.app import App

class RecorderControllerIos:
    is_available = False

    def __init__(self):
        try:
            if HAS_IOS_AUDIO:
                # iOS AVFoundation classes
                self.AVAudioSession = autoclass('AVAudioSession')
                self.AVAudioRecorder = autoclass('AVAudioRecorder')
                self.NSURL = autoclass('NSURL')
                self.NSMutableDictionary = autoclass('NSMutableDictionary')
                self.NSNumber = autoclass('NSNumber')

                # Audio session setup
                self.audio_session = self.AVAudioSession.sharedInstance()
                self.recorder = None
                self.is_available = True
            else:
                self.is_available = False
        except Exception as e:
            print(f"iOS audio not available: {e}")
            self.is_available = False

    def _request_microphone_permission(self):
        try:
            error = self.audio_session.requestRecordPermission_(None)
            if error:
                print(f"Permission request error: {error}")
                return False
            return self.audio_session.recordPermission() == 1684369017  # AVAudioSessionRecordPermissionGranted
        except Exception as e:
            print(f"Error requesting microphone permission: {e}")
            return False

    def _setup_audio_session(self):
        try:
            success = self.audio_session.setCategory_error_(
                objc_str("AVAudioSessionCategoryPlayAndRecord"), None
            )
            if not success:
                return False
            success = self.audio_session.setActive_error_(True, None)
            return success
        except Exception as e:
            print(f"Error setting up audio session: {e}")
            return False

    def get_initial_status(self, status_label):
        if not HAS_IOS_AUDIO:
            status_label.text = "[!] iOS audio recording libraries are not available"
            return False
        if not self._request_microphone_permission():
            status_label.text = "[!] Microphone permission denied"
            self.is_available = False
            return False
        if not self._setup_audio_session():
            status_label.text = "[!] Failed to setup audio session"
            self.is_available = False
            return False
        status_label.text = "Audio recording is ready"
        self.is_available = True
        return True

    def start_recording(self, status_label):
        if not self.is_available:
            status_label.text = "[!] Audio recording is not available"
            return None

        try:
            app = App.get_running_app()
            # Use M4A format for iOS (better compatibility)
            recorded_file = os.path.join(app.get_home_dir(), f'tmp_{int(time.time())}.m4a')
            # Create file URL
            file_url = self.NSURL.fileURLWithPath_(objc_str(recorded_file))
            # Recording settings
            settings = self.NSMutableDictionary.alloc().init()
            settings.setObject_forKey_(
                self.NSNumber.numberWithInt_(1633772320),  # kAudioFormatMPEG4AAC
                objc_str("AVFormatIDKey")
            )
            settings.setObject_forKey_(
                self.NSNumber.numberWithFloat_(44100.0),
                objc_str("AVSampleRateKey")
            )
            settings.setObject_forKey_(
                self.NSNumber.numberWithInt_(2),  # Stereo
                objc_str("AVNumberOfChannelsKey")
            )
            settings.setObject_forKey_(
                self.NSNumber.numberWithInt_(16),
                objc_str("AVLinearPCMBitDepthKey")
            )
            settings.setObject_forKey_(
                self.NSNumber.numberWithInt_(128000),  # 128 kbps
                objc_str("AVEncoderBitRateKey")
            )
            # Create and configure recorder
            self.recorder = self.AVAudioRecorder.alloc().initWithURL_settings_error_(
                file_url, settings, None
            )
            if not self.recorder:
                status_label.text = "[!] Failed to create audio recorder"
                return None
            if not self.recorder.prepareToRecord():
                status_label.text = "[!] Failed to prepare recorder"
                return None
            if not self.recorder.record():
                status_label.text = "[!] Failed to start recording"
                return None
            status_label.text = "Recording..."
            return recorded_file

        except Exception as e:
            status_label.text = f"[!] Recording failed: {e}"
            return None

    def stop_recording(self, status_label):
        try:
            if self.recorder:
                self.recorder.stop()
                self.recorder = None
            if HAS_IOS_AUDIO and self.audio_session:
                self.audio_session.setActive_error_(False, None)
            status_label.text = "Recording stopped"
            return True

        except Exception as e:
            status_label.text = f"[!] Error stopping iOS recording: {e}"
            return False
