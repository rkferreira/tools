#define _XOPEN_SOURCE 500
#define _GNU_SOURCE
#include <ftw.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXFDS 8192

/* Lets scan this filesystem!
 * depth level is 3
 * maxfd is 8192
 * 
 * Author: Rodrigo Kellermann Ferreira
 * mainly based on man 3 ftw
 *
 *
 */

static int display_info(const char *fpath, const struct stat *sb, int tflag, struct FTW *ftwbuf)
{
	if ((ftwbuf->level == 3) && (tflag == FTW_D)) {
		printf("%-40s  %s \n", fpath, fpath + ftwbuf->base);
		return FTW_SKIP_SUBTREE;
	}
	return FTW_CONTINUE;
}

int main(int argc, char *argv[])
{
	int flags = 0;
	char *tpath;
	flags |= FTW_ACTIONRETVAL;
	flags |= FTW_D;

	if (argc >= 2 && argv[1]) {
		tpath = argv[1];
	} else {
		tpath = ".";
	}
	//printf("%s", tpath);

	if ( nftw(tpath, display_info, MAXFDS, flags) == 0 )
		exit(EXIT_SUCCESS);
	else
		exit(EXIT_FAILURE);
}
