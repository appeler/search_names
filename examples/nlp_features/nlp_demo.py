#!/usr/bin/env python3
"""
NLP Features Demo

This example demonstrates the NLP capabilities of the modernized search_names package,
including named entity recognition (NER), semantic similarity, and entity linking.

Key Features Demonstrated:
- spaCy-based Named Entity Recognition for person detection
- Semantic similarity matching using sentence transformers
- Entity linking to knowledge bases
- Context analysis for mentions
- Enhanced name search with NLP context
"""

import json
from pathlib import Path

from search_names.logging_config import get_logger, setup_logging

# Set up logging
setup_logging()
logger = get_logger("nlp_demo")

# Optional imports with graceful degradation
try:
    from search_names.models import EntityMention
    from search_names.nlp_engine import (
        EntityLinker,
        NLPEngine,
        NLPEngineError,
        SemanticSimilarity,
        SpacyNER,
    )

    HAS_NLP = True
except ImportError as e:
    logger.warning(f"NLP features not available: {e}")
    HAS_NLP = False


def demo_named_entity_recognition():
    """Demonstrate spaCy-based Named Entity Recognition."""
    print("\n" + "=" * 60)
    print("NAMED ENTITY RECOGNITION (NER)")
    print("=" * 60)

    if not HAS_NLP:
        print("❌ NLP features not available. Install with:")
        print("pip install 'search_names[nlp]'")
        print("python -m spacy download en_core_web_sm")
        return

    # Sample text with various types of mentions
    sample_text = """
    President Joe Biden met with Senator Elizabeth Warren and Representative
    Alexandria Ocasio-Cortez yesterday. The meeting also included Dr. Anthony Fauci
    and Microsoft CEO Satya Nadella. They discussed policies with the Federal Reserve
    and the Supreme Court's recent decisions.
    """

    try:
        # Initialize spaCy NER
        ner = SpacyNER(model_name="en_core_web_sm")

        print("Extracting entities from sample text:")
        print("-" * 50)
        print("Text:", sample_text.strip())
        print()

        # Extract all entities
        entities = ner.extract_entities(sample_text, {"PERSON", "ORG", "GPE"})

        print(f"Found {len(entities)} entities:")
        for entity in entities:
            print(
                f"  '{entity.text}' ({entity.label}) at positions {entity.start}-{entity.end}"
            )

        print()

        # Extract only person entities
        person_entities = ner.extract_person_entities(sample_text)
        print(f"Found {len(person_entities)} person entities:")
        for entity in person_entities:
            print(f"  '{entity.text}' at positions {entity.start}-{entity.end}")

            # Check context
            is_person_context = ner.is_person_context(
                sample_text, entity.start, entity.end
            )
            print(f"    Person context: {is_person_context}")

    except NLPEngineError as e:
        print(f"❌ NLP Error: {e}")
        print("Make sure spaCy and the English model are installed:")
        print("pip install spacy")
        print("python -m spacy download en_core_web_sm")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_semantic_similarity():
    """Demonstrate semantic similarity matching."""
    print("\n" + "=" * 60)
    print("SEMANTIC SIMILARITY")
    print("=" * 60)

    if not HAS_NLP:
        print("❌ NLP features not available.")
        return

    try:
        # Initialize semantic similarity
        similarity = SemanticSimilarity(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Test similarity between names
        name_pairs = [
            ("John Smith", "Johnny Smith"),
            ("Elizabeth Warren", "Liz Warren"),
            ("Barack Obama", "President Obama"),
            ("Dr. Anthony Fauci", "Anthony Fauci"),
            ("Joe Biden", "Donald Trump"),  # Should be low similarity
        ]

        print("Computing similarity between name pairs:")
        print("-" * 50)

        for name1, name2 in name_pairs:
            sim_score = similarity.compute_similarity(name1, name2)
            print(f"'{name1}' <-> '{name2}': {sim_score:.3f}")

        print()

        # Find similar names in a list
        target_name = "Joe Biden"
        candidates = [
            "Joseph Biden",
            "President Biden",
            "Former VP Biden",
            "Donald Trump",
            "Barack Obama",
            "Kamala Harris",
            "Biden",
            "Joseph R. Biden Jr.",
        ]

        print(f"Finding names similar to '{target_name}':")
        similar_names = similarity.find_similar_names(
            target_name, candidates, threshold=0.3
        )

        for name, score in similar_names:
            print(f"  '{name}': {score:.3f}")

    except NLPEngineError as e:
        print(f"❌ NLP Error: {e}")
        print("Install sentence-transformers with:")
        print("pip install sentence-transformers")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_entity_linking():
    """Demonstrate entity linking to knowledge bases."""
    print("\n" + "=" * 60)
    print("ENTITY LINKING")
    print("=" * 60)

    if not HAS_NLP:
        print("❌ NLP features not available.")
        return

    # Create a simple knowledge base
    knowledge_base = {
        "Joseph R. Biden Jr.": {
            "title": "46th President of the United States",
            "aliases": ["Joe Biden", "President Biden", "Joseph Biden"],
            "party": "Democratic",
            "born": "1942",
        },
        "Elizabeth Ann Warren": {
            "title": "U.S. Senator from Massachusetts",
            "aliases": ["Elizabeth Warren", "Liz Warren", "Senator Warren"],
            "party": "Democratic",
            "born": "1949",
        },
        "Alexandria Ocasio-Cortez": {
            "title": "U.S. Representative from New York",
            "aliases": ["AOC", "Representative Ocasio-Cortez"],
            "party": "Democratic",
            "born": "1989",
        },
    }

    try:
        # Initialize semantic similarity for better linking
        try:
            similarity = SemanticSimilarity()
            linker = EntityLinker(knowledge_base, similarity)
            print("Using semantic similarity for entity linking")
        except Exception:
            linker = EntityLinker(knowledge_base)
            print("Using exact matching for entity linking")

        # Test entity mentions to link
        test_mentions = [
            EntityMention(text="Joe Biden", label="PERSON", start=0, end=9),
            EntityMention(text="Liz Warren", label="PERSON", start=0, end=10),
            EntityMention(text="AOC", label="PERSON", start=0, end=3),
            EntityMention(text="President Biden", label="PERSON", start=0, end=15),
            EntityMention(text="Unknown Person", label="PERSON", start=0, end=14),
        ]

        print("Linking entities to knowledge base:")
        print("-" * 50)

        for mention in test_mentions:
            result = linker.link_entity(mention, similarity_threshold=0.7)

            print(f"Mention: '{mention.text}'")
            if result.linked_entity_id:
                print(f"  Linked to: {result.linked_entity_name}")
                print(f"  Confidence: {result.confidence:.3f}")

                # Show entity info
                entity_info = knowledge_base.get(result.linked_entity_id, {})
                if entity_info:
                    print(f"  Title: {entity_info.get('title', 'Unknown')}")
                    print(f"  Party: {entity_info.get('party', 'Unknown')}")

                if result.alternative_entities:
                    print(
                        f"  Alternatives: {len(result.alternative_entities)} other candidates"
                    )
            else:
                print("  No entity linked")
            print()

    except Exception as e:
        print(f"❌ Error in entity linking: {e}")


def demo_full_nlp_pipeline():
    """Demonstrate the complete NLP pipeline."""
    print("\n" + "=" * 60)
    print("COMPLETE NLP PIPELINE")
    print("=" * 60)

    if not HAS_NLP:
        print("❌ NLP features not available.")
        return

    try:
        # Sample knowledge base
        kb = {
            "Dr. Anthony Fauci": {
                "title": "Director of NIAID",
                "aliases": ["Anthony Fauci", "Dr. Fauci"],
                "field": "Medicine",
            }
        }

        # Initialize full NLP engine
        nlp_engine = NLPEngine(
            enable_ner=True,
            enable_similarity=True,
            enable_linking=True,
            knowledge_base=kb,
        )

        text = "Dr. Anthony Fauci spoke about public health. Anthony Fauci has expertise in immunology."

        print("Processing text with full NLP pipeline:")
        print(f"Text: {text}")
        print("-" * 50)

        # Process with full pipeline
        results = nlp_engine.process_text(
            text, extract_entities=True, link_entities=True
        )

        print(f"Entities found: {len(results['entities'])}")
        for entity in results["entities"]:
            print(f"  '{entity.text}' ({entity.label})")

        print(f"\nPerson entities: {len(results['person_entities'])}")
        for entity in results["person_entities"]:
            print(f"  '{entity.text}'")

        print(f"\nLinked entities: {len(results['linked_entities'])}")
        for link_result in results["linked_entities"]:
            print(
                f"  '{link_result.mention.text}' -> {link_result.linked_entity_name or 'No match'}"
            )
            print(f"    Confidence: {link_result.confidence:.3f}")

    except Exception as e:
        print(f"❌ Error in NLP pipeline: {e}")


def demo_enhanced_name_search():
    """Demonstrate enhanced name search with NLP context."""
    print("\n" + "=" * 60)
    print("ENHANCED NAME SEARCH WITH NLP")
    print("=" * 60)

    if not HAS_NLP:
        print("❌ NLP features not available.")
        return

    try:
        # Create NLP engine for search enhancement
        nlp_engine = NLPEngine(enable_ner=True, enable_similarity=False)

        # Sample corpus
        text_corpus = """
        Senator Elizabeth Warren introduced the bill yesterday. Warren has been
        advocating for this policy for months. The Warren proposal received support
        from Representative Ocasio-Cortez. Elizabeth Warren's office confirmed the
        meeting. Warren Street in Boston was also mentioned in the discussion.
        """

        # Names to search for
        search_names = ["Elizabeth Warren", "Warren", "Ocasio-Cortez"]

        print("Enhancing name search with NLP context analysis:")
        print(f"Corpus: {text_corpus.strip()}")
        print(f"Searching for: {search_names}")
        print("-" * 50)

        # Use NLP-enhanced search
        enhanced_results = nlp_engine.enhance_name_search(
            search_names, text_corpus, context_window=50
        )

        for result in enhanced_results:
            search_name = result["search_name"]
            matches = result["matches"]
            person_matches = result["person_matches"]

            print(f"\nSearch term: '{search_name}'")
            print(f"Total matches: {result['match_count']}")
            print(f"Person context matches: {person_matches}")

            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                context = match["context"].strip()
                is_person = match["is_person_context"]
                print(
                    f"  Match {i + 1}: {is_person and '👤' or '📍'} {'Person' if is_person else 'Other'}"
                )
                print(f"    Context: '...{context}...'")

    except Exception as e:
        print(f"❌ Error in enhanced search: {e}")


def save_nlp_examples():
    """Save example configurations and results."""
    print("\n" + "=" * 60)
    print("SAVING NLP CONFIGURATION EXAMPLES")
    print("=" * 60)

    output_dir = Path("nlp_features")
    output_dir.mkdir(exist_ok=True)

    # Example knowledge base
    sample_kb = {
        "Political Figures": {
            "Joe Biden": {
                "full_name": "Joseph Robinette Biden Jr.",
                "title": "46th President of the United States",
                "aliases": ["President Biden", "Joseph Biden", "POTUS"],
                "party": "Democratic",
                "born": "1942-11-20",
            },
            "Elizabeth Warren": {
                "full_name": "Elizabeth Ann Warren",
                "title": "U.S. Senator from Massachusetts",
                "aliases": ["Liz Warren", "Senator Warren"],
                "party": "Democratic",
                "born": "1949-06-22",
            },
        }
    }

    # NLP configuration example
    nlp_config = {
        "nlp_settings": {
            "spacy_model": "en_core_web_sm",
            "similarity_model": "sentence-transformers/all-MiniLM-L6-v2",
            "entity_types": ["PERSON", "ORG", "GPE"],
            "similarity_threshold": 0.8,
            "context_window": 100,
        },
        "entity_linking": {
            "enable_semantic_matching": True,
            "min_confidence": 0.7,
            "max_alternatives": 5,
        },
    }

    # Save files
    files_to_save = [
        ("sample_knowledge_base.json", sample_kb),
        ("nlp_config.json", nlp_config),
    ]

    for filename, data in files_to_save:
        filepath = output_dir / filename
        try:
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")


def main():
    """Run all NLP demonstrations."""
    print("NLP Features Demo")
    print("=" * 80)
    print("This demo showcases the NLP capabilities of the modernized")
    print("search_names package for advanced entity recognition and linking.")

    # Check dependencies
    if not HAS_NLP:
        print("\n❌ NLP features are not available.")
        print("\nTo enable NLP features, install the optional dependencies:")
        print("pip install 'search_names[nlp]'")
        print("python -m spacy download en_core_web_sm")
        print("\nThis demo will show what would be possible with NLP features enabled.")

    # Run all demonstrations
    demo_named_entity_recognition()
    demo_semantic_similarity()
    demo_entity_linking()
    demo_full_nlp_pipeline()
    demo_enhanced_name_search()
    save_nlp_examples()

    print("\n" + "=" * 80)
    print("NLP Demo completed!")
    print("\nKey NLP capabilities:")
    print("- Named Entity Recognition (NER) with spaCy")
    print("- Semantic similarity matching with transformers")
    print("- Entity linking to knowledge bases")
    print("- Context-aware name search")
    print("- Graceful degradation when dependencies unavailable")
    print("=" * 80)


if __name__ == "__main__":
    main()
