#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <errno.h>
#include <sys/wait.h>

static int exec_prog(const char **argv)
{
    pid_t   my_pid;
    int     status;

    if (0 == (my_pid = fork())) {
        if (-1 == execve(argv[0], (char **)argv , NULL)) {
            perror("[MV] Child process execve failed [%m]");
            return -1;
        }
    }

    while (0 == waitpid(my_pid , &status , WNOHANG)) {
        sleep(1); // second
    }

    if (status != 0) {
    	printf("[MV] %s WEXITSTATUS %d WIFEXITED %d [status %d]\n",
            argv[0], WEXITSTATUS(status), WIFEXITED(status), status);
    }

    if (1 != WIFEXITED(status) || 0 != WEXITSTATUS(status)) {
        perror("[MV] %s failed, halt system");
        return -1;
    }
    return 0;
}

int main (int argc, const char *argv[])
{
    const char** luargv = (const char**) calloc(argc + 3, sizeof(char *));
    luargv[0] = "/home/user/traqumoto/Applications/torch/install/bin/th"; //"/usr/bin/lua";
    luargv[1] = "/home/user/traqumoto/src/traqumoto.lua";
    for (int i = 1; i < argc; i++)
    {
        luargv[i + 1] = argv[i];
    }
    exec_prog(luargv);

    return 0;
}
