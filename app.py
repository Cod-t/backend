from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, DateTime
from datetime import date
import joblib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # replace with your database URI
db = SQLAlchemy(app)
api = Api(app)

model = joblib.load("model.pkl")


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
    cod_strokeYN = db.Column(db.Boolean)
    age = db.Column(db.Integer)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name).isoformat() if isinstance(c.type, (Date, DateTime)) else getattr(self, c.name) for c in self.__table__.columns}

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    rate = db.Column(db.Float)
    entry_date = db.Column(db.Date)

    # Relationship
    patient = db.relationship('Patient', backref=db.backref('predictions', lazy=True))
    def to_dict(self):
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return {c.name: getattr(self, c.name).isoformat() if isinstance(c.type, (Date, DateTime)) else getattr(self, c.name) for c in self.__table__.columns}

class PatientListAPI(Resource):
    def get(self):
        # @TODO: add the prediction history for each patient to the response
        patients = Patient.query.all()
        return {'patients': [patient.to_dict() for patient in patients]}    
    
    def post(self):
        patient = Patient(**request.json)
        db.session.add(patient)
        db.session.commit()

        # Prepare the data for prediction
        data = [patient.age,
                patient.sex,
                patient.year_of_diagnosis,
                patient.race_recode_W_B_AI_API,
                patient.treatment,
                patient.year_of_follow_up_recode,
                patient.breast, patient.endocrine,
                patient.eye_and_adnexa,
                patient.gastrointestinal,
                patient.gynecological,
                patient.head_and_neck,
                patient.hematopoietic,
                patient.male_genital,
                patient.musculoskeletal,
                patient.nervous_system,
                patient.respiratory,
                patient.skin,
                patient.unspecified,
                patient.urinary,
                patient.cod_strokeYN
                ]

        # Make a prediction
        prediction = model.predict([data])

        # Create a new PredictionHistory instance with the prediction
        prediction_history = PredictionHistory(rate=prediction[0], patient=patient, entry_date=date.today())
        db.session.add(prediction_history)
        db.session.commit()

        response = {'patient': patient.to_dict(), 'prediction': prediction_history.rate}
        return response


class PatientAPI(Resource):
    def get(self, id):
        # @TODO: add the prediction history to the response 
        patient = Patient.query.get(id)
        return patient.to_dict()
    
    def patch(self, id):
        body = request.json
        patient = Patient.query.get(id)
        
        if 'name' in body:
            patient.name = body['name']
        if 'sex' in body:
            patient.sex = body['sex']
        if 'year_of_diagnosis' in body:
            patient.year_of_diagnosis = body['year_of_diagnosis']
        if 'race_recode_W_B_AI_API' in body:
            patient.race_recode_W_B_AI_API = body['race_recode_W_B_AI_API']
        if 'treatment' in body:
            patient.treatment = body['treatment']
        if 'year_of_follow_up_recode' in body:
            patient.year_of_follow_up_recode = body['year_of_follow_up_recode']
        if 'breast' in body:
            patient.breast = body['breast']
        if 'endocrine' in body:
            patient.endocrine = body['endocrine']
        if 'eye_and_adnexa' in body:
            patient.eye_and_adnexa = body['eye_and_adnexa']
        if 'gastrointestinal' in body:
            patient.gastrointestinal = body['gastrointestinal']
        if 'gynecological' in body:
            patient.gynecological = body['gynecological']
        if 'head_and_neck' in body:
            patient.head_and_neck = body['head_and_neck']
        if 'hematopoietic' in body:
            patient.hematopoietic = body['hematopoietic']
        if 'male_genital' in body:
            patient.male_genital = body['male_genital']
        if 'musculoskeletal' in body:
            patient.musculoskeletal = body['musculoskeletal']
        if 'nervous_system' in body:
            patient.nervous_system = body['nervous_system']
        if 'respiratory' in body:
            patient.respiratory = body['respiratory']
        if 'skin' in body:
            patient.skin = body['skin']
        if 'unspecified' in body:
            patient.unspecified = body['unspecified']
        if 'urinary' in body:
            patient.urinary = body['urinary']
        if 'cod_strokeYN' in body:
            patient.cod_strokeYN = body['cod_strokeYN']
            
            
            
        # after this patient is updated in the database, we need to create a new prediction history for that patient
        # Create a new PredictionHistory instance with the updated patient data

        data = [patient.age,
                patient.sex,
                patient.year_of_diagnosis,
                patient.race_recode_W_B_AI_API,
                patient.treatment,
                patient.year_of_follow_up_recode,
                patient.breast, patient.endocrine,
                patient.eye_and_adnexa,
                patient.gastrointestinal,
                patient.gynecological,
                patient.head_and_neck,
                patient.hematopoietic,
                patient.male_genital,
                patient.musculoskeletal,
                patient.nervous_system,
                patient.respiratory,
                patient.skin,
                patient.unspecified,
                patient.urinary,
                patient.cod_strokeYN
                ]
        
        prediction = model.predict([data])

        prediction_history = PredictionHistory(rate=prediction[0], patient=patient, entry_date=date.today())
        db.session.add(prediction_history)
        db.session.commit()

        response = {'patient': patient.to_dict(), 'prediction': prediction_history.rate}
        return response

    def delete(self, id):
        Patient.query.filter_by(id=id).delete()
        db.session.commit()
        return {'result': 'success'}

class PatientPredictionHistoryAPI(Resource):
    def get(self, patient_id):
        history = PredictionHistory.query.filter_by(patient_id=patient_id).all()
        return {'history': [record.to_dict() for record in history]}

    def delete(self, id):
        PredictionHistory.query.filter_by(id=id).delete()
        db.session.commit()
        return {'result': 'success'}

api.add_resource(PatientListAPI, '/patients', endpoint = 'patients')
api.add_resource(PatientAPI, '/patient/<int:id>', endpoint = 'patient')
api.add_resource(PatientPredictionHistoryAPI, '/patientHistorys/<int:patient_id>', '/patientHistory/<int:id>', endpoint = 'history')



if __name__ == '__main__':
    app.run(port=5000)   



