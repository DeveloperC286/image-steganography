# Image Steganography
[![pipeline status](https://gitlab.com/DeveloperC/image-steganography/badges/master/pipeline.svg)](https://gitlab.com/DeveloperC/image-steganography/commits/master)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)


This Python program provides the capability to conduct image steganography. Encoding or decoding any data into a .png image, with nominal changes to the appearance of the encoded image. The program also has the added capability of automatically implementing AES encryption/decryption on the data file, therefore encoded data if detected, is still confidential.


## Content
 * [Benefits](#benefits)
 * [Limitations](#limitations)
 * [Installing Dependencies](#installing-dependencies)
 * [Non-Encryption Usage](#non-encryption-usage)
   + [Encoding](#encoding)
   + [Decoding](#decoding)
 * [Encryption Usage](#encryption-usage)
   + [Encoding](#encoding-1)
   + [Decoding](#decoding-1)


## Benefits
 * Nominal or no appearance change.
 * CBC AES encryption/decryption inbuilt.


## Limitations
 * Limited available encoding space depending upon image size.


## Installing Dependencies
via Arch Linux's package manager.
```
pacman -S python2-pillow python2-numpy python2-pycryptodome
```

via pip and a virtual environment.
```
virtualenv -p python2 .venv
source .venv/bin/activate
pip2 install -r requirements.txt
```

## Non-Encryption Usage
### Encoding
```
python2 image-steganography.py --encode --input input.image.png --data input.data --output output.image.png
```

Encodes the data `input.data` into the image `input.image.png` and outputs the image containing the steganography as `output.image.png`.


### Decoding
```
python2 image-steganography.py --decode --input output.image.png  --output output.data
```

Decodes the data encoded into `output.image.png` and saves the decoded data file as `output.data`.


## Encryption Usage
### Encoding
```
python2 image-steganography.py --encode --input input.image.png --data input.data --output output.image.png --key 1234567890123456
```

Encrypts `input.data` with the provided key and outputs the encrypted version as `input.data.enc`. Encodes the data `input.data.enc` into the image `input.image.png` and outputs the image containing the steganography as `output.image.png`.


### Decoding
```
python2 image-steganography.py --decode --input output.image.png  --output output.data --key 1234567890123456
```

Decodes the data encoded into `output.image.png` and saves the decoded data file as `output.data.enc`. The data file `output.data.enc` is then decrypted using the provided key and saved as `output.data`.
