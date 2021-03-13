from distrobuild.settings import settings


def base() -> str:
    return f"dist-{settings.tag_prefix}{settings.version}"


def compose() -> str:
    return f"{base()}-compose"


def testing() -> str:
    return f"{base()}-testing"


def scratch() -> str:
    return "__scratch"
