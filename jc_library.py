import os
from nbgrader.api import Gradebook

# test cases
# python3 -c "import jc_library; jc_library.add_students('~/testcourse/', ['bestreito','zestreito','gestreito'])"
# python3 -c "import jc_library; jc_library.print_students('~/testcourse/')"

# adds students to db after checking if student already exists or not
# expects arg 2 to be an array of strings
def add_students(course_dir, students):
	__set_db_dir(course_dir)
	try:
		gradebook = Gradebook("sqlite:///gradebook.db")
		for student in students:
			gradebook.update_or_create_student(student)
		gradebook.close()
	except Exception as e:
		print(e)
	return

def print_students(course_dir):
	__set_db_dir(course_dir)
	try:
		gradebook = Gradebook("sqlite:///gradebook.db")
		print(gradebook.students)
		gradebook.close()
	except Exception as e:
		print(e)
	return

def __set_db_dir(course_dir):
	course_dir = os.path.expanduser(course_dir)
	os.chdir(course_dir)
	return