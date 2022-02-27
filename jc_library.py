import sys, os
from nbgrader.api import Gradebook
from nbgrader.plugins.export import ExportPlugin
from canvasapi import Canvas

# Canvas API URL
API_URL = ""
# Canvas API key
API_KEY = ""
# Canvas Course ID (found in the course URL)
COURSE_ID = 123

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


# INCOMPLETE returns a 2d array in the format of assignment_array[string studentID, float grade]
def get_assignment_grades(course_dir, assignment):
	gradebook = __set_db(course_dir)
	exporter = ExportPlugin(gradebook)
	try:
		print("")
	except Exception as e:
		print(e)
	gradebook.close()
	return # finish this


# adds students to local nbgrader db after checking if student already exists or not
# expects arg 2 to be an array of string NetIDs
def nb_add_students(course_dir, students):
	gradebook = __set_db(course_dir)
	for student in students:
		try:
			gradebook.add_student(student)
		except Exception as e:
			print("%s (%s)" % (e, student))
	gradebook.close()


# removes student from local nbgrader db
# expects arg 2 to be student ID as string
def nb_remove_student(course_dir, student):
	gradebook = __set_db(course_dir)
	try:
		gradebook.remove_student(student)
	except Exception as e:
		print(e)
	gradebook.close()


# DEBUGGING FUNCTION to print nbgrader db student list
def nb_print_students(course_dir):
	gradebook = __set_db(course_dir)
	for student in gradebook.students:
		print(student)
	gradebook.close()


# DEBUGGING FUNCTION to print canvas course student list
def c_print_students(course_id):
	course = __set_course(course_id)
	for i in course.get_users():
		print(i)

# DEBUGGING FUNCTION to print nbgrader db assignment list
def nb_print_assignments(course_dir):
	gradebook = __set_db(course_dir)
	for assignment in gradebook.assignments:
		print(assignment)
	gradebook.close()


# sets current gradebook.db for internal use
def __set_db(course_dir):
	try:
		course_dir = os.path.expanduser(course_dir) # this line accommodates for ~/ usage
		os.chdir(course_dir) # set working directory
		return Gradebook("sqlite:///gradebook.db")
	except Exception as e:
		sys.exit(e) # prints error and exits program


# sets the active Canvas course for API use
def __set_course(course_id):
	try:
		return canvas.get_course(course_id)
	except Exception as e:
		sys.exit(e) # prints error and exits program


### TESTING ZONE
c_print_students(COURSE_ID)