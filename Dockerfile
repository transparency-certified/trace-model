ARG PARENT_IMAGE=cirss/repro-parent:latest

FROM ${PARENT_IMAGE}

# copy exports into new Docker image
COPY exports /repro/exports

# copy trace-model's own package source so base-setup can install it (provides
# the tro_fingerprint_state / merge_states console scripts the demos invoke)
COPY pyproject.toml /repro/
COPY src /repro/src

# copy the repro boot setup script from the distribution and run it
ADD ${REPRO_DIST}/boot-setup /repro/dist/
RUN bash /repro/dist/boot-setup

USER repro

# install required external repro modules
RUN repro.require python-dev master ${REPROS_DEV} --default --code
RUN repro.require shell-notebook master ${REPROS_DEV}
RUN repro.require graphviz-runtime master ${REPROS_DEV} --util
RUN repro.require gnupg-runtime master ${REPROS_DEV}
RUN repro.require gnupg-api master ${REPROS_DEV}

# install geist (CIRSS module): GEIST_INSTALL=git makes geist-p's base-setup
# install geist-p[rdflib] from git@main (the unreleased query2df fix), keeping
# the module wiring and the package on the same ref.
ENV GEIST_INSTALL=git
RUN repro.require geist-p main ${CIRSS}

RUN sudo apt-get update && sudo apt install graphviz-dev -y

# install contents of the exports directory as a repro module
RUN repro.require trace-model exports --demo

# use a local directory named tmp for each demo
RUN repro.env REPRO_DEMO_TMP_DIRNAME tmp

CMD  /bin/bash -il
