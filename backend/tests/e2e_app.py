"""Browser-only provider double. Production app.main never imports this module."""

from app.domain.extraction import ExtractionOutput
from app.main import create_app


class BrowserExtractor:
    provider = "test"
    model = "browser-fixture"
    configured = True

    def extract(self, payload):
        # The intentionally wrong draft gives the browser test something to correct.
        return ExtractionOutput(
            preferences=[
                {
                    "source_id": source["source_id"],
                    "participant_id": source["participant_id"],
                    "statement": "I prefer a mobile-only project.",
                    "kind": "desire",
                    "quote": source["text"],
                    "uncertainty_note": "Test fixture; review the wording.",
                }
                for source in payload["new_sources"]
            ]
        ), {"total_tokens": 0}


app = create_app(extractor=BrowserExtractor())
