from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated
import pickle
import pandas as pd

#import the ml modeel
with open('model.pkl','rb') as f:
    model=pickle.load(f)

app = FastAPI()
tier_1 = ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Chennai", "Hyderabad", "Pune"]
tier_2 = ["Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Surat", "Nagpur", "Indore"]
tier_3 = ["Patna", "Ranchi", "Bhubaneswar", "Mysore", "Coimbatore", "Varanasi", "Guwahati"]

#pydantic model to validate incoming data
class UserInput(BaseModel):

    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the user')]
    weight:Annotated[float,Field(...,gt=0,lt=120,description='Weight of the user')]
    height:Annotated[float,Field(...,gt=0,lt=120,description='Height of the user')]
    city:Annotated[str,Field(...,description='The city that user belongs to')]
    income_lpa:Annotated[float,Field(...,gt=0,description='income of the person')]
    occupation:Annotated[Literal['retired','freelancer','student','government_job','business_owner','unemployed','private_job'],Field(...,gt=0,lt=120,description='Type of job')]
    smoker:Annotated[bool,Field(...,description='smoker or not')]


    @computed_field
    @property
    def bmi(self)->float:
        return self.weight/(self.height**2)
    
    @computed_field
    @property
    def lifestyle_rish(self)->str:
        if self.smoker and self.bmi > 30:
            return "high"
        if self.smoker and self.bmi >27:
             return " medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self)-> int:
         if self.age < 25:
              return "young"
         elif self.age <45:
               return "adult"
         elif self.age <60:
              return "middle_aged"
         return "senior"   
    
    
    @computed_field
    @property
    def city_tier(self)->str:
       if self.city in tier_1:
        return "city_tier_1"
       elif self.city in tier_2:
        return "city_tier_2"
       elif self.city in tier_3:
        return "city_tier_3"
       else: 
        return "other"
       
@app.post('/predict')
def  predict_premium(data: UserInput):

    input_df=pd.DataFrame(
        [
            {
                'bmi':data.bmi,
                'age_group':data.age_group,
                'lifestyle_risk':data.lifestyle_risk,
                'city_tier':data.city_tier,
                'income_lpa':data.income_lpa,
                'occupation':data.occupation

            }
        ]
    ) 

    prediction=model.predict(input_df)[0]

    return JSONResponse(status_code=200,content={'predicted_category':prediction})
       


        