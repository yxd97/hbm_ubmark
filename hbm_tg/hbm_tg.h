#ifndef HBM_TG_H
#define HBM_TG_H

const unsigned MEM_PORT_WIDTH = 512;
const unsigned MEM_PACK_SIZE = MEM_PORT_WIDTH / 32;
struct mem_word_t {
    int data[MEM_PACK_SIZE];
};

const unsigned BUFFER_SIZE = 4096 * 64 / MEM_PORT_WIDTH; // exactly one URAM block

enum {
    HK_PATTERN_SEQ_RD = 0,
    HK_PATTERN_SEQ_RD_BURST = 1,
    HK_PATTERN_SEQ_WR = 2,
    HK_PATTERN_SEQ_WR_BURST = 3,
    HK_PATTERN_RANDOM_RD = 4,
    HK_PATTERN_RANDOM_WR = 5,
    HK_PATTERN_RANDOM_RDWR = 6
};

extern "C" {
void hbm_tg(
    mem_word_t* maxi,
    unsigned size,
    int pattern,
    unsigned range
);
}

#endif
