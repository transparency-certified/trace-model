"""Verify that vocab + example data load together and produce coherent graphs."""

from pathlib import Path
import pytest
from rdflib import Graph, Namespace, RDF, RDFS, URIRef

TROV = Namespace("https://w3id.org/trace/2023/05/trov#")

DEMO_DIR = Path(__file__).parent.parent / "demo" / "02-tro-examples"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"
VOCAB_PATH = EXPORTS_DIR / "trace-vocab.jsonld"


def load_combined(vocab: Path, *data_paths: Path) -> Graph:
    g = Graph()
    g.parse(vocab, format="json-ld")
    for p in data_paths:
        g.parse(p, format="json-ld")
    return g


class TestVocabAndExample01Combined:

    @pytest.fixture
    def vocab_only(self):
        g = Graph()
        g.parse(VOCAB_PATH, format="json-ld")
        return g

    @pytest.fixture
    def combined(self):
        return load_combined(
            VOCAB_PATH,
            DEMO_DIR / "01-two-artifacts-no-trp" / "tro" / "tro.jsonld",
        )

    def test_combined_has_more_triples_than_vocab_alone(self, vocab_only, combined):
        assert len(combined) > len(vocab_only)

    def test_vocab_classes_present(self, combined):
        vocab_classes = [
            TROV.TransparentResearchObject,
            TROV.ArtifactComposition,
            TROV.ResearchArtifact,
            TROV.ArtifactArrangement,
            TROV.ArtifactLocation,
            TROV.CompositionFingerprint,
            TROV.TimeStampingAuthority,
        ]
        for cls in vocab_classes:
            assert (cls, RDF.type, RDFS.Class) in combined, \
                f"Vocab class {cls} not found as rdfs:Class"

    def test_example_instances_use_vocab_types(self, combined):
        """Every rdf:type used on an instance in the example should correspond
        to a class declared in the vocabulary."""
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        vocab_classes = set(combined.subjects(RDF.type, RDFS.Class))
        for s, _, o in combined.triples((None, RDF.type, None)):
            if str(s).startswith(base) and o != RDFS.Class:
                assert o in vocab_classes, \
                    f"Instance {s} uses type {o} not declared in vocabulary"

    def test_vocab_properties_present(self, combined):
        vocab_props = [
            TROV.wasAssembledBy,
            TROV.wasTimestampedBy,
            TROV.hasComposition,
            TROV.hasArrangement,
            TROV.hasArtifactLocation,
            TROV.hasFingerprint,
            TROV.hasArtifact,
        ]
        for prop in vocab_props:
            assert (prop, RDF.type, RDF.Property) in combined, \
                f"Vocab property {prop} not found as rdf:Property"

    def test_example_predicates_declared_in_vocab(self, combined):
        """Every trov: predicate used in the example should be declared
        as an rdf:Property in the vocabulary."""
        trov_ns = str(TROV)
        vocab_props = set(combined.subjects(RDF.type, RDF.Property))
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        for s, p, o in combined:
            if str(s).startswith(base) and str(p).startswith(trov_ns):
                assert p in vocab_props, \
                    f"Predicate {p} used in example but not declared in vocabulary"


class TestVocabAndExample02Combined:

    @pytest.fixture
    def combined(self):
        return load_combined(
            VOCAB_PATH,
            DEMO_DIR / "02-three-artifacts-one-trp" / "tro" / "tro.jsonld",
        )

    def test_combined_loads(self, combined):
        assert len(combined) > 0

    def test_example_instances_use_vocab_types(self, combined):
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        vocab_classes = set(combined.subjects(RDF.type, RDFS.Class))
        for s, _, o in combined.triples((None, RDF.type, None)):
            if str(s).startswith(base) and o != RDFS.Class:
                assert o in vocab_classes, \
                    f"Instance {s} uses type {o} not declared in vocabulary"

    def test_example_predicates_declared_in_vocab(self, combined):
        trov_ns = str(TROV)
        vocab_props = set(combined.subjects(RDF.type, RDF.Property))
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        for s, p, o in combined:
            if str(s).startswith(base) and str(p).startswith(trov_ns):
                assert p in vocab_props, \
                    f"Predicate {p} used in example but not declared in vocabulary"


class TestVocabAndExample03Combined:

    @pytest.fixture
    def combined(self):
        return load_combined(
            VOCAB_PATH,
            DEMO_DIR / "03-skope-lbda-processing" / "tro" / "tro.jsonld",
        )

    def test_combined_loads(self, combined):
        assert len(combined) > 0

    def test_example_instances_use_vocab_types(self, combined):
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        vocab_classes = set(combined.subjects(RDF.type, RDFS.Class))
        for s, _, o in combined.triples((None, RDF.type, None)):
            if str(s).startswith(base) and o != RDFS.Class:
                assert o in vocab_classes, \
                    f"Instance {s} uses type {o} not declared in vocabulary"

    def test_example_predicates_declared_in_vocab(self, combined):
        trov_ns = str(TROV)
        vocab_props = set(combined.subjects(RDF.type, RDF.Property))
        base = "https://github.com/transparency-certified/trace-model/tree/master/"
        for s, p, o in combined:
            if str(s).startswith(base) and str(p).startswith(trov_ns):
                assert p in vocab_props, \
                    f"Predicate {p} used in example but not declared in vocabulary"
