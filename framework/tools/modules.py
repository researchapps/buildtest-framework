############################################################################
#
#  Copyright 2017
#
#   https://github.com/HPC-buildtest/buildtest-framework
#
#  This file is part of buildtest.
#
#    buildtest is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    buildtest is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with buildtest.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

"""
This python module does the following
	 - get module listing
	 - get unique application
	 - get unique application version
	 - get easybuild toolchains
 	 - check if software exists based on argument -s
	 - check if toolchain exists based on argument -t
	 - check if easyconfig passes

:author: Shahzeb Siddiqui (Pfizer)
"""
import os
import sys

from framework.env import config_opts
#from framework.tools.utility import get_appname, get_appversion, get_toolchain_name, get_toolchain_version


def get_module_list():
	"""
	returns a complete list of modules and full path in module tree
	"""
	modulefiles = []
	BUILDTEST_MODULE_EBROOT = config_opts['DEFAULT']['BUILDTEST_MODULE_EBROOT']
	# if there is no : then there is only one module tree
	if BUILDTEST_MODULE_EBROOT.find(":") == 0:
		if not os.path.exists(BUILDTEST_MODULE_EBROOT):
			print "Invalid module tree: ", BUILDTEST_MODULE_EBROOT
			sys.exit(0)

		for root, dirs, files in os.walk(BUILDTEST_MODULE_EBROOT):
			for file in files:
				modulefiles.append(os.path.join(root,file))

	# more than one module tree, process each module tree and return list of module files
	else:
		mod_trees = BUILDTEST_MODULE_EBROOT.split(":")
		for moduletree in mod_trees:
			# check if each module tree is valid path
			if not os.path.exists(moduletree):
				print "Invalid module tree", moduletree
				sys.exit(0)

			for root, dirs, files in os.walk(moduletree):
				for file in files:
					modulefiles.append(os.path.join(root,file))

	return modulefiles

def load_modules(shell_type):
        """
        return a string that loads the software and toolchain module.
        """

	from framework.tools.utility import get_appname, get_appversion, get_toolchain_name, get_toolchain_version
	shell_magic = "#!/" + os.path.join("bin",shell_type)

        appname = get_appname()
        appversion = get_appversion()
        tcname = get_toolchain_name()
        tcversion = get_toolchain_version()

	BUILDTEST_MODULE_NAMING_SCHEME = config_opts['DEFAULT']['BUILDTEST_MODULE_NAMING_SCHEME']
	header = shell_magic
        header+= """
module purge
"""
        # for dummy toolchain you can load software directly. Ensure a clean environment by running module purge
        if len(tcname) == 0:
                moduleload = "module load " + appname + "/" + appversion  + "\n"
        else:
                if BUILDTEST_MODULE_NAMING_SCHEME == "HMNS":
                        moduleload = "module load " + tcname + "/" + tcversion + "\n"
                        moduleload += "module load " + appname + "/" + appversion + "\n"
                elif BUILDTEST_MODULE_NAMING_SCHEME == "FNS":
                        moduleload = "module load " + tcname + "/" + tcversion + "\n"
                        toolchain_name = appname + "-" + tcversion
                        appversion = appversion.replace(toolchain_name,'')
                        if appversion[-1] == "-":
                                appversion = appversion[:-1]

                        moduleload += " module load " + appname + "/" + appversion + "-" + tcname + "-" + tcversion + "\n"

        header = header + moduleload
        return header
