# The lines below extract out program names from the cmake cache
# This is used to automatically generate a documentation page.
C_ = $(shell sed -n -e 's/;/ /g'                                \
                    -e 's/SOLVER_EXECUTABLES:STRING=//gp'       \
                    -e 's/PROGRAMS:STRING=//gp'                 \
                    build/CMakeCache.txt)
C  = $(addprefix bin/, $(C_))

Python_ = $(shell sed -n -e 's/;/ /g'                           \
                         -e 's/PYs:STRING=//gp'                 \
                         build/CMakeCache.txt)
Python  = $(addprefix bin/, $(Python_))


scripts_ = $(shell sed -n -e 's/;/ /g'                          \
                          -e 's/SCRIPTS:STRING=//gp'            \
                          build/CMakeCache.txt)
scripts  = $(addprefix bin/, $(scripts_))

GUIs_  = $(shell sed -n -e 's/;/ /g'                            \
                        -e 's/GUIs:STRING=//gp'                 \
                        build/CMakeCache.txt)
GUIs   = $(addprefix bin/, $(GUIs_))

PWD := $(shell pwd)

UNAME := $(shell uname | tr [A-Z] [a-z])

help:
	@echo "Makefile options:"
	@echo "	make fab	 Compile all files and copy scripts from src to bin"
	@echo "	make doc	 Saves command names and docstrings into commands.html"
	@echo "	make zip	 Bundles relevant files in fab.zip"
	@echo "	make dist	 Copies files to Web directory"
	@echo " make install Copies files to /usr/local/bin"
	@echo "	make clean	 Removes compiled executables and scripts from bin"

fab:
	@echo "Building with CMake"
	@mkdir -p build

	@cd build;                                         \
	 cmake ../src;                                     \
	 echo $(PWD);                                      \
	 make;                                             \
	 make install | sed s@$(PWD)/src/../@@g

	
doc: commands.html
commands.html: fab
	@# Dump all of the command names
	@echo "	Storing command names"
	@echo "<html>\n<body>\n<pre>\ncommands:" > commands.html
	@for name in $(C) $(scripts) $(GUIs); do               \
	    echo "   "$$name >> commands.html;                 \
	done
	  
	@echo "" >> commands.html
	
	@# Dump command docstrings
	@echo "	Storing command docstrings"
	@for name in $(C) $(scripts) ; do                        \
	   ./$$name >> commands.html;                           \
	   echo "" >> commands.html;                            \
	done

zip: commands.html
	rm -f fab_$(UNAME).zip fab_src.zip
	zip -r fab_$(UNAME).zip commands.html Makefile src bin
	zip -r fab_src.zip commands.html Makefile src

dist: zip
	cp fab_$(UNAME).zip ../../Web/fab_$(UNAME).zip 
	cp fab_src.zip ../../Web/fab_src.zip
	cp bin/fab_set.py ../../Web/
	cp bin/fab_send ../../Web/
	cp commands.html ../../Web/

install: fab
	cp bin/* /usr/local/bin/

clean:
	@echo "Removing executables and scripts from bin"
	@rm -f $(Python) $(scripts) $(GUIs) $(C)
	@echo "Deleting build directory"
	@rm -rf build
	
