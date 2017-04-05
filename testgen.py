from setup import *
import os.path 
import os, sys
import shutil
import yaml
def generate_binary_test(software,toolchain,verbose):
	toplevel_cmakelist_file=BUILDTEST_ROOT + "CMakeLists.txt"
	testingdir_cmakelist_file=BUILDTEST_TESTDIR + "CMakeLists.txt"
	swname = software[0]
	commandfile=BUILDTEST_SOURCEDIR + swname + "/command.yaml"  


	# if CMakeLists.txt does not exist in top-level directory, create the header
	if os.path.isfile(toplevel_cmakelist_file) == False:
		init_CMakeList(toplevel_cmakelist_file)

	create_dir(BUILDTEST_TESTDIR,verbose)
	# if BUILDTEST_TESTDIR/CMakeLists.txt does not exist, then create it
	if os.path.isfile(testingdir_cmakelist_file) == False:
		fd=open(testingdir_cmakelist_file,'w')
		fd.close()
	# if command.txt does not exist then report error
	if os.path.isfile(commandfile) == False:
		print "Warning: Cannot find command file:", commandfile, "Skipping binary test"
	else:
	    process_binary_file(commandfile,software,toolchain,verbose)

# generate test for source
def generate_source_test(software,toolchain,configmap,codedir,verbose):
	appname=software[0]
	appver=software[1]
	tcname=toolchain[0]
	tcver=toolchain[1]
	
	destdir=BUILDTEST_TESTDIR+appname+"/"+appver+"/"+tcname+"/"+tcver+"/"
	cmakelist=destdir+"CMakeLists.txt"

	# testname is key value "name" with .sh extension
	testname=configmap["name"]+".sh"
	testpath=destdir+testname
	sourcefilepath=codedir+configmap["source"]
	executable=configmap["source"]+".exe"

	flags=""
	# if buildopts key exists in dictionary
	if "buildopts" in configmap:
		flags=configmap["buildopts"]

	fd=open(testpath,'w')
	header=load_modules(software,toolchain)
	fd.write(header)
	
	buildcmd=""
	compiler=""
	compiler,testblockname=process_testblock(configmap)
	
	if testblockname == "generic" or testblockname == "intel" or testblockname == "mpi" or testblockname == "intel-mpi":
		buildcmd = compiler + " -o " + executable + " " + sourcefilepath + " " + flags + "\n"
	if testblockname == "generic" or testblockname == "intel" or testblockname == "cuda":
		runcmd = "./" + executable + "\n"
	elif testblockname == "mpi" or testblockname == "intel-mpi":
		runcmd = "mpirun -np 2 ./" + executable + "\n"

	clean="rm ./" + executable 
	fd.write(buildcmd)
	fd.write(runcmd)
	fd.write(clean)
	fd.close()

	fd=open(cmakelist,'a')
	add_test_str="add_test(NAME " + appname + "-" + appver + "-" + tcname + "-" + tcver + "-" + testname + "\t COMMAND sh " + testname + "\t WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}) \n"
	fd.write(add_test_str)
	fd.close()

	print "Creating Test: ",testpath	
# get the appropriate compiler based on the testblock used. Compiler/Wrappers can be gcc,icc,nvcc,javac,python,R,perl,etc...
def process_testblock(configmap):
	# get extension for source file
	ext = os.path.splitext(configmap["source"])[1]
	compiler=""

	testblockname=configmap["testblock"]
	# determine compiler based on testblockname and its file extension
	if ext == ".c":
		if testblockname == "generic":
			compiler="gcc"
		elif testblockname == "intel":
			compiler="icc"
		elif testblockname == "mpi":
			compiler="mpicc"
		elif testblockname == "intel-mpi":
			compiler="mpiicc"
		elif testblockname == "cuda":
			compiler="nvcc"
	elif ext == ".cpp":
		if testblockname == "generic":
			compiler="g++"
		elif testblockname == "intel":
			compiler="icpc"
		elif testblockname == "mpi":
			compiler="mpic++"
		elif testblockname == "intel-mpi":
			compiler="mpiicpc"
	elif ext == ".f90" or ext == ".f" or ext == ".f77":
		if testblockname == "generic":
			compiler="gfortran"
		elif testblockname == "intel":
			compiler="ifort"
		elif testblockname == "mpi":
			compiler="mpifort"
		elif testblockname == "intel-mpi":
			compiler="mpiifort"
	if testblockname == "python":
		compiler="python"
	return compiler,testblockname
# read binary file (command.txt) and create template shell script 
def process_binary_file(filename,software,toolchain,verbose):
	name,version=software
	toolchain_name,toolchain_version=toolchain
	#print "values",name,version,toolchain_name,toolchain_version
	# if top level software directory is not present, create it
	test_name_dir=BUILDTEST_TESTDIR + name
	test_version_dir=test_name_dir + "/" + version
	test_toolchain_name_dir=test_version_dir + "/" + toolchain_name
	test_toolchain_version_dir=test_toolchain_name_dir + "/" + toolchain_version

	test_cmakelist = BUILDTEST_TESTDIR + "/CMakeLists.txt"
	test_name_cmakelist = test_name_dir + "/CMakeLists.txt"
	test_version_cmakelist = test_version_dir + "/CMakeLists.txt"
	test_toolchain_name_cmakelist = test_toolchain_name_dir + "/CMakeLists.txt"
	test_toolchain_version_cmakelist = test_toolchain_version_dir + "/CMakeLists.txt"

	test_destdir=test_toolchain_version_dir
	# if testdirectory exist, delete and recreate it inorder for reproducible test builds
	if os.path.isdir(test_destdir):
		shutil.rmtree(test_destdir)

	# create directories if they don't exist
	# Directory Format: <software>/<version>/toolchain-name>/<toolchain-version>
	create_dir(test_name_dir,verbose)
	create_dir(test_version_dir,verbose)
	create_dir(test_toolchain_name_dir,verbose)
	create_dir(test_toolchain_version_dir,verbose)
	
	# create CMakeList.txt file in each directory of <software>/<version>/<toolchain-name>/<toolchain-version> if it doesn't exist
	create_file(test_name_cmakelist,verbose)
	create_file(test_version_cmakelist,verbose)
	create_file(test_toolchain_name_cmakelist,verbose)
	create_file(test_toolchain_version_cmakelist,verbose)

	check_CMakeLists(test_cmakelist,name,verbose)
	check_CMakeLists(test_name_cmakelist,version,verbose)
	check_CMakeLists(test_version_cmakelist,toolchain_name,verbose)
	check_CMakeLists(test_toolchain_name_cmakelist,toolchain_version,verbose)

		
	header=load_modules(software,toolchain)

	fd=open(filename,'r')
	content=yaml.load(fd)
	# if key binaries is not in yaml file, exit program
	if "binaries" not in content:
		print "Cant find key binaries in file: ", filename, " Exiting program"
		sys.exit(1)

	# create a binary test script for each key,value item in dictionary
	binarydict=content["binaries"]
	for key in binarydict:
		testname=key+".sh"
		testpath=test_destdir + "/" + testname
		fd=open(testpath,'w')
		fd.write(header)
		# if paramter is specified then write both executable and parameter to file otherwise only write the executable
		if binarydict[key]:
			fd.write(key + " " + binarydict[key])
		else:
			fd.write(key)
		fd.close()

		fd=open(test_toolchain_version_cmakelist,'a')
		add_test_str="add_test(NAME " + name + "-" + version + "-" + toolchain_name + "-" + toolchain_version + "-" + testname + "\t COMMAND sh " + testname + "\t WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}) \n"
		fd.write(add_test_str)

		print "Creating Test:", testpath
		
# create directory if it doesn't exist
def create_dir(dirname,verbose):
	if not os.path.isdir(dirname):
		os.mkdir(dirname)
		if verbose >= 1:
			print "Creating Directory: ",dirname

# create an empty file if it doesn't exist
def create_file(filename,verbose):
	if not os.path.isfile(filename):
		fd=open(filename,'w')
		fd.close()
		if verbose >= 1:
			print "Creating Empty File:", filename

# used for writing CMakeLists.txt with tag <software>, <version>, & toolchain
def check_CMakeLists(filename,tag, verbose):
	fd=open(filename,'r')
	content=fd.read().strip().split("\n")
	cmd="add_subdirectory("+tag+")"
	if cmd not in content:
		fd.close()
		fd=open(filename,'a')
		fd.write(cmd+"\n")
		fd.close()
		if verbose >= 1:
			print "writing:", cmd, "to file:",filename 
	else:
		fd.close()	
#def write_binary_test(filename):
def init_CMakeList(filename):
	header = """ 
cmake_minimum_required(VERSION 2.8)
include(CTest)
ENABLE_TESTING()
add_subdirectory(""" + BUILDTEST_TESTDIR + ")"
	fd=open(filename,'w')
	fd.write(header)
	fd.close()
# return a string that loads the software and toolchain module. 
def load_modules(software,toolchain):
	# for dummy toolchain you can load software directly. Ensure a clean environment by running module purge
	if toolchain[0] == "dummy":
		header="""
#!/bin/sh
module purge
module load """ + software[0] + "/" + software[1] + """
"""
	else:
		header="""
#!/bin/sh
module purge
module load """ + toolchain[0] + "/" + toolchain[1] + """
module load """ + software[0] + "/" + software[1] + """
"""
	
	return header
			