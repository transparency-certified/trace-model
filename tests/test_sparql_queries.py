"""SPARQL queries over TROV examples, replicating the geist template queries."""

from pathlib import Path
import pytest
from rdflib import Graph, Namespace, RDF

TROV = Namespace("https://w3id.org/trace/2023/05/trov#")

DEMO_DIR = Path(__file__).parent.parent / "demo" / "02-tro-examples"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"
VOCAB_PATH = EXPORTS_DIR / "trace-vocab.jsonld"

PREFIXES = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX trov: <https://w3id.org/trace/2023/05/trov#>
"""


def load_example(example_dir: str) -> Graph:
    g = Graph()
    g.parse(VOCAB_PATH, format="json-ld")
    g.parse(DEMO_DIR / example_dir / "tro" / "tro.jsonld", format="json-ld")
    return g


class TestExample01Queries:

    @pytest.fixture
    def graph(self):
        return load_example("01-two-artifacts-no-trp")

    def test_find_tro_and_trs(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?tro ?trs
            WHERE {
                ?tro rdf:type trov:TransparentResearchObject .
                ?tro trov:wasAssembledBy ?trs .
            }
        """))
        assert len(results) == 1
        assert "tro" in str(results[0][0])
        assert "trs" in str(results[0][1])

    def test_find_artifacts(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?artifact ?mimeType ?sha256
            WHERE {
                ?comp rdf:type trov:ArtifactComposition .
                ?comp trov:hasArtifact ?artifact .
                ?artifact trov:mimeType ?mimeType .
                ?artifact trov:sha256 ?sha256 .
            }
            ORDER BY ?artifact
        """))
        assert len(results) == 2
        for row in results:
            assert str(row[1]) == "text/plain"
            assert len(str(row[2])) == 64

    def test_find_arrangement_locations(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?arrangement ?artifact ?location
            WHERE {
                ?arrangement rdf:type trov:ArtifactArrangement .
                ?arrangement trov:hasArtifactLocation ?loc .
                ?loc trov:hasArtifact ?artifact .
                ?loc trov:hasLocation ?location .
            }
            ORDER BY ?arrangement ?location
        """))
        assert len(results) == 2
        locations = {str(row[2]) for row in results}
        assert locations == {"file1", "file2"}

    def test_find_fingerprint(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?comp ?sha256
            WHERE {
                ?comp rdf:type trov:ArtifactComposition .
                ?comp trov:hasFingerprint ?fp .
                ?fp trov:sha256 ?sha256 .
            }
        """))
        assert len(results) == 1
        assert len(str(results[0][1])) == 64


class TestExample02Queries:

    @pytest.fixture
    def graph(self):
        return load_example("02-three-artifacts-one-trp")

    def test_find_trs_capabilities(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?trs ?capability ?capType
            WHERE {
                ?trs rdf:type trov:TransparentResearchSystem .
                ?trs trov:hasCapability ?capability .
                ?capability rdf:type ?capType .
            }
        """))
        assert len(results) == 1
        assert "CanProvideInternetIsolation" in str(results[0][2])

    def test_find_trp_arrangement_flow(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?trp ?in ?out
            WHERE {
                ?trp rdf:type trov:TransparentResearchPerformance .
                ?trp trov:accessedArrangement ?in .
                ?trp trov:contributedToArrangement ?out .
            }
            ORDER BY ?trp
        """))
        # KNOWN BUG: example uses modifiedArrangement instead of
        # contributedToArrangement, so this returns 0 results
        if len(results) == 0:
            pytest.xfail("Example uses trov:modifiedArrangement "
                         "instead of trov:contributedToArrangement")
        assert len(results) == 1

    def test_find_warrant_chain(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?troAttr ?troAttrType ?trpAttr ?trpAttrType ?cap ?capType
            WHERE {
                ?tro trov:hasAttribute ?troAttr .
                ?troAttr rdf:type ?troAttrType .
                ?troAttr trov:warrantedBy ?trpAttr .
                ?trpAttr rdf:type ?trpAttrType .
                ?trpAttr trov:warrantedBy ?cap .
                ?cap rdf:type ?capType .
            }
        """))
        assert len(results) >= 1
        row = results[0]
        assert "IncludesAllInputData" in str(row[1])
        assert "InternetIsolation" in str(row[3])
        assert "CanProvideInternetIsolation" in str(row[5])

    def test_find_performance_times(self, graph):
        results = list(graph.query(PREFIXES + """
            SELECT ?trp ?start ?end
            WHERE {
                ?trp rdf:type trov:TransparentResearchPerformance .
                ?trp trov:startedAtTime ?start .
                ?trp trov:endedAtTime ?end .
            }
        """))
        assert len(results) == 1
        assert "2023-05-05" in str(results[0][1])


class TestExample03Queries:
    """Replicates the SPARQL queries from templates.geist for the SKOPE example."""

    @pytest.fixture
    def graph(self):
        return load_example("03-skope-lbda-processing")

    def test_query_tro_trs(self, graph):
        """Replicate query_tro_trs_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?tro ?trs
            WHERE {
                ?tro rdf:type trov:TransparentResearchObject .
                ?tro trov:wasAssembledBy ?trs .
                ?trs rdf:type trov:TransparentResearchSystem .
            }
            ORDER BY ?tro ?trs
        """))
        assert len(results) == 1

    def test_query_trs_capabilities(self, graph):
        """Replicate query_trs_capability_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?trs ?capability_id ?capability_type
            WHERE {
                ?trs rdf:type trov:TransparentResearchSystem .
                ?trs trov:hasCapability ?capability_id .
                ?capability_id rdf:type ?capability_type .
            }
            ORDER BY ?trs ?capability_id ?capability_type
        """))
        assert len(results) == 2
        cap_types = {str(row[2]) for row in results}
        assert TROV.CanProvideInternetIsolation in {row[2] for row in results}
        assert TROV.CanRecordInternetAccess in {row[2] for row in results}

    def test_query_trp_arrangement_flow(self, graph):
        """Replicate query_trp_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?trp ?in ?out
            WHERE {
                ?trp rdf:type trov:TransparentResearchPerformance .
                ?trp trov:accessedArrangement ?in .
                ?trp trov:contributedToArrangement ?out .
            }
            ORDER BY ?trp ?in ?out
        """))
        assert len(results) == 3
        for row in results:
            assert "arrangement" in str(row[1])
            assert "arrangement" in str(row[2])

    def test_query_arrangement_artifacts(self, graph):
        """Replicate query_arrangement_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?arrangement ?artifact
            WHERE {
                ?tro rdf:type trov:TransparentResearchObject .
                ?tro trov:hasArrangement ?arrangement .
                ?arrangement trov:hasArtifactLocation ?loc .
                ?loc trov:hasArtifact ?artifact .
            }
            ORDER BY ?arrangement ?artifact
        """))
        assert len(results) > 0
        arrangements = {str(row[0]) for row in results}
        assert len(arrangements) == 4

    def test_query_artifact_details(self, graph):
        """Replicate query_artifact_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?artifact ?mimeType ?sha256
            WHERE {
                ?comp rdf:type trov:ArtifactComposition .
                ?comp trov:hasArtifact ?artifact .
                ?artifact trov:mimeType ?mimeType .
                ?artifact trov:sha256 ?sha256 .
            }
            ORDER BY ?artifact
        """))
        assert len(results) == 6
        mime_types = {str(row[1]) for row in results}
        assert "application/x-netcdf" in mime_types
        assert "text/html" in mime_types
        assert "image/png" in mime_types

    def test_query_trp_details(self, graph):
        """Replicate query_trp_details_str from templates.geist."""
        results = list(graph.query(PREFIXES + """
            SELECT DISTINCT ?trp ?description ?start ?end
            WHERE {
                ?trp rdf:type trov:TransparentResearchPerformance .
                ?trp rdfs:comment ?description .
                ?trp trov:startedAtTime ?start .
                ?trp trov:endedAtTime ?end .
            }
            ORDER BY ?trp ?start ?end
        """))
        assert len(results) == 3
        for row in results:
            assert "2023-05-08" in str(row[2])

    def test_performances_form_sequential_chain(self, graph):
        """Verify the three TRPs form a sequential chain:
        trp/1 reads arrangement/1, writes arrangement/2
        trp/2 reads arrangement/2, writes arrangement/3
        trp/3 reads arrangement/3, writes arrangement/4"""
        results = list(graph.query(PREFIXES + """
            SELECT ?trp ?in ?out
            WHERE {
                ?trp rdf:type trov:TransparentResearchPerformance .
                ?trp trov:accessedArrangement ?in .
                ?trp trov:contributedToArrangement ?out .
            }
            ORDER BY ?trp
        """))
        assert len(results) == 3
        for i, row in enumerate(results):
            assert str(row[1]).endswith(f"arrangement/{i+1}")
            assert str(row[2]).endswith(f"arrangement/{i+2}")
