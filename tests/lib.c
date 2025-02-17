// SPDX-License-Identifier: LGPL-3.0-only
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <dpack/codec.h>
#include "test-lib.h"

__AFL_FUZZ_INIT();

static int
pack_to_file(char * file)
{
	struct dpack_encoder  enc;
	struct lib_afl        lib;
	char                 *out = NULL;
	int                   fd;
	int                   ret = EXIT_FAILURE;

	lib_init_afl(&lib);
	lib.uint8 = 5;
	lib.int_array_nb = 5;

	fd = open(file, O_WRONLY | O_CREAT |  O_CLOEXEC, 0640);
	if (fd < 0) {
		printf("Cannot open file %s\n", file);
		return 1;
	}
	
	out = malloc(LIB_AFL_PACKED_SIZE_MAX);
	if (!out) {
		printf("Cannot alloc %d io\n", LIB_AFL_PACKED_SIZE_MAX);
		out = NULL;
		goto error;
	}

	dpack_encoder_init_buffer(&enc, out, LIB_AFL_PACKED_SIZE_MAX);
	if (lib_encode_afl(&enc, &lib)) {
		printf("Fail to encode lib_afl\n");
		goto error;
	}

	dpack_encoder_fini(&enc, DPACK_DONE);
	if (write(fd, out, dpack_encoder_space_used(&enc)) < 0) {
		printf("Fail to write %s file\n", file);
		goto error;
	}

	ret = 0;
error:
	lib_fini_afl(&lib);
	close(fd);
	free(out);
	return ret;
}

int main(int argc, char * const argv[])
{
	struct dpack_decoder   dec;
	struct dpack_encoder   enc;
	struct lib_afl         lib;
	char                  *out;
	int                    ret = EXIT_FAILURE;
	bool                   abort = DPACK_ABORT;

	if (argc == 2)
		return pack_to_file(argv[1]);

	out = malloc(LIB_AFL_PACKED_SIZE_MAX);
	if (!out)
		return EXIT_FAILURE;

#ifdef __AFL_HAVE_MANUAL_CONTROL
	__AFL_INIT();
#endif
	unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

	while (__AFL_LOOP(UINT_MAX)) {

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wconversion"
		size_t len = __AFL_FUZZ_TESTCASE_LEN;
#pragma GCC diagnostic pop

		if (len < LIB_AFL_PACKED_SIZE_MIN)
			goto end;

		if (len > LIB_AFL_PACKED_SIZE_MAX)
			goto end;

		assert(!lib_init_afl(&lib));
		dpack_decoder_init_buffer(&dec, (const char *)buf, len);
		dpack_encoder_init_buffer(&enc, out, LIB_AFL_PACKED_SIZE_MAX);
		ret = lib_decode_afl(&dec, &lib);
		if (!ret) {
			assert(!lib_encode_afl(&enc, &lib));
			abort = DPACK_DONE;
		}
		dpack_encoder_fini(&enc, abort);
		dpack_decoder_fini(&dec);
		lib_fini_afl(&lib);
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
	free(out);
	return ret;
}
