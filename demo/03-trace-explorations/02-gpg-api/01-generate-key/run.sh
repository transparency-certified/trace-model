#!/usr/bin/env bash

TRO_DECLARATION=../../common/tro/tro.jsonld
PUBLIC_KEY_FILE=tmp/public.gpg
PRIVATE_KEY_FILE=tmp/private.asc
SIGNATURE_FILE=tmp/signature.asc

# ------------------------------------------------------------------------------

bash_cell 'generate a key pair' << END_CELL

# delete contents of GnuPG home directory for this REPRO
gnupg-runtime.purge-keys

# generate a new key pair
python3 << END_PYTHON

import gnupg
import os

gpg = gnupg.GPG()
key_settings = gpg.gen_key_input(
    key_type = 'RSA',
    key_length = 1024,
    name_real = 'repro user',
    name_email = 'repro@repros.dev',
    passphrase = 'repro'
)
key = gpg.gen_key(key_settings)

END_PYTHON

# list the gpg keys
gpg --list-keys | grep uid

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'export the public key' << END_CELL

python3 << END_PYTHON

import gnupg

# export the public key
gpg = gnupg.GPG()
public_key = gpg.export_keys('repro@repros.dev')

# write the public key to a file
with open("${PUBLIC_KEY_FILE}", "w") as text_file:
    text_file.write(public_key)

END_PYTHON

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'export the private key' << END_CELL

python3 << END_PYTHON

import gnupg

# export the public key
gpg = gnupg.GPG()
private_key = gpg.export_keys('repro@repros.dev', secret=True, passphrase='repro')

# write the private key to a file
with open("${PRIVATE_KEY_FILE}", "w") as text_file:
    text_file.write(private_key)

END_PYTHON

END_CELL

# ------------------------------------------------------------------------------
