from fastapi import APIRouter
from app.api.v1.endpoints import auth, transactions, tax_rules, profile, receipts, dashboard, agent

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["User Profile"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(tax_rules.router, prefix="/tax-rules", tags=["Tax Rules"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["Receipt Processing"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(agent.router, prefix="/agent", tags=["AI Agent"])
