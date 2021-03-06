PYTHON=python
MODULE=matrix
CMD=$(PYTHON) -m $(MODULE) -p

export PYTHONPATH := ../..

# we need wildcard expansion here to get a list of individual files
# this will cause the implicit rule to fire for each file
SOURCES=$(wildcard *.mat)
OUTPUTS=$(patsubst %.mat,%.parse,$(SOURCES))
CMPS=$(patsubst %.mat,%.cmp,$(SOURCES))

all: progs

# quote for GNU make docs:
#.SECONDARY with no prerequisites causes all targets to be treated as secondary
# (i.e., no target is removed because it is considered intermediate).
# this way we keep the generate .s files
.SECONDARY:

# ignore errors so all tests will be run
# also, make it depend on an empty target so each test will always run regardless
# (this is easier than make it dependent on all kinds of files in the matrix module
# the $< will make sure the input is the first file and not the FORCE also ($^ would do that) 
%.parse : %.mat FORCE
	@- ($(CMD) -d -o $(basename $@) $< 2>&1 >/dev/null) || echo $< did not compile
	@- if ! (cat ./$@ | diff --brief - $(basename $@).cmp 2>&1 > /dev/null) ; then echo $(basename $@).mat output not as expected ; fi

progs: $(OUTPUTS)

clean:
	rm -f *.grammar *.tok *.parse *.ast *.s *.out

.PHONY: all clean progs

FORCE:

