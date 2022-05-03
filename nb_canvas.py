import sys, os, configparser, shutil
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
		lines = [
			'c = get_config()\n\n',
			'c.CourseDirectory.course_id = "%s"\n\n' % course_id,
			'c.ClearSolutions.begin_solution_delimeter = "BEGIN MY SOLUTION"\n',
			'c.ClearSolutions.end_solution_delimeter = "END MY SOLUTION"\n',
			'c.ClearSolutions.code_stub = {\n',
			'	"python": "# your code here\\nraise NotImplementedError",\n',
			'	"C#": "// your code here",\n',
			'	"C++11": "// your code here",\n',
			'	"C++14": "// your code here",\n',
			'	"C++17": "// your code here"\n',
			'}\n'
		]
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
	print("---Gradebook Student List---")
	for student in gradebook.students:
		print("%s - %s %s - %s" %(
			student.id,
			student.first_name,
			student.last_name,
			student.email
			))
	print()


# adds students to gradebook, or updates existing entries
# expects arg 1 to be an array of string NetIDs
def __db_add_students(students):
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


# removes student from local gradebook
# expects arg 1 to be student ID as string
def __db_remove_student(student):
	try:
		gradebook.remove_student(student)
	except Exception as e:
		print(e)


# Check if assignment exists within gradebook and return it if found
def __db_check_assignment(assignment_name):
	for assignment in gradebook.assignments:
		if assignment.name == assignment_name:
			return True
	return False


# Print db assignment list
def __db_print_assignments():
	print("---%s Gradebook Assignment List---" % os.getcwd().split('/')[-1])
	for assignment in gradebook.assignments:
		print(assignment.name)
		print(assignment.id)
	print()


# Add assignment to gradebook
def __db_create_assignment(assignment_name, canvas_assignment_name):
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
	else:
		print("Gradebook Error: Cannot find %s on Canvas" % assignment_name)


# Remove assignment from gradebook
def __db_remove_assignment(assignment_name):
	try:
		gradebook.remove_assignment(assignment_name)
		print('Gradebook assignment "%s" deleted successfully' % assignment_name)
		return True
	except Exception as e:
		print("Gradebook Error: %s" % e)
		return False


# Return score from student submission
def __db_get_submission_score(submission):
	score = submission.score
	return score


def __db_get_assignment_max_score(assignment_name):
	try:
		submissions = gradebook.assignment_submissions(assignment_name)
		max_score = 0
		for submission in submissions:
			if submission.max_score > max_score:
				max_score = submission.max_score
		return max_score
	except Exception as e:
		print("Gradebook Error: %s" % e)


def __db_get_assignment_submissions(assignment_name):
	submissions = gradebook.assignment_submissions(assignment_name)
	s = submissions
	return s



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
	finally:
		nb_api.unrelease(assignment_name)
		shutil.rmtree("%srelease/%s" % (course_dir, assignment_name), ignore_errors=True)
		if os.path.exists("%ssubmitted/" % (course_dir)):
			for student in os.listdir("%ssubmitted/" % (course_dir)):
				shutil.rmtree("%ssubmitted/%s/%s" % (course_dir, student, assignment_name), ignore_errors=True)
		if os.path.exists("%sautograded/" % (course_dir)):
			for student in os.listdir("%sautograded/" % (course_dir)):
				shutil.rmtree("%sautograded/%s/%s" % (course_dir, student, assignment_name), ignore_errors=True)
		if os.path.exists("%sfeedback/" % (course_dir)):
			for student in os.listdir("%sfeedback/" % (course_dir)):
				shutil.rmtree("%sfeedback/%s/%s" % (course_dir, student, assignment_name), ignore_errors=True)
		#shutil.rmtree("%sautograded/%s" % (course_dir, assignment_name))
		#shutil.rmtree("%ssubmitted/%s" % (course_dir, assignment_name))
		#shutil.rmtree("%sfeedback/%s" % (course_dir, assignment_name))


# Get and return feedback files for submissions
def __nb_get_feedback_files(student_name, assignment_name):
	if exists("%sfeedback/%s/%s/" % (course_dir, student_name, assignment_name)):
		feedback_files = (os.listdir("%sfeedback/%s/%s/" % (course_dir, student_name, assignment_name)))
		for i in range(len(feedback_files)):
			if not feedback_files[i].endswith('.html'):
				feedback_files[i] = None # purge non-html files from feedback list
		feedback_files = list(filter(None, feedback_files)) # remove all null elements
		return feedback_files



########## PRIVATE CANVAS FUNCTIONS ##########

# return Canvas student list
def __c_get_students():
	return course.get_users(enrollment_type = ["student"], sort = "username")


# Return internal Canvas id of student (note: this is not the login_id)
def __c_get_student_internal_id(student_id):
	students = __c_get_students()
	for student in students:
		if student.login_id == student_id:
			return student.id


# DEBUGGING FUNCTION to print Canvas course student list
def __c_print_students():
	print("---%s Canvas Student List---" % course)
	for student in __c_get_students():
		print(vars(student))
		print("%s - %s" % (student.login_id, student.name))
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
def __c_create_assignment(assignment_name, *args):
	if __c_check_assignment(assignment_name) != False:
		print('Canvas Error: Assignment "%s" already exists' % assignment_name)
		return False
	try:
		if len(args) == 0:
			course.create_assignment({
				"name": assignment_name
			})
			print('Canvas assignment "%s" created successfully' % assignment_name)
			return True
		elif len(args) == 1:
			course.create_assignment({
				"name": assignment_name,
				"description": '<a href="%s">%s</a>' % (args[0], assignment_name)
			})
			print('Canvas assignment "%s" created successfully' % assignment_name)
			return True
		else:
			print("Incorrect number of arguments in __c_create_assignment()")
			return False
	except Exception as e:
		print("Canvas Error: %s" % e)
		return False


# Remove an assignment from Canvas
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


# Update max score of Canvas assignment
def __c_update_assignment_max_score(assignment_name, max_score):
	assignment = __c_check_assignment(assignment_name)
	try:
		assignment.edit(assignment = {"points_possible" : max_score})
	except Exception as e:
		print(e)


# Make assignment visible to students on Canvas
def __c_publish_assignment(assignment_name):
	assignment = __c_check_assignment(assignment_name)
	try:
		assignment.edit(assignment = {"published" : True})
	except Exception as e:
		print(e)


# Post Gradebook grade to Canvas
def __c_post_grade(assignment_name, student_name, grade):
	assignment = __c_check_assignment(assignment_name)
	# First check if max possible_points has been updated
	db_max = int(__db_get_assignment_max_score(assignment_name))
	if not assignment:
		print("Canvas Error: Cannot find %s" % assignment_name)
		return False
	if db_max != assignment.points_possible:
		print("Notice: Updating max possible points for Canvas assignment")
		__c_update_assignment_max_score(assignment_name, db_max)
	print("Grading: %s" % student_name)
	submission = __c_get_submission(assignment_name, student_name)
	submission.edit(submission = {"posted_grade" : grade})


# Post assignment feedback to Canvas
def __c_post_feedback(assignment_name, student_name):
	submission = __c_get_submission(assignment_name, student_name)
	# get feedback html files
	feedback_files = __nb_get_feedback_files(student_name, assignment_name)
	if feedback_files:
		for feedback in feedback_files:
			submission.upload_comment("%sfeedback/vle/%s/%s" % (course_dir, assignment_name, feedback))


# Get student's assignment submission from Canvas
def __c_get_submission(assignment_name, student_name):
	assignment = __c_check_assignment(assignment_name)
	# Verify that assignment has been published
	if not assignment.published:
		__c_publish_assignment(assignment_name)
	student_internal_id = __c_get_student_internal_id(student_name)
	return assignment.get_submission(student_internal_id)



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
def create_assignment(assignment_name, *args):
	sanitized_assignment_name = ''.join(filter(str.isalnum, assignment_name))
	if len(args) == 0:
		__c_create_assignment(assignment_name)
	elif len(args) == 1:
		__c_create_assignment(assignment_name, args[0])
	else:
		print("Incorrect number of args in create_assignment()")
		return False
	__nb_create_assignment(sanitized_assignment_name)
	__db_create_assignment(sanitized_assignment_name, assignment_name)


def remove_assignment(assignment_name):
	sanitized_assignment_name = ''.join(filter(str.isalnum, assignment_name))
	__c_remove_assignment(assignment_name)
	__nb_remove_assignment(sanitized_assignment_name)
	__db_remove_assignment(sanitized_assignment_name)


def publish_assignment(assignment_name):
	nb_api.generate_assignment(assignment_name)
	nb_api.release_assignment(assignment_name)
	__c_publish_assignment(assignment_name)


# publishes assignment grades AND feedback to Canvas
def post_grades(assignment_name):
	db_submissions = __db_get_assignment_submissions(assignment_name)
	for db_submission in db_submissions:
		__c_post_grade(assignment_name, db_submission.student_id, db_submission.score)
		__c_post_feedback(assignment_name, db_submission.student_id)
	return


############################################################################

# Initialize config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

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

# Initialize Gradebook
gradebook = __set_db()


### TESTING ZONE
#remove_assignment("Assignment1")
#create_assignment("Assignment1")
#publish_assignment("Assignment1")
#post_grades("Assignment1")
#print(__nb_get_feedback_files("vle", "Assignment1"))


# Close Gradebook
#gradebook.close()
