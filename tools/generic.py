def get_software_name_version(software):
	""" return the software as two separate values name and version """
	if software == None:
		return None,None
	else:
		return software[0],software[1]

def add_arg_to_runcmd(runcmd,arglist):
        # add each argument to runcmd
        print arglist
        for arg in arglist:
        # skip argument if value is not specified, by default set to None
                if arg == None:
                        continue
                # in case argument is not a string, convert it anyways
                runcmd+= " " + str(arg)
        return runcmd


def load_modules(software,toolchain):
        """
        return a string that loads the software and toolchain module. 
        """
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


def print_dictionary(dictionary):
        """
        prints the content of dictionary
        """
        for key in dictionary:
                print key, sset(dictionary[key])

def print_set(setcollection):
        """
        prints the content of set 
        """
        for item in setcollection:
                print item
class sset(set):
    def __str__(self):
        return ', '.join([str(i) for i in self])

