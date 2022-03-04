import sys, os, configparser
from os.path import exists
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


# creates required course directories if they do not exist
def __create_course(course_dir):
	try:
		os.makedirs("%ssource" % course_dir)
	except:
		pass
	finally:
		os.chdir(course_dir) # set working directory
		course_id = os.getcwd().split('/')[-1]
		lines = ['c = get_config()\n\n', 'c.CourseDirectory.course_id = "%s"\n\n' % course_id]
		if not exists("%snbgrader_config.py" % course_dir):
			os.system("nbgrader generate_config --quiet")
			with open("%snbgrader_config.py" % course_dir, 'r') as file:
				default_config = file.read()
			with open("%snbgrader_config.py" % course_dir, 'w') as file:
				file.writelines(lines)
			with open("%snbgrader_config.py" % course_dir, 'a') as file:
				file.write(default_config)


########## PRIVATE GRADEBOOK FUNCTIONS ##########

# DEBUGGING FUNCTION to print gradebook student list
def __db_print_students():
	gradebook = __set_db()
	print("---Gradebook Student List---")
	for student in gradebook.students:
		print("%s - %s %s - %s" %(
			student.id,
			student.first_name,
			student.last_name,
			student.email
			))
	print()
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
	print("---%s Gradebook Assignment List---" % os.getcwd().split('/')[-1])
	for assignment in gradebook.assignments:
		print(assignment.name)
		print(assignment.id)
	print()
	gradebook.close()


# Add assignment to gradebook
def __db_create_assignment(assignment_name, canvas_assignment_name):
	gradebook = __set_db()
	canvas_assignment = __c_check_assignment(canvas_assignment_name)
	if canvas_assignment:
		try:
			gradebook.add_assignment(assignment_name)
			gradebook.update_or_create_assignment(assignment_name, id = canvas_assignment.id)
			print('Gradebook assignment "%s" created successfully' % assignment_name)
			return True
		except Exception as e:
			print("Gradebook Error: %s" % e)
			return False
		finally:
			gradebook.close()
	else:
		print("Gradebook Error: Cannot find %s on Canvas" % assignment_name)


# Remove assignment from gradebook
def __db_remove_assignment(assignment_name):
	gradebook = __set_db()
	try:
		gradebook.remove_assignment(assignment_name)
		print('Gradebook assignment "%s" deleted successfully' % assignment_name)
		return True
	except Exception as e:
		print("Gradebook Error: %s" % e)
		return False
	finally:
		gradebook.close()


# Return score and max_score from student submission
def __db_get_student_score(assignment_name, student_id):
	gradebook = __set_db()
	try:
		score = gradebook.find_submission(assignment_name, student_id).score
		max_score = gradebook.find_submission(assignment_name, student_id).max_score
		grade = [score, max_score]
		return grade
	except Exception as e:
		print("Gradebook Error: %s" % e)


########## PRIVATE NBGRADER FUNCTIONS ##########

# DEBUGGING FUNCTION to print nbgrader source folder assignment list
def __nb_print_assignments():
	print("---%s nbgrader Assignment List---" % os.getcwd().split('/')[-1])
	for assignment in nb_api.get_source_assignments():
		print(assignment)
	print()


# creates an nbgrader assignment
def __nb_create_assignment(assignment_name):
	try:
		os.makedirs("%ssource/%s" % (course_dir, assignment_name))
		print('nbgrader assignment "%s" created successfully' % assignment_name)
		return True
	except Exception as e:
		print("nbgrader Error: %s" % e)
		return False

# NOTICE: Will only delete empty assignment folders
# Assignments containing notebooks must be deleted manually
def __nb_remove_assignment(assignment_name):
	try:
		os.rmdir("%ssource/%s" % (course_dir, assignment_name))
		print('nbgrader assignment "%s" deleted successfully' % assignment_name)
		return True
	except Exception as e:
		print("nbgrader Error: %s" % e)
		return False



########## PRIVATE CANVAS FUNCTIONS ##########

# return Canvas student list
def __c_get_students():
	return course.get_users(enrollment_type = ["student"], sort = "username")


# DEBUGGING FUNCTION to print Canvas course student list
def __c_print_students():
	print("---%s Canvas Student List---" % course)
	for i in __c_get_students():
		print("%s - %s" % (i.login_id, i.name))
	print()


# return Canvas assignment list
def __c_get_assignments():
	return course.get_assignments()


# DEBUGGING FUNCTION to print Canvas course assignment list
def __c_print_assignments():
	print("---%s Canvas Assignment List---" % course)
	for i in __c_get_assignments():
		print(i)
	print()


# Create new assignment within Canvas
def __c_create_assignment(assignment_name, url):
	if __c_check_assignment(assignment_name) != False:
		print('Canvas Error: Assignment "%s" already exists' % assignment_name)
		return False
	course.create_assignment({
		"name": assignment_name,
		"description": '<a href="%s">%s</a>' % (url, assignment_name)
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



########## PUBLIC FUNCTIONS ##########

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
def create_assignment(assignment_name, url):
	sanitized_assignment_name = ''.join(filter(str.isalnum, assignment_name))
	__c_create_assignment(assignment_name, url)
	#time.sleep(1)
	__nb_create_assignment(sanitized_assignment_name)
	#time.sleep(1)
	__db_create_assignment(sanitized_assignment_name, assignment_name)


def remove_assignment(assignment_name):
	sanitized_assignment_name = ''.join(filter(str.isalnum, assignment_name))
	__c_remove_assignment(assignment_name)
	__nb_remove_assignment(sanitized_assignment_name)
	__db_remove_assignment(sanitized_assignment_name)


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
if " " in course_dir: # Verify there are no spaces in course name
	sys.exit("Error: Course name cannot contain spaces or special characters")
course_dir = os.path.expanduser(course_dir) # this line accommodates for ~/ usage
__create_course(course_dir)
config_loader = PyFileConfigLoader(filename = "nbgrader_config.py")
nbconfig = config_loader.load_config()
nb_api = NbGraderAPI(config = nbconfig)


### TESTING ZONE
