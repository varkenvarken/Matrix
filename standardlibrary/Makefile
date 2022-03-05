SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
CC = gcc
COMPILE_OPTS = -c
LINK_OPTS = -shared

all: matrix_stdlib.so

# the rules to compile .c to .o are implicit

matrix_stdlib.so: $(OBJECTS)
	$(CC) $(LINK_OPTS) -o $@ $^

clean:
	rm *.o

.PHONY: all clean
