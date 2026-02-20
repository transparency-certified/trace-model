#!/usr/bin/env bash

TRO_DECLARATION=../../common/tro/tro.jsonld
PUBLIC_KEY_FILE=data/public.gpg
PRIVATE_KEY_FILE=data/private.asc
SIGNATURE_FILE=tmp/signature.asc

# ------------------------------------------------------------------------------

bash_cell 'delete the gnupg home directory and keys' << END_CELL

# delete contents of GnuPG home directory for this REPRO
gnupg-runtime.purge-keys

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'import the private key for repro@repros.dev' << END_CELL

python3 << END_PYTHON

import gnupg

# read the private key from the file
with open("${PRIVATE_KEY_FILE}", "r") as private_key_file:
    private_key_text = private_key_file.read()

# import the private key and trust it
gpg = gnupg.GPG()
gpg.import_keys(private_key_text)

END_PYTHON

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'list the imported public key using the gpg cli' << END_CELL

echo Public keys:
echo
gpg --list-keys
echo
echo Private keys:
echo
gpg --list-secret-keys
echo

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'sign and verify the tro.jsonld for repro@repros.dev (detach=True)' << END_CELL

python3 << END_PYTHON

import gnupg

# Read the message from the file
with open("${TRO_DECLARATION}", "r") as tro_declaration_file:
    tro_declaration_text = bytes(tro_declaration_file.read(), "utf-8")

# Sign the message with the private key
gpg = gnupg.GPG()
signed_text = gpg.sign(tro_declaration_text, keyid="repro@repros.dev", passphrase="repro", detach=True)

# Write the signed message to a file
with open("${SIGNATURE_FILE}", "w") as text_file:
    text_file.write(str(signed_text))
verified = gpg.verify_data("${SIGNATURE_FILE}", tro_declaration_text)
if not verified: 
    raise ValueError("Signature could not be verified!")
else:
    print("Signature has been verified successfully!")

END_PYTHON

END_CELL

# ------------------------------------------------------------------------------