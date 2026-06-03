from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies.llm import get_llm_provider
from backend.api.schemas.leveling import GenerateLevelingRequest, LevelingPlanResponse
from backend.infrastructure.repository.leveling_repository import get_leveling_plan
from backend.llm.base.interface import ILLMProvider
from backend.services.leveling_service import generate_leveling_plan

router = APIRouter(prefix="/leveling", tags=["Leveling"])


@router.post("/generate", response_model=LevelingPlanResponse, status_code=201)
async def trigger_leveling_generation(
    request: GenerateLevelingRequest,
    llm: ILLMProvider = Depends(get_llm_provider),
):
    try:
        plan = await generate_leveling_plan(
            session_id=request.session_id,
            readiness_id=request.readiness_id,
            llm=llm,
        )
        return plan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração do plano: {str(e)}") from e


@router.get("/plan/{plan_id}", response_model=LevelingPlanResponse)
async def get_plan(plan_id: UUID):
    plan = await get_leveling_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de nivelamento não encontrado.")
    return plan
