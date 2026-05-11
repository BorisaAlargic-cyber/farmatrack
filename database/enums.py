"""Enumerations used across FarmaTrack models."""

import enum


class PigCategory(str, enum.Enum):
    PIGLET = "piglet"
    FINISHER = "finisher"
    GILT = "gilt"
    SOW = "sow"


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    TREATED = "treated"
    QUARANTINED = "quarantined"


class ScanSource(str, enum.Enum):
    EAR_TAG = "ear_tag"
    MANUAL = "manual"
