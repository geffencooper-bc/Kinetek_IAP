# This makefile compiles all the .cpp files in the 
# current directory and links them together

#CC specifies which compiler we're using
CXX = g++

#COMPILER_FLAGS specifies the additional compilation options we're using
# -w suppresses all warnings, -g adds debug information
COMPILER_FLAGS = -w -g -std=c++11

#INCLUDE_PATHS specifies the paths to the header files
INCLUDE_PATHS = -I.

#LIBRARY_PATHS specifies the paths to the libs
#LIBRARY_PATHS 

#LINKER_FLAGS specifies the libraries we're linking against
#LINKER_FLAGS

#EXEC_NAME specifies the name of our exectuable
EXEC = exec

SRCS := $(wildcard *.cpp) 
OBJS := $(patsubst %.cpp,%.o,$(SRCS)) 
# 1 make all depends on ArcadeSystem 
all: $(EXEC)

# the .o files come from the wilcard statements
$(EXEC): $(OBJS) 
	$(CXX) $^ $(INCLUDE_PATHS) $(COMPILER_FLAGS) -o $@ 

# 3 all the .o files rely on the .cpp files
# make typically does this implicitly but we
# only want each .o to rely only on its .cpp
DEPS := $(OBJS:.o=.d)

-include $(DEPS)

$(OBJS): %.o: %.cpp
	$(CXX) -MMD -c $(INCLUDE_PATHS) $(COMPILER_FLAGS) $< -o $@
clean:
	/bin/rm -f *.o *.d $(EXEC)