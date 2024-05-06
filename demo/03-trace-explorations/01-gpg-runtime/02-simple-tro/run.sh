#!/usr/bin/env bash

TRO_DECLARATION=../../common/tro/tro.jsonld
PUBLIC_KEY_FILE=data/public.gpg
PRIVATE_KEY_FILE=data/private.asc
SIGNATURE_FILE=tmp/signature.asc

# ------------------------------------------------------------------------------

bash_cell 'delete gnupg home directory' << 'END_CELL'

# delete contents of the .gnupg directory for this REPRO
gnupg-runtime.purge-keys

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'import jsonld' << END_CELL

# Import TRO as JSON-LD and export as N-TRIPLES
geist destroy rdflib --dataset kb --quiet
geist create rdflib --dataset kb --inputformat json-ld --inputfile ${TRO_DECLARATION} --infer owl

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'import the private key for repro@repros.dev' << END_CELL

# delete contents of the .gnupg directory for this REPRO
gnupg-runtime.purge-keys

# import the private key file
gpg --import --pinentry-mode loopback --passphrase=repro ${PRIVATE_KEY_FILE} 2>&1
echo

# list the gpg keys
gpg --list-keys

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'sign the tro.jsonld file with the private key' << END_CELL

rm -f ${SIGNATURE_FILE}
gpg --detach-sign --local-user repro@repros.dev \
    --pinentry-mode loopback --passphrase=repro \
    -a -o ${SIGNATURE_FILE}             \
    ${TRO_DECLARATION} 2>&1

END_CELL

# ------------------------------------------------------------------------------

bash_cell 'verify the signature with the public key' << END_CELL

gpg -v --verify ${SIGNATURE_FILE} ${TRO_DECLARATION} 2>&1 | tail -6

END_CELL

# ------------------------------------------------------------------------------