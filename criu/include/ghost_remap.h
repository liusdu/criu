#ifndef __CR_GHOST_REMAP_H__
#define __CR_GHOST_REMAP_H__
struct ghost_remap {
	struct list_head node;
	uint64_t ino;
	char *remap_path;
};

extern int add_ghost_remap(char *key);
extern char *ghost_remap_lookup_id(uint64_t ino);
#endif
