"""Permission Layer — derive the caller's scope (role + company boundary, ABAC-style). Plugs into
vkp-jwt-rbac when the service is fronted by it; here it reads role/companyId from the request."""


def scope(ctx: dict) -> dict:
    role = (ctx.get("role") or "USER").upper()
    company_id = ctx.get("companyId")
    return {"role": role,
            "companyBoundary": None if role == "ADMIN" else company_id,
            "policy": "admin:all" if role == "ADMIN" else "customer:company-scoped"}
