#include "hbm_tg.h"
#include <ap_int.h>

void seq_read(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size
) {
    #pragma HLS inline off
    seq_read_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline off
        buffer[i] = maxi[i];
    }
}

void seq_read_burst(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size
) {
    #pragma HLS inline off
    seq_read_burst_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline II=1
        buffer[i] = maxi[i];
    }
}

void seq_write(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size
) {
    #pragma HLS inline off
    seq_write_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline off
        maxi[i] = buffer[i];
    }
}

void seq_write_burst(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size
) {
    #pragma HLS inline off
    seq_write_burst_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline II=1
        maxi[i] = buffer[i];
    }
}

class LfsrRng {
    public:
        LfsrRng(unsigned seed) {
            #pragma HLS inline
            this->state = seed;
        }

        unsigned next() {
            #pragma HLS inline
            unsigned bit = (state >> 0) ^ (state >> 1) ^ (state >> 3) ^ (state >> 4);
            state = (state >> 1) | (bit << 31);
            return state;
        }

        void reset(unsigned seed) {
            #pragma HLS inline
            this->state = seed;
        }

    private:
        unsigned state;
};

void random_read(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size,
    unsigned range
) {
    #pragma HLS inline off
    LfsrRng rng(0xdeafbeef);
    rand_read_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline II=1
        buffer[i] = maxi[rng.next() % range];
    }
}

void random_write(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size,
    unsigned range
) {
    #pragma HLS inline off
    LfsrRng rng(0xdeafbeef);
    rand_write_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline II=1
        maxi[rng.next() % range] = buffer[i];
    }
}

void random_read_write(
    mem_word_t* maxi,
    mem_word_t* buffer,
    unsigned size,
    unsigned range
) {
    #pragma HLS inline off
    LfsrRng rng(0xdeafbeef);
    rand_readwrite_loop: for (unsigned i = 0; i < size; i++) {
        #pragma HLS pipeline II=1
        #pragma HLS dependence variable=maxi inter false
        if (rng.next() % 2) {
            maxi[rng.next() % range] = buffer[i];
        } else {
            buffer[i] = maxi[rng.next() % range];
        }
    }
}

extern "C" {
/*!
 * \brief generate memory traffic
 * \param maxi axi master interface to the hbm subsystem
 * \param size size of the traffic (in number of accesses), max 512 (i.e. 32KB)
 * \param pattern traffic pattern
 * \param range range of the random traffic (max 512)
*/
void hbm_tg(
    mem_word_t* maxi,
    unsigned size,
    int pattern,
    unsigned range
) {
    #pragma HLS INTERFACE m_axi port=maxi offset=slave bundle=gmem depth=BUFFER_SIZE
    #pragma HLS INTERFACE s_axilite port=maxi bundle=control
    #pragma HLS INTERFACE s_axilite port=size bundle=control
    #pragma HLS INTERFACE s_axilite port=pattern bundle=control
    #pragma HLS INTERFACE s_axilite port=range bundle=control
    #pragma HLS INTERFACE s_axilite port=return bundle=control

    mem_word_t buffer[BUFFER_SIZE];
    #pragma HLS bind_storage variable=buffer type=ram_2p impl=uram
    #pragma HLS aggregate variable=buffer

    switch (pattern) {
        case HK_PATTERN_SEQ_RD:
            seq_read(maxi, buffer, size);
            break;
        case HK_PATTERN_SEQ_RD_BURST:
            seq_read_burst(maxi, buffer, size);
            break;
        case HK_PATTERN_SEQ_WR:
            seq_write(maxi, buffer, size);
            break;
        case HK_PATTERN_SEQ_WR_BURST:
            seq_write_burst(maxi, buffer, size);
            break;
        case HK_PATTERN_RANDOM_RD:
            random_read(maxi, buffer, size, range);
            break;
        case HK_PATTERN_RANDOM_WR:
            random_write(maxi, buffer, size, range);
            break;
        case HK_PATTERN_RANDOM_RDWR:
            random_read_write(maxi, buffer, size, range);
            break;
        default:
            break;
    }

}
}
