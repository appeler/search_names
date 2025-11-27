#!/usr/bin/env python

"""
Tests for nlp_engine module
"""

import unittest
from unittest.mock import MagicMock, patch

from search_names.models import EntityMention
from search_names.nlp_engine import (
    EntityLinker,
    NLPEngine,
    NLPEngineError,
    SemanticSimilarity,
    SpacyNER,
)


class TestNLPEngineError(unittest.TestCase):
    """Test NLPEngineError exception."""

    def test_nlp_engine_error(self):
        """Test NLPEngineError exception creation."""
        error = NLPEngineError("Test error message")
        self.assertEqual(str(error), "Test error message")


class TestSpacyNER(unittest.TestCase):
    """Test SpacyNER class."""

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_spacy_ner_init_success(self, mock_spacy):
        """Test successful SpacyNER initialization."""
        mock_nlp = MagicMock()
        mock_spacy.load.return_value = mock_nlp

        ner = SpacyNER("en_core_web_sm")

        self.assertEqual(ner.model_name, "en_core_web_sm")
        self.assertEqual(ner.nlp, mock_nlp)
        mock_spacy.load.assert_called_once_with(
            "en_core_web_sm",
            disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"],
        )


    @patch("search_names.nlp_engine.spacy", create=True)
    def test_spacy_ner_model_load_error(self, mock_spacy):
        """Test SpacyNER initialization with model load error."""
        mock_spacy.load.side_effect = OSError("Model not found")

        with self.assertRaises(NLPEngineError) as context:
            SpacyNER("invalid_model")

        self.assertIn("Could not load spaCy model", str(context.exception))

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_extract_entities(self, mock_spacy):
        """Test entity extraction."""
        # Mock spaCy document and entities
        mock_ent1 = MagicMock()
        mock_ent1.text = "John Doe"
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 8

        mock_ent2 = MagicMock()
        mock_ent2.text = "New York"
        mock_ent2.label_ = "GPE"
        mock_ent2.start_char = 15
        mock_ent2.end_char = 23

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2]

        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        mock_spacy.load.return_value = mock_nlp

        ner = SpacyNER()
        entities = ner.extract_entities("John Doe lives in New York", {"PERSON", "GPE"})

        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].text, "John Doe")
        self.assertEqual(entities[0].label, "PERSON")
        self.assertEqual(entities[1].text, "New York")
        self.assertEqual(entities[1].label, "GPE")

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_extract_person_entities(self, mock_spacy):
        """Test person entity extraction with filtering."""
        # Mock entities with different lengths
        mock_ent1 = MagicMock()
        mock_ent1.text = "J"  # Too short
        mock_ent1.label_ = "PERSON"
        mock_ent1.start_char = 0
        mock_ent1.end_char = 1

        mock_ent2 = MagicMock()
        mock_ent2.text = "  John Doe  "  # Has whitespace
        mock_ent2.label_ = "PERSON"
        mock_ent2.start_char = 5
        mock_ent2.end_char = 16

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent1, mock_ent2]

        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        mock_spacy.load.return_value = mock_nlp

        ner = SpacyNER()
        entities = ner.extract_person_entities(
            "J and   John Doe   are here", min_length=2
        )

        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].text, "John Doe")  # Whitespace should be stripped

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_is_person_context(self, mock_spacy):
        """Test person context detection."""
        mock_nlp = MagicMock()
        mock_spacy.load.return_value = mock_nlp

        ner = SpacyNER()

        # Test text with person indicators
        text1 = "Mr. John Doe said that the project was successful."
        self.assertTrue(ner.is_person_context(text1, 4, 12, context_window=50))

        # Test text without person indicators
        text2 = "The company Apple Inc. reported strong earnings."
        self.assertFalse(ner.is_person_context(text2, 12, 22, context_window=50))

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_extract_entities_error(self, mock_spacy):
        """Test error handling during entity extraction."""
        mock_nlp = MagicMock()
        mock_nlp.side_effect = Exception("Processing error")
        mock_spacy.load.return_value = mock_nlp

        ner = SpacyNER()
        entities = ner.extract_entities("Test text")

        # Should return empty list on error
        self.assertEqual(entities, [])

    @patch("search_names.nlp_engine.spacy", create=True)
    def test_extract_entities_no_model(self, mock_spacy):
        """Test entity extraction when model not loaded."""
        mock_spacy.load.return_value = None

        ner = SpacyNER()
        ner.nlp = None  # Simulate failed model loading

        with self.assertRaises(NLPEngineError) as context:
            ner.extract_entities("Test text")

        self.assertIn("spaCy model not loaded", str(context.exception))


class TestSemanticSimilarity(unittest.TestCase):
    """Test SemanticSimilarity class."""

    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_semantic_similarity_init_success(self, mock_transformer):
        """Test successful SemanticSimilarity initialization."""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        similarity = SemanticSimilarity("test-model")

        self.assertEqual(similarity.model_name, "test-model")
        self.assertEqual(similarity.model, mock_model)
        mock_transformer.assert_called_once_with("test-model")


    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_semantic_similarity_model_load_error(self, mock_transformer):
        """Test initialization with model load error."""
        mock_transformer.side_effect = Exception("Model load error")

        with self.assertRaises(NLPEngineError) as context:
            SemanticSimilarity()

        self.assertIn(
            "Could not load sentence transformer model", str(context.exception)
        )

    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    @patch("search_names.nlp_engine.np", create=True)
    def test_compute_similarity(self, mock_np, mock_transformer):
        """Test similarity computation."""
        # Mock embeddings
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.8, 0.6, 0.0]
        mock_model = MagicMock()
        mock_model.encode.return_value = [embedding1, embedding2]
        mock_transformer.return_value = mock_model

        # Mock numpy operations
        mock_np.dot.return_value = 0.8
        mock_np.linalg.norm.side_effect = [1.0, 1.0]

        similarity = SemanticSimilarity()
        score = similarity.compute_similarity("text1", "text2")

        self.assertEqual(score, 0.8)
        mock_model.encode.assert_called_once_with(["text1", "text2"])

    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_compute_similarity_error(self, mock_transformer):
        """Test error handling during similarity computation."""
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception("Encoding error")
        mock_transformer.return_value = mock_model

        similarity = SemanticSimilarity()
        score = similarity.compute_similarity("text1", "text2")

        # Should return 0.0 on error
        self.assertEqual(score, 0.0)

    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_find_similar_names(self, mock_transformer):
        """Test finding similar names."""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        similarity = SemanticSimilarity()

        # Mock compute_similarity method
        with patch.object(similarity, "compute_similarity") as mock_compute:
            mock_compute.side_effect = [0.9, 0.7, 0.6, 0.3]  # Decreasing similarity

            candidates = ["John Smith", "Jane Doe", "John Doe", "Bob Wilson"]
            similar = similarity.find_similar_names("John", candidates, threshold=0.6)

            # Should return names with similarity >= 0.6, sorted by score
            expected = [("John Smith", 0.9), ("Jane Doe", 0.7), ("John Doe", 0.6)]
            self.assertEqual(similar, expected)

    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_find_similar_names_no_model(self, mock_transformer):
        """Test finding similar names when model not loaded."""
        mock_transformer.return_value = None

        similarity = SemanticSimilarity()
        similarity.model = None  # Simulate failed model loading

        with self.assertRaises(NLPEngineError) as context:
            similarity.find_similar_names("John", ["Jane"])

        self.assertIn("Sentence transformer model not loaded", str(context.exception))


class TestEntityLinker(unittest.TestCase):
    """Test EntityLinker class."""

    def setUp(self):
        """Set up test data."""
        self.knowledge_base = {
            "John Smith": {
                "id": "person_1",
                "aliases": ["J. Smith", "Johnny Smith"],
                "occupation": "Engineer",
            },
            "Jane Doe": {
                "id": "person_2",
                "aliases": ["J. Doe"],
                "occupation": "Doctor",
            },
        }

        self.mock_semantic = MagicMock()

    def test_entity_linker_init(self):
        """Test EntityLinker initialization."""
        linker = EntityLinker(self.knowledge_base, self.mock_semantic)

        self.assertEqual(linker.knowledge_base, self.knowledge_base)
        self.assertEqual(linker.semantic_model, self.mock_semantic)

        # Check indices were created
        self.assertIn("John Smith", linker.exact_match_index)
        self.assertIn("J. Smith", linker.exact_match_index)
        self.assertIn("john smith", linker.normalized_index)

    def test_normalize_name(self):
        """Test name normalization."""
        linker = EntityLinker(self.knowledge_base)

        normalized = linker._normalize_name("John O'Connor-Smith Jr.")
        self.assertEqual(normalized, "john oconnorsmith jr")

    def test_link_entity_exact_match(self):
        """Test entity linking with exact match."""
        linker = EntityLinker(self.knowledge_base)

        mention = EntityMention(text="John Smith", label="PERSON", start=0, end=10)

        result = linker.link_entity(mention)

        self.assertEqual(result.linked_entity_id, "John Smith")
        self.assertEqual(result.linked_entity_name, "John Smith")
        self.assertEqual(result.confidence, 1.0)

    def test_link_entity_alias_match(self):
        """Test entity linking with alias match."""
        linker = EntityLinker(self.knowledge_base)

        mention = EntityMention(text="J. Smith", label="PERSON", start=0, end=8)

        result = linker.link_entity(mention)

        self.assertEqual(result.linked_entity_id, "John Smith")
        self.assertEqual(result.confidence, 1.0)

    def test_link_entity_normalized_match(self):
        """Test entity linking with normalized match."""
        linker = EntityLinker(self.knowledge_base)

        mention = EntityMention(text="JOHN SMITH", label="PERSON", start=0, end=10)

        result = linker.link_entity(mention)

        self.assertEqual(result.linked_entity_id, "John Smith")
        self.assertEqual(result.confidence, 0.9)

    def test_link_entity_semantic_match(self):
        """Test entity linking with semantic similarity."""
        self.mock_semantic.find_similar_names.return_value = [
            ("John Smith", 0.85),
            ("Jane Doe", 0.75),
        ]

        linker = EntityLinker(self.knowledge_base, self.mock_semantic)

        mention = EntityMention(
            text="Jon Smith",  # Similar but not exact
            label="PERSON",
            start=0,
            end=9,
        )

        result = linker.link_entity(mention, similarity_threshold=0.8)

        self.assertEqual(result.linked_entity_id, "John Smith")
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(len(result.alternative_entities), 1)
        self.assertEqual(result.alternative_entities[0]["entity_name"], "Jane Doe")

    def test_link_entity_no_match(self):
        """Test entity linking when no match found."""
        linker = EntityLinker(self.knowledge_base)

        mention = EntityMention(text="Unknown Person", label="PERSON", start=0, end=14)

        result = linker.link_entity(mention)

        self.assertIsNone(result.linked_entity_id)
        self.assertIsNone(result.linked_entity_name)
        self.assertEqual(result.confidence, 0.0)


class TestNLPEngine(unittest.TestCase):
    """Test main NLPEngine class."""

    def setUp(self):
        """Set up test data."""
        self.sample_kb = {"John Smith": {"id": "1"}, "Jane Doe": {"id": "2"}}

    @patch("search_names.nlp_engine.SpacyNER")
    @patch("search_names.nlp_engine.SemanticSimilarity")
    @patch("search_names.nlp_engine.EntityLinker")
    def test_nlp_engine_init_all_components(
        self, mock_linker, mock_similarity, mock_ner
    ):
        """Test NLP engine initialization with all components."""
        mock_ner_instance = MagicMock()
        mock_similarity_instance = MagicMock()
        mock_linker_instance = MagicMock()

        mock_ner.return_value = mock_ner_instance
        mock_similarity.return_value = mock_similarity_instance
        mock_linker.return_value = mock_linker_instance

        engine = NLPEngine(
            knowledge_base=self.sample_kb,
            enable_ner=True,
            enable_similarity=True,
            enable_linking=True,
        )

        self.assertEqual(engine.spacy_ner, mock_ner_instance)
        self.assertEqual(engine.semantic_similarity, mock_similarity_instance)
        self.assertEqual(engine.entity_linker, mock_linker_instance)


    @patch("search_names.nlp_engine.SpacyNER")
    def test_nlp_engine_init_with_errors(self, mock_ner):
        """Test NLP engine initialization handling component errors."""
        mock_ner.side_effect = NLPEngineError("spaCy initialization error")

        # Should not raise exception, just log warning
        engine = NLPEngine(enable_ner=True)

        self.assertIsNone(engine.spacy_ner)

    @patch("search_names.nlp_engine.SpacyNER")
    def test_process_text_with_entities(self, mock_ner):
        """Test text processing with entity extraction."""
        mock_entity = EntityMention(text="John Doe", label="PERSON", start=0, end=8)

        mock_ner_instance = MagicMock()
        mock_ner_instance.extract_person_entities.return_value = [mock_entity]
        mock_ner.return_value = mock_ner_instance

        engine = NLPEngine(enable_ner=True)
        results = engine.process_text("John Doe is here", extract_entities=True)

        self.assertEqual(len(results["entities"]), 1)
        self.assertEqual(len(results["person_entities"]), 1)
        self.assertEqual(results["entities"][0].text, "John Doe")

    def test_process_text_no_ner(self):
        """Test text processing without NER component."""
        engine = NLPEngine(enable_ner=False)
        results = engine.process_text("John Doe is here", extract_entities=True)

        self.assertEqual(results["entities"], [])
        self.assertEqual(results["person_entities"], [])

    @patch("search_names.nlp_engine.SpacyNER")
    def test_enhance_name_search(self, mock_ner):
        """Test enhanced name search functionality."""
        mock_ner_instance = MagicMock()
        mock_ner_instance.extract_person_entities.return_value = []
        mock_ner_instance.is_person_context.return_value = True
        mock_ner.return_value = mock_ner_instance

        engine = NLPEngine(enable_ner=True)

        text = "John Doe said that Jane Smith was present."
        search_names = ["John Doe", "Jane Smith"]

        results = engine.enhance_name_search(search_names, text)

        self.assertEqual(len(results), 2)

        # Check first result (John Doe)
        john_result = results[0]
        self.assertEqual(john_result["search_name"], "John Doe")
        self.assertEqual(john_result["match_count"], 1)
        self.assertEqual(john_result["person_matches"], 1)

        # Check match details
        match = john_result["matches"][0]
        self.assertEqual(match["text"], "John Doe")
        self.assertEqual(match["start"], 0)
        self.assertEqual(match["end"], 8)
        self.assertTrue(match["is_person_context"])

    def test_enhance_name_search_no_matches(self):
        """Test enhanced name search with no matches."""
        engine = NLPEngine(enable_ner=False)

        text = "The weather is nice today."
        search_names = ["John Doe"]

        results = engine.enhance_name_search(search_names, text)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["match_count"], 0)
        self.assertEqual(results[0]["matches"], [])


class TestIntegration(unittest.TestCase):
    """Integration tests for NLP components."""

    @patch("search_names.nlp_engine.spacy", create=True)
    @patch("search_names.nlp_engine.SentenceTransformer", create=True)
    def test_full_pipeline(self, mock_transformer, mock_spacy):
        """Test full NLP pipeline integration."""
        # Mock spaCy
        mock_ent = MagicMock()
        mock_ent.text = "John Smith"
        mock_ent.label_ = "PERSON"
        mock_ent.start_char = 0
        mock_ent.end_char = 10

        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]

        mock_nlp = MagicMock()
        mock_nlp.return_value = mock_doc
        mock_spacy.load.return_value = mock_nlp

        # Mock sentence transformers
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        knowledge_base = {
            "John Smith": {"id": "person_1"},
            "Jane Doe": {"id": "person_2"},
        }

        engine = NLPEngine(
            knowledge_base=knowledge_base,
            enable_ner=True,
            enable_similarity=True,
            enable_linking=True,
        )

        # Process text with entity linking
        results = engine.process_text(
            "John Smith is a software engineer.",
            extract_entities=True,
            link_entities=True,
        )

        # Verify results structure
        self.assertIn("entities", results)
        self.assertIn("person_entities", results)
        self.assertIn("linked_entities", results)
        self.assertGreater(len(results["entities"]), 0)


if __name__ == "__main__":
    unittest.main()
