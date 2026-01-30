// SPDX-License-Identifier: LGPL-3.0-only
#include <test-clnt/lib.h>
#include <galv/rpc_clnt.h>
#include <utils/unsk.h>

int main(int argc __unused, char * const argv[] __unused)
{
	int ret;
	struct galv_rpc_clnt clnt;
	const struct sockaddr_un peer = UNSK_NAMED_ADDR("sock");
	struct rpc_tuple tuple = {
		.a = 12,
		.b = 8,
	};

	ret = galv_rpc_clnt_open(&clnt, O_CLOEXEC);
	if (ret)
		return ret;

	ret = galv_rpc_clnt_connect(&clnt, &peer, UNSK_NAMED_ADDR_LEN("sock"));
	if (ret)
		goto close;

	ret = rpc_req_add(&clnt, &tuple, NULL);
close:
	galv_rpc_clnt_close(&clnt);
	return ret;
}

int
rpc_clt_add(void *ctx __unused, uint32_t status, int32_t req)
{
	if (status) {
		errno = status;
		perror("Receive error");
	} else
		printf("req ans is %d\n", req);
	return 0;
}
