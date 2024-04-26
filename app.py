from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, DateTime,exc
from datetime import date
import urllib.request
import json
import os
import ssl
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # replace with your database URI
db = SQLAlchemy(app)
api = Api(app)


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

def calculate_prediction(patient):
    data =  {
        "Inputs": {
            "data": [
            {
                "Sex": patient.sex,
                "Year.of.diagnosis": patient.year_of_diagnosis,
                "Race.recode..W..B..AI..API.": patient.race_recode_W_B_AI_API,
                "treatment": patient.treatment,
                "Year.of.follow.up.recode": patient.year_of_follow_up_recode,
                "Breast": patient.breast,
                "Endocrine": patient.endocrine,
                "Eye, and adnexa": patient.eye_and_adnexa,
                "Gastrointestinal": patient.gastrointestinal,
                "Gynecological": patient.gynecological,
                "Head and Neck": patient.head_and_neck,
                "hematopoietic": patient.hematopoietic,
                "Male Genital": patient.male_genital,
                "Musculoskeletal": patient.musculoskeletal,
                "Nervous System": patient.nervous_system,
                "Respiratory": patient.respiratory,
                "Skin": patient.skin,
                "Unspecified": patient.unspecified,
                "Urinary": patient.urinary,
                "Age": patient.age
            }
            ]
        },
        "GlobalParameters": {
            # "method": "predict",
            "method": "predict_proba"
        }
    }


    # Make a prediction
    body = str.encode(json.dumps(data))
    url = 'http://5ab60f81-79a1-4dd1-be2b-500e0a07e324.eastus2.azurecontainer.io/score'
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ.get('API_KEY')
    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    req = urllib.request.Request(url, body, headers)



    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        return {"fail":"failed to get prediction"}
    return result

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    sex = db.Column(db.String(10))
    year_of_diagnosis = db.Column(db.Integer)
    race_recode_W_B_AI_API = db.Column(db.String(50))
    treatment = db.Column(db.String(255))
    year_of_follow_up_recode = db.Column(db.Integer)
    breast = db.Column(db.Boolean)
    endocrine = db.Column(db.Boolean)
    eye_and_adnexa = db.Column(db.Boolean)
    gastrointestinal = db.Column(db.Boolean)
    gynecological = db.Column(db.Boolean)
    head_and_neck = db.Column(db.Boolean)
    hematopoietic = db.Column(db.Boolean)
    male_genital = db.Column(db.Boolean)
    musculoskeletal = db.Column(db.Boolean)
    nervous_system = db.Column(db.Boolean)
    respiratory = db.Column(db.Boolean)
    skin = db.Column(db.Boolean)
    unspecified = db.Column(db.Boolean)
    urinary = db.Column(db.Boolean)
    age = db.Column(db.Integer)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name).isoformat() if isinstance(c.type, (Date, DateTime)) else getattr(self, c.name) for c in self.__table__.columns}

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    negative_rate = db.Column(db.Float)
    positive_rate = db.Column(db.Float)
    entry_date = db.Column(db.Date)

    # Relationship
    patient = db.relationship('Patient', backref=db.backref('predictions', lazy=True))
    def to_dict(self):
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return {c.name: getattr(self, c.name).isoformat() if isinstance(c.type, (Date, DateTime)) else getattr(self, c.name) for c in self.__table__.columns}

class PatientListAPI(Resource):
    def get(self):
        patients = Patient.query.all()
        result = []
        for patient in patients:
          
            temp_dict = patient.to_dict()
            patient_info = defaultdict(lambda: None, temp_dict)
            history = PredictionHistory.query.filter_by(patient_id=patient.id).order_by(PredictionHistory.entry_date.desc()).first()


            if history:
                patient_info['negative'] =history.negative_rate
                patient_info['positive'] = history.positive_rate
            else:
                patient_info['negative'] = None
                patient_info['positive'] = None

            result.append(patient_info)

        # history = PredictionHistory.query.filter_by(patient_id=patient_id).all
        # loop over each patient 
        # add prediction to the dictionary
        # return result
        return {'patients': result}    
    
    def post(self):
        try:
            patient = Patient(**request.json)
            db.session.add(patient)
            db.session.commit()
        except exc.IntegrityError:
            return {"error": "User already exists"}

        return patient.to_dict()
        
        # Prepare the data for prediction
        # @add a spearete logic for getting the prediction
        # pos make the backend clean 
        # neg require 2 apis calls in the frontend

        # 
        # result = calculate_prediction(patient)
        # Create a new PredictionHistory instance with the prediction
        # prediction_history = PredictionHistory(negative_rate=result['Results'][0][0],positive_rate=result['Results'][0][1], patient=patient, entry_date=date.today())
        # db.session.add(prediction_history)
        # db.session.commit()

        # response = {'patient': patient.to_dict(), 'prediction': {
        #     "negative":prediction_history.negative_rate,
        #     "positive": prediction_history.positive_rate
        #     }
     

class PatientAPI(Resource):
    # Get patient by id
    def get(self, id):
        patient = Patient.query.get(id)
        if patient:
            return patient.to_dict()
        else:
            return {"error": "Patient not found"}, 404
    
    def patch(self, id):
        body = request.json
        patient = Patient.query.get(id)
        # @TODO:clean the following if statements by adding all the keys in a list and iterate over it
        keys = ['name', 'age', 'sex', 'year_of_diagnosis',
         'race_recode_W_B_AI_API', 'treatment',
          'year_of_follow_up_recode', 'breast',
           'endocrine', 'eye_and_adnexa', 'gastrointestinal',
            'gynecological', 'head_and_neck', 'hematopoietic', 'male_genital',
             'musculoskeletal', 'nervous_system', 'respiratory', 'skin', 'unspecified',
              'urinary']

        for key in keys:
            if key in body:
                setattr(patient, key, body[key])

            
        # after this patient is updated in the database, we need to create a new prediction history for that patient
        # Create a new PredictionHistory instance with the updated patient data
        db.session.commit()
        return patient.to_dict()

    def delete(self, id):
        Patient.query.filter_by(id=id).delete()
        db.session.commit()
        return {'success': 'Patient deleted successfully'}

class PatientPredictionHistoryAPI(Resource):
    def get(self, patient_id):
        history = PredictionHistory.query.filter_by(patient_id=patient_id).all()
        return {'history': [record.to_dict() for record in history]}

    # calculate the prediction for the patient by id and add it to the history
    def post(self, patient_id):
        patient = Patient.query.filter_by(id=patient_id).first()
        result = calculate_prediction(patient)
        prediction_history = PredictionHistory(negative_rate=result['Results'][0][0],positive_rate=result['Results'][0][1], patient=patient, entry_date=date.today())
        db.session.add(prediction_history)
        db.session.commit()
        return prediction_history.to_dict()

    def delete(self, id):
        PredictionHistory.query.filter_by(id=id).delete()
        db.session.commit()
        return {'success': 'History deleted successfully'}


class PatientCountAPI(Resource):
    def get(self):
        count = Patient.query.count()
        return {'count': count}


api.add_resource(PatientCountAPI, '/patientCount', endpoint='patientCount')
api.add_resource(PatientListAPI, '/patients', endpoint = 'patients')
api.add_resource(PatientAPI, '/patient/<int:id>', endpoint = 'patient')
api.add_resource(PatientPredictionHistoryAPI, '/patientHistorys/<int:patient_id>', '/patientHistory/<int:id>', endpoint = 'history')

# /patients  POST return id from the response (frontend)
# THEN
# /patientHistorys/<int:patient_id> POST

if __name__ == '__main__':
    app.run(port=5000)   



