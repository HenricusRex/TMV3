import os
import tempfile
import win32ui
import win32print
from PIL import Image, ImageWin

# Win32-defined constants for GetDeviceCaps
HORZRES, VERTRES = 8, 10  # printable area
LOGPIXELSX, LOGPIXELSY = 88, 90  # dots per inch
PHYSICALWIDTH, PHYSICALHEIGHT = 110, 111  # total area
PHYSICALOFFSETX, PHYSICALOFFSETY = 112, 113  # left/top margin


class PrintToolbar(object):
    def __init__(self, *args, **kw):
        # Page setup parameters
        self._dpi = 300
        self._auto_orientation = False
        self._fit_to_margin = False
        self._printer_name = win32print.GetDefaultPrinter()

    def print_figure(self):
        """Print graph to printer"""
        # Save figure to a temporary file
        handle, file_name = tempfile.mkstemp(suffix='.png')
        os.close(handle)
        self.canvas.figure.savefig(file_name, dpi=self._dpi)

        # Create a device context from the printer
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(self._printer_name)
        printable_area = hDC.GetDeviceCaps(HORZRES), hDC.GetDeviceCaps(VERTRES)
        printer_size = hDC.GetDeviceCaps(PHYSICALWIDTH), hDC.GetDeviceCaps(PHYSICALHEIGHT)
        # printer_margins = hDC.GetDeviceCaps(PHYSICALOFFSETX), hDC.GetDeviceCaps(PHYSICALOFFSETY)

        # Open the image, and work out how much to multiply each pixel
        # by to get it as big as possible on the page without
        # distorting.
        bmp = Image.open(file_name)

        if self._auto_orientation:
            # Rotate it if it's wider than it is high
            if bmp.size[0] > bmp.size[1]:
                bmp = bmp.rotate(90)
        ratios = [1.0 * printable_area[0] / bmp.size[0], 1.0 * printable_area[1] / bmp.size[1]]
        scale = min(ratios)

        if not self._fit_to_margin and scale > 1.0:
            scale = 1.0

        # Start the print job and create a device-independent bitmap
        # with PIL to send through the printing API
        hDC.StartDoc(file_name)
        hDC.StartPage()
        dib = ImageWin.Dib(bmp)
        scaled_width, scaled_height = [int(scale * i) for i in bmp.size]
        x1 = int((printer_size[0] - scaled_width) / 2)
        y1 = int((printer_size[1] - scaled_height) / 2)
        x2 = x1 + scaled_width
        y2 = y1 + scaled_height
        dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

        # Delete the temporary file
        os.remove(file_name)