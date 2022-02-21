import sys, os
from nbgrader.api import Gradebook


# adds students to db after checking if student already exists or not
# expects arg 2 to be an array of strings
def add_students(course_dir, students):
	gradebook = __set_db(course_dir)
	for student in students:
		gradebook.update_or_create_student(student)
	gradebook.close()

# print list of students
def print_students(course_dir):
	gradebook = __set_db(course_dir)
	for student in gradebook.students:
		print(student)
	gradebook.close()

# print list of assignments
def print_assignments(course_dir):
	gradebook = __set_db(course_dir)
	for assignment in gradebook.assignments:
		print(assignment)
	gradebook.close()

# set gradebook.db for internal use
def __set_db(course_dir):
	try:
		course_dir = os.path.expanduser(course_dir) # this line accommodates for ~/ usage
		os.chdir(course_dir) # set working directory
		return Gradebook("sqlite:///gradebook.db")
	except Exception as e:
		sys.exit(e) # prints error and exits program