// SPDX-License-Identifier: LGPL-3.0-only
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <dpack/codec.h>
#include <execinfo.h>
#include <signal.h>
#include <json-c/json_util.h>
#include <json-c/json_tokener.h>
#include <test-typescript/lib.h>
#include <hed/rpc_clnt.h>
#include <stdlib.h>

__AFL_FUZZ_INIT();

#define STACK_DEPTH   128
static void handler(int sig __unused)
{
	void *buffer[STACK_DEPTH];
	char **strings;
	int size, i;

	size = backtrace(buffer, STACK_DEPTH);
	strings = backtrace_symbols(buffer, size);
	fprintf(stderr, "Aborted.  Backtrace:\n");
	for (i = 0; i < size; i++) {
		if (strings[i][0] == '.' && strings[i][1] == '/')
			strings[i] += 2;
		fprintf(stderr, " %3d   %s\n", i, strings[i]);
	}
	fprintf(stderr, "\n");
	free(strings);
	exit(1);
}

static int
pack_to_file(char * file __unused)
{
	return 0;
}

int main(int argc, char * const argv[])
{
	int ret;
	struct galv_rpc_clnt clnt;
	const struct sockaddr_un peer = UNSK_NAMED_ADDR("sock");

	signal(SIGABRT, handler);

	if (argc == 2)
		return pack_to_file(argv[1]);

	ret = hed_rpc_clnt_open(&clnt, O_CLOEXEC);
	if (ret)
		return ret;

	ret = hed_rpc_clnt_connect(&clnt, &peer, UNSK_NAMED_ADDR_LEN("sock"));
	if (ret)
		goto close;

#ifdef __AFL_HAVE_MANUAL_CONTROL
	__AFL_INIT();
#endif
	unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

	while (__AFL_LOOP(UINT_MAX)) {

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wconversion"
		size_t len __unused = __AFL_FUZZ_TESTCASE_LEN;
#pragma GCC diagnostic pop

		struct json_object *request = json_tokener_parse((const char *)buf);
		if (!request)
			goto end;

		struct json_object *response = json_object_new_object();
		if (!response) {
			json_object_put(request);
			goto end;
		}

		ret = ts_rsync_from_json(&clnt, request, response);
		json_object_put(request);
		if (!ret)
			json_object_to_fd(1, response, JSON_C_TO_STRING_PLAIN);
		json_object_put(response);

end:
#ifdef __AFL_LEAK_CHECK
		__AFL_LEAK_CHECK();
#else
	/*
	 * To remove warning:
	 * label at end of compound statement is a C23 extension
	 */
		;
#endif
	}
close:
	hed_rpc_clnt_close(&clnt);
	return ret;
}

