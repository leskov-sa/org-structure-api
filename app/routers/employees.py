from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/departments/{department_id}/employees", tags=["employees"])

@router.post("/", response_model=schemas.EmployeeOut)
def create_employee(
    department_id: int,
    emp: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    new_emp = models.Employee(
        department_id=department_id,
        full_name=emp.full_name.strip(),
        position=emp.position.strip(),
        hired_at=emp.hired_at
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp
