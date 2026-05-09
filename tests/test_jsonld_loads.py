"""Verify that TROV JSON-LD examples parse as valid RDF."""

from pathlib import Path
import pytest
from rdflib import Graph, Namespace, RDF

TROV = Namespace("https://w3id.org/trace/2023/05/trov#")

DEMO_DIR = Path(__file__).parent.parent / "demo" / "02-tro-examples"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"


def load_jsonld(path: Path) -> Graph:
    g = Graph()
    g.parse(path, format="json-ld")
    return g


class TestVocabularyLoads:

    def test_trace_vocab_parses(self):
        g = load_jsonld(EXPORTS_DIR / "trace-vocab.jsonld")
        assert len(g) > 0

    def test_trace_vocab_defines_tro_class(self):
        g = load_jsonld(EXPORTS_DIR / "trace-vocab.jsonld")
        assert (TROV.TransparentResearchObject, RDF.type, None) in g


class TestExample01TwoArtifactsNoTrp:

    @pytest.fixture
    def graph(self):
        return load_jsonld(DEMO_DIR / "01-two-artifacts-no-trp" / "tro" / "tro.jsonld")

    def test_parses(self, graph):
        assert len(graph) > 0

    def test_has_tro(self, graph):
        tros = list(graph.subjects(RDF.type, TROV.TransparentResearchObject))
        assert len(tros) == 1

    def test_has_trs(self, graph):
        trs_list = list(graph.subjects(RDF.type, TROV.TrustedResearchSystem))
        assert len(trs_list) == 1

    def test_has_composition(self, graph):
        comps = list(graph.subjects(RDF.type, TROV.ArtifactComposition))
        assert len(comps) == 1

    def test_has_two_artifacts(self, graph):
        artifacts = list(graph.subjects(RDF.type, TROV.ResearchArtifact))
        assert len(artifacts) == 2

    def test_has_arrangement(self, graph):
        arrangements = list(graph.subjects(RDF.type, TROV.ArtifactArrangement))
        assert len(arrangements) == 1

    def test_tro_linked_to_trs(self, graph):
        tros = list(graph.subjects(RDF.type, TROV.TransparentResearchObject))
        trs_links = list(graph.objects(tros[0], TROV.wasAssembledBy))
        assert len(trs_links) == 1

    def test_all_predicates_in_known_namespaces(self, graph):
        trov_ns = str(TROV)
        rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
        owl_ns = "http://www.w3.org/2002/07/owl#"
        known = (trov_ns, rdf_ns, rdfs_ns, owl_ns)
        for s, p, o in graph:
            assert any(str(p).startswith(ns) for ns in known), \
                f"Unexpected predicate namespace: {p}"


class TestExample02ThreeArtifactsOneTrp:

    @pytest.fixture
    def graph(self):
        return load_jsonld(DEMO_DIR / "02-three-artifacts-one-trp" / "tro" / "tro.jsonld")

    def test_parses(self, graph):
        assert len(graph) > 0

    def test_has_tro(self, graph):
        tros = list(graph.subjects(RDF.type, TROV.TransparentResearchObject))
        assert len(tros) == 1

    def test_has_trs(self, graph):
        trs_list = list(graph.subjects(RDF.type, TROV.TrustedResearchSystem))
        assert len(trs_list) == 1, \
            f"Expected TrustedResearchSystem, found types: " \
            f"{[str(o) for s, o in graph.subject_objects(RDF.type) if 'System' in str(o)]}"

    def test_has_three_artifacts(self, graph):
        artifacts = list(graph.subjects(RDF.type, TROV.ResearchArtifact))
        assert len(artifacts) == 3

    def test_has_two_arrangements(self, graph):
        arrangements = list(graph.subjects(RDF.type, TROV.ArtifactArrangement))
        assert len(arrangements) == 2

    def test_has_performance(self, graph):
        trps = list(graph.subjects(RDF.type, TROV.TrustedResearchPerformance))
        assert len(trps) == 1, \
            f"Expected TrustedResearchPerformance, found types: " \
            f"{[str(o) for s, o in graph.subject_objects(RDF.type) if 'Performance' in str(o)]}"

    def test_has_capability(self, graph):
        caps = list(graph.subjects(RDF.type, TROV.CanProvideInternetIsolation))
        assert len(caps) == 1

    def test_performance_links_to_arrangements(self, graph):
        trps = list(graph.subjects(RDF.type, TROV.TrustedResearchPerformance))
        if not trps:
            trps = list(graph.subjects(RDF.type, TROV.TransparentResearchPerformance))
        assert len(trps) >= 1
        trp = trps[0]
        accessed = list(graph.objects(trp, TROV.accessedArrangement))
        assert len(accessed) == 1
        contributed = list(graph.objects(trp, TROV.contributedToArrangement))
        modified = list(graph.objects(trp, TROV.modifiedArrangement))
        assert len(contributed) + len(modified) == 1, \
            f"Expected contributedToArrangement, found contributed={len(contributed)}, modified={len(modified)}"

    def test_warrant_chain(self, graph):
        tro_attrs = list(graph.subjects(RDF.type, TROV.IncludesAllInputData))
        assert len(tro_attrs) == 1
        warrants = list(graph.objects(tro_attrs[0], TROV.warrantedBy))
        assert len(warrants) >= 1

    def test_no_unknown_predicates(self, graph):
        trov_ns = str(TROV)
        rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
        owl_ns = "http://www.w3.org/2002/07/owl#"
        known = (trov_ns, rdf_ns, rdfs_ns, owl_ns)
        for s, p, o in graph:
            assert any(str(p).startswith(ns) for ns in known), \
                f"Unexpected predicate namespace: {p}"


SCHEMA = Namespace("https://schema.org")


class TestExample03SkopeLbdaProcessing:

    @pytest.fixture
    def graph(self):
        return load_jsonld(DEMO_DIR / "03-skope-lbda-processing" / "tro" / "tro.jsonld")

    def test_parses(self, graph):
        assert len(graph) > 0

    def test_has_tro(self, graph):
        tros = list(graph.subjects(RDF.type, TROV.TransparentResearchObject))
        assert len(tros) == 1

    def test_has_trs(self, graph):
        trs_list = list(graph.subjects(RDF.type, TROV.TrustedResearchSystem))
        assert len(trs_list) == 1, \
            f"Expected TrustedResearchSystem, found types: " \
            f"{[str(o) for s, o in graph.subject_objects(RDF.type) if 'System' in str(o)]}"

    def test_has_six_artifacts(self, graph):
        artifacts = list(graph.subjects(RDF.type, TROV.ResearchArtifact))
        assert len(artifacts) == 6

    def test_has_four_arrangements(self, graph):
        arrangements = list(graph.subjects(RDF.type, TROV.ArtifactArrangement))
        assert len(arrangements) == 4

    def test_has_three_performances(self, graph):
        trps = list(graph.subjects(RDF.type, TROV.TrustedResearchPerformance))
        if not trps:
            trps = list(graph.subjects(RDF.type, TROV.TransparentResearchPerformance))
        assert len(trps) == 3, \
            f"Expected 3 performances, found types: " \
            f"{[str(o) for s, o in graph.subject_objects(RDF.type) if 'Performance' in str(o)]}"

    def test_has_two_capabilities(self, graph):
        cap1 = list(graph.subjects(RDF.type, TROV.CanProvideInternetIsolation))
        cap2 = list(graph.subjects(RDF.type, TROV.CanRecordInternetAccess))
        assert len(cap1) == 1
        assert len(cap2) == 1

    def test_performances_form_chain(self, graph):
        trps = list(graph.subjects(RDF.type, TROV.TrustedResearchPerformance))
        if not trps:
            trps = list(graph.subjects(RDF.type, TROV.TransparentResearchPerformance))
        for trp in trps:
            accessed = list(graph.objects(trp, TROV.accessedArrangement))
            contributed = list(graph.objects(trp, TROV.contributedToArrangement))
            assert len(accessed) == 1, f"{trp} missing accessedArrangement"
            assert len(contributed) == 1, f"{trp} missing contributedToArrangement"

    def test_no_unknown_predicates(self, graph):
        trov_ns = str(TROV)
        rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        rdfs_ns = "http://www.w3.org/2000/01/rdf-schema#"
        owl_ns = "http://www.w3.org/2002/07/owl#"
        schema_ns = str(SCHEMA)
        known = (trov_ns, rdf_ns, rdfs_ns, owl_ns, schema_ns)
        for s, p, o in graph:
            assert any(str(p).startswith(ns) for ns in known), \
                f"Unexpected predicate namespace: {p}"
