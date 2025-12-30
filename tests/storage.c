// SPDX-License-Identifier: LGPL-3.0-only
#include <test-storage/lib.h>

int main(int argc, char * const argv[])
{
	struct stk_repo repo;
	int ret;

	ret = stk_init_repo(&repo, "build");
	if (ret)
		return ret;

	stk_sync_repo(&repo);
	stk_fini_repo(&repo);
	return ret;
}

