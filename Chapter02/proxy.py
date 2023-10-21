import sys
import socket
import threading

# This function will take an input as bytes or a string and prints
# a hexdump to the console containing both hexadecimal values and
# ASCII-printable characters.  Useful for understanding unknown
# protocols, finding user credentials in plaintext protocols, etc.

# This contains ASCII printable characters or a dot (.) if they dont
# Uses Boolean short-circuit technique:
# for each integer in the range of 0 to 255, if the length of the 
# character equals 3, we get the character otherwise we get a dot
# The list is then joined into a string
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range (256)])

def hexdump(src, length=16, show=True): 
    # Checks if a string and decodes the bytes if a byte string was passed in
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        # Grab piece of string to dump and put in word variable
        word = str(src[i:i+length])

        # Translate built-in function used to sub the string
        # representation of each character for the corresponding 
        # character in the raw string
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3

        # 
        results.append(f'{i:04x}    {hexa:<{hexwidth}}  {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results