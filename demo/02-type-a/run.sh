#!/usr/bin/env bash

# paths to data files
TRS=../common/trs
TRO=../common/tro

# *****************************************************************************

bash_cell import_tro_jsonld << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist destroy --dataset kb --quiet
geist create --dataset kb --quiet
geist import --format jsonld --file ${TRS}/trs-02-type-a.jsonld
geist import --format jsonld --file ${TRO}/tro-02-from-type-a-trs.jsonld

END_CELL

# *****************************************************************************

bash_cell export_tro_ntriples << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist export --format nt | sort

END_CELL

# *****************************************************************************

source ../common/trs-queries.sh

