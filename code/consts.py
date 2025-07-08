# Roles
from enum import Enum


class ROLE(Enum):
    HUMAN = "human"
    AI = "AI"
    SYSTEM = "system"


# NODES
MANAGER = "manager"
LLM_TAGS_GENERATOR = "llm_tags_generator"
SPACY_TAGS_GENERATOR = "spacy_tags_generator"
GAZETTEER_TAGS_GENERATOR = "gazetteer_tags_generator"
TAG_TYPE_ASSIGNER = "tag_type_assigner"
TAGS_AGGREGATOR = "tags_aggregator"
TAGS_SELECTOR = "tags_selector"
TAGS_GENERATOR = "tags_generator"
TLDR_GENERATOR = "tldr_generator"
TITLE_GENERATOR = "title_generator"
REFERENCES_GENERATOR = "references_generator"
REFERENCES_SELECTOR = "references_selector"
REVIEWER = "reviewer"

# STATE KEYS
INPUT_TEXT = "input_text"
TITLE = "title"
TLDR = "tldr"
LLM_TAGS = "llm_tags"
SPACY_TAGS = "spacy_tags"
GAZETTEER_TAGS = "gazetteer_tags"
CANDIDATE_TAGS = "candidate_tags"
SELECTED_TAGS = "selected_tags"
MANAGER_BRIEF = "manager_brief"
REFERENCE_SEARCH_QUERIES = "reference_search_queries"
CANDIDATE_REFERENCES = "candidate_references"
SELECTED_REFERENCES = "selected_references"

MANAGER_MESSAGES = "manager_messages"
TITLE_GEN_MESSAGES = "title_gen_messages"
LLM_TAGS_GEN_MESSAGES = "llm_tags_gen_messages"
TAG_TYPE_ASSIGNER_MESSAGES = "tag_type_assigner_messages"
TAGS_SELECTOR_MESSAGES = "tags_selector_messages"
TLDR_GEN_MESSAGES = "tldr_gen_messages"
REFERENCES_GEN_MESSAGES = "references_gen_messages"
REFERENCES_SELECTOR_MESSAGES = "references_selector_messages"
REVIEWER_MESSAGES = "reviewer_messages"

MAX_REVISIONS = "max_revisions"
REVISION_ROUND = "revision_round"
NEEDS_REVISION = "needs_revision"
TLDR_FEEDBACK = "tldr_feedback"
TITLE_FEEDBACK = "title_feedback"
REFERENCES_FEEDBACK = "references_feedback"
TLDR_APPROVED = "tldr_approved"
TITLE_APPROVED = "title_approved"
REFERENCES_APPROVED = "references_approved"
