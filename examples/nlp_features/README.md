# NLP Features Examples

This directory demonstrates the advanced NLP capabilities of the modernized search_names package.

## Key Features

### Named Entity Recognition (NER)
- spaCy-based entity extraction
- Person entity identification
- Context analysis for mentions
- Configurable entity types

### Semantic Similarity
- Sentence transformer-based similarity matching
- Fuzzy name matching with confidence scores
- Similar name discovery
- Configurable similarity thresholds

### Entity Linking
- Knowledge base integration
- Exact and semantic matching
- Alternative entity suggestions
- Confidence-based ranking

## Files

### `nlp_demo.py`
Main demonstration script showing:
- Named entity recognition with spaCy
- Semantic similarity calculations
- Entity linking to knowledge bases
- Complete NLP pipeline integration
- Enhanced name search with context

### Generated Files
- `sample_knowledge_base.json`: Example entity knowledge base
- `nlp_config.json`: NLP configuration template

## Usage Examples

### Basic NER
```python
from search_names.nlp_engine import SpacyNER

ner = SpacyNER(model_name="en_core_web_sm")
entities = ner.extract_person_entities(text)
```

### Semantic Similarity
```python
from search_names.nlp_engine import SemanticSimilarity

similarity = SemanticSimilarity()
score = similarity.compute_similarity("Joe Biden", "President Biden")
```

### Entity Linking
```python
from search_names.nlp_engine import EntityLinker

linker = EntityLinker(knowledge_base, similarity_model)
result = linker.link_entity(mention)
```

### Full Pipeline
```python
from search_names.nlp_engine import NLPEngine

nlp = NLPEngine(enable_ner=True, enable_linking=True, knowledge_base=kb)
results = nlp.process_text(text, extract_entities=True, link_entities=True)
```

## Optional Dependencies

```bash
# For NLP features
pip install 'search_names[nlp]'

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Configuration

The system supports flexible configuration:
- spaCy model selection
- Entity type filtering
- Similarity thresholds
- Context window sizes
- Knowledge base integration

## Graceful Degradation

All NLP features gracefully degrade when optional dependencies are unavailable, providing helpful error messages and installation instructions.
