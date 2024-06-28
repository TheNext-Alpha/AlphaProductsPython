from flask_restful import Resource, reqparse, abort
from models.models import (
    JobApplicationForm, NewJoinerApproval, InterviewSchedules, DeductionHead, OneTimeDeduction, 
    ScheduledDeduction, IAR, IAR_Remarks, IAR_Types, EmailTypes, EmailStorageSystem, AvailableJobs,
    StaffInfo, StaffDepartment, StaffTransfer, StaffShift, UserCampus, Users, UserType, Salaries, MarkDayOffDeps,
    MarkDayOffHRs, AllowanceHead, OneTimeAllowance, ScheduledAllowance
)
from datetime import datetime, date
from app import db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import and_
import json
from sqlalchemy.exc import SQLAlchemyError



class DateTimeEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()


class JobApplicationFormResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":"first_name", "headerName": "First Name", "width": width},
                {"field":"last_name", "headerName": "Last Name", "width": width},
                {"field":"father_name", "headerName": "Father's Name", "width": width},
                {"field":"cnic", "headerName": "CNIC", "width": width},
                {"field":"passport_number", "headerName": "Passport Number", "width": width},
                {"field":"dob", "headerName": "Date of Birth", "width": width},
                {"field":"age", "headerName": "Age", "width": width},
                {"field":"gender", "headerName": "Gender", "width": width},
                {"field":"cell_phone", "headerName": "Cell Phone", "width": width},
                {"field":"alternate_number", "headerName": "Alternate Number", "width": width},
                {"field":"email", "headerName": "Email Address", "width": width},
                {"field":"residence", "headerName": "Address", "width": width},
                {"field":"education_level", "headerName": "Education Level", "width": width},
                {"field":"education_level_others", "headerName": "Others", "width": width},
                {"field":"degree", "headerName": "Degree", "width": width},
                {"field":"specialization", "headerName": "Specialization", "width": width},
                {"field":"institute", "headerName": "Institute", "width": width},
                {"field":"fresh", "headerName": "Fresh", "width": width},
                {"field":"experienced", "headerName": "Experienced", "width": width},
                {"field":"total_years_of_experience", "headerName": "Total Years of Experience", "width": width},
                {"field":"name_of_last_employer", "headerName": "Name of Last Employer", "width": width},
                {"field":"employment_duration_from", "headerName": "Employment Duration: From", "width": width},
                {"field":"employment_duration_to", "headerName": "Employment Duration: To", "width": width},
                {"field":"designation", "headerName": "Designation", "width": width},
                {"field":"reason_for_leaving", "headerName": "Reason For Leaving(if already left)", "width": width},
                {"field":"last_drawn_gross_salary", "headerName": "Last Drawn Gross Salary", "width": width},
                {"field":"benefits_if_any", "headerName": "Benefits if any", "width": width},
                {"field":"preferred_campus", "headerName": "Preferred Campus", "width": width},
                {"field":"preferred_location", "headerName": "Preferred Location", "width": width},
                {"field":"preferred_job_type", "headerName": "Preferred Job Type", "width": width},
                {"field":"section", "headerName": "Section", "width": width},
                {"field":"subject", "headerName": "Subject", "width": width},
                {"field":"expected_salary", "headerName": "Expected Salary", "width": width},
                {"field":"cv_path", "headerName": "CV", "width": width},
                {"field":"coverLetter_Path", "headerName": "Cover Letter", "width": width}
            ]
            
            if id:
                job_application_form = JobApplicationForm.query.get_or_404(id)
                
                return {
                    "data": [job_application_form.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = JobApplicationForm.query.order_by(JobApplicationForm.id)
                total = query.count()

                # Apply pagination
                job_application_forms = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [form.to_dict() for form in job_application_forms],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Initial_id', required=True)
        parser.add_argument('First_name', required=True)
        parser.add_argument('Last_name', required=True)
        parser.add_argument('Father_name', required=True)
        parser.add_argument('Cnic', required=True)
        parser.add_argument('Passport_number')
        parser.add_argument('Dob', required=True)
        parser.add_argument('Age', required=True, type=int)
        parser.add_argument('Gender', required=True)
        parser.add_argument('Cell_phone', required=True)
        parser.add_argument('Alternate_number')
        parser.add_argument('Email', required=True)
        parser.add_argument('Residence', required=True)
        parser.add_argument('Education_level', required=True)
        parser.add_argument('Education_level_others')
        parser.add_argument('Degree', required=True)
        parser.add_argument('Specialization', required=True)
        parser.add_argument('Institute', required=True)
        parser.add_argument('Fresh', type=bool)
        parser.add_argument('Experienced', type=bool)
        parser.add_argument('Total_years_of_experience')
        parser.add_argument('Name_of_last_employer')
        parser.add_argument('Employment_duration_from')
        parser.add_argument('Employment_duration_to')
        parser.add_argument('Designation')
        parser.add_argument('Reason_for_leaving')
        parser.add_argument('Last_drawn_gross_salary')
        parser.add_argument('Benefits_if_any')
        parser.add_argument('Preferred_campus')
        parser.add_argument('Preferred_location')
        parser.add_argument('Preferred_job_type')
        parser.add_argument('Section')
        parser.add_argument('Subject')
        parser.add_argument('Expected_salary', required=True)
        parser.add_argument('Cv_path', required=True)
        parser.add_argument('CoverLetter_Path')
        parser.add_argument('Status', type=bool)

        args = parser.parse_args()

        try:
            # Validate inputs
            if JobApplicationForm.validate_phone_number(args['Cell_phone']):
                raise ValueError("Invalid phone number format.")
            if JobApplicationForm.validate_cnic(args['Cnic']):
                raise ValueError("Invalid CNIC format.")
            if args['Email'] and JobApplicationForm.validate_email(args['Email']):
                raise ValueError("Invalid email format.")
            if args['Passport_number'] and not JobApplicationForm.validate_passport_number(args['Passport_number']):
                raise ValueError("Invalid passport number format.")

            employment_duration_from = datetime.strptime(args['Employment_duration_from'], '%Y-%m-%d') if args['Employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['Employment_duration_to'], '%Y-%m-%d') if args['Employment_duration_to'] else None

            job_application_form = JobApplicationForm(
                Initial_id=args['Initial_id'],
                First_name=args['First_name'],
                Last_name=args['Last_name'],
                Father_name=args['Father_name'],
                Cnic=args['Cnic'],
                Passport_number=args['Passport_number'],
                Dob=datetime.strptime(args['Dob'], '%Y-%m-%d'),
                Age=args['Age'],
                Gender=args['Gender'],
                Cell_phone=args['Cell_phone'],
                Alternate_number=args['Alternate_number'],
                Email=args['Email'],
                Residence=args['Residence'],
                Education_level=args['Education_level'],
                Education_level_others=args['Education_level_others'],
                Degree=args['Degree'],
                Specialization=args['Specialization'],
                Institute=args['Institute'],
                Fresh=args['Fresh'],
                Experienced=args['Experienced'],
                Total_years_of_experience=args['Total_years_of_experience'],
                Name_of_last_employer=args['Name_of_last_employer'],
                Employment_duration_from=employment_duration_from,
                Employment_duration_to=employment_duration_to,
                Designation=args['designation'],
                Reason_for_leaving=args['reason_for_leaving'],
                Last_drawn_gross_salary=args['last_drawn_gross_salary'],
                Benefits_if_any=args['benefits_if_any'],
                Preferred_campus=args['preferred_campus'],
                Preferred_location=args['preferred_location'],
                Preferred_job_type=args['preferred_job_type'],
                Section=args['section'],
                Subject=args['subject'],
                Expected_salary=args['expected_salary'],
                Cv_path=args['cv_path'],
                CoverLetter_Path=args['coverLetter_Path'],
                Status=args['status']
            )

            db.session.add(job_application_form)
            db.session.commit()

            return {'message': 'Job application form created successfully'}, 201
        except ValueError as e:
            return {'error': 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Initial_id')
        parser.add_argument('First_name')
        parser.add_argument('Last_name')
        parser.add_argument('Father_name')
        parser.add_argument('Cnic')
        parser.add_argument('Passport_number')
        parser.add_argument('Dob')
        parser.add_argument('Age', type=int)
        parser.add_argument('Gender')
        parser.add_argument('Cell_phone')
        parser.add_argument('Alternate_number')
        parser.add_argument('Email')
        parser.add_argument('Residence')
        parser.add_argument('Education_level')
        parser.add_argument('Education_level_others')
        parser.add_argument('Degree')
        parser.add_argument('Specialization')
        parser.add_argument('Institute')
        parser.add_argument('Fresh', type=bool)
        parser.add_argument('Experienced', type=bool)
        parser.add_argument('Total_years_of_experience')
        parser.add_argument('Name_of_last_employer')
        parser.add_argument('Employment_duration_from')
        parser.add_argument('Employment_duration_to')
        parser.add_argument('Designation')
        parser.add_argument('Reason_for_leaving')
        parser.add_argument('Last_drawn_gross_salary')
        parser.add_argument('Benefits_if_any')
        parser.add_argument('Preferred_campus')
        parser.add_argument('Preferred_location')
        parser.add_argument('Preferred_job_type')
        parser.add_argument('Section')
        parser.add_argument('Subject')
        parser.add_argument('Expected_salary')
        parser.add_argument('Cv_path')
        parser.add_argument('CoverLetter_Path')
        parser.add_argument('Status', type=bool)

        args = parser.parse_args()

        try:
            job_application_form = JobApplicationForm.query.get_or_404(id)

            if args['Cell_phone'] and not JobApplicationForm.validate_phone_number(args['Cell_phone']):
                raise ValueError("Invalid phone number format.")
            if args['Cnic'] and not JobApplicationForm.validate_cnic(args['Cnic']):
                raise ValueError("Invalid CNIC format.")
            if args['Email'] and not JobApplicationForm.validate_email(args['Email']):
                raise ValueError("Invalid email format.")
            if args['Passport_number'] and not JobApplicationForm.validate_passport_number(args['Passport_number']):
                raise ValueError("Invalid passport number format.")

            employment_duration_from = datetime.strptime(args['Employment_duration_from'], '%Y-%m-%d') if args['Employment_duration_from'] else None
            employment_duration_to = datetime.strptime(args['Employment_duration_to'], '%Y-%m-%d') if args['Employment_duration_to'] else None

            for key, value in args.items():
                if value is not None:
                    setattr(job_application_form, key, value)

            job_application_form.employment_duration_from = employment_duration_from
            job_application_form.employment_duration_to = employment_duration_to

            db.session.commit()
            return {'message': 'Job application form updated successfully'}, 200
        except ValueError as e:
            return {'error': 'Validation Error', 'message': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

    def delete(self, id):
        try:
            job_application_form = JobApplicationForm.query.get_or_404(id)
            db.session.delete(job_application_form)
            db.session.commit()
            return {'message': 'Job application form deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

class NewJoinerApprovalResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
            {"fields": "NewJoinerApproval_StaffId", "headerName": "Staff ID", "width": width},
            {"fields": "NewJoinerApproval_Salary", "headerName": "Salary", "width": width},
            {"fields": "NewJoinerApproval_HiringApprovedBy", "headerName": "Hiring Approved By", "width": width},
            {"fields": "NewJoinerApproval_Remarks", "headerName": "Remarks", "width": width},
            {"fields": "NewJoinerApproval_FileVerified", "headerName": "File Verified", "width": width},
            {"fields": "NewJoinerApproval_EmpDetailsVerified", "headerName": "Employee Details Verified", "width": width},
            {"fields": "NewJoinerApproval_AddToPayrollMonth", "headerName": "Add to Payroll Month", "width": width},
        ]
            if id:
                new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
                return {
                    "data": [new_joiner_approval.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                
                query = NewJoinerApproval.query.order_by(NewJoinerApproval.NewJoinerApproval_Id)
                total = query.count()

                # Apply pagination
                new_joiner_approvals = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [approval.to_dict() for approval in new_joiner_approvals],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new joiner approval record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('NewJoinerApproval_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('NewJoinerApproval_Salary', type=float, required=True, help='Salary is required')
        parser.add_argument('NewJoinerApproval_HiringApprovedBy', type=int, required=True, help='Hiring approved by is required')
        parser.add_argument('NewJoinerApproval_Remarks', type=str, required=False)
        parser.add_argument('NewJoinerApproval_FileVerified', type=bool, required=True, help='File verified is required')
        parser.add_argument('NewJoinerApproval_EmpDetailsVerified', type=bool, required=True, help='Employee details verified is required')
        parser.add_argument('NewJoinerApproval_AddToPayrollMonth', type=str, required=True, help='Add to payroll month is required')
        parser.add_argument('CreatedBy', type=int, required=True, help='Creator ID is required')
        
        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval(
                NewJoinerApproval_StaffId=args['NewJoinerApproval_StaffId'],
                NewJoinerApproval_Salary=args['NewJoinerApproval_Salary'],
                NewJoinerApproval_HiringApprovedBy=args['NewJoinerApproval_HiringApprovedBy'],
                NewJoinerApproval_Remarks=args.get('NewJoinerApproval_Remarks'),
                NewJoinerApproval_FileVerified=args['NewJoinerApproval_FileVerified'],
                NewJoinerApproval_EmpDetailsVerified=args['NewJoinerApproval_EmpDetailsVerified'],
                NewJoinerApproval_AddToPayrollMonth=args['NewJoinerApproval_AddToPayrollMonth'],
                CreatedBy=args['CreatedBy'],
                CreatedDate=datetime.utcnow()
            )

            db.session.add(new_joiner_approval)
            db.session.commit()
            
            # Create salary record for the new joiner
            self.create_employee_salary(new_joiner_approval.NewJoinerApproval_StaffId, new_joiner_approval.NewJoinerApproval_Salary)

            return {"message": "New joiner approval created successfully", "newJoinerApproval": new_joiner_approval.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, approval_id):
        
        """
        Handles updating an existing joiner approval record by its ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('NewJoinerApproval_Salary', type=float, required=False)
        parser.add_argument('NewJoinerApproval_HiringApprovedBy', type=int, required=False)
        parser.add_argument('NewJoinerApproval_Remarks', type=str, required=False)
        parser.add_argument('NewJoinerApproval_FileVerified', type=bool, required=False)
        parser.add_argument('NewJoinerApproval_EmpDetailsVerified', type=bool, required=False)
        parser.add_argument('NewJoinerApproval_AddToPayrollMonth', type=str, required=False)
        parser.add_argument('UpdatedBy', type=int, required=True, help='Updater ID is required')
        
        args = parser.parse_args()

        try:
            new_joiner_approval = NewJoinerApproval.query.get(approval_id)
            if not new_joiner_approval:
                return {'message': 'New joiner approval record not found'}, 404

            for key, value in args.items():
                if value is not None:
                    setattr(new_joiner_approval, key, value)

            new_joiner_approval.updatedBy = args['UpdatedBy']
            new_joiner_approval.updatedDate = datetime.utcnow()

            db.session.commit()

            # Update the corresponding salary record
            self.update_employee_salary(new_joiner_approval.NewJoinerApproval_StaffId, new_joiner_approval.NewJoinerApproval_Salary)

            return {"message": "New joiner approval updated successfully", "newJoinerApproval": new_joiner_approval.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def create_employee_salary(self, staff_id, total_salary):
        """
        Creates a new salary record for the given staff ID.
        """
        try:
            staff_info = StaffInfo.query.get(staff_id)
            if not staff_info:
                return

            is_non_teacher = staff_info.IsNonTeacher
            basic = total_salary / 2

            new_salary = Salaries(
                BasicAmount=basic,
                AllowancesAmount=basic,
                TotalAmount=total_salary,
                AnnualLeaves=10,
                RemainingAnnualLeaves=10,
                DailyHours=8,
                PFAmount=basic / 12,
                EOBIAmount=basic / 12,
                SESSIAmount=basic / 12,
                SalaryMode=1,
                IsProbationPeriod=False,
                From=datetime.utcnow(),
                To=datetime.utcnow(),
                EmployeeId=staff_id,
                CreatedOn=datetime.utcnow(),
                IsActive=True,
                CreatedByUserId=get_jwt_identity(),
                HouseRent=basic / 2,
                MedicalAllowance=basic / 10,
                UtilityAllowance=basic / 5,
                IncomeTax=0,
                Toil=0,
                ConveyanceAllowance=basic / 5,
                StaffLunch=0,
                CasualLeaves=12 if is_non_teacher else 10,
                SickLeaves=7,
                RemainingCasualLeaves=12 if is_non_teacher else 10,
                RemainingSickLeaves=7,
                StudyLeaves=5,
                RemainingStudyLeaves=5,
                Loan=0,
                Arrears=0
            )

            db.session.add(new_salary)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating employee salary: {str(e)}")

    def update_employee_salary(self, staff_id, total_salary):
        """
        Updates the existing active salary record for the given staff ID.
        """
        try:
            salary = Salaries.query.filter_by(EmployeeId=staff_id, IsActive=True).first()
            if not salary:
                return

            staff_info = StaffInfo.query.get(staff_id)
            if not staff_info:
                return

            is_non_teacher = staff_info.IsNonTeacher
            basic = total_salary / 2

            salary.BasicAmount = basic
            salary.AllowancesAmount = basic
            salary.TotalAmount = total_salary
            salary.PFAmount = basic / 12
            salary.EOBIAmount = basic / 12
            salary.SESSIAmount = basic / 12
            salary.From = datetime.utcnow()
            salary.To = datetime.utcnow()
            salary.HouseRent = basic / 2
            salary.MedicalAllowance = basic / 10
            salary.UtilityAllowance = basic / 5
            salary.ConveyanceAllowance = basic / 5
            salary.UpdatedOn = datetime.utcnow()
            salary.UpdatedByUserId = get_jwt_identity()

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating employee salary: {str(e)}")
    
    def delete(self, id):
        try:
            new_joiner_approval = NewJoinerApproval.query.get_or_404(id)
            db.session.delete(new_joiner_approval)
            db.session.commit()
            return {'message': 'New joiner approval deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Internal Server Error', 'message': str(e)}, 500

class InterviewSchedulesResource(Resource):
    
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":'Interview_type_id', "headerName": "Interview Type ID", "width": width},
                {"field":'Date', "headerName": "Date", "width": width},
                {"field":'Time', "headerName": "Time", "width": width},
                {"field":'Venue', "headerName": "Venue", "width": width},
                {"field":'Job_application_form_id', "headerName": "Job Application Form Id", "width": width},
                {"field":'Interview_conductor_id', "headerName": "Interview Conductor Id", "width": width},
                {"field":'Demo_topic', "headerName": "Demo Topic", "width": width},
                {"field":'Position', "headerName": "Position", "width": width},
                {"field":'Location', "headerName": "Location", "width": width},
                {"field":'Created_by', "headerName": "Created By", "width": width},
                {"field":'Create_date', "headerName": "Created Date", "width": width},
                {"field":'Campus_id', "headerName": "Campus Id", "width": width}
            ]
            
            if id is None:
                
                query = InterviewSchedules.query.order_by(InterviewSchedules.Id)
                total = query.count()

                # Apply pagination
                interviews = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [interview.to_dict() for interview in interviews],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
            else:
                interview = InterviewSchedules.query.get(id)
                if interview is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                interview = interview.to_dict()
                return {
                    "data": [interview.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('InterviewTypeId', type=int, required=True, help="Interview type ID is required")
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Time', type=str, required=False)
        parser.add_argument('Venue', type=str, required=False)
        parser.add_argument('JobApplicationFormId', type=int, required=False)
        parser.add_argument('InterviewConductorId', type=str, required=False)
        parser.add_argument('DemoTopic', type=str, required=False)
        parser.add_argument('Position', type=str, required=False)
        parser.add_argument('Location', type=str, required=False)
        parser.add_argument('CreatedBy', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_schedule = InterviewSchedules(
                interviewTypeId=args['InterviewTypeId'],
                date=datetime.strptime(args['Date'], '%Y-%m-%d') if args['Date'] else None,
                time=datetime.strptime(args['Time'], '%H:%M:%S').time() if args['Time'] else None,
                venue=args['Venue'],
                jobApplicationFormId=args['JobApplicationFormId'],
                interviewConductorId=args['InterviewConductorId'],
                demoTopic=args['DemoTopic'],
                position=args['Position'],
                location=args['Location'],
                createdBy=args['CreatedBy'],
                createDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S') if args['CreateDate'] else datetime.utcnow(),
                campusId=args['CampusId']
            )
            db.session.add(new_schedule)
            db.session.commit()
            return {"message": "Interview schedule created", "id": new_schedule.id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating interview schedule: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('InterviewTypeId', type=int, required=False)
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Time', type=str, required=False)
        parser.add_argument('Venue', type=str, required=False)
        parser.add_argument('JobApplicationFormId', type=int, required=False)
        parser.add_argument('InterviewConductorId', type=str, required=False)
        parser.add_argument('DemoTopic', type=str, required=False)
        parser.add_argument('Position', type=str, required=False)
        parser.add_argument('Location', type=str, required=False)
        parser.add_argument('CreatedBy', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        schedule = InterviewSchedules.query.get(id)
        if schedule is None:
            abort(404, message=f"Interview schedule {id} doesn't exist")

        try:
            if args['InterviewTypeId'] is not None:
                schedule.InterviewTypeId = args['InterviewTypeId']
            if args['Date']:
                schedule.Date = datetime.strptime(args['Date'], '%Y-%m-%d')
            if args['Time']:
                schedule.Time = datetime.strptime(args['Time'], '%H:%M:%S').time()
            if args['Venue']:
                schedule.Venue = args['Venue']
            if args['JobApplicationFormId'] is not None:
                schedule.JobApplicationFormId = args['JobApplicationFormId']
            if args['InterviewConductorId']:
                schedule.InterviewConductorId = args['InterviewConductorId']
            if args['DemoTopic']:
                schedule.DemoTopic = args['DemoTopic']
            if args['Position']:
                schedule.Position = args['Position']
            if args['Location']:
                schedule.Location = args['Location']
            if args['CreatedBy'] is not None:
                schedule.CreatedBy = args['CreatedBy']
            if args['CreateDate']:
                schedule.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')
            if args['CampusId'] is not None:
                schedule.CampusId = args['CampusId']
            
            db.session.commit()
            return {"message": "Interview schedule updated", "id": schedule.id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating interview schedule: {str(e)}")
    
    def delete(self, id):
        schedule = InterviewSchedules.query.get(id)
        if schedule is None:
            abort(404, message=f"Interview schedule {id} doesn't exist")

        try:
            db.session.delete(schedule)
            db.session.commit()
            return {"message": "Interview schedule deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting interview schedule: {str(e)}")

class DeductionHeadResource(Resource):
    def get(self, id=None):

        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            columns = [
                {"field": "DeductionHead_Id", "headerName": "Deduction Head Id", "width": width},
                {"field": "DeductionHead_Name", "headerName": "Deduction Head Name", "width": width}
            ]
            
            if id is None:
                query = DeductionHead.query.order_by(DeductionHead.DeductionHead_Id)
                total = query.count()

                # Apply pagination
                deductionHeads = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [deductionHead.to_dict() for deductionHead in deductionHeads],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

            else:
                deductionHeads = DeductionHead.query.get(id)
                if deductionHeads is None:
                    abort(404, message=f"deductionHeads {id} doesn't exist")
                
                deductionHeads = deductionHeads.to_dict()
                return {
                    "data": [deductionHeads.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('DeductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        try:
            new_head = DeductionHead(DeductionHead_Name=args['DeductionHead_Name'])
            db.session.add(new_head)
            db.session.commit()
            return {"message": "Deduction head created", "id": new_head.DeductionHead_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating deduction head: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('DeductionHead_Name', type=str, required=True, help="Deduction head name is required")
        args = parser.parse_args()

        head = DeductionHead.query.get(id)
        if head is None:
            abort(404, message=f"DeductionHead {id} doesn't exist")

        try:
            head.DeductionHead_Name = args['DeductionHead_Name']
            db.session.commit()
            return {"message": "Deduction head updated", "id": head.DeductionHead_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating deduction head: {str(e)}")
    
    def delete(self, id):
        head = DeductionHead.query.get(id)
        if head is None:
            abort(404, message=f"DeductionHead {id} doesn't exist")

        try:
            db.session.delete(head)
            db.session.commit()
            return {"message": "Deduction head deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting deduction head: {str(e)}")

class OneTimeDeductionResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
        
            columns = [
                {"field":"OneTimeDeduction_Id", "headername": "Id", "width": width},
                {"field":"OneTimeDeduction_StaffId", "headername": "Staff Id", "width": width},
                {"field":"OneTimeDeduction_DeductionHeadId", "headername": "Deduction Head Id", "width": width},
                {"field":"OneTimeDeduction_Amount", "headername": "Amount", "width": width},
                {"field":"OneTimeDeduction_DeductionMonth", "headername": "Deduction Month", "width": width},
                {"field":"OneTimeDeduction_ApprovedBy", "headername": "Approved By", "width": width},
                {"field":"CreatorId", "headername": "Creator Id", "width": width},
                {"field":"CeateDate", "headername": "Created Date", "width": width},
                {"field":"UdatorId", "headername": "Updator Id", "width": width},
                {"field":"UpdateDate", "headername": "Updated Date", "width": width},
                {"field":"InActive", "headername": "In active", "width": width}
            ]

            if id is None:
                
                query = OneTimeDeduction.query.order_by(OneTimeDeduction.OneTimeDeduction_Id)
                total = query.count()

                # Apply pagination
                oneTimeDeductions = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [oneTimeDeduction.to_dict() for oneTimeDeduction in oneTimeDeductions],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200

            else:
                oneTimeDeductions = OneTimeDeduction.query.get(id)
                if oneTimeDeductions is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                return {
                    "data": [oneTimeDeductions.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200

        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('OneTimeDeduction_DeductionHeadId', type=int, required=True, help="Deduction head ID is required")
        parser.add_argument('OneTimeDeduction_Amount', type=float, required=True, help="Amount is required")
        parser.add_argument('OneTimeDeduction_DeductionMonth', type=str, required=True, help="Deduction month is required")
        parser.add_argument('OneTimeDeduction_ApprovedBy', type=int, required=True, help="Approved by is required")
        parser.add_argument('CreatorId', type=int, required=True, help="Creator ID is required")
        parser.add_argument('UreateDate', type=str, required=True, help="Create date is required")
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=str, required=False)
        parser.add_argument('InActive', type=bool, required=True, help="Inactive status is required")
        args = parser.parse_args()

        try:
            new_deduction = OneTimeDeduction(
                OneTimeDeduction_StaffId=args['OneTimeDeduction_StaffId'],
                OneTimeDeduction_DeductionHeadId=args['OneTimeDeduction_DeductionHeadId'],
                OneTimeDeduction_Amount=args['OneTimeDeduction_Amount'],
                OneTimeDeduction_DeductionMonth=args['OneTimeDeduction_DeductionMonth'],
                OneTimeDeduction_ApprovedBy=args['OneTimeDeduction_ApprovedBy'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S'),
                UpdatorId=args.get('UpdatorId'),
                UpdateDate=datetime.strptime(args['UpdateDate'], '%Y-%m-%d %H:%M:%S') if args['UpdateDate'] else None,
                InActive=args['InActive']
            )
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "One-time deduction created", "id": new_deduction.OneTimeDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating one-time deduction: {str(e)}")
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeDeduction_Id', type=int, required=False)
        parser.add_argument('OneTimeDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('OneTimeDeduction_Amount', type=float, required=False)
        parser.add_argument('OneTimeDeduction_DeductionMonth', type=str, required=False)
        parser.add_argument('OneTimeDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=str, required=False)
        parser.add_argument('InActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = OneTimeDeduction.query.get(id)
        if deduction is None:
            abort(404, message=f"OneTimeDeduction {id} doesn't exist")

        try:
            if args['OneTimeDeduction_StaffId'] is not None:
                deduction.OneTimeDeduction_StaffId = args['OneTimeDeduction_StaffId']
            if args['OneTimeDeduction_DeductionHeadId'] is not None:
                deduction.OneTimeDeduction_DeductionHeadId = args['OneTimeDeduction_DeductionHeadId']
            if args['OneTimeDeduction_Amount'] is not None:
                deduction.OneTimeDeduction_Amount = args['OneTimeDeduction_Amount']
            if args['OneTimeDeduction_DeductionMonth']:
                deduction.OneTimeDeduction_DeductionMonth = args['OneTimeDeduction_DeductionMonth']
            if args['OneTimeDeduction_ApprovedBy'] is not None:
                deduction.OneTimeDeduction_ApprovedBy = args['OneTimeDeduction_ApprovedBy']
            if args['CreatorId'] is not None:
                deduction.CreatorId = args['CreatorId']
            if args['CreateDate']:
                deduction.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')
            if args['UpdatorId'] is not None:
                deduction.UpdatorId = args['UpdatorId']
            if args['UpdateDate']:
                deduction.UpdateDate = datetime.strptime(args['UpdateDate'], '%Y-%m-%d %H:%M:%S')
            if args['InActive'] is not None:
                deduction.InActive = args['InActive']

            db.session.commit()
            return {"message": "One-time deduction updated", "id": deduction.OneTimeDeduction_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating one-time deduction: {str(e)}")
    
    def delete(self, id):
        deduction = OneTimeDeduction.query.get(id)
        if deduction is None:
            abort(404, message=f"OneTimeDeduction {id} doesn't exist")

        try:
            db.session.delete(deduction)
            db.session.commit()
            return {"message": "One-time deduction deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting one-time deduction: {str(e)}")

class ScheduledDeductionResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            columns = [
                {"field":"ScheduledDeduction_Id", "headerName": "Id", "width": width},
                {"field":"ScheduledDeduction_StaffId", "headerName": "Staff Id", "width": width},
                {"field":"ScheduledDeduction_DeductionHeadId", "headerName": "Deduction head Id", "width": width},
                {"field":"ScheduledDeduction_AmountPerMonth", "headerName": "Amount Per Month", "width": width},
                {"field":"ScheduledDeduction_StartDate", "headerName": "Start Date", "width": width},
                {"field":"ScheduledDeduction_EndDate", "headerName": "End Date", "width": width},
                {"field":"ScheduledDeduction_ApprovedBy", "headerName": "Approved By", "width": width},
                {"field":"CreatorId", "headerName": "Creator Id", "width": width},
                {"field":"CreateDate", "headerName": "Created Date", "width": width},
                {"field":"UpdatorId", "headerName": "Updator Id", "width": width},
                {"field":"UpdateDate", "headerName": "Updated Date", "width": width},
                {"field":"InActive", "headerName": "In Active", "width": width}
            ]
            
            # if id is None:
            if id:
                
                deduction = ScheduledDeduction.query.get(id)
                if deduction is None:
                    abort(404, message=f"Interview schedule {id} doesn't exist")
                
                return {
                    "data": [deduction.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
                
            else:

                query = ScheduledDeduction.query.order_by(ScheduledDeduction.ScheduledDeduction_Id)
                total = query.count()

                # Apply pagination
                deductions = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [deduction.to_dict() for deduction in deductions],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledDeduction_StaffId', type=int, required=True, help="Staff ID is required")
        parser.add_argument('ScheduledDeduction_DeductionHeadId', type=int, required=True, help="Deduction Head ID is required")
        parser.add_argument('ScheduledDeduction_AmountPerMonth', type=float, required=True, help="Amount Per Month is required")
        parser.add_argument('ScheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="Start Date is required and must be in ISO format")
        parser.add_argument('ScheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help="End Date is required and must be in ISO format")
        parser.add_argument('ScheduledDeduction_ApprovedBy', type=int, required=True, help="Approved By is required")
        parser.add_argument('CreatorId', type=int, required=True, help="Creator ID is required")
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('InActive', type=bool, required=True, help="Inactive status is required")
        args = parser.parse_args()

        new_deduction = ScheduledDeduction(
            ScheduledDeduction_StaffId=args['ScheduledDeduction_StaffId'],
            ScheduledDeduction_DeductionHeadId=args['ScheduledDeduction_DeductionHeadId'],
            ScheduledDeduction_AmountPerMonth=args['ScheduledDeduction_AmountPerMonth'],
            ScheduledDeduction_StartDate=args['ScheduledDeduction_StartDate'],
            ScheduledDeduction_EndDate=args['ScheduledDeduction_EndDate'],
            ScheduledDeduction_ApprovedBy=args['ScheduledDeduction_ApprovedBy'],
            CreatorId=args['CreatorId'],
            UpdatorId=args.get('UpdatorId'),
            UpdateDate=args.get('UpdateDate'),
            InActive=args['InActive']
        )

        try:
            db.session.add(new_deduction)
            db.session.commit()
            return {"message": "Scheduled deduction created", "id": new_deduction.ScheduledDeduction_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating scheduled deduction: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledDeduction_StaffId', type=int, required=False)
        parser.add_argument('ScheduledDeduction_DeductionHeadId', type=int, required=False)
        parser.add_argument('ScheduledDeduction_AmountPerMonth', type=float, required=False)
        parser.add_argument('ScheduledDeduction_StartDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('ScheduledDeduction_EndDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('ScheduledDeduction_ApprovedBy', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('InActive', type=bool, required=False)
        args = parser.parse_args()

        deduction = ScheduledDeduction.query.get(id)
        if not deduction:
            abort(404, message=f"Scheduled Deduction {id} does not exist")

        try:
            if args.get('ScheduledDeduction_StaffId') is not None:
                deduction.ScheduledDeduction_StaffId = args['ScheduledDeduction_StaffId']
            if args.get('ScheduledDeduction_DeductionHeadId') is not None:
                deduction.ScheduledDeduction_DeductionHeadId = args['ScheduledDeduction_DeductionHeadId']
            if args.get('ScheduledDeduction_AmountPerMonth') is not None:
                deduction.ScheduledDeduction_AmountPerMonth = args['ScheduledDeduction_AmountPerMonth']
            if args.get('ScheduledDeduction_StartDate') is not None:
                deduction.ScheduledDeduction_StartDate = args['ScheduledDeduction_StartDate']
            if args.get('ScheduledDeduction_EndDate') is not None:
                deduction.ScheduledDeduction_EndDate = args['ScheduledDeduction_EndDate']
            if args.get('ScheduledDeduction_ApprovedBy') is not None:
                deduction.ScheduledDeduction_ApprovedBy = args['ScheduledDeduction_ApprovedBy']
            if args.get('CreatorId') is not None:
                deduction.CreatorId = args['CreatorId']
            if args.get('UpdatorId') is not None:
                deduction.UpdatorId = args['UpdatorId']
            
            deduction.UpdateDate = datetime.utcnow()
            if args.get('InActive') is not None:
                deduction.InActive = args['InActive']

            db.session.commit()
            return {"message": "Scheduled deduction updated", "id": deduction.ScheduledDeduction_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating scheduled deduction: {str(e)}")

    def delete(self, id):
        deduction = ScheduledDeduction.query.get(id)
        if not deduction:
            abort(404, message=f"Scheduled Deduction {id} does not exist")

        try:
            db.session.delete(deduction)
            db.session.commit()
            return {"message": "Scheduled deduction deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting scheduled deduction: {str(e)}")

class IARResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
        
            columns = [
                {"field":"id", "headerName": "id", "width": width},
                {"field":"form_Id", "headerName": "Form Id", "width": width},
                {"field":"IAR_Type_Id", "headerName": "IAR Type Id", "width": width},
                {"field":"status_Check", "headerName": "Status Check", "width": width},
                {"field":"remarks", "headerName": "Remarks", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createdDate", "headerName": "Created Date", "width": width}
            ]
            
            if id:
                
                iar = IAR.query.get(id)
                if iar is None:
                    abort(404, message=f"IAR {id} doesn't exist")
                
                return {
                    "data": [iar.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = IAR.query.order_by(IAR.Id)
                total = query.count()

                # Apply pagination
                iars = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [iar.to_dict() for iar in iars],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500
                
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Form_Id', type=int, required=True, help="Form ID is required")
        parser.add_argument('IAR_Type_Id', type=int, required=True, help="IAR Type ID is required")
        parser.add_argument('Status_Check', type=bool, required=True, help="Status Check is required")
        parser.add_argument('Remarks', type=str, required=True, help="Remarks are required")
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_iar = IAR(
                Form_Id=args['Form_Id'],
                IAR_Type_Id=args['IAR_Type_Id'],
                Status_Check=args['Status_Check'],
                Remarks=args['Remarks'],
                CreatorId=args.get('CreatorId'),
                CreatedDate=datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S') if args['CreatedDate'] else datetime.utcnow()
            )
            db.session.add(new_iar)
            db.session.commit()
            return {"message": "IAR created", "id": new_iar.Id}, 200
        except ValueError as ve:
            db.session.rollback()
            return {"error": f"Value error: {str(ve)}"}, 400
        except TypeError as te:
            db.session.rollback()
            return jsonify({"error": f"Type error: {str(te)}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Error creating IAR: {str(e)}"}), 400
        
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Form_Id', type=int, required=False)
        parser.add_argument('IAR_Type_Id', type=int, required=False)
        parser.add_argument('Status_Check', type=bool, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        args = parser.parse_args()

        iar = IAR.query.get(id)
        if iar is None:
            abort(404, message=f"IAR {id} doesn't exist")

        try:
            if args['Form_Id'] is not None:
                iar.form_Id = args['form_Id']
            if args['IAR_Type_Id'] is not None:
                iar.IAR_Type_Id = args['IAR_Type_Id']
            if args['Status_Check'] is not None:
                iar.Status_Check = args['Status_Check']
            if args['Remarks'] is not None:
                iar.Remarks = args['Remarks']
            if args['CreatorId'] is not None:
                iar.CreatorId = args['CreatorId']
            if args['CreatedDate']:
                iar.CreatedDate = datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S')

            db.session.commit()
            return {"message": "IAR updated", "id": iar.Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR: {str(e)}")

    def delete(self, id):
        iar = IAR.query.get(id)
        if iar is None:
            abort(404, message=f"IAR {id} doesn't exist")

        try:
            # Delete related IAR_Remarks entries first
            IAR_Remarks.query.filter_by(IAR_Id=id).delete()
            
            db.session.delete(iar)
            db.session.commit()
            return {"message": "IAR deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR: {str(e)}")

class IARRemarksResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
        
            columns = [
                {"field":"id", "headerName": "id", "width": width},
                {"field":"IAR_Id", "headerName": "IAR id", "width": width},
                {"field":"remarks", "headerName": "Remarks", "width": width},
                {"field":"status", "headerName": "Status", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createDate", "headerName": "Created Date", "width": width}
            ]
            if id is None:
                query = IAR_Remarks.query.order_by(IAR_Remarks.id)
                total = query.count()

                # Apply pagination
                remarks = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [remark.to_dict() for remark in remarks],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                remark = IAR_Remarks.query.get(id)
                if remark is None:
                    abort(404, message=f"IAR_Remarks {id} doesn't exist")
                return {
                    "data": [remark.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('IAR_Id', type=int, required=True, help="IAR ID is required")
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_remark = IAR_Remarks(
                IAR_Id=args['IAR_Id'],
                remarks=args['Remarks'],
                status=args['Status'],
                creatorId=args.get('CreatorId'),
                createDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S') if args['CreateDate'] else datetime.utcnow()
            )
            db.session.add(new_remark)
            db.session.commit()
            return {"message": "IAR_Remarks created", "id": new_remark.id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Remarks: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('IAR_Id', type=int, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=str, required=False)
        args = parser.parse_args()

        remark = IAR_Remarks.query.get(id)
        if remark is None:
            abort(404, message=f"IAR_Remarks {id} doesn't exist")

        try:
            if args['IAR_Id'] is not None:
                remark.IAR_Id = args['IAR_Id']
            if args['Remarks'] is not None:
                remark.Remarks = args['Remarks']
            if args['Status'] is not None:
                remark.Status = args['Status']
            if args['CreatorId'] is not None:
                remark.CreatorId = args['CreatorId']
            if args['CreateDate']:
                remark.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S')

            db.session.commit()
            return {"message": "IAR_Remarks updated", "id": remark.id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR_Remarks: {str(e)}")

    def delete(self, id):
        remark = IAR_Remarks.query.get(id)
        if remark is None:
            abort(404, message=f"IAR_Remarks {id} doesn't exist")

        try:
            db.session.delete(remark)
            db.session.commit()
            return {"message": "IAR_Remarks deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR_Remarks: {str(e)}")

class IARTypesResource(Resource):
    def get(self, id=None, ):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field": "id", "headerName": "Id", "width": width},
                {"field": "name", "headerName": "Name", "width": width}
            ]
            if id:
                iar_type = IAR_Types.query.get(id)
                if iar_type is None:
                    abort(404, message=f"IAR_Types {id} doesn't exist")
                return {
                    "data": [iar_type.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            else:
                query = IAR_Types.query.order_by(IAR_Types.Id)
                total = query.count()

                # Apply pagination
                types = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [iar_type.to_dict() for iar_type in types],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
                
        except NotFound as e:
            return {"error": str(e)}, 404
        
        except BadRequest as e:
            return {"error": str(e)}, 400
        
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=True, help="Name is required")
        args = parser.parse_args()

        try:
            new_type = IAR_Types(name=args['Name'])
            db.session.add(new_type)
            db.session.commit()
            return jsonify({"message": "IAR_Types created", "id": new_type.Id}), 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating IAR_Types: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        iar_type = IAR_Types.query.get(id)
        if iar_type is None:
            abort(404, message=f"IAR_Types {id} doesn't exist")

        try:
            if args['Name'] is not None:
                iar_type.name = args['Name']

            db.session.commit()
            return jsonify({"message": "IAR_Types updated", "id": iar_type.Id}), 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating IAR_Types: {str(e)}")

    def delete(self, id):
        iar_type = IAR_Types.query.get(id)
        if iar_type is None:
            abort(404, message=f"IAR_Types {id} doesn't exist")

        try:
            db.session.delete(iar_type)
            db.session.commit()
            return jsonify({"message": "IAR_Types deleted"}), 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting IAR_Types: {str(e)}")

class EmailTypesResource(Resource):
    
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}

            columns = [
                {"field":"id", "headerName": "Id", "width": width},
                {"field":"name", "headerName": "Name", "width": width},
            ]
            
            if id is None:
                query = EmailTypes.query.order_by(EmailTypes.id)
                total = query.count()

                # Apply pagination
                email_types = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [email_type.to_dict() for email_type in email_types],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            
            else:
                email_type = EmailTypes.query.get(id)
                if email_type is None:
                    abort(404, message=f"EmailTypes {id} doesn't exist")
                
                return {
                    "data": [email_type.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        try:
            new_email_type = EmailTypes(name=args['Name'])
            db.session.add(new_email_type)
            db.session.commit()
            return {"message": "EmailTypes created", "id": new_email_type.Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailTypes: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Name', type=str, required=False)
        args = parser.parse_args()

        email_type = EmailTypes.query.get(id)
        if email_type is None:
            abort(404, message=f"EmailTypes {id} doesn't exist")

        try:
            if args['Name'] is not None:
                email_type.Name = args['Name']
            db.session.commit()
            return {"message": "EmailTypes updated", "id": email_type.Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating EmailTypes: {str(e)}")

    def delete(self, id):
        email_type = EmailTypes.query.get(id)
        if email_type is None:
            abort(404, message=f"EmailTypes {id} doesn't exist")

        try:
            db.session.delete(email_type)
            db.session.commit()
            return {"message": "EmailTypes deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting EmailTypes: {str(e)}")

class EmailStorageSystemResource(Resource):
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                raise {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}

            columns = [
                {"field":"email_Id", "headerName": "", "width": width},
                {"field":"email_Title", "headerName": "", "width": width},
                {"field":"email_Subject", "headerName": "", "width": width},
                {"field":"email_Body", "headerName": "", "width": width},
                {"field":"status", "headerName": "", "width": width},
                {"field":"creatorId", "headerName": "", "width": width},
                {"field":"createdDate", "headerName": "", "width": width},
                {"field":"updatorId", "headerName": "", "width": width},
                {"field":"updatedDate", "headerName": "", "width": width},
                {"field":"emailType", "headerName": "", "width": width}
            ]
            if id is None:
                
                query = EmailStorageSystem.query.order_by(EmailStorageSystem.email_Id)
                total = query.count()

                # Apply pagination
                emails = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [email.to_dict() for email in emails],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                email = EmailStorageSystem.query.get(id)
                if email is None:
                    abort(404, message=f"EmailStorageSystem {id} doesn't exist")
                return {
                    "data": [email.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Email_Title', type=str, required=False)
        parser.add_argument('Email_Subject', type=str, required=False)
        parser.add_argument('Email_Body', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdatedDate', type=str, required=False)
        parser.add_argument('EmailType', type=int, required=False)
        args = parser.parse_args()

        try:
            new_email = EmailStorageSystem(
                Email_Title=args['Email_Title'],
                Email_Subject=args['Email_Subject'],
                Email_Body=args['Email_Body'],
                Status=args['Status'],
                CreatorId=args.get('CreatorId'),
                CreatedDate=datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S') if args['CreatedDate'] else datetime.utcnow(),
                UpdatorId=args.get('UpdatorId'),
                UpdatedDate=datetime.strptime(args['UpdatedDate'], '%Y-%m-%d %H:%M:%S') if args['UpdatedDate'] else None,
                EmailType=args.get('EmailType')
            )
            db.session.add(new_email)
            db.session.commit()
            return {"message": "EmailStorageSystem created", "Email_Id": new_email.email_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating EmailStorageSystem: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Email_Title', type=str, required=False)
        parser.add_argument('Email_Subject', type=str, required=False)
        parser.add_argument('Email_Body', type=str, required=False)
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatedDate', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=False)
        parser.add_argument('UpdatedDate', type=str, required=False)
        parser.add_argument('EmailType', type=int, required=False)
        args = parser.parse_args()

        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")

        try:
            if args['Email_Title'] is not None:
                email.Email_Title = args['Email_Title']
            if args['Email_Subject'] is not None:
                email.Email_Subject = args['Email_Subject']
            if args['Email_Body'] is not None:
                email.Email_Body = args['Email_Body']
            if args['Status'] is not None:
                email.Status = args['Status']
            if args['CZeatorId'] is not None:
                email.CreatorId = args['CreatorId']
            if args['CreatedDate']:
                email.CreatedDate = datetime.strptime(args['CreatedDate'], '%Y-%m-%d %H:%M:%S')
            if args['UpdatorId'] is not None:
                email.UpdatorId = args['UpdatorId']
            
            email.UpdatedDate = datetime.strptime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
            
            if args['EmailType'] is not None:
                email.EmailType = args['EmailType']
            db.session.commit()
            return {"message": "EmailStorageSystem updated", "Email_Id": email.Email_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating EmailStorageSystem: {str(e)}")

    def delete(self, id):
        email = EmailStorageSystem.query.get(id)
        if email is None:
            abort(404, message=f"EmailStorageSystem {id} doesn't exist")

        try:
            db.session.delete(email)
            db.session.commit()
            return {"message": "EmailStorageSystem deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting EmailStorageSystem: {str(e)}")

class AvailableJobsResource(Resource):
    @jwt_required()
    def get(self, id=None):
        
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            columns = [
                {"field":"job_Id", "headerName": "Id", "width": width},
                {"field":"job_Title", "headerName": "Title", "width": width},
                {"field":"job_Level", "headerName": "Level", "width": width},
                {"field":"job_PostedBy", "headerName": "Posted By", "width": width},
                {"field":"job_Status", "headerName": "Status", "width": width},
                {"field":"creatorId", "headerName": "Creator Id", "width": width},
                {"field":"createdDate", "headerName": "Created Date", "width": width},
                {"field":"updatorId", "headerName": "Updator Id", "width": width},
                {"field":"updatedDate", "headerName": "Updated Date", "width": width}
            ]
            if id is None:
                query = AvailableJobs.query.order_by(AvailableJobs.job_Id)
                total = query.count()

                # Apply pagination
                jobs = query.paginate(page=page_no, per_page=page_size, error_out=False).items

                return {
                    "data": [job.to_dict() for job in jobs],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "columns": columns
                }, 200
            else:
                job = AvailableJobs.query.get(id)
                if job is None:
                    abort(404, message=f"AvailableJobs {id} doesn't exist")
                return {
                    "data": [job.to_dict()],
                    "total": 1,
                    "pageNo": page_no,
                    "pageSize": page_size, 
                    "columns": columns
                }, 200
            
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('job_Title', type=str, required=True, help="Job Title is required")
        parser.add_argument('job_Level', type=str, required=True, help="Job Level is required")
        parser.add_argument('job_PostedBy', type=int, required=False)
        parser.add_argument('job_Status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        args = parser.parse_args()

        try:
            new_job = AvailableJobs(
                job_Title=args['job_Title'],
                job_Level=args['job_Level'],
                job_PostedBy=args.get('job_PostedBy'),
                job_Status=args.get('job_Status'),
                creatorId=args.get('creatorId'),
                createdDate=datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S') if args['createdDate'] else datetime.utcnow(),
                updatorId=args.get('updatorId'),
                updatedDate=datetime.strptime(args['updatedDate'], '%Y-%m-%d %H:%M:%S') if args['updatedDate'] else None
            )
            db.session.add(new_job)
            db.session.commit()
            return {"message": "AvailableJobs created", "job_Id": new_job.job_Id}, 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error creating AvailableJobs: {str(e)}")

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('job_Title', type=str, required=False)
        parser.add_argument('job_Level', type=str, required=False)
        parser.add_argument('job_PostedBy', type=int, required=False)
        parser.add_argument('job_Status', type=bool, required=False)
        parser.add_argument('creatorId', type=int, required=False)
        parser.add_argument('createdDate', type=str, required=False)
        parser.add_argument('updatorId', type=int, required=False)
        parser.add_argument('updatedDate', type=str, required=False)
        args = parser.parse_args()

        job = AvailableJobs.query.get(id)
        if job is None:
            abort(404, message=f"AvailableJobs {id} doesn't exist")

        try:
            if args['job_Title'] is not None:
                job.job_Title = args['job_Title']
            if args['job_Level'] is not None:
                job.job_Level = args['job_Level']
            if args['job_PostedBy'] is not None:
                job.job_PostedBy = args['job_PostedBy']
            if args['job_Status'] is not None:
                job.job_Status = args['job_Status']
            if args['creatorId'] is not None:
                job.creatorId = args['creatorId']
            if args['createdDate']:
                job.createdDate = datetime.strptime(args['createdDate'], '%Y-%m-%d %H:%M:%S')
            if args['updatorId'] is not None:
                job.updatorId = args['updatorId']
            
            job.updatedDate = datetime.strptime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
            db.session.commit()
            return {"message": "AvailableJobs updated", "job_Id": job.job_Id}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error updating AvailableJobs: {str(e)}")

    def delete(self, id):
        job = AvailableJobs.query.get(id)
        if job is None:
            abort(404, message=f"AvailableJobs {id} doesn't exist")

        try:
            db.session.delete(job)
            db.session.commit()
            return {"message": "AvailableJobs deleted"}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=f"Error deleting AvailableJobs: {str(e)}")

class StaffInfoResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            if id:
                staff = StaffInfo.query.get_or_404(id)
                print("Date of Joining: ", staff.S_JoiningDate)
                
                return json.loads(json.dumps({
                    "Employee Name": str(staff.Staff_ID) + " | " + staff.S_Name,
                    "Designation": staff.Designation_ID,
                    "Campus": staff.CampusId,
                    "Department": staff.DepartmentId,
                    "Date of Joining": staff.S_JoiningDate
                    }, indent=4, cls=DateTimeEncoder)), 200
            else:
                
                query = StaffInfo.query.order_by(StaffInfo.Staff_ID)
                total = query.count()
                
                paginated_staff = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                
                return {
                    "data": [json.loads(json.dumps(staff.to_dict())) for staff in paginated_staff],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                }, 200
        except Exception as e:
            return {"error": str(e)}, 500
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Personal_ID', type=str)
        parser.add_argument('S_Name', type=str, required=True, help='Name is required')
        parser.add_argument('S_FName', type=str)
        parser.add_argument('S_Gender', type=int, required=True, help='Gender is required')
        parser.add_argument('S_CNIC', type=str)
        parser.add_argument('S_Email', type=str)
        parser.add_argument('S_ContactNo', type=str)
        parser.add_argument('S_DoB', type=str, required=True, help='Date of Birth is required')
        parser.add_argument('S_JoiningDate', type=str, required=True, help='Joining Date is required')
        parser.add_argument('S_firstJOrderNo', type=str)
        parser.add_argument('S_JoiningDesg', type=int)
        parser.add_argument('S_JoiningGrade', type=int)
        parser.add_argument('S_firstJPlace', type=str)
        parser.add_argument('S_PresentDesignation', type=int)
        parser.add_argument('S_PresentGrade', type=int)
        parser.add_argument('S_SchoolName', type=str)
        parser.add_argument('S_District', type=str)
        parser.add_argument('S_Union', type=str)
        parser.add_argument('S_WardNo', type=str)
        parser.add_argument('S_Village', type=str)
        parser.add_argument('Designation_ID', type=int, required=True, help='Designation ID is required')
        parser.add_argument('Grade_ID', type=int)
        parser.add_argument('IsActive', type=bool, required=True, help='IsActive is required')
        parser.add_argument('IsNonTeacher', type=bool, required=True, help='IsNonTeacher is required')
        parser.add_argument('S_Salary', type=float)
        parser.add_argument('UpdaterId', type=int)
        parser.add_argument('UpdaterIP', type=str)
        parser.add_argument('UpdaterTerminal', type=str)
        parser.add_argument('UpdateDate', type=str)
        parser.add_argument('CreatorId', type=int)
        parser.add_argument('CreatorIP', type=str)
        parser.add_argument('CreatorTerminal', type=str)
        parser.add_argument('CreateDate', type=str)
        parser.add_argument('PhotoPath', type=str)
        parser.add_argument('IsDisable', type=bool, required=True, help='IsDisable is required')
        parser.add_argument('disableDetail', type=str)
        parser.add_argument('EOBI', type=str)
        parser.add_argument('ProbationPeriod', type=float)
        parser.add_argument('ProbationEndDate', type=str)
        parser.add_argument('IsPermanent', type=bool, required=True, help='IsPermanent is required')
        parser.add_argument('IsTerminate', type=bool)
        parser.add_argument('DepartmentId', type=int)
        parser.add_argument('HouseNo', type=str)
        parser.add_argument('Street_Sector_BlockNo', type=str)
        parser.add_argument('AreaId', type=int)
        parser.add_argument('CityId', type=int)
        parser.add_argument('District', type=str)
        parser.add_argument('Province', type=str)
        parser.add_argument('CountryId', type=int)
        parser.add_argument('PresentAddress', type=str)
        parser.add_argument('TempAddress', type=str)
        parser.add_argument('Whatsapp', type=str)
        parser.add_argument('EmergencyContactName', type=str)
        parser.add_argument('EmergencyContactNo', type=str)
        parser.add_argument('HomeNo', type=str)
        parser.add_argument('Rent_Personal', type=str)
        parser.add_argument('MaritalStatus', type=str)
        parser.add_argument('AccountTitle', type=str)
        parser.add_argument('AccountNo', type=str)
        parser.add_argument('BankName', type=str)
        parser.add_argument('Branch', type=str)
        parser.add_argument('IsFatherName', type=bool)
        parser.add_argument('FHWName', type=str)
        parser.add_argument('FHWCNIC', type=str)
        parser.add_argument('FWHDOB', type=str)
        parser.add_argument('CampusId', type=int)
        parser.add_argument('BarcodeId', type=str, required=True, help='BarcodeId is required')
        parser.add_argument('IsAppearLive', type=bool, required=True, help='IsAppearLive is required')
        parser.add_argument('Category', type=int)
        parser.add_argument('FId', type=int)
        parser.add_argument('Initials', type=str)
        parser.add_argument('IsSalaryOn', type=bool)
        parser.add_argument('EmpId', type=int)
        parser.add_argument('IsAEN', type=int)
        parser.add_argument('ReportingOfficerId', type=int)
        parser.add_argument('FileNumber', type=int)
        parser.add_argument('FileLocation', type=str)
        parser.add_argument('IsExit', type=bool)
        parser.add_argument('Grace_In', type=int)
        parser.add_argument('Grace_Out', type=int)
        parser.add_argument('ShiftType', type=int)
        args = parser.parse_args()

        try:
            new_staff = StaffInfo(
                Personal_ID=args['Personal_ID'],
                S_Name=args['S_Name'],
                S_FName=args['S_FName'],
                S_Gender=args['S_Gender'],
                S_CNIC=args['S_CNIC'],
                S_Email=args['S_Email'],
                S_ContactNo=args['S_ContactNo'],
                S_DoB=datetime.strptime(args['S_DoB'], '%Y-%m-%d'),
                S_JoiningDate=datetime.strptime(args['S_JoiningDate'], '%Y-%m-%d'),
                S_firstJOrderNo=args['S_firstJOrderNo'],
                S_JoiningDesg=args['S_JoiningDesg'],
                S_JoiningGrade=args['S_JoiningGrade'],
                S_firstJPlace=args['S_firstJPlace'],
                S_PresentDesignation=args['S_PresentDesignation'],
                S_PresentGrade=args['S_PresentGrade'],
                S_SchoolName=args['S_SchoolName'],
                S_District=args['S_District'],
                S_Union=args['S_Union'],
                S_WardNo=args['S_WardNo'],
                S_Village=args['S_Village'],
                Designation_ID=args['Designation_ID'],
                Grade_ID=args['Grade_ID'],
                IsActive=args['IsActive'],
                IsNonTeacher=args['IsNonTeacher'],
                S_Salary=args['S_Salary'],
                UpdaterId=args['UpdaterId'],
                UpdaterIP=args['UpdaterIP'],
                UpdaterTerminal=args['UpdaterTerminal'],
                UpdateDate=datetime.strptime(args['UpdateDate'], '%Y-%m-%d') if args['UpdateDate'] else None,
                CreatorId=args['CreatorId'],
                CreatorIP=args['CreatorIP'],
                CreatorTerminal=args['CreatorTerminal'],
                CreateDate=datetime.strptime(args['CreateDate'], '%Y-%m-%d %H:%M:%S') if args['CreateDate'] else datetime.utcnow(),
                PhotoPath=args['PhotoPath'],
                IsDisable=args['IsDisable'],
                disableDetail=args['disableDetail'],
                EOBI=args['EOBI'],
                ProbationPeriod=args['ProbationPeriod'],
                ProbationEndDate=datetime.strptime(args['ProbationEndDate'], '%Y-%m-%d') if args['ProbationEndDate'] else None,
                IsPermanent=args['IsPermanent'],
                IsTerminate=args['IsTerminate'],
                DepartmentId=args['DepartmentId'],
                HouseNo=args['HouseNo'],
                Street_Sector_BlockNo=args['Street_Sector_BlockNo'],
                AreaId=args['AreaId'],
                CityId=args['CityId'],
                District=args['District'],
                Province=args['Province'],
                CountryId=args['CountryId'],
                PresentAddress=args['PresentAddress'],
                TempAddress=args['TempAddress'],
                Whatsapp=args['Whatsapp'],
                EmergencyContactName=args['EmergencyContactName'],
                EmergencyContactNo=args['EmergencyContactNo'],
                HomeNo=args['HomeNo'],
                Rent_Personal=args['Rent_Personal'],
                MaritalStatus=args['MaritalStatus'],
                AccountTitle=args['AccountTitle'],
                AccountNo=args['AccountNo'],
                BankName=args['BankName'],
                Branch=args['Branch'],
                IsFatherName=args['IsFatherName'],
                FHWName=args['FHWName'],
                FHWCNIC=args['FHWCNIC'],
                FWHDOB=datetime.strptime(args['FWHDOB'], '%Y-%m-%d') if args['FWHDOB'] else None,
                CampusId=args['CampusId'],
                BarcodeId=args['BarcodeId'],
                IsAppearLive=args['IsAppearLive'],
                Category=args['Category'],
                FId=args['FId'],
                Initials=args['Initials'],
                IsSalaryOn=args['IsSalaryOn'],
                EmpId=args['EmpId'],
                IsAEN=args['IsAEN'],
                ReportingOfficerId=args['ReportingOfficerId'],
                FileNumber=args['FileNumber'],
                FileLocation=args['FileLocation'],
                IsExit=args['IsExit'],
                Grace_In=args['Grace_In'],
                Grace_Out=args['Grace_Out'],
                ShiftType=args['ShiftType'],
            )

            db.session.add(new_staff)
            db.session.commit()
            return new_staff.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('Personal_ID', type=str)
        parser.add_argument('S_Name', type=str)
        parser.add_argument('S_FName', type=str)
        parser.add_argument('S_Gender', type=int)
        parser.add_argument('S_CNIC', type=str)
        parser.add_argument('S_Email', type=str)
        parser.add_argument('S_ContactNo', type=str)
        parser.add_argument('S_DoB', type=str)
        parser.add_argument('S_JoiningDate', type=str)
        parser.add_argument('S_firstJOrderNo', type=str)
        parser.add_argument('S_JoiningDesg', type=int)
        parser.add_argument('S_JoiningGrade', type=int)
        parser.add_argument('S_firstJPlace', type=str)
        parser.add_argument('S_PresentDesignation', type=int)
        parser.add_argument('S_PresentGrade', type=int)
        parser.add_argument('S_SchoolName', type=str)
        parser.add_argument('S_District', type=str)
        parser.add_argument('S_Union', type=str)
        parser.add_argument('S_WardNo', type=str)
        parser.add_argument('S_Village', type=str)
        parser.add_argument('Designation_ID', type=int)
        parser.add_argument('Grade_ID', type=int)
        parser.add_argument('IsActive', type=bool)
        parser.add_argument('IsNonTeacher', type=bool)
        parser.add_argument('S_Salary', type=float)
        parser.add_argument('UpdaterId', type=int)
        parser.add_argument('UpdaterIP', type=str)
        parser.add_argument('UpdaterTerminal', type=str)
        parser.add_argument('UpdateDate', type=str)
        parser.add_argument('CreatorId', type=int)
        parser.add_argument('CreatorIP', type=str)
        parser.add_argument('CreatorTerminal', type=str)
        parser.add_argument('CreateDate', type=str)
        parser.add_argument('PhotoPath', type=str)
        parser.add_argument('IsDisable', type=bool)
        parser.add_argument('disableDetail', type=str)
        parser.add_argument('EOBI', type=str)
        parser.add_argument('ProbationPeriod', type=float)
        parser.add_argument('ProbationEndDate', type=str)
        parser.add_argument('IsPermanent', type=bool)
        parser.add_argument('IsTerminate', type=bool)
        parser.add_argument('DepartmentId', type=int)
        parser.add_argument('HouseNo', type=str)
        parser.add_argument('Street_Sector_BlockNo', type=str)
        parser.add_argument('AreaId', type=int)
        parser.add_argument('CityId', type=int)
        parser.add_argument('District', type=str)
        parser.add_argument('Province', type=str)
        parser.add_argument('CountryId', type=int)
        parser.add_argument('PresentAddress', type=str)
        parser.add_argument('TempAddress', type=str)
        parser.add_argument('Whatsapp', type=str)
        parser.add_argument('EmergencyContactName', type=str)
        parser.add_argument('EmergencyContactNo', type=str)
        parser.add_argument('HomeNo', type=str)
        parser.add_argument('Rent_Personal', type=str)
        parser.add_argument('MaritalStatus', type=str)
        parser.add_argument('AccountTitle', type=str)
        parser.add_argument('AccountNo', type=str)
        parser.add_argument('BankName', type=str)
        parser.add_argument('Branch', type=str)
        parser.add_argument('IsFatherName', type=bool)
        parser.add_argument('FHWName', type=str)
        parser.add_argument('FHWCNIC', type=str)
        parser.add_argument('FWHDOB', type=str)
        parser.add_argument('CampusId', type=int)
        parser.add_argument('BarcodeId', type=str)
        parser.add_argument('IsAppearLive', type=bool)
        parser.add_argument('Category', type=int)
        parser.add_argument('FId', type=int)
        parser.add_argument('Initials', type=str)
        parser.add_argument('IsSalaryOn', type=bool)
        parser.add_argument('EmpId', type=int)
        parser.add_argument('IsAEN', type=int)
        parser.add_argument('ReportingOfficerId', type=int)
        parser.add_argument('FileNumber', type=int)
        parser.add_argument('FileLocation', type=str)
        parser.add_argument('IsExit', type=bool)
        parser.add_argument('Grace_In', type=int)
        parser.add_argument('Grace_Out', type=int)
        parser.add_argument('ShiftType', type=int)
        args = parser.parse_args()

        try:
            staff = StaffInfo.query.get_or_404(id)

            if args['Personal_ID'] is not None:
                staff.Personal_ID = args['Personal_ID']
            if args['S_Name'] is not None:
                staff.S_Name = args['S_Name']
            if args['S_FName'] is not None:
                staff.S_FName = args['S_FName']
            if args['S_Gender'] is not None:
                staff.S_Gender = args['S_Gender']
            if args['S_CNIC'] is not None:
                staff.S_CNIC = args['S_CNIC']
            if args['S_Email'] is not None:
                staff.S_Email = args['S_Email']
            if args['S_ContactNo'] is not None:
                staff.S_ContactNo = args['S_ContactNo']
            if args['S_DoB'] is not None:
                staff.S_DoB = datetime.strptime(args['S_DoB'], '%Y-%m-%d')
            if args['S_JoiningDate'] is not None:
                staff.S_JoiningDate = datetime.strptime(args['S_JoiningDate'], '%Y-%m-%d')
            if args['S_firstJOrderNo'] is not None:
                staff.S_firstJOrderNo = args['S_firstJOrderNo']
            if args['S_JoiningDesg'] is not None:
                staff.S_JoiningDesg = args['S_JoiningDesg']
            if args['S_JoiningGrade'] is not None:
                staff.S_JoiningGrade = args['S_JoiningGrade']
            if args['S_firstJPlace'] is not None:
                staff.S_firstJPlace = args['S_firstJPlace']
            if args['S_PresentDesignation'] is not None:
                staff.S_PresentDesignation = args['S_PresentDesignation']
            if args['S_PresentGrade'] is not None:
                staff.S_PresentGrade = args['S_PresentGrade']
            if args['S_SchoolName'] is not None:
                staff.S_SchoolName = args['S_SchoolName']
            if args['S_District'] is not None:
                staff.S_District = args['S_District']
            if args['S_Union'] is not None:
                staff.S_Union = args['S_Union']
            if args['S_WardNo'] is not None:
                staff.S_WardNo = args['S_WardNo']
            if args['S_Village'] is not None:
                staff.S_Village = args['S_Village']
            if args['Designation_ID'] is not None:
                staff.Designation_ID = args['Designation_ID']
            if args['Grade_ID'] is not None:
                staff.Grade_ID = args['Grade_ID']
            if args['IsActive'] is not None:
                staff.IsActive = args['IsActive']
            if args['IsNonTeacher'] is not None:
                staff.IsNonTeacher = args['IsNonTeacher']
            if args['S_Salary'] is not None:
                staff.S_Salary = args['S_Salary']
            if args['UpdaterId'] is not None:
                staff.UpdaterId = args['UpdaterId']
            if args['UpdaterIP'] is not None:
                staff.UpdaterIP = args['UpdaterIP']
            if args['UpdaterTerminal'] is not None:
                staff.UpdaterTerminal = args['UpdaterTerminal']
            
            staff.UpdateDate = datetime.strptime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
            if args['CreatorId'] is not None:
                staff.CreatorId = args['CreatorId']
            if args['CreatorIP'] is not None:
                staff.CreatorIP = args['CreatorIP']
            if args['CreatorTerminal'] is not None:
                staff.CreatorTerminal = args['CreatorTerminal']
            if args['CreateDate'] is not None:
                staff.CreateDate = datetime.strptime(args['CreateDate'], '%Y-%m-%d')
            if args['PhotoPath'] is not None:
                staff.PhotoPath = args['PhotoPath']
            if args['IsDisable'] is not None:
                staff.IsDisable = args['IsDisable']
            if args['disableDetail'] is not None:
                staff.disableDetail = args['disableDetail']
            if args['EOBI'] is not None:
                staff.EOBI = args['EOBI']
            if args['ProbationPeriod'] is not None:
                staff.ProbationPeriod = args['ProbationPeriod']
            if args['ProbationEndDate'] is not None:
                staff.ProbationEndDate = datetime.strptime(args['ProbationEndDate'], '%Y-%m-%d')
            if args['IsPermanent'] is not None:
                staff.IsPermanent = args['IsPermanent']
            if args['IsTerminate'] is not None:
                staff.IsTerminate = args['IsTerminate']
            if args['DepartmentId'] is not None:
                staff.DepartmentId = args['DepartmentId']
            if args['HouseNo'] is not None:
                staff.HouseNo = args['HouseNo']
            if args['Street_Sector_BlockNo'] is not None:
                staff.Street_Sector_BlockNo = args['Street_Sector_BlockNo']
            if args['AreaId'] is not None:
                staff.AreaId = args['AreaId']
            if args['CityId'] is not None:
                staff.CityId = args['CityId']
            if args['District'] is not None:
                staff.District = args['District']
            if args['Province'] is not None:
                staff.Province = args['Province']
            if args['CountryId'] is not None:
                staff.CountryId = args['CountryId']
            if args['PresentAddress'] is not None:
                staff.PresentAddress = args['PresentAddress']
            if args['TempAddress'] is not None:
                staff.TempAddress = args['TempAddress']
            if args['Whatsapp'] is not None:
                staff.Whatsapp = args['Whatsapp']
            if args['EmergencyContactName'] is not None:
                staff.EmergencyContactName = args['EmergencyContactName']
            if args['EmergencyContactNo'] is not None:
                staff.EmergencyContactNo = args['EmergencyContactNo']
            if args['HomeNo'] is not None:
                staff.HomeNo = args['HomeNo']
            if args['Rent_Personal'] is not None:
                staff.Rent_Personal = args['Rent_Personal']
            if args['MaritalStatus'] is not None:
                staff.MaritalStatus = args['MaritalStatus']
            if args['AccountTitle'] is not None:
                staff.AccountTitle = args['AccountTitle']
            if args['AccountNo'] is not None:
                staff.AccountNo = args['AccountNo']
            if args['BankName'] is not None:
                staff.BankName = args['BankName']
            if args['Branch'] is not None:
                staff.Branch = args['Branch']
            if args['IsFatherName'] is not None:
                staff.IsFatherName = args['IsFatherName']
            if args['FHWName'] is not None:
                staff.FHWName = args['FHWName']
            if args['FHWCNIC'] is not None:
                staff.FHWCNIC = args['FHWCNIC']
            if args['FWHDOB'] is not None:
                staff.FWHDOB = datetime.strptime(args['FWHDOB'], '%Y-%m-%d')
            if args['CampusId'] is not None:
                staff.CampusId = args['CampusId']
            if args['BarcodeId'] is not None:
                staff.BarcodeId = args['BarcodeId']
            if args['IsAppearLive'] is not None:
                staff.IsAppearLive = args['IsAppearLive']
            if args['Category'] is not None:
                staff.Category = args['Category']
            if args['FId'] is not None:
                staff.FId = args['FId']
            if args['Initials'] is not None:
                staff.Initials = args['Initials']
            if args['IsSalaryOn'] is not None:
                staff.IsSalaryOn = args['IsSalaryOn']
            if args['EmpId'] is not None:
                staff.EmpId = args['EmpId']
            if args['IsAEN'] is not None:
                staff.IsAEN = args['IsAEN']
            if args['ReportingOfficerId'] is not None:
                staff.ReportingOfficerId = args['ReportingOfficerId']
            if args['FileNumber'] is not None:
                staff.FileNumber = args['FileNumber']
            if args['FileLocation'] is not None:
                staff.FileLocation = args['FileLocation']
            if args['IsExit'] is not None:
                staff.IsExit = args['IsExit']
            if args['Grace_In'] is not None:
                staff.Grace_In = args['Grace_In']
            if args['Grace_Out'] is not None:
                staff.Grace_Out = args['Grace_Out']
            if args['ShiftType'] is not None:
                staff.ShiftType = args['ShiftType']

            db.session.commit()
            return staff.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    def delete(self, id):
        try:
            staff = StaffInfo.query.get_or_404(id)
            db.session.delete(staff)
            db.session.commit()
            return {"message": "Staff member deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class StaffDepartmentResource(Resource):
    def get(self, id=None):
        try:
            # Parse and validate pagination parameters
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            parser.add_argument('width', type=str, default="150", location='args', help='width must be an string')

            # Check if request content type is JSON and parse the body if so
            if request.content_type == 'application/json':
                parser.add_argument('pageNo', type=int, default=1, location='json', help='Page number must be an integer')
                parser.add_argument('pageSize', type=int, default=10, location='json', help='Page size must be an integer')
                parser.add_argument('width', type=str, default="150", location='json', help='width must be an string')

            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            width = args['width']
            
            if page_no < 1 or page_size < 1:
                return {"error": str(BadRequest("pageNo and pageSize must be positive integers"))}
            
            if id:
                department = StaffDepartment.query.get_or_404(id)
                return jsonify({"data": department.to_dict()})
            else:
                query = StaffDepartment.query.order_by(StaffDepartment.Id)
                total = query.count()
                departments = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                return jsonify({
                    "data": [dept.to_dict() for dept in departments],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                })

        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('DepartmentName', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdaterIP', type=str, required=False)
        parser.add_argument('UpdaterTerminal', type=str, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatorIP', type=str, required=False)
        parser.add_argument('CreatorTerminal', type=str, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('ManagerId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_department = StaffDepartment(
                DepartmentName=args['DepartmentName'],
                status=args['status'],
                UpdaterId=args['UpdaterId'],
                UpdaterIP=args['UpdaterIP'],
                UpdaterTerminal=args['UpdaterTerminal'],
                UpdateDate=args['UpdateDate'],
                CreatorId=args['CreatorId'],
                CreatorIP=args['CreatorIP'],
                CreatorTerminal=args['CreatorTerminal'],
                CreateDate=datetime.utcnow(),
                CampusId=args['CampusId'],
                ManagerId=args['ManagerId']
            )

            db.session.add(new_department)
            db.session.commit()
            return {"message": "Staff department created", "id": new_department.Id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('DepartmentName', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdaterIP', type=str, required=False)
        parser.add_argument('UpdaterTerminal', type=str, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreatorIP', type=str, required=False)
        parser.add_argument('CreatorTerminal', type=str, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('ManagerId', type=int, required=False)
        args = parser.parse_args()

        try:
            department = StaffDepartment.query.get_or_404(id)

            if args['DepartmentName']:
                department.DepartmentName = args['DepartmentName']
            if args['status'] is not None:
                department.status = args['status']
            if args['UpdaterId']:
                department.UpdaterId = args['UpdaterId']
            if args['UpdaterIP']:
                department.UpdaterIP = args['UpdaterIP']
            if args['UpdaterTerminal']:
                department.UpdaterTerminal = args['UpdaterTerminal']
            
            department.UpdateDate = datetime.utcnow()
            
            if args['CreatorId']:
                department.CreatorId = args['CreatorId']
            if args['CreatorIP']:
                department.CreatorIP = args['CreatorIP']
            if args['CreatorTerminal']:
                department.CreatorTerminal = args['CreatorTerminal']
            if args['CreateDate']:
                department.CreateDate = args['CreateDate']
            if args['CampusId']:
                department.CampusId = args['CampusId']
            if args['ManagerId']:
                department.ManagerId = args['ManagerId']

            db.session.commit()
            return {"message": "Staff department updated", "id": department.Id}, 200
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        try:
            department = StaffDepartment.query.get_or_404(id)
            db.session.delete(department)
            db.session.commit()
            return {"message": "Staff department deleted"}, 200
        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class StaffTransferResource(Resource):
    
    def get(self, id=None):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('pageNo', type=int, default=1, location='args', help='Page number must be an integer')
            parser.add_argument('pageSize', type=int, default=10, location='args', help='Page size must be an integer')
            args = parser.parse_args()

            page_no = args['pageNo']
            page_size = args['pageSize']
            
            if id:
                staff_transfer = StaffTransfer.query.get_or_404(id)
                return jsonify({"data": staff_transfer.to_dict()})
            else:
                query = StaffTransfer.query.order_by(StaffTransfer.Id)
                total = query.count()
                transfers = query.paginate(page=page_no, per_page=page_size, error_out=False).items
                return jsonify({
                    "data": [transfer.to_dict() for transfer in transfers],
                    "total": total,
                    "pageNo": page_no,
                    "pageSize": page_size
                })

        except NotFound as e:
            return {"error": str(e)}, 404
        except BadRequest as e:
            return {"error": str(e)}, 400
        except InternalServerError as e:
            return {"error": "An internal server error occurred. Please try again later."}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new staff transfer request.
        Parses incoming request data, creates a new StaffTransfer record,
        and updates related tables within a single transaction.
        """
        # Parse the incoming request data
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=True, help='StaffId is required')
        parser.add_argument('Transfer_Type', type=str, required=True, help='Transfer_Type is required')
        parser.add_argument('Transfer_Date', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='Transfer_Date is required in format %Y-%m-%dT%H:%M:%S')
        parser.add_argument('Reason_for_Transfer', type=str, required=True, help='Reason_for_Transfer is required')
        parser.add_argument('Transfer_from_Campus', type=int, required=True, help='Transfer_from_Campus is required')
        parser.add_argument('Transfer_To_Campus', type=int, required=True, help='Transfer_To_Campus is required')
        parser.add_argument('DepartmentId', type=int, required=True, help='DepartmentId is required')
        parser.add_argument('DesignationId', type=int, required=True, help='DesignationId is required')
        parser.add_argument('ReportingOfficerId', type=int, required=True, help='ReportingOfficerId is required')
        parser.add_argument('Transfer_initiated_by', type=int, required=True, help='Transfer_initiated_by is required')
        parser.add_argument('Transfer_approval', type=int, required=True, help='Transfer_approval is required')
        parser.add_argument('Remarks', type=str, required=True, help='Remarks is required')
        args = parser.parse_args()

        try:
            # Retrieve the staff record
            staff = StaffInfo.query.get(args['StaffId'])
            if staff is None:
                return {"message": "Staff not found"}, 404

            # Determine the from_campus_id based on the IsAEN flag
            from_campus_id = 11 if staff.IsAEN == 1 else staff.CampusId
            to_campus_id = args['Transfer_To_Campus']

            # Create a new StaffTransfer record
            new_transfer = StaffTransfer(
                StaffId=args['StaffId'],
                Transfer_Type=args['Transfer_Type'],
                Transfer_Date=args['Transfer_Date'],
                Reason_for_Transfer=args['Reason_for_Transfer'],
                Transfer_from_Campus=from_campus_id,
                Transfer_To_Campus=to_campus_id,
                DepartmentId=args['DepartmentId'],
                DesignationId=args['DesignationId'],
                ReportingOfficerId=args['ReportingOfficerId'],
                Transfer_initiated_by=args['Transfer_initiated_by'],
                Transfer_approval=args['Transfer_approval'],
                Remarks=args['Remarks'],
                status=True,
                CampusId=from_campus_id,
                # CreatorId=get_jwt_identity(),
                CreateDate=datetime.utcnow()
            )

            # Start a database transaction
            with db.session.begin_nested():
                db.session.add(new_transfer)
                db.session.flush()

                # Update related tables
                self.update_staff_info(args['StaffId'], to_campus_id, args['ReportingOfficerId'], args['DepartmentId'], args['DesignationId'])
                self.update_staff_shift(args['StaffId'], to_campus_id)
                self.update_user_campus(args['StaffId'], to_campus_id, staff.CampusId)
                self.update_user(args['StaffId'], to_campus_id)

            # Commit the transaction
            db.session.commit()
            return {"message": "Staff transfer created and related tables updated successfully"}, 201
        except SQLAlchemyError as e:
            # Rollback transaction in case of database error
            db.session.rollback()
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            # Rollback transaction in case of any unexpected error
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def update_staff_info(self, staff_id, to_campus_id, reporting_officer_id, department_id, designation_id):
        """
        Updates the StaffInfo table with the new transfer details, 
        including setting the IsAEN flag if transferring to campus 11.
        """
        staff = StaffInfo.query.get(staff_id)
        if to_campus_id == 11:
            staff.IsAEN = 1  # Set IsAEN flag if transferring to campus 11
        else:
            staff.IsAEN = 0  # Unset IsAEN flag for other campuses
        
        staff.CampusId = to_campus_id
        staff.DepartmentId = department_id
        staff.Designation_ID = designation_id
        staff.ReportingOfficerId = reporting_officer_id
        staff.UpdateDate = datetime.utcnow()
        db.session.add(staff)

    def update_staff_shift(self, staff_id, to_campus_id):
        """
        Updates the StaffShift table with the new campus ID and sets the UpdatedOn date.
        """
        staff_shift = StaffShift.query.filter_by(StaffId=staff_id).first()
        
        if staff_shift:
            staff_shift.CampusId = to_campus_id
            staff_shift.UpdatedOn = datetime.utcnow()
            db.session.add(staff_shift)

    def update_user_campus(self, staff_id, to_campus_id, current_campus_id):
        """
        Updates the UserCampus table with the new campus ID.
        Inserts a new record if necessary.
        """
        user_campus = UserCampus.query.filter_by(staffId=staff_id, campusId=current_campus_id).first()
        
        if user_campus:
            user_campus.campusId = to_campus_id
            user_campus.updateDate = datetime.utcnow()
            db.session.add(user_campus)
        else:
            user_id = UserCampus.query.filter_by(staffId=staff_id).first().userId
            
            new_user_campus = UserCampus(
                userId=user_id,
                campusId=to_campus_id,
                staffId=staff_id,
                date=datetime.utcnow(),
                status=True
            )
            db.session.add(new_user_campus)

    def update_user(self, staff_id, to_campus_id):
        """
        Updates the Users table with the new campus ID and sets the IsAEN flag if transferring to campus 11
        """
        user_id = UserCampus.query.filter_by(staffId=staff_id).first().userId
        user = Users.query.get(user_id)
        
        if to_campus_id == 11:
            user.IsAEN = 1  # Set IsAEN flag if transferring to campus 11
        else:
            user.IsAEN = 0  # Unset IsAEN flag for other campuses
        
        user.campusId = to_campus_id
        user.updateDate = datetime.utcnow()
        db.session.add(user)
    
    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=False)
        parser.add_argument('Transfer_Type', type=str, required=False)
        parser.add_argument('Transfer_Date', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('Reason_for_Transfer', type=str, required=False)
        parser.add_argument('Transfer_from_Campus', type=int, required=False)
        parser.add_argument('Transfer_To_Campus', type=int, required=False)
        parser.add_argument('DepartmentId', type=int, required=False)
        parser.add_argument('DesignationId', type=int, required=False)
        parser.add_argument('ReportingOfficerId', type=int, required=False)
        parser.add_argument('Transfer_initiated_by', type=int, required=False)
        parser.add_argument('Transfer_approval', type=int, required=False)
        parser.add_argument('Remarks', type=str, required=False)
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('CreatorId', type=int, required=False)
        parser.add_argument('CreateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('UpdaterId', type=int, required=False)
        parser.add_argument('UpdateDate', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        args = parser.parse_args()

        try:
            transfer = StaffTransfer.query.get_or_404(id)

            if args['StaffId'] is not None:
                transfer.StaffId = args['StaffId']
            if args['Transfer_Type'] is not None:
                transfer.Transfer_Type = args['Transfer_Type']
            if args['Transfer_Date'] is not None:
                transfer.Transfer_Date = args['Transfer_Date']
            if args['Reason_for_Transfer'] is not None:
                transfer.Reason_for_Transfer = args['Reason_for_Transfer']
            if args['Transfer_from_Campus'] is not None:
                transfer.Transfer_from_Campus = args['Transfer_from_Campus']
            if args['Transfer_To_Campus'] is not None:
                transfer.Transfer_To_Campus = args['Transfer_To_Campus']
            if args['DepartmentId'] is not None:
                transfer.DepartmentId = args['DepartmentId']
            if args['DesignationId'] is not None:
                transfer.DesignationId = args['DesignationId']
            if args['ReportingOfficerId'] is not None:
                transfer.ReportingOfficerId = args['ReportingOfficerId']
            if args['Transfer_initiated_by'] is not None:
                transfer.Transfer_initiated_by = args['Transfer_initiated_by']
            if args['Transfer_approval'] is not None:
                transfer.Transfer_approval = args['Transfer_approval']
            if args['Remarks'] is not None:
                transfer.Remarks = args['Remarks']
            if args['status'] is not None:
                transfer.status = args['status']
            if args['CampusId'] is not None:
                transfer.CampusId = args['CampusId']
            if args['CreatorId'] is not None:
                transfer.CreatorId = args['CreatorId']
            if args['CreateDate'] is not None:
                transfer.CreateDate = args['CreateDate']
            if args['UpdaterId'] is not None:
                transfer.UpdaterId = args['UpdaterId']
            if args['UpdateDate'] is not None:
                transfer.UpdateDate = datetime.utcnow()

            db.session.commit()
            return {"message": "Staff transfer updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        try:
            transfer = StaffTransfer.query.get_or_404(id)
            db.session.delete(transfer)
            db.session.commit()
            return {"message": "Staff transfer deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class StaffShiftResource(Resource):
    def get(self, staff_id=None):
        try:
            if staff_id:
                staff_shift = StaffShift.query.get(staff_id)
                if staff_shift is None:
                    return {"message": f"StaffShift with StaffId {staff_id} not found"}, 404
                return staff_shift.to_dict(), 200
            else:
                staff_shifts = StaffShift.query.all()
                return [shift.to_dict() for shift in staff_shifts], 200
        except SQLAlchemyError as e:
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('StaffId', type=int, required=True)
        parser.add_argument('ShiftId', type=int, required=True)
        parser.add_argument('CreatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True)
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatedByUserId', type=int, required=True)
        parser.add_argument('UpdatedByUserId', type=int, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        try:
            new_shift = StaffShift(
                StaffId=args['StaffId'],
                ShiftId=args['ShiftId'],
                CreatedOn=args['CreatedOn'],
                UpdatedOn=args.get('UpdatedOn'),
                CreatedByUserId=args['CreatedByUserId'],
                UpdatedByUserId=args.get('UpdatedByUserId'),
                CampusId=args.get('CampusId')
            )
            db.session.add(new_shift)
            db.session.commit()
            return {"message": "StaffShift created successfully", "StaffId": new_shift.StaffId}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, staff_id):
        parser = reqparse.RequestParser()
        parser.add_argument('ShiftId', type=int, required=False)
        parser.add_argument('CreatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=False)
        parser.add_argument('CreatedByUserId', type=int, required=False)
        parser.add_argument('UpdatedByUserId', type=int, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        args = parser.parse_args()

        try:
            staff_shift = StaffShift.query.get(staff_id)
            if staff_shift is None:
                return {"message": f"StaffShift with StaffId {staff_id} not found"}, 404

            if args['ShiftId'] is not None:
                staff_shift.ShiftId = args['ShiftId']
            if args['CreatedOn'] is not None:
                staff_shift.CreatedOn = args['CreatedOn']
            if args['UpdatedOn'] is not None:
                staff_shift.UpdatedOn = args['UpdatedOn']
            if args['CreatedByUserId'] is not None:
                staff_shift.CreatedByUserId = args['CreatedByUserId']
            if args['UpdatedByUserId'] is not None:
                staff_shift.UpdatedByUserId = args['UpdatedByUserId']
            if args['CampusId'] is not None:
                staff_shift.CampusId = args['CampusId']

            db.session.commit()
            return {"message": "StaffShift updated successfully", "StaffId": staff_shift.StaffId}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, staff_id):
        try:
            staff_shift = StaffShift.query.get(staff_id)
            if staff_shift is None:
                return {"message": f"StaffShift with StaffId {staff_id} not found"}, 404

            db.session.delete(staff_shift)
            db.session.commit()
            return {"message": "StaffShift deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class SalaryResource(Resource):
    
    def get(self, salary_id):
        """
        Handles the retrieval of a salary record by its ID.
        """
        try:
            salary = Salaries.query.get(salary_id)
            if salary:
                return salary.to_dict(), 200
            else:
                return {'message': 'Salary record not found'}, 404
        except SQLAlchemyError as e:
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def post(self):
        """
        Handles the creation of a new salary record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('BasicAmount', type=float, required=True, help='BasicAmount is required')
        parser.add_argument('AllowancesAmount', type=float, required=True, help='AllowancesAmount is required')
        parser.add_argument('TotalAmount', type=float, required=True, help='TotalAmount is required')
        parser.add_argument('AnnualLeaves', type=int, required=True, help='AnnualLeaves is required')
        parser.add_argument('RemainingAnnualLeaves', type=int, required=True, help='RemainingAnnualLeaves is required')
        parser.add_argument('DailyHours', type=int, required=True, help='DailyHours is required')
        parser.add_argument('PFAmount', type=float, required=True, help='PFAmount is required')
        parser.add_argument('EOBIAmount', type=float, required=True, help='EOBIAmount is required')
        parser.add_argument('SESSIAmount', type=float, required=True, help='SESSIAmount is required')
        parser.add_argument('SalaryMode', type=int, required=True, help='SalaryMode is required')
        parser.add_argument('IsProbationPeriod', type=bool, required=True, help='IsProbationPeriod is required')
        parser.add_argument('From', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='From date is required')
        parser.add_argument('To', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='To date is required')
        parser.add_argument('EmployeeId', type=int, required=True, help='EmployeeId is required')
        parser.add_argument('CreatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), required=True, help='CreatedOn date is required')
        parser.add_argument('UpdatedOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), help='UpdatedOn date is optional')
        parser.add_argument('InActiveOn', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'), help='InActiveOn date is optional')
        parser.add_argument('IsActive', type=bool, required=True, help='IsActive is required')
        parser.add_argument('CreatedByUserId', type=int, required=True, help='CreatedByUserId is required')
        parser.add_argument('UpdatedByUserId', type=int, help='UpdatedByUserId is optional')
        parser.add_argument('InActiveByUserId', type=int, help='InActiveByUserId is optional')
        parser.add_argument('HouseRent', type=float, help='HouseRent is optional')
        parser.add_argument('MedicalAllowance', type=float, help='MedicalAllowance is optional')
        parser.add_argument('UtilityAllowance', type=float, help='UtilityAllowance is optional')
        parser.add_argument('IncomeTax', type=float, help='IncomeTax is optional')
        parser.add_argument('Toil', type=float, help='Toil is optional')
        parser.add_argument('ConveyanceAllowance', type=float, help='ConveyanceAllowance is optional')
        parser.add_argument('StaffLunch', type=float, help='StaffLunch is optional')
        parser.add_argument('CasualLeaves', type=int, help='CasualLeaves is optional')
        parser.add_argument('SickLeaves', type=int, help='SickLeaves is optional')
        parser.add_argument('RemainingCasualLeaves', type=int, required=True, help='RemainingCasualLeaves is required')
        parser.add_argument('RemainingSickLeaves', type=int, required=True, help='RemainingSickLeaves is required')
        parser.add_argument('StudyLeaves', type=int, help='StudyLeaves is optional')
        parser.add_argument('RemainingStudyLeaves', type=int, required=True, help='RemainingStudyLeaves is required')
        parser.add_argument('Loan', type=int, required=True, help='Loan is required')
        parser.add_argument('Arrears', type=int, required=True, help='Arrears is required')

        args = parser.parse_args()

        try:
            new_salary = Salaries(
                BasicAmount=args['BasicAmount'],
                AllowancesAmount=args['AllowancesAmount'],
                TotalAmount=args['TotalAmount'],
                AnnualLeaves=args['AnnualLeaves'],
                RemainingAnnualLeaves=args['RemainingAnnualLeaves'],
                DailyHours=args['DailyHours'],
                PFAmount=args['PFAmount'],
                EOBIAmount=args['EOBIAmount'],
                SESSIAmount=args['SESSIAmount'],
                SalaryMode=args['SalaryMode'],
                IsProbationPeriod=args['IsProbationPeriod'],
                From=args['From'],
                To=args['To'],
                EmployeeId=args['EmployeeId'],
                CreatedOn=args['CreatedOn'],
                UpdatedOn=args.get('UpdatedOn'),
                InActiveOn=args.get('InActiveOn'),
                IsActive=args['IsActive'],
                CreatedByUserId=args['CreatedByUserId'],
                UpdatedByUserId=args.get('UpdatedByUserId'),
                InActiveByUserId=args.get('InActiveByUserId'),
                HouseRent=args.get('HouseRent'),
                MedicalAllowance=args.get('MedicalAllowance'),
                UtilityAllowance=args.get('UtilityAllowance'),
                IncomeTax=args.get('IncomeTax'),
                Toil=args.get('Toil'),
                ConveyanceAllowance=args.get('ConveyanceAllowance'),
                StaffLunch=args.get('StaffLunch'),
                CasualLeaves=args.get('CasualLeaves'),
                SickLeaves=args.get('SickLeaves'),
                RemainingCasualLeaves=args['RemainingCasualLeaves'],
                RemainingSickLeaves=args['RemainingSickLeaves'],
                StudyLeaves=args.get('StudyLeaves'),
                RemainingStudyLeaves=args['RemainingStudyLeaves'],
                Loan=args['Loan'],
                Arrears=args['Arrears']
            )

            db.session.add(new_salary)
            db.session.commit()
            return {"message": "Salary record created successfully", "salary": new_salary.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500


            salary.UpdatedOn = datetime.utcnow()

            db.session.commit()
            return {"message": "Salary record updated successfully", "salary": salary.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, salary_id):
        """
        Handles deleting a salary record by its ID.
        """
        try:
            salary = Salaries.query.get(salary_id)
            if not salary:
                return {'message': 'Salary record not found'}, 404

            db.session.delete(salary)
            db.session.commit()
            return {"message": "Salary record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class MarkDayOffDepsResource(Resource):
    
    def get(self, id=None):
        """
        Retrieve a single MarkDayOffDeps record by ID or all records if no ID is provided.
        """
        if id:
            mark_day_off = MarkDayOffDeps.query.get(id)
            if mark_day_off:
                return mark_day_off.to_dict(), 200
            return {'message': 'MarkDayOffDeps record not found'}, 404
        else:
            mark_days_off = MarkDayOffDeps.query.all()
            return [mark_day_off.to_dict() for mark_day_off in mark_days_off], 200

    def post(self):
        """
        Create a new MarkDayOffDeps record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=True, help='Date is required')
        parser.add_argument('Staff_Id', type=int, required=True, help='Staff ID is required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            mark_day_off = MarkDayOffDeps(
                Date=datetime.fromisoformat(args['Date']),
                Staff_Id=args['Staff_Id'],
                Description=args.get('Description'),
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow(),
                status=args.get('status'),
                CampusId=args.get('CampusId'),
                AcademicYearId=args.get('AcademicYearId')
            )

            db.session.add(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffDeps record created successfully"}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self):
        """
        Update existing MarkDayOffDeps records for multiple staff members.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('Staff_Ids', type=int, action='append', required=True, help='Staff IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('status', type=bool, required=False)
        parser.add_argument('CampusId', type=int, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            
            updated_records = []
            for staff_id in args['Staff_Ids']:
                
                mark_day_off = MarkDayOffDeps.query.filter_by(Staff_Id=staff_id).first()
                
                if not mark_day_off:
                    continue  # Skip if the record does not exist

                if args['Date']:
                    mark_day_off.Date = datetime.fromisoformat(args['Date'])
                if args['Description']:
                    mark_day_off.Description = args['Description']
                if args['status'] is not None:
                    mark_day_off.status = args['status']
                if args['CampusId']:
                    mark_day_off.CampusId = args['CampusId']
                if args['AcademicYearId']:
                    mark_day_off.AcademicYearId = args['AcademicYearId']

                mark_day_off.UpdatorId = args['UpdatorId']
                mark_day_off.UpdateDate = datetime.utcnow()

                updated_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffDeps records updated successfully", "MarkDayOffDeps": updated_records}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a MarkDayOffDeps record by ID.
        """
        try:
            mark_day_off = MarkDayOffDeps.query.get(id)
            if not mark_day_off:
                return {'message': 'MarkDayOffDeps record not found'}, 404

            db.session.delete(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffDeps record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class MarkDayOffHRsResource(Resource):
    def get(self, id=None):
        """
        Retrieve a single MarkDayOffHRs record by ID or all records if no ID is provided.
        """
        if id:
            mark_day_off = MarkDayOffHRs.query.get(id)
            if mark_day_off:
                return mark_day_off.to_dict(), 200
            return {'message': 'MarkDayOffHRs record not found'}, 404
        else:
            mark_days_off = MarkDayOffHRs.query.all()
            return [mark_day_off.to_dict() for mark_day_off in mark_days_off], 200

    def post(self):
        """
        Create new MarkDayOffHRs records for multiple campuses.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=True, help='Date is required')
        parser.add_argument('CampusIds', type=int, action='append', required=True, help='Campus IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            created_records = []
            for campus_id in args['CampusIds']:
                mark_day_off = MarkDayOffHRs(
                    Date=datetime.fromisoformat(args['Date']),
                    CampusIds=campus_id,
                    Description=args.get('Description'),
                    CreatorId=args['CreatorId'],
                    CreateDate=datetime.utcnow(),
                    Status=args.get('Status'),
                    AcademicYearId=args.get('AcademicYearId')
                )
                db.session.add(mark_day_off)
                created_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffHRs records created successfully"}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self):
        """
        Update existing MarkDayOffHRs records for multiple campuses.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Date', type=str, required=False)
        parser.add_argument('CampusIds', type=int, action='append', required=True, help='Campus IDs are required')
        parser.add_argument('Description', type=str, required=False)
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('Status', type=bool, required=False)
        parser.add_argument('AcademicYearId', type=int, required=False)
        
        args = parser.parse_args()

        try:
            updated_records = []
            for campus_id in args['CampusIds']:
                mark_day_off = MarkDayOffHRs.query.filter_by(CampusIds=campus_id).first()
                if not mark_day_off:
                    continue  # Skip if the record does not exist

                if args['Date']:
                    mark_day_off.Date = datetime.fromisoformat(args['Date'])
                if args['Description']:
                    mark_day_off.Description = args['Description']
                if args['Status'] is not None:
                    mark_day_off.status = args['status']
                if args['AcademicYearId']:
                    mark_day_off.AcademicYearId = args['AcademicYearId']

                mark_day_off.UpdatorId = args['UpdatorId']
                mark_day_off.UpdateDate = datetime.utcnow()

                updated_records.append(mark_day_off.to_dict())
            
            db.session.commit()

            return {"message": "MarkDayOffHRs records updated successfully", "MarkDayOffHRs": updated_records}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a MarkDayOffHRs record by ID.
        """
        try:
            mark_day_off = MarkDayOffHRs.query.get(id)
            if not mark_day_off:
                return {'message': 'MarkDayOffHRs record not found'}, 404

            db.session.delete(mark_day_off)
            db.session.commit()

            return {"message": "MarkDayOffHRs record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class AllowanceHeadResource(Resource):
    def get(self, id=None):
        """
        Retrieve a single AllowanceHead record by ID or all records if no ID is provided.
        """
        if id:
            allowance_head = AllowanceHead.query.get(id)
            if allowance_head:
                return allowance_head.to_dict(), 200
            return {'message': 'AllowanceHead record not found'}, 404
        else:
            allowance_heads = AllowanceHead.query.all()
            return [allowance_head.to_dict() for allowance_head in allowance_heads], 200

    def post(self):
        """
        Create a new AllowanceHead record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('AllowanceHead_Name', type=str, required=True, help='AllowanceHead Name is required')
        args = parser.parse_args()

        try:
            allowance_head = AllowanceHead(
                AllowanceHead_Name=args['AllowanceHead_Name']
            )
            db.session.add(allowance_head)
            db.session.commit()

            return {"message": "AllowanceHead record created successfully", "AllowanceHead_Id": allowance_head.AllowanceHead_Id}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing AllowanceHead record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('AllowanceHead_Name', type=str, required=True, help='AllowanceHead Name is required')
        args = parser.parse_args()

        try:
            allowance_head = AllowanceHead.query.get(id)
            if not allowance_head:
                return {'message': 'AllowanceHead record not found'}, 404

            allowance_head.AllowanceHead_Name = args['AllowanceHead_Name']
            db.session.commit()

            return {"message": "AllowanceHead record updated successfully", "AllowanceHead": allowance_head.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete an AllowanceHead record by ID.
        """
        try:
            allowance_head = AllowanceHead.query.get(id)
            if not allowance_head:
                return {'message': 'AllowanceHead record not found'}, 404

            db.session.delete(allowance_head)
            db.session.commit()

            return {"message": "AllowanceHead record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class OneTimeAllowanceResource(Resource):

    def get(self, id=None):
        """
        Retrieve a single OneTimeAllowance record by ID or all records if no ID is provided.
        """
        if id:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if one_time_allowance:
                return one_time_allowance.to_dict(), 200
            return {'message': 'OneTimeAllowance record not found'}, 404
        else:
            one_time_allowances = OneTimeAllowance.query.all()
            return [one_time_allowance.to_dict() for one_time_allowance in one_time_allowances], 200

    def post(self):
        """
        Create a new OneTimeAllowance record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('OneTimeAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('OneTimeAllowance_Amount', type=float, required=True, help='Amount is required')
        parser.add_argument('OneTimeAllowance_PamentMonth', type=str, required=True, help='Payment Month is required')
        parser.add_argument('OneTimeAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('OneTimeAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('InActive', type=bool, required=True, help='InActive is required')
        args = parser.parse_args()

        try:
            one_time_allowance = OneTimeAllowance(
                OneTimeAllowance_StaffId=args['OneTimeAllowance_StaffId'],
                OneTimeAllowance_AllowanceHeadId=args['OneTimeAllowance_AllowanceHeadId'],
                OneTimeAllowance_Amount=args['OneTimeAllowance_Amount'],
                OneTimeAllowance_PamentMonth=args['OneTimeAllowance_PamentMonth'],
                OneTimeAllowance_ApprovedBy=args['OneTimeAllowance_ApprovedBy'],
                OneTimeAllowance_Taxable=args['OneTimeAllowance_Taxable'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow(),
                InActive = args['InActive']
            )
            db.session.add(one_time_allowance)
            db.session.commit()

            return {"message": "OneTimeAllowance record created successfully", "OneTimeAllowance": one_time_allowance.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing OneTimeAllowance record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('OneTimeAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('OneTimeAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('OneTimeAllowance_Amount', type=float, required=True, help='Amount is required')
        parser.add_argument('OneTimeAllowance_PamentMonth', type=str, required=True, help='Payment Month is required')
        parser.add_argument('OneTimeAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('OneTimeAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        args = parser.parse_args()

        try:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if not one_time_allowance:
                return {'message': 'OneTimeAllowance record not found'}, 404

            one_time_allowance.OneTimeAllowance_StaffId = args['OneTimeAllowance_StaffId']
            one_time_allowance.OneTimeAllowance_AllowanceHeadId = args['OneTimeAllowance_AllowanceHeadId']
            one_time_allowance.OneTimeAllowance_Amount = args['OneTimeAllowance_Amount']
            one_time_allowance.OneTimeAllowance_PamentMonth = args['OneTimeAllowance_PamentMonth']
            one_time_allowance.OneTimeAllowance_ApprovedBy = args['OneTimeAllowance_ApprovedBy']
            one_time_allowance.OneTimeAllowance_Taxable = args['OneTimeAllowance_Taxable']
            one_time_allowance.UpdatorId = args['UpdatorId']
            one_time_allowance.UpdateDate = datetime.utcnow()

            db.session.commit()

            return {"message": "OneTimeAllowance record updated successfully", "OneTimeAllowance": one_time_allowance.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a OneTimeAllowance record by ID.
        """
        try:
            one_time_allowance = OneTimeAllowance.query.get(id)
            if not one_time_allowance:
                return {'message': 'OneTimeAllowance record not found'}, 404

            db.session.delete(one_time_allowance)
            db.session.commit()

            return {"message": "OneTimeAllowance record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

class ScheduledAllowanceResource(Resource):

    def get(self, id=None):
        """
        Retrieve a single ScheduledAllowance record by ID or all records if no ID is provided.
        """
        if id:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if scheduled_allowance:
                return scheduled_allowance.to_dict(), 200
            return {'message': 'ScheduledAllowance record not found'}, 404
        else:
            scheduled_allowances = ScheduledAllowance.query.all()
            return [scheduled_allowance.to_dict() for scheduled_allowance in scheduled_allowances], 200

    def post(self):
        """
        Create a new ScheduledAllowance record.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('ScheduledAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('ScheduledAllowance_AmountPerMonth', type=float, required=True, help='Amount Per Month is required')
        parser.add_argument('ScheduledAllowance_StartDate', type=str, required=True, help='Start Date is required')
        parser.add_argument('ScheduledAllowance_EndDate', type=str, required=True, help='End Date is required')
        parser.add_argument('ScheduledAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('CreatorId', type=int, required=True, help='Creator ID is required')
        parser.add_argument('ScheduledAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        args = parser.parse_args()

        try:
            scheduled_allowance = ScheduledAllowance(
                ScheduledAllowance_StaffId=args['ScheduledAllowance_StaffId'],
                ScheduledAllowance_AllowanceHeadId=args['ScheduledAllowance_AllowanceHeadId'],
                ScheduledAllowance_AmountPerMonth=args['ScheduledAllowance_AmountPerMonth'],
                ScheduledAllowance_StartDate=datetime.fromisoformat(args['ScheduledAllowance_StartDate']),
                ScheduledAllowance_EndDate=datetime.fromisoformat(args['ScheduledAllowance_EndDate']),
                ScheduledAllowance_ApprovedBy=args['ScheduledAllowance_ApprovedBy'],
                CreatorId=args['CreatorId'],
                CreateDate=datetime.utcnow(),
                ScheduledAllowance_Taxable=args['ScheduledAllowance_Taxable']
            )
            db.session.add(scheduled_allowance)
            db.session.commit()

            return {"message": "ScheduledAllowance record created successfully", "ScheduledAllowance": scheduled_allowance.to_dict()}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def put(self, id):
        """
        Update an existing ScheduledAllowance record by ID.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ScheduledAllowance_StaffId', type=int, required=True, help='Staff ID is required')
        parser.add_argument('ScheduledAllowance_AllowanceHeadId', type=int, required=True, help='Allowance Head ID is required')
        parser.add_argument('ScheduledAllowance_AmountPerMonth', type=float, required=True, help='Amount Per Month is required')
        parser.add_argument('ScheduledAllowance_StartDate', type=str, required=True, help='Start Date is required')
        parser.add_argument('ScheduledAllowance_EndDate', type=str, required=True, help='End Date is required')
        parser.add_argument('ScheduledAllowance_ApprovedBy', type=int, required=True, help='Approved By is required')
        parser.add_argument('UpdatorId', type=int, required=True, help='Updator ID is required')
        parser.add_argument('ScheduledAllowance_Taxable', type=bool, required=True, help='Taxable is required')
        args = parser.parse_args()

        try:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if not scheduled_allowance:
                return {'message': 'ScheduledAllowance record not found'}, 404

            scheduled_allowance.ScheduledAllowance_StaffId = args['ScheduledAllowance_StaffId']
            scheduled_allowance.ScheduledAllowance_AllowanceHeadId = args['ScheduledAllowance_AllowanceHeadId']
            scheduled_allowance.ScheduledAllowance_AmountPerMonth = args['ScheduledAllowance_AmountPerMonth']
            scheduled_allowance.ScheduledAllowance_StartDate = datetime.fromisoformat(args['ScheduledAllowance_StartDate'])
            scheduled_allowance.ScheduledAllowance_EndDate = datetime.fromisoformat(args['ScheduledAllowance_EndDate'])
            scheduled_allowance.ScheduledAllowance_ApprovedBy = args['ScheduledAllowance_ApprovedBy']
            scheduled_allowance.UpdatorId = args['UpdatorId']
            scheduled_allowance.UpdateDate = datetime.utcnow()
            scheduled_allowance.ScheduledAllowance_Taxable = args['ScheduledAllowance_Taxable']

            db.session.commit()

            return {"message": "ScheduledAllowance record updated successfully", "ScheduledAllowance": scheduled_allowance.to_dict()}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500

    def delete(self, id):
        """
        Delete a ScheduledAllowance record by ID.
        """
        try:
            scheduled_allowance = ScheduledAllowance.query.get(id)
            if not scheduled_allowance:
                return {'message': 'ScheduledAllowance record not found'}, 404

            db.session.delete(scheduled_allowance)
            db.session.commit()

            return {"message": "ScheduledAllowance record deleted successfully"}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {'error': f"Database error occurred: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {'error': f"An unexpected error occurred: {str(e)}"}, 500