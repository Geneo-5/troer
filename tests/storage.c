// SPDX-License-Identifier: LGPL-3.0-only
#include <json-c/json_util.h>
#include <test-storage/lib.h>

int main(void)
{
	struct stk_repo repo;
	struct json_object *obj;
	int ret;

	ret = stk_open_repo(&repo, "build", O_RDWR | O_CREAT | O_TRUNC, 0600);
	if (ret) {
		printf("open create fail\n");
		goto exit;
	}

	ret = stk_repo_update_test_object(&repo, 5);
	if (ret) {
		printf("update object fail\n");
		goto exit;
	}

	for (int i = 0; i < 10; i++) {
		struct stk_tuple t = {
			.a = i,
			.b = 5,
		};

		ret = stk_repo_update_test_collection(&repo, i, &t);
		if (ret) {
			printf("update collection fail nb %d\n", i);
			goto exit;
		}
	}

	ret = stk_sync_repo(&repo);
	if (ret) {
		printf("sync fail\n");
		goto exit;
	}

	ret = stk_reload_repo(&repo);
	if (ret) {
		printf("reload fail\n");
		goto exit;
	}

	stk_close_repo(&repo);
	ret = stk_open_repo(&repo, "build", O_RDWR, 0600);
	if (ret) {
		printf("open fail\n");
		goto exit;
	}

	obj = stk_repo_to_json(&repo);
	if (!obj) {
		printf("Fail to decode to json\n");
		goto exit;
	}

	ret = json_object_to_fd(1, obj, JSON_C_TO_STRING_PRETTY);
	json_object_put(obj);
	if (ret) {
		printf("Fail to write json\n");
		goto exit;
	}
exit:
	stk_close_repo(&repo);
	return ret;
}

