// SPDX-License-Identifier: LGPL-3.0-only
#define CONFIG_TEST_LIB_ASSERT
#include <dpack/codec.h>
#include "test-lib.h"

__AFL_FUZZ_INIT();

int main(int argc, char * const argv[])
{
	struct dpack_decoder   dec;
	struct dpack_encoder   enc;
	struct afl_sample      spl;
	char                  *out;
	int                    ret = EXIT_FAILURE;

	if (argc == 2)
		return pack_to_file(argv[1]);

	out = malloc(AFL_SAMPLE_PACKED_SIZE_MAX);
	if (!out)
		return EXIT_FAILURE;

#ifdef __AFL_HAVE_MANUAL_CONTROL
	__AFL_INIT();
#endif
	unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

	while (__AFL_LOOP(10000)) {
		size_t len = __AFL_FUZZ_TESTCASE_LEN;

		if (len < AFL_SAMPLE_PACKED_SIZE_MIN)
			continue;

		if (len > AFL_SAMPLE_PACKED_SIZE_MAX)
			continue;

		assert(!afl_sample_init(&spl));
		dpack_decoder_init_buffer(&dec, (const char *)buf, len);
		dpack_encoder_init_buffer(&enc, out, AFL_SAMPLE_PACKED_SIZE_MAX);
		ret = afl_sample_unpack(&dec, &spl);
		if (!ret)
			assert(!afl_sample_pack(&enc, &spl));
		dpack_encoder_fini(&enc);
		dpack_decoder_fini(&dec);
		afl_sample_fini(&spl);
	}
	free(out);
	return ret;
}
