from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json
import os

app = FastAPI()

DATA_FILE = "patients.json"


# ---------------------------
# Patient Model
# ---------------------------
class Patient(BaseModel):
    name: Annotated[str, Field(..., description="Name of patient")]
    city: Annotated[str, Field(..., description="City of patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="Gender of patient")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of patient")]
    height: Annotated[float, Field(..., gt=0, description="Height in meters")]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kilograms")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "underweight"
        elif self.bmi < 25:
            return "normal"
        elif self.bmi < 30:
            return "overweight"
        else:
            return "obese"


# ---------------------------
# File Handling
# ---------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------
# Routes
# ---------------------------
@app.get("/")
def hello():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {"message": "A fully functional API to manage your patient records"}


@app.get("/view")
def view():
    data = load_data()
    return data


@app.get("/patient/{patient_id}")
def view_patient(
    patient_id: str = Path(..., description="ID of the patient in DB", example="P001")
):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")


@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort by height, weight, or bmi"),
    order: str = Query("asc", description="Sort in asc or desc order"),
):
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid field. Choose from {valid_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")

    data = load_data()
    patients = list(data.values())

    reverse = True if order == "desc" else False
    sorted_data = sorted(patients, key=lambda x: x.get(sort_by, 0), reverse=reverse)

    return sorted_data


@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()

    # Generate new patient ID
    new_id = f"P{len(data) + 1:03d}"

    # Save patient
    data[new_id] = patient.model_dump()

    save_data(data)

    return JSONResponse(
        status_code=201, content={"message": "Patient created successfully", "id": new_id}
    )


@app.delete("/delete/{patient_id}")
def delete_patient(
    patient_id: str = Path(..., description="ID of the patient to delete", example="P001")
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Remove the patient
    deleted_patient = data.pop(patient_id)

    save_data(data)

    return {"message": f"Patient {patient_id} deleted successfully", "deleted_data": deleted_patient}

