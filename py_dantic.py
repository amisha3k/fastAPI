from pydantic import BaseModel,EmailStr,AnyUrl,Field
from typing import List, Dict, optional,Annotated

class Patient(BaseModel):

    name: Annotated[str, Field(max_length=50)]
    age : int =Field(gt=0,lt=120)
    weight: float =Field(gt=0)
    linkedin_url: Anyurl
    married : bool 
    allergies: optional[List[str]]  =None #optional
    contact : Dict[str,str]

    # @feild_validator('email')
    # @classmethod
    # def email_valid ator:
    

def insert_patient_data(patient: Patient):
    print(patient.name)
    print(patient.age)

patient_info={'name':'nitish','age':30,'weight': 60.55,'married': True,}
patient1=Patient(**patient_info)

insert_patient_data(patient1)