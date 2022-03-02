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


########## PRIVATE GRADEBOOK FUNCTIONS ##########

# DEBUGGING FUNCTION to print gradebook student list
def __db_print_students():
	gradebook = __set_db()
	print("\n---Gradebook Student List---")
	for student in gradebook.students:
		print("%s - %s %s - %s" %(
			student.id,
			student.first_name,
			student.last_name,
			student.email
			))
	gradebook.close()


# adds students to gradebook, or updates existing entries
# expects arg 1 to be an array of string NetIDs
def __db_add_students(students):
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


# removes student from local gradebook
# expects arg 1 to be student ID as string
def __db_remove_student(student):
	gradebook = __set_db()
	try:
		gradebook.remove_student(student)
	except Exception as e:
		print(e)
	finally:
		gradebook.close()


# Add assignment to gradebook
def __db_create_assignment(assignment_name):
	gradebook = __set_db()
	try:
		gradebook.add_assignment(assignment_name)
		print('Gradebook assignment "%s" created successfully' % assignment_name)
		return True
	except Exception as e:
		print(e)
		print('Error: Gradebook assignment "%s" already exists' % assignment_name)
		return False
	finally:
		gradebook.close()


# Check if assignment exists within gradebook
def __db_check_assignment(assignment_name):
	gradebook = __set_db()
	for assignment in gradebook.assignments:
		if assignment.name == assignment_name:
			return True
	return False
	gradebook.close()


# Print db assignment list
def __db_print_assignments():
	gradebook = __set_db()
	print("\n---%s Gradebook Assignment List---" % os.getcwd().split('/')[-1])
	for assignment in gradebook.assignments:
		print(assignment.name)
	gradebook.close()


# Remove assignment from gradebook
def __db_remove_assignment(assignment_name):
	gradebook = __set_db()
	try:
		gradebook.remove_assignment(assignment_name)
		print('Gradebook assignment "%s" deleted successfully' % assignment_name)
		return True
	except Exception as e:
		print(e)
		print('Gradebook assignment "%s" does not exist or cannot be deleted' % assignment_name)
		return False
	finally:
		gradebook.close()


########## PRIVATE NBGRADER FUNCTIONS ##########

# DEBUGGING FUNCTION to print nbgrader source folder assignment list
def __nb_print_assignments():
	print("\n---%s nbgrader Assignment List---" % os.getcwd().split('/')[-1])
	for assignment in nb_api.get_source_assignments():
		print(assignment)


# creates an nbgrader assignment
def __nb_create_assignment(assignment_name):
	try:
		os.mkdir("%ssource/%s" % (course_dir, assignment_name))
		print('nbgrader assignment "%s" created successfully' % assignment_name)
		return True
	except Exception as e:
		print(e)
		print('Error: nbgrader assignment "%s" already exists' % assignment_name)
		return False

# NOTICE: Will only delete empty assignment folders
# Assignments containing notebooks must be deleted manually
def __nb_remove_assignment(assignment_name):
	try:
		os.rmdir("%ssource/%s" % (course_dir, assignment_name))
		print('nbgrader assignment "%s" deleted successfully' % assignment_name)
		return True
	except Exception as e:
		print(e)
		print("Error: nbgrader assignment folder contains files and must be deleted manually")
		return False


########## PRIVATE CANVAS FUNCTIONS ##########

# return Canvas student list
def __c_get_students():
	return course.get_users(enrollment_type = ["student"], sort = "username")


# DEBUGGING FUNCTION to print Canvas course student list
def __c_print_students():
	print("\n---%s Canvas Student List---" % course)
	for i in __c_get_students():
		print("%s - %s" % (i.login_id, i.name))


# return Canvas assignment list
def __c_get_assignments():
	return course.get_assignments()


# DEBUGGING FUNCTION to print Canvas course assignment list
def __c_print_assignments():
	print("\n---%s Canvas Assignment List---" % course)
	for i in __c_get_assignments():
		print(i)


# Create new assignment within Canvas
def __c_create_assignment(assignment_name, hub_url):
	if __c_check_assignment(assignment_name) != False:
		print('Error: Canvas assignment "%s" already exists' % assignment_name)
		return False
	course.create_assignment({
		"name": assignment_name,
		"description": '<a href="%s">%s</a>' % (hub_url, assignment_name)
	})
	print('Canvas assignment "%s" created successfully' % assignment_name)
	return True

def __c_remove_assignment(assignment_name):
	assignment = __c_check_assignment(assignment_name)
	if assignment != False:
		assignment.delete()
		print('Canvas assignment "%s" deleted successfully' % assignment_name)
	else:
		print('Canvas assignment "%s" does not exist or cannot be deleted' % assignment_name)


# Check if assignment exists within Canvas
def __c_check_assignment(assignment_name):
	assignments = course.get_assignments()
	for assignment in assignments:
		if assignment.name == assignment_name:
			return assignment
	return False


########## PUBLIC COMBINED FUNCTIONS ##########

# Prints assignments from Canvas, Gradebook, and nbgrader
def print_assignments():
	__c_print_assignments()
	__db_print_assignments()
	__nb_print_assignments()


# updates gradebook.db with student list from Canvas
def import_students():
	students = __c_get_students()
	__db_add_students(students)


# Creates an assignment on Canvas, Gradebook, and nbgrader
def create_assignment(assignment_name, hub_url):
	__c_create_assignment(assignment_name, hub_url)
	__nb_create_assignment(assignment_name)
	__db_create_assignment(assignment_name)


def remove_assignment(assignment_name):
	__c_remove_assignment(assignment_name)
	__nb_remove_assignment(assignment_name)
	__db_remove_assignment(assignment_name)


# INCOMPLETE - publishes assignment grades from gradebook.db to Canvas
def publish_grades(assignment_name):
	return


############################################################################

# Initialize config
config = configparser.ConfigParser()
config.read("config.ini")

# Initialize Canvas objects
canvas = Canvas(config["Canvas"]["API_URL"], config["Canvas"]["API_KEY"])
course = __set_course(int(config["Canvas"]["COURSE_ID"]))

# Initialize nbgrader objects
course_dir = config["nbgrader"]["COURSE_DIRECTORY"]
course_dir = os.path.expanduser(course_dir) # this line accommodates for ~/ usage
os.chdir(course_dir) # set working directory
config_loader = PyFileConfigLoader(filename = "nbgrader_config.py")
nbconfig = config_loader.load_config()
nb_api = NbGraderAPI(config = nbconfig)


### TESTING ZONE
#create_assignment("ps2", "http://example.com")
remove_assignment("ps2")
print_assignments()