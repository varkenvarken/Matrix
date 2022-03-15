SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
INCLUDES = $(patsubst %.c,%.h,$(SOURCES))

CC = gcc -fPIC -g
COMPILE_OPTS = -c -fPIC -g
LINK_OPTS = -shared -fPIC -g

all: matrix_stdlib.so

# the rules to compile .c to .o are implicit

matrix_stdlib.so: $(OBJECTS)
	$(CC) $(LINK_OPTS) -o $@ $^

clean:
	rm *.o

.PHONY: all clean
