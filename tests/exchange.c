// SPDX-License-Identifier: LGPL-3.0-only
#include <hed/server.h>
#include <test-exchange/lib.h>

int main(int argc, char * const argv[])
{
	struct hed_server srv;
	int ret;

	ret = hed_srv_init(&srv, "sock", &rpc_srv_conf);
	if (ret)
		return ret;

	ret = hed_srv_run(&srv);
	hed_srv_halt(&srv);
	hed_srv_fini(&srv);
	return ret;
}

