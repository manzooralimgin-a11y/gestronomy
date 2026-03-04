from enum import Enum


class AgentName(str, Enum):
    finance = "finance"
    inventory = "inventory"
    labor = "labor"
    quality = "quality"
    guest = "guest"
    supply = "supply"
    energy = "energy"
    marketing = "marketing"
    meta = "meta"


class AutonomyLevel(str, Enum):
    full = "full"
    semi = "semi"
    human_required = "human_required"


class AlertSeverity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class OrderChannel(str, Enum):
    dine_in = "dine_in"
    takeout = "takeout"
    delivery = "delivery"
    drive_thru = "drive_thru"
    app = "app"


class ShiftRole(str, Enum):
    server = "server"
    cook = "cook"
    host = "host"
    bartender = "bartender"
    dishwasher = "dishwasher"
    manager = "manager"
    prep_cook = "prep_cook"
