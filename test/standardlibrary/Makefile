SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
CC = gcc -fPIC -g
COMPILE_OPTS = -c -fPIC
LINK_OPTS = -g ../../standardlibrary/matrix_stdlib.so -lm

PROGS=$(patsubst %.c,%.out,$(SOURCES))
CMPS=$(patsubst %.c,%.cmp,$(SOURCES))

all: progs

# the rules to compile .c to .o are implicit

%.out : %.o
	@- $(CC) -o $@ $< $(LINK_OPTS) || echo $< did not assemble or link
	@- if ! (./$@ | diff --brief - $(basename $@).cmp 2>&1 > /dev/null) ; then echo $(basename $@).mat output not as expected ; fi

progs: $(PROGS)


clean:
	rm -f *.o *.out

.PHONY: all clean
