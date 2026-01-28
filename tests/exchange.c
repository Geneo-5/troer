// SPDX-License-Identifier: LGPL-3.0-only
#include <hed/server.h>
#include <test-exchange/lib.h>

static const uint8_t test_data[] = {
	'\x01', '\x00', '\x03', '\x00', '\x00', (uint8_t)'\x92', '\x01', '\x02'
};

static int
pack_to_file(char * file)
{
	int fd;
	int ret = 0;

	fd = open(file, O_WRONLY | O_CREAT |  O_CLOEXEC, 0640);
	if (fd < 0) {
		printf("Cannot open file %s\n", file);
		return 1;
	}

	if (write(fd, test_data, sizeof(test_data)) < 0) {
		printf("Fail to write %s file\n", file);
		ret = 1;
	}
	close(fd);
	return ret;
}

int main(int argc, char * const argv[])
{
	struct hed_server srv;
	int ret;

	if (argc == 2)
		return pack_to_file(argv[1]);

	ret = hed_srv_init(&srv, "sock", &rpc_srv_conf, &rpc_srv_factory);
	if (ret)
		return ret;
	//ret = hed_srv_run(&srv);
	hed_srv_process(&srv);
	hed_srv_process(&srv);
	hed_srv_halt(&srv);
	hed_srv_fini(&srv);
	return 0;
}


int
rpc_srv_add(struct galv_rpc_msg *msg, struct rpc_tuple *req)
{
	int32_t ans;

	ans  = rpc_tuple_get_a(req);
	ans += rpc_tuple_get_b(req);

	return rpc_ans_add(msg, 0, ans);
}
