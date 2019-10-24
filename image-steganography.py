#!/usr/bin/python2
# https://gitlab.com/DeveloperC/image-steganography
import argparse
import logging
import os
import random
import re
import struct
import sys

from Crypto.Cipher import AES
from PIL import Image
from cStringIO import StringIO
from numpy import *


def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    """Encrypts the file provided from in_filename using CBC AES encryption
    with the provided key, outputting the encrypted file to the path provided
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


def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):
    """Decrypts the file provided from in_filename using CBC AES decryption
    with the provided key, outputting the decrypted file to the path provided
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


def read_binary_string(input):
    """Returns a string which contains the binary representation of
    the input provided.

    Parameters
    ----------
    input : str
        The path to the file to read the binary representation of.

    Returns
    -------
    binary_string : str
        A string which is the binary representation of the input.

    """

    return re.sub("[^0-1]", "",
                  str(unpackbits(fromfile(input, dtype="uint8"))))


def write_binary_string(binary_string, output):
    """Writes the binary representation within the provided binary_string
    to the output path provided. Modified from http://bit.ly/2vnIJ99

    Parameters
    ----------
    output : str
        The path to the output file being written to.
    binary_string : str
        The binary representation of the file, to be written.

    """

    sio = StringIO(binary_string)
    f = open(output, 'wb')

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
        A string containing the binary representation of the data to be
         encoded.

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

        logging.info("Bit of space " + str(space))

        logging.info(
            "Bits needed to encode data " + str(binary_string_len))
        logging.info("Bits needed to encode length " + str(forLength))
        logging.info("Total " + str(forLength + binary_string_len))

        logging.info(
            "Checking enough space in the image to encode for the data file.")
        if (binary_string_len + forLength) > space:
            logging.error(
                "Not enough space in image for the file to be encoded...")
            logging.error("Need: " + str(space))
            logging.error("Have: " + str(binary_string_len + forLength))
            sys.exit(2)

        logging.info("Adding the size of the data file to the image.")
        pos = 1
        index = 1
        pixel = list(pixels[(index % width), (index / width)])
        pixel[0] = len(binary_string_len_binary_string)
        pixels[(index % width), (index / width)] = tuple(pixel)

        for i in range(0, (forLength - 1)):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index / width)])
            pixel[pos] = int(binary_string_len_binary_string[i])
            pixels[(index % width), (index / width)] = tuple(pixel)
            pos = pos + 1

        logging.info("Adding the data to the image.")
        for i in range(0, binary_string_len):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index / width)])
            if str(pixel[pos] % 2) != binary_string[i]:
                if pixel[pos] == 255:
                    pixel[pos] = 254
                else:
                    pixel[pos] = pixel[pos] + 1

            pixels[(index % width), (index / width)] = tuple(pixel)
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

        pixel = list(pixels[(index % width), (index / width)])
        binary_string_len_binary_string_len = pixel[0]
        binary_string_len_binary_string = ""

        logging.info("Working out encoded data length...")
        for i in range(0, binary_string_len_binary_string_len):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index / width)])

            binary_string_len_binary_string += str(pixel[pos] % 2)

            pos = pos + 1

        length = int(binary_string_len_binary_string, 2)
        logging.info("Data length " + str(length) + "...")

        binary_data = ""

        logging.info("Decoding the embedded data...")
        for i in range(0, length):
            if pos > 2:
                pos = 0
                index = index + 1

            pixel = list(pixels[(index % width), (index / width)])

            binary_data += str(pixel[pos] % 2)

            pos = pos + 1

        return binary_data
    else:
        print("Unsupported image mode: %s" % image.mode)
        sys.exit(1)


def main(argv):
    """The main method for taking in the arguments and calling the
     relevant subroutines.

    Parameters
    ----------
    argv : list
        A list containing the arguments provided by the user.

    """

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', action="store_true", default=False,
                        help='Causes the program to be verbose in it\'s output'
                             ' logging.')
    parser.add_argument('-e', '--encode', action="store_true", default=False,
                        help="Takes the .png provided through the --input"
                             " argument, encodes the data file provided"
                             " through the --data arguments and outputs the"
                             " resulting image to the path provided by the"
                             " --output argument. If the --key argument is"
                             " present the data file is encrypted with the"
                             " key via CBC AES before encoding.")
    parser.add_argument('-d', '--decode', action="store_true", default=False,
                        help="Takes the .png provided through the --input"
                             " argument, decodes the data file embedded and"
                             " outputs the decoded file to the path provided"
                             " by the --output argument. If the --key argument"
                             " is present the decoded file is decrypted with"
                             " the key via CBC AES before outputting the"
                             " decoded file to the provided path.")
    parser.add_argument('-i', '--input', type=str,
                        help="The path to the .png to use as input.")
    parser.add_argument('-o', '--output', type=str,
                        help="The path to the outputted encoded .png when ran"
                             " in encode mode or the path to the outputted "
                             "decoded data when ran in decode mode.")
    parser.add_argument('--data', type=str,
                        help="The data to encode into the input .png when"
                             " encoding.")
    parser.add_argument('-k', '--key', default='', type=str,
                        help="The cryptographic key to use in the AES CBC"
                             " encryption/decryption.")
    args = parser.parse_args()

    data_file = args.data

    if args.verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s",
                            level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    if ((args.decode is True and args.encode is True) or (
            args.decode is False and args.encode is False)):
        logging.warning("Encoding or Decoding not selected, see help.")
        sys.exit(2)
    elif (args.encode is True):
        logging.info("Encoding.")

        if args.output != "" and args.input != "" and data_file != "":
            logging.info(" input = " + args.input)
            logging.info(" output = " + args.output)
            logging.info(" data_file = " + data_file)

            if (args.key != ""):
                logging.info(" Encrypting data file...")
                encrypt_file(args.key, data_file)
                data_file += ".enc"

            logging.info(" Reading in image " + args.input + " to encode...")
            encoding = open_image(args.input)
            logging.info(" Encoding the image...")
            encoded = steganography_encode(encoding,
                                           read_binary_string(data_file))
            logging.info(" Saving the encoded image as " + args.output + "...")
            save_image(encoded, args.output)

            if (args.key != ""):
                logging.info(" Deleting the encrypting data file...")
                os.remove(data_file)
        else:
            logging.warning(
                "Not the required arguments for encoding, see help.")
            sys.exit(2)
    elif (args.decode is True):
        logging.info("Decoding.")

        if args.output != "" and args.input != "":
            logging.info(" input = " + args.input)
            logging.info(" output = " + args.output)

            logging.info(" Reading in image " + args.input + " to decode...")
            decoding = open_image(args.input)
            logging.info(" Decoding the image...")
            decoded = steganography_decode(decoding)

            if (args.key != ""):
                logging.info(
                    " Saving the decoded encrypted data as " + args.output
                    + ".enc...")
                write_binary_string(decoded, args.output + '.enc')
                logging.info(" Decrypting the data file...")
                decrypt_file(args.key, args.output + '.enc')
                logging.info(" Deleting the encrypting data file...")
                os.remove(args.output + '.enc')
            else:
                logging.info(
                    " Saving the decoded data as " + args.output + "...")
                write_binary_string(decoded, args.output)

        else:
            logging.warning(
                "Not the required arguments for decoding. See help.")
            sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
