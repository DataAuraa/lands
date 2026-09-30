"""
Simulation Scenario API Router.
Controls the 12-step live disaster demonstration scenario.
"""
from fastapi import APIRouter, HTTPException
from simulation.risk_generator import scenario_simulator

router = APIRouter(prefix="/simulation", tags=["Simulation Engine"])


@router.get("/steps")
def get_all_scenario_steps():
    """Retrieve all 12 steps of the primary project demonstration scenario."""
    return scenario_simulator.get_all_steps()


@router.get("/step/{step_number}")
def get_scenario_step(step_number: int):
    """Retrieve details for a specific demonstration phase (1 through 12)."""
    if step_number < 1 or step_number > 12:
        raise HTTPException(status_code=400, detail="Step number must be between 1 and 12")
    return scenario_simulator.get_step(step_number)
