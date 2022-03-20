SOURCES = $(wildcard *.c)
OBJECTS = $(patsubst %.c,%.o,$(SOURCES))
INCLUDES = $(patsubst %.c,%.h,$(SOURCES))

CC = gcc -fPIC -O3
COMPILE_OPTS = -c -fPIC -O3
# https://stackoverflow.com/questions/19023018/overriding-c-library-functions-calling-original
# we wrap the error function with our own
LINK_OPTS = -Wl,--wrap=error -shared -fPIC -O3

all: matrix_stdlib.so

# the rules to compile .c to .o are implicit

matrix_stdlib.so: $(OBJECTS)
	$(CC) $(LINK_OPTS) -o $@ $^

clean:
	rm *.o

.PHONY: all clean
