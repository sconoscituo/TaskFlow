from enum import Enum
class PlanType(str, Enum):
    FREE = "free"; PRO = "pro"  # 월 9,900원; TEAM = "team"  # 월 29,900원
PLAN_LIMITS = {
    PlanType.FREE: {"projects": 3,  "members": 1,  "ai_decompose": False},
    PlanType.PRO:  {"projects": 20, "members": 5,  "ai_decompose": True},
    PlanType.TEAM: {"projects": 999,"members": 50, "ai_decompose": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 9900, PlanType.TEAM: 29900}
