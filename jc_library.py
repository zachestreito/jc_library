import sys, os, configparser
from traitlets.config.loader import PyFileConfigLoader
from nbgrader.api import Gradebook
from nbgrader.plugins.export import ExportPlugin
from nbgrader.apps import NbGraderAPI
from canvasapi import Canvas


########## INITIALIZATION FUNCTIONS ##########

# sets current gradebook.db for internal use
def __set_db():
	try:
		return Gradebook("sqlite:///gradebook.db", course_id = nb_api.course_id)
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
def __nb_print_students():
	gradebook = __set_db()
	print("\n---nbgrader Student List---")
	for student in gradebook.students:
		print("%s - %s %s - %s" %(
			student.id,
			student.first_name,
			student.last_name,
			student.email
			))
	gradebook.close()


# DEBUGGING FUNCTION to print nbgrader db assignment list
def __nb_print_assignments():
	gradebook = __set_db()
	for assignment in gradebook.assignments:
		print(assignment)
	gradebook.close()


# INCOMPLETE returns a 2d array in the format of assignment_array[string studentID, float grade]
def __nb_get_assignment_grades(assignment):
	gradebook = __set_db()
	exporter = ExportPlugin(gradebook)
	try:
		print("")
	except Exception as e:
		print(e)
	gradebook.close()
	return # finish this


# adds students to db, or updates existing entries
# expects arg 1 to be an array of string NetIDs
def __nb_add_students(students):
	gradebook = __set_db()
	for student in students:
		try:
			gradebook.update_or_create_student(
				student.login_id,
				first_name = student.name.split()[0],
				last_name = student.name.split()[1],
				email = student.email
				)
		except Exception as e:
			print("%s (%s)" % (e, student))
	gradebook.close()


# removes student from local nbgrader db
# expects arg 1 to be student ID as string
def __nb_remove_student(student):
	gradebook = __set_db()
	try:
		gradebook.remove_student(student)
	except Exception as e:
		print(e)
	gradebook.close()


########## PRIVATE CANVAS FUNCTIONS ##########

# return Canvas student list
def __c_get_students():
	return course.get_users(enrollment_type = ['student'], sort = 'username')

# DEBUGGING FUNCTION to print canvas course student list
def __c_print_students():
	print("\n---%s Canvas Student List---" % course)
	for i in __c_get_students():
		print("%s - %s" % (i.login_id, i.name))

# return Canvas assignment list
def __c_get_assignments():
	return course.get_assignments()

# DEBUGGING FUNCTION to print canvas course assignment list
def __c_print_assignments():
	print("\n---%s Canvas Assignment List---" % course)
	for i in __c_get_assignments():
		print(i)

# Create new assignment within canvas
def __c_create_assignment(assignment_name):
	course.create_assignment({
		'name': assignment_name
	})


########## PUBLIC COMBINED FUNCTIONS ##########

# INCOMPLETE update gradebook.db with student list from Canvas
def import_students():
	students = __c_get_students()
	__nb_add_students(students)


############################################################################

# Initialize config
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize Canvas objects
canvas = Canvas(config['Canvas']['API_URL'], config['Canvas']['API_KEY'])
course = __set_course(int(config['Canvas']['COURSE_ID']))

# Initialize nbgrader objects
course_dir = config['nbgrader']['COURSE_DIRECTORY']
course_dir = os.path.expanduser(course_dir) # this line accommodates for ~/ usage
os.chdir(course_dir) # set working directory
config_loader = PyFileConfigLoader(filename = "nbgrader_config.py")
nbconfig = config_loader.load_config()
nb_api = NbGraderAPI(config = nbconfig)


### TESTING ZONE
#__c_print_students()
#__c_print_assignments()
import_students()
__nb_print_students()