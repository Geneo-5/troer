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
#include <test-lib/lib.h>

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
pack_to_file(char * file)
{
	struct dpack_decoder_buffer dec_buf;
	struct dpack_decoder * dec = (struct dpack_decoder *)&dec_buf;
	struct dpack_encoder_buffer enc_buf;
	struct dpack_encoder * enc = (struct dpack_encoder *)&enc_buf;
	struct lib_afl        lib = {0};
	struct json_object   *obj = NULL;
	char                 *out = NULL;
	int                   fd;
	int                   ret = EXIT_FAILURE;

	if (lib_init_afl(&lib))
		return ret;

	lib.uint8 = 5;
	stroll_lvstr_lend(&lib.string, "testPattern_1");

	if (lib_chk_afl(&lib)) {
		printf("Bad format for lib_afl\n");
		return 1;
	}

	fd = open(file, O_WRONLY | O_CREAT |  O_CLOEXEC, 0640);
	if (fd < 0) {
		printf("Cannot open file %s\n", file);
		return 1;
	}

	out = malloc(LIB_AFL_PACKED_SIZE_MAX);
	if (!out) {
		printf("Cannot alloc %zu io\n", LIB_AFL_PACKED_SIZE_MAX);
		out = NULL;
		goto error;
	}

	dpack_encoder_init_buffer(&enc_buf, out, LIB_AFL_PACKED_SIZE_MAX);
	if (lib_enc_afl(enc, &lib)) {
		printf("Fail to encode lib_afl\n");
		goto error;
	}

	dpack_encoder_fini(&enc, DPACK_DONE);
/*
	if (write(fd, out, dpack_encoder_space_used(&enc)) < 0) {
		printf("Fail to write %s file\n", file);
		goto error;
	}
*/
	dpack_decoder_init_buffer(&dec_buf, out, dpack_encoder_space_used(enc));

	obj = lib_dec_afl_to_json(dec);
	if (!obj) {
		printf("Fail to decode to json\n");
		goto error;
	}

	if (json_object_to_fd(fd, obj, JSON_C_TO_STRING_PLAIN) < 0) {
		printf("Fail to write %s file\n", file);
		goto error;
	}

	ret = 0;
error:
	if (obj)
		json_object_put(obj);
	dpack_encoder_fini(enc, DPACK_DONE);
	dpack_decoder_fini(dec);
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
	uint8_t               *out;
	int                    ret = EXIT_FAILURE;
	bool                   abort = DPACK_ABORT;

	signal(SIGABRT, handler);

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
		size_t len __unused = __AFL_FUZZ_TESTCASE_LEN;
#pragma GCC diagnostic pop

/*
		if (len < LIB_AFL_PACKED_SIZE_MIN)
			goto end;

		if (len > LIB_AFL_PACKED_SIZE_MAX)
			goto end;

		assert(!lib_init_afl(&lib));
		dpack_decoder_init_buffer(&dec, buf, len);
		dpack_encoder_init_buffer(&enc, out, LIB_AFL_PACKED_SIZE_MAX);
		ret = lib_decode_afl(&dec, &lib);
		if (!ret) {
			assert(!lib_encode_afl(&enc, &lib));
			abort = DPACK_DONE;
		}
		dpack_encoder_fini(&enc, abort);
		dpack_decoder_fini(&dec);
		lib_fini_afl(&lib);
*/
		struct json_object *obj = json_tokener_parse((const char *)buf);
		if (!obj)
			goto end;

		dpack_encoder_init_buffer(&enc, out, LIB_AFL_PACKED_SIZE_MAX);
		ret = lib_enc_afl_from_json(&enc, obj);
		if (!ret) {
			dpack_decoder_init_buffer(&dec, out,
					dpack_encoder_space_used(&enc));
			assert(!lib_init_afl(&lib));
			assert(!lib_dec_afl(&dec, &lib));
			dpack_encoder_fini(&enc, DPACK_DONE);
			dpack_encoder_init_buffer(&enc, out, LIB_AFL_PACKED_SIZE_MAX);
			assert(!lib_enc_afl(&enc, &lib));
			abort = DPACK_DONE;
			dpack_decoder_fini(&dec);
			lib_fini_afl(&lib);
		}
		dpack_encoder_fini(&enc, abort);
		json_object_put(obj);
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
