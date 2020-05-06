# Image Steganography
[![pipeline status](https://gitlab.com/DeveloperC/image-steganography/badges/master/pipeline.svg)](https://gitlab.com/DeveloperC/image-steganography/commits/master) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This Python program provides the capability to conduct image steganography. Encoding or decoding any data into a .png image, with nominal changes to the appearance of the encoded image. The program also has the added capability of automatically implementing AES encryption/decryption on the data file, therefore encoded data if detected, is still confidential.

## Benefits
<ul>
  <li>Nominal or no appearance change.</li>
  <li>CBC AES encryption/decryption inbuilt.</li>
</ul>

## Limitations
<ul>
  <li>Limited available encoding space depending upon image size.</li>
</ul>

## Installing Dependencies
via Arch Linux's package manager.
<ul>
  <li><b>pacman -S python2-pillow python2-numpy python2-pycryptodome</b></li>
</ul>

via pip and a virtual environment.
<ul>
  <li><b>virtualenv -p python2 .venv</b></li>
  <li><b>source .venv/bin/activate</b></li>
  <li><b>pip2 install -r requirements.txt</b></li>
</ul>

## Non-Encryption Usage

### Encoding
<b>python2 image-steganography.py --encode --input input.image.png --data input.data --output output.image.png</b>
<br/>
Encodes the data 'input.data' into the image 'input.image.png' and outputs the image containing the steganography as 'output.image.png'.

### Decoding
<b>python2 image-steganography.py --decode --input output.image.png  --output output.data</b>
<br/>
Decodes the data encoded into 'output.image.png' and saves the decoded data file as 'output.data'.

## Encryption Usage

### Encoding
<b>python2 image-steganography.py --encode --input input.image.png --data input.data --output output.image.png --key 1234567890123456</b>
<br/>
Encrypts 'input.data' with the provided key and outputs the encrypted version as 'input.data.enc'. Encodes the data 'input.data.enc' into the image 'input.image.png' and outputs the image containing the steganography as 'output.image.png'.

### Decoding
<b>python2 image-steganography.py --decode --input output.image.png  --output output.data --key 1234567890123456</b>
<br/>
Decodes the data encoded into 'output.image.png' and saves the decoded data file as 'output.data.enc'. The data file 'output.data.enc' is then decrypted using the provided key and saved as 'output.data'.
