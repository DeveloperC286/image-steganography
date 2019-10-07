#!/usr/bin/python
#https://gitlab.com/DeveloperC/Image-Steganography
import getopt
import sys
import logging
import os
import random
import struct
import re

from cStringIO import StringIO
from PIL import Image
from numpy import *
from Crypto.Cipher import AES


def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    """Encrypts the file provided from in_filename using CBC AES encryption with
    the provided key, outputting the encrypted file to the path provided
    in out_filename. Modified from http://bit.ly/1Ks4MMe

    Parameters
    ----------
    key : str
        Key to be used in the AES encryption. Must be either 16, 24 or 32
        bytes long.
    in_filename : str
        Path to the input file undergoing AES encryption.
    out_filename : str
        Path for the output file from the operation of the input file
        undergoing AES encryption. Will default if not set to
        '<in_filename>.enc'.
    chunksize : int
        The chunksize to use in the encryption. Must be divisible by 16.
        Will default to 64*1024.

    """

    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    """Decrypts the file provided from in_filename using CBC AES decryption with
    the provided key, oututting the decrypted file to the path provided
    in out_filename. Modified from http://bit.ly/1Ks4MMe

    Parameters
    ----------
    key : str
        Key to be used in the AES decryption. Must be either 16, 24 or 32
        bytes long.
    in_filename : str
        Path to the input file undergoing AES decryption.
    out_filename : str
        Path for the output file from the operation of the input file
        undergoing AES decryption. Will default if not set to in_filename
        minus the last extension.
    chunksize : int
        The chunksize to use in the decryption. Must be divisible by 16.
        Will default to 24*1024.

    """

    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


def open_image(path):
    """Returns a new image object of the image at the path provided.

    Parameters
    ----------
    path : str
        The path to the image file to open.

    Returns
    -------
    image : PIL.PngImagePlugin.PngImageFile
        An image object of the .png at the provided path.

    """
    return (Image.open(path))


def save_image(image, path):
    """Saves the provided image as a .png at the provided path.

    Parameters
    ----------
    path : str
        The path to save image object to.
    image : PIL.PngImagePlugin.PngImageFile
        The image object to be saved.

    """

    image.save(path, 'png')


def read_binary_string(input_file):
    """Returns a string which contains the binary representation of
    the input_file provided.

    Parameters
    ----------
    input_file : str
        The path to the file to read the binary representation of.

    Returns
    -------
    binary_string : str
        A string which is the binary representation of the input_file.

    """

    return re.sub("[^0-1]", "", str(unpackbits(fromfile(input_file, dtype="uint8"))))


def write_binary_string(binary_string, output_file):
    """Writes the binary representation within the provided binary_string
    to the output_file path provided. Modified from http://bit.ly/2vnIJ99

    Parameters
    ----------
    output_file : str
        The path to the output file being written to.
    binary_string : str
        The binary representation of the file, to be written.

    """

    sio = StringIO(binary_string)
    f = open(output_file, 'wb')

    while 1:
        b = sio.read(8)

        if not b:
            break

        if len(b) < 8:
            b = b + '0' * (8 - len(b))

        f.write(chr(int(b, 2)))

    f.close()


def steganography_encode(image, binary_string):
    """Returns an image object which is the provided image object which has
    had encoded within it the provided binary_string.

    Parameters
    ----------
    image : PIL.PngImagePlugin.PngImageFile
        The image object for which the binary_string will be encoded into.
    binary_string : str
        A string containing the binary representation of the data to be encoded.

    Returns
    -------
    image : PIL.PngImagePlugin.PngImageFile
        An image object with the binary_string encoded.

    """

    if image.mode == 'RGB':
        width, height = image.size
        pixels = image.load()
        space = (width * height * 3)
        binary_string_len = len(binary_string)
        binary_string_len_binary_string = bin(binary_string_len)[2:]
        forLength = (1 + len(binary_string_len_binary_string))

        logging.info("    Bit of space "+str(space))

        logging.info("    Bits needed to encode data "+str(binary_string_len))
        logging.info("    Bits needed to encode length "+str(forLength))
        logging.info("    Total "+str(forLength+binary_string_len))

        logging.info("    Checking enough space in the image to encode for the data file.")
        if (binary_string_len + forLength) > space:
            logging.error("    Not enough space in image for the file to be encoded...")
            logging.error("    Need: "+str(space))
            logging.error("    Have: "+str(binary_string_len + forLength))
            sys.exit(2)

        logging.info("")
        logging.info("    Adding the size of the data file to the image.")
        pos = 1
        index = 1
        pixel = list(pixels[(index % width), (index/width)])
        pixel[0] = len(binary_string_len_binary_string)
        pixels[(index % width), (index/width)] = tuple(pixel)

        for i in range(0, (forLength-1)):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index/width)])
            pixel[pos] = int(binary_string_len_binary_string[i])
            pixels[(index % width), (index/width)] = tuple(pixel)
            pos = pos + 1

        logging.info("")
        logging.info("    Adding the data to the image.")
        for i in range(0, binary_string_len):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index/width)])
            if str(pixel[pos] % 2) != binary_string[i]:
                if pixel[pos] == 255:
                    pixel[pos] = 254
                else:
                    pixel[pos] = pixel[pos] + 1

            pixels[(index % width), (index/width)] = tuple(pixel)
            pos = pos + 1

        return image
    else:
        print(" Unsupported image mode: %s" % image.mode)
        sys.exit(1)


def steganography_decode(image):
    """Returns a string which contains the binary representation of the
    decoded data from the provided image.

    Parameters
    ----------
    image : PIL.PngImagePlugin.PngImageFile
        The image object from which to decoded the binary_string.


    Returns
    -------
    binary_string : str
        A string containing the binary representation of the data decoded.

    """

    if image.mode == 'RGB':
        width, height = image.size
        pixels = image.load()

        pos = 1
        index = 1

        pixel = list(pixels[(index % width), (index/width)])
        binary_string_len_binary_string_len = pixel[0]
        binary_string_len_binary_string = ""

        logging.info("    Working out encoded data length...")
        for i in range(0, binary_string_len_binary_string_len):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index/width)])

            binary_string_len_binary_string += str(pixel[pos] % 2)

            pos = pos + 1

        length = int(binary_string_len_binary_string, 2)
        logging.info("    Data length "+str(length)+"...")

        binary_data = ""

        logging.info("    Decoding the embeded data...")
        for i in range(0, length):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index/width)])

            binary_data += str(pixel[pos] % 2)

            pos = pos + 1

        return binary_data
    else:
        print("Unsupported image mode: %s" % image.mode)
        sys.exit(1)


def usage():
    """Prints the usage for the program."""

    print("==== USAGE ====");
    print("-e, --encode");
    print("Takes the .png provided through the --input agruement, encodes the data file provided through the --data agruement and outputs the resulting image to the path provided by the --output agruement. If the --key agruement is present the data file is encryped with the key via CBC AES before encoding.");
    print("");
    print("-d, --decode");
    print("Takes the .png provided through the --input agruement, decodes the data file embedded and outputs the decoded file to the path provided by the --output agruement. If the --key agruement is present the decoded file is decryped with the key via CBC AES before outputing the decoded file to the provided path.");
    print("");
    print("-i, --input");
    print("The path to the .png to use as input.");
    print("");
    print("-o, --output");
    print("The path to the outputed encoded .png when ran in encode mode or the path to the outputed decoded data when ran in decode mode.");
    print("");
    print("--data");
    print("The data to encode into the input .png when encoding.");
    print("");
    print("-k, --key");
    print("The cryptographic key to use in the AES CBC encryption/decryption.");
    print("");
    print("-v, --verbose");
    print("Causes the program to be verbose in it's operation.");
    print("");
    print("-h, --help");
    print("Displays this message.");
    print("");


def main(argv):
    """The main method for taking in the agruements and calling the relevant subroutines.

    Parameters
    ----------
    argv : list
        A list containing the agruements provided by the user.

    """

    # sorting out args provided
    try:
        opts, args = getopt.getopt(argv, 'hvedo:i:k:', ['help', 'verbose', 'decode', 'encode', 'output=', 'input=', 'data=', 'key='])
    except getopt.GetoptError:
        logging.info("Error getting/parsing the arguements.")
        sys.exit(2)

    encode = False
    decode = False
    input_file = ""
    output_file = ""
    data_file = ""
    key = ""
    verbose = False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ("-e", "--encode"):
            encode = True
        elif opt in ("-d", "--decode"):
            decode = True
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt == '--data':
            data_file = arg
        elif opt in ("-k", "--key"):
            key = arg
        else:
            logging.warning("Unreconcised arguemeant "+opt)

    # setting output verbose level from args
    if verbose:
        logging.basicConfig(format=" % (levelname)s:  % (message)s", level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format=" % (levelname)s:  % (message)s")

    if ((decode is True and encode is True) or (decode is False and encode is False)):
        logging.warning("Encoding or Decoding not selected, see usage.")
        sys.exit(2)
    elif (encode is True):
        logging.info("Encoding.")

        logging.info(" Checking have all needed agruements.")
        if output_file != "" and input_file != "" and data_file != "":
            logging.info(" input_file = "+input_file)
            logging.info(" output_file = "+output_file)
            logging.info(" data_file = "+data_file)

            if (key != ""):
                logging.info(" Encrypting data file...")
                encrypt_file(key, data_file)
                data_file += ".enc"

            logging.info(" Reading in image "+input_file+" to encode...")
            encoding = open_image(input_file)
            logging.info(" Encoding the image...")
            encoded = steganography_encode(encoding, read_binary_string(data_file))
            logging.info(" Saving the encoded image as "+output_file+"...")
            save_image(encoded, output_file)

            if (key != ""):
                logging.info(" Deleting the encrypting data file...")
                os.remove(data_file)
        else:
            logging.warning("Not the required arguements for encoding. See usage.")
            sys.exit(2)
    elif (decode is True):
        logging.info("Decoding.")

        logging.info(" Checking have all needed agruements.")
        if output_file != "" and input_file != "":
            logging.info(" input_file = "+input_file)
            logging.info(" output_file = "+output_file)

            logging.info(" Reading in image "+input_file+" to decode...")
            decoding = open_image(input_file)
            logging.info(" Decoding the image...")
            decoded = steganography_decode(decoding)

            if (key != ""):
                logging.info(" Saving the decoded encrypted data as "+output_file+".enc...")
                write_binary_string(decoded, output_file+'.enc')
                logging.info(" Decrpyting the data file...")
                decrypt_file(key, output_file+'.enc')
                logging.info(" Deleting the encrypting data file...")
                os.remove(output_file+'.enc')
            else:
                logging.info(" Saving the decoded data as "+output_file+"...")
                write_binary_string(decoded, output_file)

        else:
            logging.warning("Not the required arguements for decoding. See usage.")
            sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
