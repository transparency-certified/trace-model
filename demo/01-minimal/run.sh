#!/usr/bin/env bash

# paths to data files
TRACE=../common/trace
TRS=../common/trs
TRO=../common/tro

# *****************************************************************************

bash_cell import_tro_jsonld << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist destroy --dataset kb --quiet
geist create --dataset kb --infer owl --quiet
geist import --format jsonld --file ${TRS}/trs-01-minimal.jsonld
geist import --format jsonld --file ${TRO}/tro-01-from-minimal-trs.jsonld

END_CELL

# *****************************************************************************

bash_cell export_ntriples << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist export --format nt | sort | grep trov

END_CELL

# *****************************************************************************

bash_cell import_trace_vocab_jsonld << END_CELL

# Import TRO and TRS as JSON-LD and export as N-TRIPLES
geist import --format jsonld --file ${TRACE}/trace-vocab.jsonld

END_CELL


# *****************************************************************************

source ../common/trs-queries.sh





