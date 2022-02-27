import sys, os, configparser
from nbgrader.api import Gradebook
from nbgrader.plugins.export import ExportPlugin
from canvasapi import Canvas


########## INITIALIZATION FUNCTIONS ##########

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


########## PRIVATE NBGRADER FUNCTIONS ##########

# DEBUGGING FUNCTION to print nbgrader db student list
def __nb_print_students(course_dir):
	for student in gradebook.students:
		print(student)
	gradebook.close()


# DEBUGGING FUNCTION to print nbgrader db assignment list
def __nb_print_assignments(course_dir):
	for assignment in gradebook.assignments:
		print(assignment)
	gradebook.close()


# INCOMPLETE returns a 2d array in the format of assignment_array[string studentID, float grade]
def __nb_get_assignment_grades(course_dir, assignment):
	exporter = ExportPlugin(gradebook)
	try:
		print("")
	except Exception as e:
		print(e)
	gradebook.close()
	return # finish this


# adds students to local nbgrader db after checking if student already exists or not
# expects arg 2 to be an array of string NetIDs
def __nb_add_students(course_dir, students):
	for student in students:
		try:
			gradebook.add_student(student)
		except Exception as e:
			print("%s (%s)" % (e, student))
	gradebook.close()


# removes student from local nbgrader db
# expects arg 2 to be student ID as string
def __nb_remove_student(course_dir, student):
	try:
		gradebook.remove_student(student)
	except Exception as e:
		print(e)
	gradebook.close()


########## PRIVATE CANVAS FUNCTIONS ##########

# DEBUGGING FUNCTION to print canvas course student list
def __c_print_students(course_id):
	print("\n---%s Student List---" % course)
	for i in course.get_users(enrollment_type = ['student']):
		print(i)


# DEBUGGING FUNCTION to print canvas course student list
def __c_print_assignments(course_id):
	print("\n---%s Assignment List---" % course)
	for i in course.get_assignments():
		print(i)

# Create new assignment within canvas
def __c_create_assignment(assignment_name):
	course.create_assignment({
		'name': assignment_name
	})


############################################################################

# Initialize config
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize Canvas objects
canvas = Canvas(config['Canvas']['API_URL'], config['Canvas']['API_KEY'])
course = __set_course(int(config['Canvas']['COURSE_ID']))

# Initialize nbgrader database
gradebook = __set_db(config['nbgrader']['COURSE_DIRECTORY'])

### TESTING ZONE
__c_create_assignment('ps1')
__c_print_students(course)
__c_print_assignments(course)