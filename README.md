# Mada - Medication Adherence Call Schedule System

An AI-powered phone call system for medication adherence monitoring. This web application enables doctors to register patients with their diagnosis, medications, and health information, then automatically generates an IVR call schedule for medication reminders and general checkups.

## Features

- **Patient Registration**: Register patients with comprehensive health data including:
  - Personal information (name, age, sex, height, weight)
  - Diagnosis
  - Multiple medications with dosage, frequency, and duration
  - Doctor assignment

- **Intelligent Call Scheduling**: Automatically generates call schedules based on:
  - Medication frequency (once, twice, three, or four times daily)
  - Treatment duration
  - Weekly checkup calls

- **Call Tracking**: Monitor all scheduled and completed calls with:
  - Real-time status updates (pending, completed, missed)
  - Call logs with duration and notes
  - Automated flagging of missed calls

- **Doctor Dashboard**: 
  - View all registered patients
  - Monitor call schedules
  - Review flagged calls for follow-up
  - Access detailed patient information

## Installation

1. Clone the repository:
```bash
git clone https://github.com/raghavsb7/Mada.git
cd Mada
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Register a Patient

1. Navigate to "Register Patient" from the main menu
2. Fill in patient information:
   - Personal details (name, age, sex, height, weight, phone)
   - Diagnosis
   - Doctor name
3. Add medications with:
   - Medication name
   - Dosage (e.g., 500mg)
   - Frequency (once/twice/three/four times daily)
   - Duration in days
   - Special instructions (optional)
4. Click "Register Patient & Generate Schedule"

### View Call Schedule

- Navigate to "Call Schedule" to see all upcoming and past calls
- Filter by status: All, Pending, Completed, Missed, or Flagged
- Simulate calls (for testing) by clicking "✓ Answered" or "✗ Missed"

### Monitor Flagged Calls

- Navigate to "Flagged Calls" to see patients who missed their calls
- View patient details and take appropriate follow-up action

### Patient Management

- View all patients in the "Patients" list
- Click on any patient to see:
  - Complete health information
  - Medications
  - Call schedule
  - Call history

## Call Schedule Logic

The system generates calls based on medication frequency:

- **Once Daily**: One call per day at 9 AM
- **Twice Daily**: Calls at 9 AM and 8 PM
- **Three Times Daily**: Calls at 8 AM, 2 PM, and 8 PM
- **Four Times Daily**: Calls at 8 AM, 12 PM, 4 PM, and 8 PM

Additionally:
- Weekly checkup calls are scheduled (up to 4 weeks)
- Schedules are generated for up to 30 days initially
- Missed calls are automatically flagged for doctor review

## Database Schema

### Patient
- Personal information (name, age, sex, height, weight)
- Contact information (phone)
- Medical information (diagnosis)
- Doctor assignment

### Medication
- Linked to patient
- Name, dosage, frequency, duration
- Special instructions

### CallSchedule
- Scheduled time
- Call type (medication_reminder or checkup)
- Status (pending, completed, missed, flagged)

### CallLog
- Call time and duration
- Answered status
- Notes
- Flagged indicator

## API Endpoints

- `GET /api/patients` - List all patients
- `GET /api/schedule/<patient_id>` - Get call schedule for a patient

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with responsive design

## Development

To run in development mode:

```bash
python app.py
```

The application runs on `http://0.0.0.0:5000` with debug mode enabled.

## Future Enhancements

- Integration with actual IVR systems (Twilio, Vonage, etc.)
- SMS reminders as backup
- Patient mobile app for medication confirmation
- Analytics dashboard for adherence statistics
- Multi-language support
- Email notifications for doctors
- Customizable call schedules
- Patient history and trends

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
