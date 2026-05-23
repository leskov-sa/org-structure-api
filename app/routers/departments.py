from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/departments", tags=["departments"])

def get_subtree(db: Session, dept_id: int, depth: int, include_employees: bool):
    """Рекурсивное получение поддерева"""
    if depth <= 0:
        return None
    
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not dept:
        return None
    
    employees = []
    if include_employees:
        employees = db.query(models.Employee).filter(
            models.Employee.department_id == dept_id
        ).order_by(models.Employee.created_at).all()
    
    children = []
    if depth > 1:
        child_depts = db.query(models.Department).filter(models.Department.parent_id == dept_id).all()
        for child in child_depts:
            child_data = get_subtree(db, child.id, depth - 1, include_employees)
            if child_data:
                children.append(child_data)
    
    return {
        "id": dept.id,
        "name": dept.name,
        "parent_id": dept.parent_id,
        "created_at": dept.created_at,
        "employees": employees,
        "children": children
    }

@router.post("/", response_model=schemas.DepartmentOut)
def create_department(dep: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Department).filter(
        models.Department.parent_id == dep.parent_id,
        models.Department.name == dep.name.strip()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Name must be unique within parent")
    
    new_dep = models.Department(
        name=dep.name.strip(),
        parent_id=dep.parent_id
    )
    db.add(new_dep)
    db.commit()
    db.refresh(new_dep)
    return new_dep

@router.get("/{id}")
def get_department(
    id: int,
    depth: int = Query(1, ge=1, le=5),
    include_employees: bool = Query(True),
    db: Session = Depends(get_db)
):
    department = db.query(models.Department).filter(models.Department.id == id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return get_subtree(db, id, depth, include_employees)

@router.patch("/{id}", response_model=schemas.DepartmentOut)
def update_department(id: int, dep_update: schemas.DepartmentUpdate, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if dep_update.name:
        department.name = dep_update.name.strip()
    
    if dep_update.parent_id is not None:
        if dep_update.parent_id == id:
            raise HTTPException(status_code=400, detail="Cannot set parent to itself")
        
        # Проверка на цикл
        current_id = dep_update.parent_id
        visited = set()
        while current_id and current_id not in visited:
            if current_id == id:
                raise HTTPException(status_code=409, detail="Cannot create cycle")
            visited.add(current_id)
            parent = db.query(models.Department).filter(models.Department.id == current_id).first()
            current_id = parent.parent_id if parent else None
        
        department.parent_id = dep_update.parent_id
    
    db.commit()
    db.refresh(department)
    return department

@router.delete("/{id}")
def delete_department(
    id: int,
    mode: str = Query(...),
    reassign_to_department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    department = db.query(models.Department).filter(models.Department.id == id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if mode == "cascade":
        db.delete(department)
        db.commit()
        return Response(status_code=204)
    
    elif mode == "reassign":
        if not reassign_to_department_id:
            raise HTTPException(status_code=400, detail="reassign_to_department_id required")
        target = db.query(models.Department).filter(models.Department.id == reassign_to_department_id).first()
        if not target:
            raise HTTPException(status_code=404, detail="Target department not found")
        
        db.query(models.Employee).filter(models.Employee.department_id == id).update(
            {"department_id": reassign_to_department_id}
        )
        db.delete(department)
        db.commit()
        return Response(status_code=204)
    
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'cascade' or 'reassign'")
