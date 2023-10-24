# -*- coding: utf-8 -*-

import time
import subprocess
from io import BytesIO
from PIL import Image
import picamera2 # picamera is optional
from pibooth.language import get_translated_text
from pibooth.camera.base import BaseCamera


def get_rpi_camera_proxy(port=None):
    """Return camera proxy if a Raspberry Pi compatible camera is found
    else return None.

    :param port: look on given port number
    :type port: int
    """ # picamera is not installed
    return picamera2.Picamera2()



class RpiCamera(BaseCamera):

    """Camera management
    """


    def _specific_initialization(self):
        """Camera initialization.
        """
        self._cam.configure(self._cam.create_preview_configuration())

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        if self._window:  # No window means no preview displayed
            rect = self.get_rect(self._cam.MAX_RESOLUTION)

            # Create an image padded to the required size (required by picamera)
            size = (((rect.width + 31) // 32) * 32, ((rect.height + 15) // 16) * 16)

            image = self.build_overlay(size, str(text), alpha)
            self._overlay = self._cam.add_overlay(image.tobytes(), image.size, layer=3,
                                                  window=tuple(rect), fullscreen=False)

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay:
            self._cam.remove_overlay(self._overlay)
            self._overlay = None

    def _post_process_capture(self, capture_data):
        """Rework capture data.

        :param capture_data: binary data as stream
        :type capture_data: :py:class:`io.BytesIO`
        """
        # "Rewind" the stream to the beginning so we can read its content
        capture_data.seek(0)
        return Image.open(capture_data)

    def preview(self, window, flip=True):
        """Display a preview on the given Rect (flip if necessary).
        """
        if self._cam is not None:
            # Already running
            return

        self._window = window
        rect = self.get_rect(self._cam.MAX_RESOLUTION)
        if self._cam.hflip:
            if flip:
                # Don't flip again, already done at init
                flip = False
            else:
                # Flip again because flipped once at init
                flip = True
        self._cam.start_preview(resolution=(rect.width, rect.height), hflip=flip,
                                fullscreen=False, window=tuple(rect))

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        timeout = int(timeout)
        if timeout < 1:
            raise ValueError("Start time shall be greater than 0")
        if not self._cam:
            raise EnvironmentError("Preview shall be started first")

        while timeout > 0:
            self._show_overlay(timeout, alpha)
            time.sleep(1)
            timeout -= 1
            self._hide_overlay()

        self._show_overlay(get_translated_text('smile'), alpha)

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time.
        """
        time.sleep(timeout)
        self._show_overlay(get_translated_text('smile'), alpha)

    def stop_preview(self):
        """Stop the preview.
        """
        self._hide_overlay()
        self._cam.stop_preview()
        self._window = None

    def capture(self,effect):
        """Capture a new picture in a file.
        """

        try:
            if self.capture_iso != self.preview_iso:
                self._cam.iso = self.capture_iso
            if self.capture_rotation != self.preview_rotation:
                self._cam.rotation = self.capture_rotation

            stream = BytesIO()
            self._cam.image_effect = effect
            self._cam.capture_file(stream, format='jpeg')
            if self.capture_iso != self.preview_iso:
                
                self._cam.iso = self.preview_iso
            if self.capture_rotation != self.preview_rotation:
                self._cam.rotation = self.preview_rotation

            self._captures.append(stream)
        finally:
            self._cam.image_effect = 'none'
        self._hide_overlay()  # If stop_preview() has not been called

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        self._cam.close()
