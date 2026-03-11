// SPDX-License-Identifier: LGPL-3.0-only
#include <test-clnt/lib.h>
#include <hed/rpc_clnt.h>
#include <utils/unsk.h>

#define SYNC

int main(int argc __unused, char * const argv[] __unused)
{
	int ret;
	struct galv_rpc_clnt clnt;
	const struct sockaddr_un peer = UNSK_NAMED_ADDR("sock");
	struct rpc_tuple tuple = {
		.a = 12,
		.b = 8,
	};

	ret = hed_rpc_clnt_open(&clnt, O_CLOEXEC);
	if (ret)
		return ret;

	ret = hed_rpc_clnt_connect(&clnt, &peer, UNSK_NAMED_ADDR_LEN("sock"));
	if (ret)
		goto close;
#ifdef SYNC
	int32_t ans;
	ret = rpc_rsync_add(&clnt, &tuple, &ans);
	if (ret < 0) {
		errno = -ret;
		perror("Receive error");
	} else if (ret > 0) {
		printf("req status is %d\n", ret);
	} else
		printf("req ans is %d\n", ans);
#else
	ret = rpc_req_add(&clnt, &tuple, NULL);
#endif
close:
	hed_rpc_clnt_close(&clnt);
	return ret;
}

#ifndef SYNC
int
rpc_clt_add(void *ctx __unused, int status, int32_t req)
{
	if (status) {
		errno = status;
		perror("Receive error");
	} else
		printf("req ans is %d\n", req);
	return 0;
}
#endif
