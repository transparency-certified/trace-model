"""Verify OWL inference over TROV vocabulary + examples."""

from pathlib import Path
import pytest
from rdflib import Graph, Namespace, RDF, RDFS
from owlrl import DeductiveClosure, OWLRL_Semantics

TROV = Namespace("https://w3id.org/trace/2023/05/trov#")

DEMO_DIR = Path(__file__).parent.parent / "demo" / "02-tro-examples"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"
VOCAB_PATH = EXPORTS_DIR / "trace-vocab.jsonld"


def load_with_inference(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        g.parse(p, format="json-ld")
    DeductiveClosure(OWLRL_Semantics).expand(g)
    return g


class TestVocabularyInference:
    """Test that the vocabulary's class hierarchy is correct under OWL inference."""

    @pytest.fixture
    def graph(self):
        return load_with_inference(VOCAB_PATH)

    def test_capability_subclass_chain(self, graph):
        """CanProvideInternetIsolation should be a subclass of TRSCapability,
        TRSAttribute, and TREAttribute via the declared hierarchy."""
        assert (TROV.CanProvideInternetIsolation, RDFS.subClassOf, TROV.TRSCapability) in graph
        assert (TROV.CanProvideInternetIsolation, RDFS.subClassOf, TROV.TRSAttribute) in graph
        assert (TROV.CanProvideInternetIsolation, RDFS.subClassOf, TROV.TREAttribute) in graph

    def test_tro_attribute_subclass_chain(self, graph):
        """IncludesAllInputData should be a subclass of TROAttribute and TREAttribute."""
        assert (TROV.IncludesAllInputData, RDFS.subClassOf, TROV.TROAttribute) in graph
        assert (TROV.IncludesAllInputData, RDFS.subClassOf, TROV.TREAttribute) in graph

    def test_trp_attribute_subclass_chain(self, graph):
        """InternetIsolation should be a subclass of TRPAttribute and TREAttribute."""
        assert (TROV.InternetIsolation, RDFS.subClassOf, TROV.TRPAttribute) in graph
        assert (TROV.InternetIsolation, RDFS.subClassOf, TROV.TREAttribute) in graph

    def test_composition_subclass(self, graph):
        """ArtifactComposition should be a subclass of ArtifactCollection."""
        assert (TROV.ArtifactComposition, RDFS.subClassOf, TROV.ArtifactCollection) in graph


class TestExample01WithInference:

    @pytest.fixture
    def graph(self):
        return load_with_inference(
            VOCAB_PATH,
            DEMO_DIR / "01-two-artifacts-no-trp" / "tro" / "tro.jsonld",
        )

    def test_tro_entailed_as_transparent_research_element(self, graph):
        """The TRO instance should be entailed as a TransparentResearchElement
        via subClassOf on TransparentResearchObject."""
        tros = list(graph.subjects(RDF.type, TROV.TransparentResearchObject))
        # KNOWN BUG: trace-vocab.jsonld declares ArtifactArrangement as
        # subClassOf TransparentResearchObject, so arrangements get
        # incorrectly entailed as TROs. Expect 2 until vocab is fixed.
        assert len(tros) == 2
        tro = [t for t in tros if str(t).endswith("/tro")][0]
        assert (tro, RDF.type, TROV.TransparentResearchElement) in graph

    def test_composition_entailed_as_artifact_collection(self, graph):
        """ArtifactComposition instances should be entailed as ArtifactCollection."""
        comps = list(graph.subjects(RDF.type, TROV.ArtifactComposition))
        assert len(comps) == 1
        assert (comps[0], RDF.type, TROV.ArtifactCollection) in graph

    def test_tsa_entailed_as_transparent_research_element(self, graph):
        tsas = list(graph.subjects(RDF.type, TROV.TimeStampingAuthority))
        assert len(tsas) == 1
        assert (tsas[0], RDF.type, TROV.TransparentResearchElement) in graph


class TestExample02WithInference:

    @pytest.fixture
    def graph(self):
        return load_with_inference(
            VOCAB_PATH,
            DEMO_DIR / "02-three-artifacts-one-trp" / "tro" / "tro.jsonld",
        )

    def test_capability_instance_entailed_as_trs_attribute(self, graph):
        """An instance of CanProvideInternetIsolation should also be
        a TRSCapability, TRSAttribute, and TREAttribute."""
        caps = list(graph.subjects(RDF.type, TROV.CanProvideInternetIsolation))
        assert len(caps) == 1
        cap = caps[0]
        assert (cap, RDF.type, TROV.TRSCapability) in graph
        assert (cap, RDF.type, TROV.TRSAttribute) in graph
        assert (cap, RDF.type, TROV.TREAttribute) in graph

    def test_tro_attribute_instance_entailed_as_tre_attribute(self, graph):
        """An instance of IncludesAllInputData should also be a TROAttribute
        and TREAttribute."""
        attrs = list(graph.subjects(RDF.type, TROV.IncludesAllInputData))
        assert len(attrs) == 1
        attr = attrs[0]
        assert (attr, RDF.type, TROV.TROAttribute) in graph
        assert (attr, RDF.type, TROV.TREAttribute) in graph

    def test_trp_attribute_instance_entailed_as_tre_attribute(self, graph):
        """An instance of InternetIsolation should also be a TRPAttribute
        and TREAttribute."""
        attrs = list(graph.subjects(RDF.type, TROV.InternetIsolation))
        assert len(attrs) == 1
        attr = attrs[0]
        assert (attr, RDF.type, TROV.TRPAttribute) in graph
        assert (attr, RDF.type, TROV.TREAttribute) in graph

    def test_domain_entailment_wasAssembledBy(self, graph):
        """Using trov:wasAssembledBy should entail the subject is a
        TransparentResearchObject (via rdfs:domain)."""
        subjects = list(graph.subjects(TROV.wasAssembledBy, None))
        assert len(subjects) >= 1
        for s in subjects:
            assert (s, RDF.type, TROV.TransparentResearchObject) in graph

    def test_range_entailment_wasAssembledBy(self, graph):
        """Using trov:wasAssembledBy should entail the object is a
        TransparentResearchSystem (via rdfs:range in the vocab).
        NOTE: the vocab currently uses TransparentResearchSystem where
        it should say TrustedResearchSystem — this test documents the
        current (incorrect) state."""
        objects = list(graph.objects(None, TROV.wasAssembledBy))
        assert len(objects) >= 1
        for o in objects:
            assert (o, RDF.type, TROV.TransparentResearchSystem) in graph


class TestExample03WithInference:

    @pytest.fixture
    def graph(self):
        return load_with_inference(
            VOCAB_PATH,
            DEMO_DIR / "03-skope-lbda-processing" / "tro" / "tro.jsonld",
        )

    def test_both_capability_types_entailed(self, graph):
        """Both CanProvideInternetIsolation and CanRecordInternetAccess
        instances should be entailed as TRSCapability."""
        for cap_type in [TROV.CanProvideInternetIsolation, TROV.CanRecordInternetAccess]:
            instances = list(graph.subjects(RDF.type, cap_type))
            assert len(instances) == 1, f"Expected 1 {cap_type}, found {len(instances)}"
            assert (instances[0], RDF.type, TROV.TRSCapability) in graph

    def test_all_trp_attributes_entailed_as_tre_attributes(self, graph):
        """All TRP attribute instances (InternetIsolation, InternetAccessRecording)
        should be entailed as TREAttribute."""
        for attr_type in [TROV.InternetIsolation, TROV.InternetAccessRecording]:
            instances = list(graph.subjects(RDF.type, attr_type))
            assert len(instances) >= 1, f"No instances of {attr_type}"
            for inst in instances:
                assert (inst, RDF.type, TROV.TREAttribute) in graph

    def test_triple_count_increases_with_inference(self, graph):
        """Sanity check: inference should have added triples beyond what
        was explicitly stated."""
        g_no_inf = Graph()
        g_no_inf.parse(VOCAB_PATH, format="json-ld")
        g_no_inf.parse(
            DEMO_DIR / "03-skope-lbda-processing" / "tro" / "tro.jsonld",
            format="json-ld",
        )
        assert len(graph) > len(g_no_inf), \
            f"Inference added no triples: {len(graph)} vs {len(g_no_inf)}"
