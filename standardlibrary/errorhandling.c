void __real_error(int status, int errnum, const char *format, ...);

// see: https://stackoverflow.com/questions/19023018/overriding-c-library-functions-calling-original
void __wrap_error(char *msg)
{
    __real_error(1, 1, msg); // exit 1, errno 1 (Operation not permitted)
}