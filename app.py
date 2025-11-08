from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mada.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    phone = db.Column(db.String(20), nullable=False)
    diagnosis = db.Column(db.String(200), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    medications = db.relationship('Medication', backref='patient', cascade='all, delete-orphan')
    call_logs = db.relationship('CallLog', backref='patient', cascade='all, delete-orphan')

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # e.g., "twice daily", "once daily"
    duration_days = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CallSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    call_type = db.Column(db.String(50), nullable=False)  # "medication_reminder", "checkup"
    status = db.Column(db.String(20), default='pending')  # pending, completed, missed, flagged
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref='schedules')

class CallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('call_schedule.id'))
    call_time = db.Column(db.DateTime, nullable=False)
    answered = db.Column(db.Boolean, default=False)
    duration = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.String(500))
    flagged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def generate_call_schedule(patient_id):
    """Generate call schedule based on medication frequency and diagnosis"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return False
    
    # Clear existing pending schedules
    CallSchedule.query.filter_by(patient_id=patient_id, status='pending').delete()
    
    medications = Medication.query.filter_by(patient_id=patient_id).all()
    
    if not medications:
        return False
    
    # Find the medication with longest duration
    max_duration = max([med.duration_days for med in medications])
    
    # Generate medication reminder calls
    current_time = datetime.utcnow()
    
    for med in medications:
        # Parse frequency to determine call schedule
        freq_lower = med.frequency.lower()
        
        if 'twice' in freq_lower or '2' in freq_lower:
            calls_per_day = 2
        elif 'thrice' in freq_lower or 'three' in freq_lower or '3' in freq_lower:
            calls_per_day = 3
        elif 'four' in freq_lower or '4' in freq_lower:
            calls_per_day = 4
        else:
            calls_per_day = 1
        
        # Schedule calls for the medication duration
        for day in range(min(med.duration_days, 30)):  # Limit to 30 days for initial schedule
            for call_num in range(calls_per_day):
                # Schedule calls at reasonable times (8 AM, 2 PM, 8 PM)
                if calls_per_day == 1:
                    hour = 9
                elif calls_per_day == 2:
                    hour = 9 if call_num == 0 else 20
                elif calls_per_day == 3:
                    hour = [8, 14, 20][call_num]
                else:
                    hour = [8, 12, 16, 20][call_num]
                
                scheduled_time = current_time + timedelta(days=day, hours=hour-current_time.hour, 
                                                         minutes=-current_time.minute, 
                                                         seconds=-current_time.second)
                
                schedule = CallSchedule(
                    patient_id=patient_id,
                    scheduled_time=scheduled_time,
                    call_type='medication_reminder'
                )
                db.session.add(schedule)
    
    # Add weekly checkup calls
    for week in range(min(max_duration // 7, 4)):  # Up to 4 weeks
        checkup_time = current_time + timedelta(weeks=week+1, hours=10-current_time.hour,
                                               minutes=-current_time.minute,
                                               seconds=-current_time.second)
        schedule = CallSchedule(
            patient_id=patient_id,
            scheduled_time=checkup_time,
            call_type='checkup'
        )
        db.session.add(schedule)
    
    db.session.commit()
    return True

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients')
def patients():
    all_patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('patients.html', patients=all_patients)

@app.route('/register_patient', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        # Create patient
        patient = Patient(
            name=request.form['name'],
            age=int(request.form['age']),
            sex=request.form['sex'],
            height=float(request.form['height']),
            weight=float(request.form['weight']),
            phone=request.form['phone'],
            diagnosis=request.form['diagnosis'],
            doctor_name=request.form['doctor_name']
        )
        db.session.add(patient)
        db.session.flush()  # Get patient ID
        
        # Add medications
        med_count = int(request.form.get('med_count', 1))
        for i in range(1, med_count + 1):
            if request.form.get(f'med_name_{i}'):
                medication = Medication(
                    patient_id=patient.id,
                    name=request.form[f'med_name_{i}'],
                    dosage=request.form[f'med_dosage_{i}'],
                    frequency=request.form[f'med_frequency_{i}'],
                    duration_days=int(request.form[f'med_duration_{i}']),
                    instructions=request.form.get(f'med_instructions_{i}', '')
                )
                db.session.add(medication)
        
        db.session.commit()
        
        # Generate call schedule
        generate_call_schedule(patient.id)
        
        flash('Patient registered successfully and call schedule created!', 'success')
        return redirect(url_for('patient_detail', patient_id=patient.id))
    
    return render_template('register_patient.html')

@app.route('/patient/<int:patient_id>')
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    schedules = CallSchedule.query.filter_by(patient_id=patient_id)\
                                  .order_by(CallSchedule.scheduled_time).all()
    call_logs = CallLog.query.filter_by(patient_id=patient_id)\
                              .order_by(CallLog.call_time.desc()).all()
    return render_template('patient_detail.html', patient=patient, 
                          schedules=schedules, call_logs=call_logs)

@app.route('/call_schedule')
def call_schedule():
    schedules = CallSchedule.query.join(Patient)\
                                  .order_by(CallSchedule.scheduled_time)\
                                  .all()
    return render_template('call_schedule.html', schedules=schedules)

@app.route('/flagged_calls')
def flagged_calls():
    flagged = CallLog.query.filter_by(flagged=True)\
                           .join(Patient)\
                           .order_by(CallLog.call_time.desc())\
                           .all()
    return render_template('flagged_calls.html', flagged_calls=flagged)

@app.route('/simulate_call/<int:schedule_id>', methods=['POST'])
def simulate_call(schedule_id):
    """Simulate an IVR call for testing"""
    schedule = CallSchedule.query.get_or_404(schedule_id)
    
    # Get answered status from request
    answered = request.form.get('answered') == 'true'
    
    # Create call log
    call_log = CallLog(
        patient_id=schedule.patient_id,
        schedule_id=schedule.id,
        call_time=datetime.utcnow(),
        answered=answered,
        duration=int(request.form.get('duration', 0)),
        notes=request.form.get('notes', ''),
        flagged=not answered  # Flag if not answered
    )
    db.session.add(call_log)
    
    # Update schedule status
    if answered:
        schedule.status = 'completed'
    else:
        schedule.status = 'missed'
        schedule.status = 'flagged'
    
    db.session.commit()
    
    flash(f'Call {"completed" if answered else "missed and flagged"}!', 
          'success' if answered else 'warning')
    return redirect(url_for('call_schedule'))

@app.route('/api/patients', methods=['GET'])
def api_patients():
    patients = Patient.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'age': p.age,
        'diagnosis': p.diagnosis,
        'phone': p.phone
    } for p in patients])

@app.route('/api/schedule/<int:patient_id>', methods=['GET'])
def api_schedule(patient_id):
    schedules = CallSchedule.query.filter_by(patient_id=patient_id).all()
    return jsonify([{
        'id': s.id,
        'scheduled_time': s.scheduled_time.isoformat(),
        'call_type': s.call_type,
        'status': s.status
    } for s in schedules])

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
