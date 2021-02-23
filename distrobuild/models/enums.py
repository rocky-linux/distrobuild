from enum import Enum


class Repo(str, Enum):
    BASEOS = "BASEOS"
    APPSTREAM = "APPSTREAM"
    POWERTOOLS = "POWERTOOLS"


class BuildStatus(str, Enum):
    QUEUED = "QUEUED"
    BUILDING = "BUILDING"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    CANCELLED = "CANCELLED"
