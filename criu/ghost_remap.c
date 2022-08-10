#include "common/err.h"
#include "common/list.h"
#include "cr_options.h"
#include "xmalloc.h"
#include "mount.h"
#include "ghost_remap.h"
#include "util.h"

#include "net.h"

// key: inode:/path
int add_ghost_remap(char *key)
{
	struct ghost_remap *ghost;
	uint64_t ino = 0;
	char *token = strdup(key);
	char *inode = strtok(token, ":");
	if (!inode)
		return -1;
	ino = strtoul(inode, NULL, 10);
	if (!ino)
		return -1;

	ghost = xmalloc(sizeof(*ghost));
	if (!ghost)
		return -1;
	ghost->ino = ino;
	ghost->remap_path = strtok(NULL, ":");
	if (!ghost->remap_path) {
		free(ghost);
		free(token);
		return -1;
	}
	list_add(&ghost->node, &opts.ghost_remap);
	return 0;
}

char *ghost_remap_lookup_id(uint64_t ino)
{
	struct ghost_remap *ghost;

	list_for_each_entry(ghost, &opts.ghost_remap, node)
		if (ghost->ino == ino)
			return ghost->remap_path;
	return NULL;
}
