PYTHON=python
MODULE=matrix
CMD=$(PYTHON) -m $(MODULE)
GCC=gcc
LINK_OPTS=-lm

export PYTHONPATH := ../..

# we need wildcard expansion here to get a list of individual files
# this will cause the implicit rule to fire for each file
SOURCES=$(wildcard *.mat)
ASSEMBLY=$(patsubst %.mat,%.s,$(SOURCES))
PROGS=$(patsubst %.mat,%.out,$(SOURCES))
CMPS=$(patsubst %.mat,%.cmp,$(SOURCES))

all: progs

# ignore errors so all tests will be run
# also, make it depend on an empty target so each test will always run regardless
# (this is easier than make it dependent on all kinds of files in the matrix module
# the $< will make sure the input is the first file and not the FORCE also ($^ would do that) 
%.s : %.mat FORCE
	@- ($(CMD) -d -o $(basename $@) $< 2>&1 >/dev/null) || echo $< did not compile

%.out : %.s
	@- $(GCC) -o $@ $< $(LINK_OPTS) || echo $< did not assemble or link
	@- if ! (./$@ | diff --brief - $(basename $@).cmp 2>&1 > /dev/null) ; then echo $(basename $@).mat output not as expected ; fi

progs: $(PROGS)

clean:
	rm -f *.grammar *.tok *.parse *.ast *.s *.out

.PHONY: all clean progs

FORCE:
