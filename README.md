# TRACE Model Demonstration

This repository demonstrates the _Transparent Research Object Vocabulary_ (__TROV__) for describing _Transparent Research Objects_ (__TROs__) and the _Transparent Research Systems_ (__TRS__'s) that produce them.

This repository is itself structured as a _Reproducible Every-Place Research Object_ (__REPRO__). It is associated with a public Docker image that aims to enable the the products of the demonstration to be reproduced at a Unix-like shell prompt on any computer that has Git, GNU Make, and Docker installed.

Make commands issued in the top-level directory are used to obtain the Docker image and run the demos.

## Setup the environment

First start the REPRO in interactive mode using the `make start-repro` command (or the shorthand `make start`).

Then Install the related Python packages using the `pip install .` command.

Finally, exit the REPRO using the `exit` command.

## Run and confirm the reproducibility of the demonstration

The demonstration and its products are stored in the `demo` directory tree:
```
trace-model$ tree demo
demo
├── 01-trov-vocab
│   ├── Makefile
│   ├── products
│   │   ├── img.gv
│   │   ├── img.svg
│   │   └── report_subclass.html
│   ├── run.sh
│   ├── run.txt
│   └── templates.geist
├── 02-tro-examples
│   ├── 01-two-artifacts-no-trp
│   │   ├── Makefile
│   │   ├── run.sh
│   │   ├── run.txt
│   │   ├── tro
│   │   │   ├── file1
.
. (additional output removed for brevity)
.
│   ├── 05-validate-tro-declaration
│   │   ├── Makefile
│   │   ├── data
│   │   │   ├── mappings.json
│   │   │   ├── tro.schema.ttl
│   │   │   ├── tro1.jsonld
│   │   │   ├── tro2.jsonld
│   │   │   ├── tro3.jsonld
│   │   │   ├── tro4.jsonld
│   │   │   └── tro5.jsonld
│   │   ├── products
│   │   │   ├── tro1.gv
│   │   │   ├── tro1.png
│   │   │   ├── tro2.gv
│   │   │   ├── tro2.png
│   │   │   ├── tro3.gv
│   │   │   ├── tro3.png
│   │   │   ├── tro4.gv
│   │   │   ├── tro4.png
│   │   │   ├── tro5.gv
│   │   │   └── tro5.png
│   │   ├── run.sh
│   │   └── run.txt
│   ├── Makefile
│   └── common
│       ├── certificate
│       │   ├── cacert.pem
│       │   └── tsa.crt
│       └── tro
│           ├── file1
│           ├── file2
│           └── tro.jsonld
└── Makefile
```

Below gives a brief description of these demonstrations:
- __01-trov-vocab__: query the _Transparent Research Object Vocabulary_ (__TROV__) and visualize the subclass relationship (check [report](https://transparency-certified.github.io/trace-model/demo/01-trov-vocab/products/report_subclass.html)).
- __02-tro-examples__: query three _Transparent Research Objects_ (__TROs__), _01-two-artifacts-no-trp_, _02-three-artifacts-one-trp_, and _03-skope-lbda-processing_ (check [TRO report](https://transparency-certified.github.io/trace-model/demo/02-tro-examples/03-skope-lbda-processing/report_file/report.html)).
- __03-trace-explorations__:
    - _01-gpg-runtime_ and _02-gpg-api_ demonstrate how a key pair can be generated and used to sign and verify a TRO declaration.
    - _03-tro-fingerprint-state_ demonstrates how a fingerprint of a given state can be computed.
    - _04-timestamp_ demonstrates how a trusted timestamp can be created and applied to a TRO.
    - _05-validate-tro-declaration_ demonstrates how a TRO declaration can be validated through 5 examples.

To establish that the demonstrations can be reproduced, first use the `make clean-demo` command to delete the files produced by the demo:
```
trace-model$ make clean-demo
------- Cleaning example 01-trov-vocab/ ----------------
removed './run.txt'
removed './products/img.gv'
removed './products/img.svg'
removed './products/report_subclass.html'
rmdir: removing directory, './products'

------- Cleaning example 02-tro-examples/ ----------------

------- Cleaning example 01-two-artifacts-no-trp/ ----------------
removed './run.txt'
.
. (additional output removed for brevity)
.
------- Cleaning example 05-validate-tro-declaration/ ----------------
removed './run.txt'
removed './products/tro1.gv'
removed './products/tro1.png'
removed './products/tro2.gv'
removed './products/tro2.png'
removed './products/tro3.gv'
removed './products/tro3.png'
removed './products/tro4.gv'
removed './products/tro4.png'
removed './products/tro5.gv'
removed './products/tro5.png'
rmdir: removing directory, './products'
```

Confirm with `git status` that version-controlled files have been deleted locally:
```
trace-model$ git status
On branch idcc24
Your branch is up to date with 'origin/idcc24'.

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    demo/01-trov-vocab/products/img.gv
        deleted:    demo/01-trov-vocab/products/img.svg
        deleted:    demo/01-trov-vocab/products/report_subclass.html
        deleted:    demo/01-trov-vocab/run.txt
        deleted:    demo/02-tro-examples/01-two-artifacts-no-trp/run.txt
        .
        . (additional output removed for brevity)
        .
        deleted:    demo/03-trace-explorations/05-validate-tro-declaration/products/tro5.png
        deleted:    demo/03-trace-explorations/05-validate-tro-declaration/run.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

Now run the demonstration with the `make run-demo` command:
```
trace-model$ make run-demo
---------- Running example 01-trov-vocab/ -------------

---------- Running example 02-tro-examples/ -------------

---------- Running example 01-two-artifacts-no-trp/ -------------
.
. (additional output removed for brevity)
.
---------- Running example 05-validate-tro-declaration/ -------------
```

Finally, use `git status` to confirm that the demostration products have been restored:

```
trace-model$ git status
On branch idcc24
Your branch is up to date with 'origin/idcc24'.

nothing to commit, working tree clean
```

## Running a single example

An individual example within the demonstration can be run by starting an interactive REPRO session.

First start the REPRO in interactive mode using the `make start-repro` command (or the shorthand `make start`).
```
trace-model$ make start-repro
repro@a6c7a4e443a8:/mnt/trace-model$
```

Set the working directory to a particular example directory:
```
repro@a6c7a4e443a8:/mnt/trace-model$ cd demo/01-trov-vocab/
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$

repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ pwd
/mnt/trace-model/demo/01-trov-vocab
```

Type `make` to run the example:
```
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ make
bash run.sh > run.txt
```

Use the `tree` command to list the files associated with the example, including the temporary files in the `tmp` subdirectory:

```
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ tree
.
|-- Makefile
|-- products
|   |-- img.gv
|   |-- img.svg
|   `-- report_subclass.html
|-- run.sh
|-- run.txt
|-- templates.geist
`-- tmp
    |-- query subclass vocab.sh
    |-- query subclass vocab.txt
    |-- load trov vocabulary without inferences.sh
    `-- load trov vocabulary without inferences.txt

2 directories, 11 files
```

The `make clean` command deletes the temporary files, the example output file, `run.txt`, and the products folder:
```
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ make clean
if [[ -f ./"run.txt" ]] ; then                       \
    rm -v ./"run.txt" ;                              \
fi
removed './run.txt'
if [[ -d ./"tmp" ]] ; then                              \
    rm -vf ./"tmp"/* ;                            \
    rmdir -v ./"tmp" ;                            \
fi
removed './tmp/query subclass vocab.sh'
removed './tmp/query subclass vocab.txt'
removed './tmp/load trov vocabulary without inferences.sh'
removed './tmp/load trov vocabulary without inferences.txt'
rmdir: removing directory, './tmp'
if [[ -d ./"products" ]] ; then                       \
    rm -vf ./"products"/* ;                           \
    rmdir -v ./"products" ;                           \
fi
removed './products/img.gv'
removed './products/img.svg'
removed './products/report_subclass.html'
rmdir: removing directory, './products'

repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ tree
.
|-- Makefile
|-- run.sh
`-- templates.geist

0 directories, 3 files
```

Confirm that the `run.txt` file and the `products` folder are the version-controlled files associated with this example that has been deleted:
```
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ git status .
On branch idcc24
Your branch is up to date with 'origin/idcc24'.

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    products/img.gv
        deleted:    products/img.svg
        deleted:    products/report_subclass.html
        deleted:    run.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

Re-run this example and confirm the `run.txt` file and the `products` folder were restored:
```
repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ make
bash run.sh > run.txt

repro@a6c7a4e443a8:/mnt/trace-model/demo/01-trov-vocab$ git status .
On branch idcc24
Your branch is up to date with 'origin/idcc24'.

nothing to commit, working tree clean

```




