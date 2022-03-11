SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
CC = gcc -fPIC
COMPILE_OPTS = -c -fPIC
LINK_OPTS = -shared -fPIC

all: matrix_stdlib.so

# the rules to compile .c to .o are implicit

matrix_stdlib.so: $(OBJECTS)
	$(CC) $(LINK_OPTS) -o $@ $^

clean:
	rm *.o

.PHONY: all clean
