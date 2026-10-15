import os


def database_url() -> str:
    return os.environ.get("FEEDBACKFORM_DATABASE_URL", "sqlite:///./data/feedbackform.db")
