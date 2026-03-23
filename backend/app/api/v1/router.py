from fastapi import APIRouter

from app.api.v1 import ai, applications, auth, cvs, jobs, users

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(cvs.router)
router.include_router(jobs.router)
router.include_router(applications.router)
router.include_router(ai.router)
