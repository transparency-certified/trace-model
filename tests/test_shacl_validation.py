"""SHACL validation of TROV examples against the TRO shape constraints."""

from pathlib import Path
import pytest
from rdflib import Graph
from pyshacl import validate

DEMO_DIR = Path(__file__).parent.parent / "demo" / "02-tro-examples"
SHAPES_PATH = (Path(__file__).parent.parent / "demo" /
               "03-trace-explorations" / "05-validate-tro-declaration" /
               "data" / "tro.schema.ttl")


def load_example(example_dir: str) -> Graph:
    g = Graph()
    g.parse(DEMO_DIR / example_dir / "tro" / "tro.jsonld", format="json-ld")
    return g


def run_shacl(data_graph: Graph):
    shapes = Graph()
    shapes.parse(SHAPES_PATH, format="turtle")
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes,
    )
    return conforms, results_text


class TestExample01ShaclValidation:

    @pytest.fixture
    def graph(self):
        return load_example("01-two-artifacts-no-trp")

    def test_conforms(self, graph):
        conforms, results_text = run_shacl(graph)
        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestExample02ShaclValidation:

    @pytest.fixture
    def graph(self):
        return load_example("02-three-artifacts-one-trp")

    def test_conforms(self, graph):
        conforms, results_text = run_shacl(graph)
        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestExample03ShaclValidation:

    @pytest.fixture
    def graph(self):
        return load_example("03-skope-lbda-processing")

    def test_conforms(self, graph):
        conforms, results_text = run_shacl(graph)
        assert conforms, f"SHACL validation failed:\n{results_text}"


class TestShaclCatchesErrors:
    """Verify that the SHACL shapes actually catch invalid TROs."""

    def test_missing_composition_fails(self):
        g = Graph()
        g.parse(data='''{
            "@context": [{
                "trov": "https://w3id.org/trace/trov/0.1#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            }],
            "@graph": [{
                "@id": "http://example.org/tro/1",
                "@type": "trov:TransparentResearchObject",
                "trov:wasAssembledBy": {
                    "@id": "http://example.org/trs/1",
                    "@type": "trov:TrustedResearchSystem",
                    "trov:publicKey": "fake-key"
                },
                "trov:hasArrangement": {
                    "@id": "http://example.org/arr/1",
                    "@type": "trov:ArtifactArrangement",
                    "trov:hasArtifactLocation": {
                        "@id": "http://example.org/loc/1",
                        "@type": "trov:ArtifactLocation",
                        "trov:artifact": { "@id": "http://example.org/art/1" },
                        "trov:path": "file1"
                    }
                }
            }]
        }''', format="json-ld")
        conforms, results_text = run_shacl(g)
        assert not conforms, "Should fail: TRO missing hasComposition"

    def test_missing_public_key_fails(self):
        g = Graph()
        g.parse(data='''{
            "@context": [{
                "trov": "https://w3id.org/trace/trov/0.1#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            }],
            "@graph": [{
                "@id": "http://example.org/trs/1",
                "@type": "trov:TrustedResearchSystem",
                "rdfs:comment": "TRS with no public key"
            }]
        }''', format="json-ld")
        conforms, results_text = run_shacl(g)
        assert not conforms, "Should fail: TRS missing publicKey"

    def test_missing_fingerprint_fails(self):
        g = Graph()
        g.parse(data='''{
            "@context": [{
                "trov": "https://w3id.org/trace/trov/0.1#"
            }],
            "@graph": [{
                "@id": "http://example.org/comp/1",
                "@type": "trov:ArtifactComposition",
                "trov:hasArtifact": {
                    "@id": "http://example.org/art/1",
                    "@type": "trov:ResearchArtifact",
                    "trov:hash": { "trov:hashAlgorithm": "sha256", "trov:hashValue": "abc123" },
                    "trov:mimeType": "text/plain"
                }
            }]
        }''', format="json-ld")
        conforms, results_text = run_shacl(g)
        assert not conforms, "Should fail: composition missing hasFingerprint"
