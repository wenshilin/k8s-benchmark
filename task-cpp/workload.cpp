//
// Created by xenon on 2020/11/6.
//

#include "workload.hpp"

#include <iostream>
#include <cmath>
#include <ctime>

using namespace linc;

namespace {
    const ull MB = 1024 * 1024;

    void computePi(ull iterCount) {
        double num = 0;

        for (ull i = 1; i <= iterCount; ++i) {
            num += 1. / static_cast<double>(i * i);
        }

        double pi = std::sqrt(num * 6);
        std::cout << "计算PI值为：" << pi << std::endl;
    }

}

void Workload::execute() noexcept {
    std::cout << "开始执行负载" << std::endl;
    auto startTimeSec = std::time(nullptr);
    startThreads();
    occupyMemory();
    waitUntilAllThreadsDone();
    auto endTimeSec = std::time(nullptr);
    std::cout << "CPU占用总时间" << (endTimeSec - startTimeSec) << "秒" << std::endl;
    cleanup();
    std::cout << "负载运行完成" << std::endl;
}

void Workload::startThreads() noexcept {
    for (int i = 0; i < cpuCount; ++i) {
        auto thread = std::make_unique<std::thread>(::computePi, iterCount);
        threads.push_back(std::move(thread));
    }
}

void Workload::occupyMemory() noexcept {
    if (memoryMb <= 0) {
        std::cout  << "无需额外占用内存" << std::endl;
        return;
    }

    int realMemoryMb = std::ceil(memoryMb);
    strings.resize(realMemoryMb);
    for (int i = 0; i < memoryMb; ++i) {
        auto str = new u_int8_t[MB];
        initOneMbMemory(str);
        strings.push_back(str);
    }
    std::cout << "内存占用完毕，实际占用内存" << realMemoryMb << "MB" << std::endl;
}

void Workload::waitUntilAllThreadsDone() noexcept {
    for (const auto& thread : threads) {
        thread->join();
    }
}

void Workload::cleanup() noexcept {
    for (u_int8_t* str : strings) {
        delete[] str;
    }
    std::cout << "占用内存已释放" << std::endl;
}

/*
 * 使用随机数初始化1MB的内存空间
 * 阻止操作系统的缓存机制
 */
void Workload::initOneMbMemory(u_int8_t mem[]) {
    int seed = randomEngine();
    for (ull i = 0; i < MB; ++i) {
        mem[i] = (i + seed) % 256;
    }
}
