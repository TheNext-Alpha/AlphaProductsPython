from app import db
from datetime import datetime
import re
from exceptions import ValidationError

class JobApplicationForm(db.Model):
    __tablename__ = 'JobApplicationForms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    initial_id = db.Column(db.String(80), nullable=False)

    # Personal Information
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    father_name = db.Column(db.String(80), nullable=False)
    cnic = db.Column(db.String(13), nullable=False)
    passport_number = db.Column(db.String(13), nullable=True)
    dob = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    cell_phone = db.Column(db.String(11), nullable=False)
    alternate_number = db.Column(db.String(11), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    residence = db.Column(db.String(200), nullable=False)

    # Qualification and Experience
    education_level = db.Column(db.String(80), nullable=True)
    education_level_others = db.Column(db.String(80))
    degree = db.Column(db.String(80), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)
    institute = db.Column(db.String(80), nullable=False)

    # Employment History
    fresh = db.Column(db.Boolean)
    experienced = db.Column(db.Boolean)
    total_years_of_experience = db.Column(db.String(50), nullable=True)
    name_of_last_employer = db.Column(db.String(80), nullable=True)
    employment_duration_from = db.Column(db.Date, nullable=True)
    employment_duration_to = db.Column(db.Date, nullable=True)
    designation = db.Column(db.String(80), nullable=True)
    reason_for_leaving = db.Column(db.String(200), nullable=True)
    last_drawn_gross_salary = db.Column(db.String(50), nullable=True)
    benefits_if_any = db.Column(db.String(200), nullable=True)

    # Preference
    preferred_campus = db.Column(db.String(80), nullable=True)
    preferred_location = db.Column(db.String(80), nullable=True)
    preferred_job_type = db.Column(db.String(80), nullable=True)
    section = db.Column(db.String(80), nullable=True)
    subject = db.Column(db.String(80), nullable=True)
    expected_salary = db.Column(db.String(50))
    cv_path = db.Column(db.String(100))
    coverLetter_Path = db.Column(db.String(100), nullable=True)

    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<JobApplicationForm {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'initial_id': self.initial_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'father_name': self.father_name,
            'cnic': self.cnic,
            'passport_number': self.passport_number,
            'dob': self.dob.isoformat(),
            'age': self.age,
            'gender': self.gender,
            'cell_phone': self.cell_phone,
            'alternate_number': self.alternate_number,
            'email': self.email,
            'residence': self.residence,
            'education_level': self.education_level,
            'education_level_others': self.education_level_others,
            'degree': self.degree,
            'specialization': self.specialization,
            'institute': self.institute,
            'fresh': self.fresh,
            'experienced': self.experienced,
            'total_years_of_experience': self.total_years_of_experience,
            'name_of_last_employer': self.name_of_last_employer,
            'employment_duration_from': self.employment_duration_from.isoformat() if self.employment_duration_from else None,
            'employment_duration_to': self.employment_duration_to.isoformat() if self.employment_duration_to else None,
            'designation': self.designation,
            'reason_for_leaving': self.reason_for_leaving,
            'last_drawn_gross_salary': self.last_drawn_gross_salary,
            'benefits_if_any': self.benefits_if_any,
            'preferred_campus': self.preferred_campus,
            'preferred_location': self.preferred_location,
            'preferred_job_type': self.preferred_job_type,
            'section': self.section,
            'subject': self.subject,
            'expected_salary': self.expected_salary,
            'cv_path': self.cv_path,
            'coverLetter_Path': self.coverLetter_Path,
            'createDate': self.createDate.isoformat(),
            'status': self.status,
        }
    
    @staticmethod
    def validate_phone_number(phone_number):
        if not re.match(r"^(?!0+$)\d{11}$", phone_number):
            raise ValidationError("Invalid phone number format.")

    @staticmethod
    def validate_cnic(cnic):
        if not re.match(r'^(?!0{13})\d{13}$', cnic):
            raise ValidationError("Invalid CNIC format.")

    @staticmethod
    def validate_email(email):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError("Invalid email format.")

class NewJoinerApproval(db.Model):
    __tablename__ = 'NewJoinerApproval'

    newJoinerApproval_Id = db.Column(db.Integer, primary_key=True)
    newJoinerApproval_StaffId = db.Column(db.Integer, nullable=False)
    newJoinerApproval_Salary = db.Column(db.Float, nullable=False)
    newJoinerApproval_HiringApprovedBy = db.Column(db.Integer, nullable=False)
    newJoinerApproval_Remarks = db.Column(db.String(200))
    newJoinerApproval_FileVerified = db.Column(db.Boolean, nullable=False)
    newJoinerApproval_EmpDetailsVerified = db.Column(db.Boolean, nullable=False)
    newJoinerApproval_AddToPayrollMonth = db.Column(db.String(20), nullable=False)
    createdDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    createdBy = db.Column(db.Integer, nullable=False)
    updatedBy = db.Column(db.Integer)
    updatedDate = db.Column(db.DateTime)
    inActive = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<NewJoinerApproval {self.newJoinerApproval_Id}>'
    
    def to_dict(self):
        return {
            "newJoinerApproval_Id": self.newJoinerApproval_Id,
            "newJoinerApproval_StaffId": self.newJoinerApproval_StaffId,
            "newJoinerApproval_Salary" : self.newJoinerApproval_Salary,
            "newJoinerApproval_HiringApprovedBy" : self.newJoinerApproval_HiringApprovedBy,
            "newJoinerApproval_Remarks" : self.newJoinerApproval_Remarks,
            "newJoinerApproval_FileVerified" : self.newJoinerApproval_FileVerified,
            "newJoinerApproval_EmpDetailsVerified" : self.newJoinerApproval_EmpDetailsVerified,
            "newJoinerApproval_AddToPayrollMonth" : self.newJoinerApproval_AddToPayrollMonth,
            "createdDate" : self.createdDate.isoformat(),
            "createdBy" : self.createdBy,
            "updatedBy" : self.updatedBy,
            "updatedDate" : self.updatedDate.isoformat() if self.updatedDate else None,
            "inActive" : self.inActive
        }

class InterviewSchedules(db.Model):
    __tablename__ = 'InterviewSchedules'
    
    id = db.Column(db.Integer, primary_key=True)
    interviewTypeId = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    time = db.Column(db.Time, nullable=True)
    venue = db.Column(db.String(500), nullable=True)
    jobApplicationFormId = db.Column(db.Integer, nullable=True)
    interviewConductorId = db.Column(db.String(300), nullable=True)
    demoTopic = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(250), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    createdBy = db.Column(db.Integer, nullable=True)
    createDate = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    campusId = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<InterviewSchedule {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "interviewTypeId": self.interviewTypeId,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.isoformat() if self.time else None,
            "venue": self.venue,
            "jobApplicationFormId": self.jobApplicationFormId,
            "interviewConductorId": self.interviewConductorId,
            "demoTopic": self.demoTopic,
            "position": self.position,
            "location": self.location,
            "createdBy": self.createdBy,
            "createDate": self.createDate.isoformat() if self.createDate else None,
            "campusId": self.campusId
            
        }

class DeductionHead(db.Model):
    __tablename__ = 'DeductionHead'
    deductionHead_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deductionHead_Name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<DeductionHead {self.deductionHead_Id}>'
    
    def to_dict(self):
        return {
            "deductionHead_Id": self.deductionHead_Id,
            "deductionHead_Name": self.deductionHead_Name
        }

class OneTimeDeduction(db.Model):
    __tablename__ = 'OneTimeDeduction'
    oneTimeDeduction_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oneTimeDeduction_StaffId = db.Column(db.Integer, nullable=False)
    oneTimeDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.deductionHead_Id'), nullable=False)
    oneTimeDeduction_Amount = db.Column(db.Float, nullable=False)
    oneTimeDeduction_DeductionMonth = db.Column(db.String(15), nullable=False)
    oneTimeDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    creatorId = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatorId = db.Column(db.Integer, nullable=True)
    updateDate = db.Column(db.DateTime, nullable=True)
    inActive = db.Column(db.Boolean, nullable=False)

    deduction_head = db.relationship('DeductionHead', backref=db.backref('oneTimeDeduction', lazy=True))
    
    def __repr__(self):
        return f'<DeductionHead {self.oneTimeDeduction_Id}>'
    
    def to_dict(self):
        return {
            "oneTimeDeduction_Id": self.oneTimeDeduction_Id,
            "oneTimeDeduction_StaffId": self.oneTimeDeduction_StaffId,
            "oneTimeDeduction_DeductionHeadId": self.oneTimeDeduction_DeductionHeadId,
            "oneTimeDeduction_Amount": self.oneTimeDeduction_Amount,
            "oneTimeDeduction_DeductionMonth": self.oneTimeDeduction_DeductionMonth,
            "oneTimeDeduction_ApprovedBy": self.oneTimeDeduction_ApprovedBy,
            "creatorId": self.creatorId,
            "createDate": self.createDate.isoformat(),
            "updatorId": self.updatorId,
            "updateDate": self.updateDate.isoformat() if self.updateDate else None,
            "inActive": self.inActive
        }

class ScheduledDeduction(db.Model):
    __tablename__ = 'ScheduledDeduction'
    scheduledDeduction_Id = db.Column(db.Integer, primary_key=True)
    scheduledDeduction_StaffId = db.Column(db.Integer, nullable=False)
    scheduledDeduction_DeductionHeadId = db.Column(db.Integer, db.ForeignKey('DeductionHead.deductionHead_Id'), nullable=False)
    scheduledDeduction_AmountPerMonth = db.Column(db.Float, nullable=False)
    scheduledDeduction_StartDate = db.Column(db.DateTime, nullable=False)
    scheduledDeduction_EndDate = db.Column(db.DateTime, nullable=False)
    scheduledDeduction_ApprovedBy = db.Column(db.Integer, nullable=False)
    creatorId = db.Column(db.Integer, nullable=False)
    createDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatorId = db.Column(db.Integer)
    updateDate = db.Column(db.DateTime)
    inActive = db.Column(db.Boolean, nullable=False)
    
    deduction_head = db.relationship('DeductionHead', backref=db.backref('scheduledDeduction', lazy=True))
    
    def __repr__(self):
        return f'<DeductionHead {self.deductionHead_Id}>'
    
    def to_dict(self):
        return {
            "scheduledDeduction_Id": self.scheduledDeduction_Id,
            "scheduledDeduction_StaffId": self.scheduledDeduction_StaffId,
            "scheduledDeduction_DeductionHeadId": self.scheduledDeduction_DeductionHeadId,
            "scheduledDeduction_AmountPerMonth": self.scheduledDeduction_AmountPerMonth,
            "scheduledDeduction_StartDate": self.scheduledDeduction_StartDate.isoformat(),
            "scheduledDeduction_EndDate": self.scheduledDeduction_EndDate.isoformat(),
            "scheduledDeduction_ApprovedBy": self.scheduledDeduction_ApprovedBy,
            "creatorId": self.creatorId,
            "createDate": self.createDate.isoformat(),
            "updatorId": self.updatorId,
            "updateDate": self.updateDate.isoformat() if self.updateDate else None,
            "inActive": self.inActive
        }

class IAR(db.Model):
    __tablename__ = 'IAR'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    form_Id = db.Column(db.Integer, nullable=False)
    IAR_Type_Id = db.Column(db.Integer, db.ForeignKey('IAR_Types.id'), nullable=False)
    status_Check = db.Column(db.Boolean, nullable=False)
    remarks = db.Column(db.String(150), nullable=False)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)

    iar_type = db.relationship('IAR_Types', backref=db.backref('iars', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'form_Id': self.form_Id,
            'IAR_Type_Id': self.IAR_Type_Id,
            'status_Check': self.status_Check,
            'remarks': self.remarks,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None
        }

class IAR_Remarks(db.Model):
    __tablename__ = 'IAR_Remarks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    IAR_Id = db.Column(db.Integer, db.ForeignKey('IAR.id'), nullable=False)
    remarks = db.Column(db.String(150), nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createDate = db.Column(db.DateTime, nullable=True)

    iar = db.relationship('IAR', backref=db.backref('IAR_Id', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'IAR_Id': self.IAR_Id,
            'remarks': self.remarks,
            'status': self.status,
            'creatorId': self.creatorId,
            'createDate': self.createDate.isoformat() if self.createDate else None
        }

class IAR_Types(db.Model):
    __tablename__ = 'IAR_Types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class EmailTypes(db.Model):
    __tablename__ = 'EmailTypes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class EmailStorageSystem(db.Model):
    __tablename__ = 'EmailStorageSystem'
    email_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_Title = db.Column(db.String(100), nullable=True)
    email_Subject = db.Column(db.String(250), nullable=True)
    email_Body = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)
    updatorId = db.Column(db.Integer, nullable=True)
    updatedDate = db.Column(db.DateTime, nullable=True)
    emailType = db.Column(db.Integer, db.ForeignKey('EmailTypes.id'), nullable=True)

    email_type = db.relationship('EmailTypes', backref=db.backref('emails', lazy=True))

    def to_dict(self):
        return {
            'email_Id': self.email_Id,
            'email_Title': self.email_Title,
            'email_Subject': self.email_Subject,
            'email_Body': self.email_Body,
            'status': self.status,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None,
            'updatorId': self.updatorId,
            'updatedDate': self.updatedDate.isoformat() if self.updatedDate else None,
            'emailType': self.emailType
        }

class AvailableJobs(db.Model):
    __tablename__ = 'AvailableJobs'
    job_Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_Title = db.Column(db.String(100), nullable=False)
    job_Level = db.Column(db.String(100), nullable=False)
    job_PostedBy = db.Column(db.Integer, nullable=True)
    job_Status = db.Column(db.Boolean, nullable=True)
    creatorId = db.Column(db.Integer, nullable=True)
    createdDate = db.Column(db.DateTime, nullable=True)
    updatorId = db.Column(db.Integer, nullable=True)
    updatedDate = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'job_Id': self.job_Id,
            'job_Title': self.job_Title,
            'job_Level': self.job_Level,
            'job_PostedBy': self.job_PostedBy,
            'job_Status': self.job_Status,
            'creatorId': self.creatorId,
            'createdDate': self.createdDate.isoformat() if self.createdDate else None,
            'updatorId': self.updatorId,
            'updatedDate': self.updatedDate.isoformat() if self.updatedDate else None
        }
