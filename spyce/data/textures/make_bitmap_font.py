"""Create bitmap font using ImageMagick tools"""

import subprocess

# characters to render
charset = [chr(c) for c in range(32, 128)]

# rows of 16 columns
charset = "\n".join("".join(charset[16*i:16*(i+1)]) for i in range(6))

# escape special chars
charset = charset.replace('%', "%%")
charset = charset.replace('\\', "\\\\")

# width of underscore cause image to shift, so add later
charset = charset.replace('_', " ")

subprocess.call([
    "convert",
    "-pointsize", "16",
    "-background", "none",
    "-fill", "white",
    "-font", "Courier",  # monospace font
    "-size", "160x114",  # characters are 10x19
    "label:"+charset,
    "label:_", "-geometry", "+150+57", "-composite",  # put back underscore
    "font.png"
])
