#include "hbm_tg.h"
#include <vector>
#include <cassert>
#include <iostream>

int main(int argc, char** argv) {
    unsigned size = 128;
    assert(size < BUFFER_SIZE);
    std::vector<mem_word_t> mem_on_hbm(size);

    std::cout << "Running sequential read test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_SEQ_RD, 0);
    std::cout << "Done." << std::endl;

    std::cout << "Running sequential read burst test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_SEQ_RD_BURST, 0);
    std::cout << "Done." << std::endl;

    std::cout << "Running sequential write test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_SEQ_WR, 0);
    std::cout << "Done." << std::endl;

    std::cout << "Running sequential write burst test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_SEQ_WR_BURST, 0);
    std::cout << "Done." << std::endl;

    std::cout << "Running random read test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_RANDOM_RD, size);
    std::cout << "Done." << std::endl;

    std::cout << "Running random write test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_RANDOM_WR, size);
    std::cout << "Done." << std::endl;

    std::cout << "Running random read/write test... ";
    hbm_tg(mem_on_hbm.data(), size, HK_PATTERN_RANDOM_RDWR, size);
    std::cout << "Done." << std::endl;

    return 0;
}
