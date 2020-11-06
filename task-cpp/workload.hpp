//
// Created by xenon on 2020/11/6.
//

#pragma once

#include <vector>
#include <thread>
#include <memory>
#include <random>

namespace linc {

    using ull = unsigned long long;

    class Workload {
    private:
        const int cpuCount;
        const double memoryMb;
        const ull iterCount;

    private:
        std::vector<std::unique_ptr<std::thread>> threads;
        std::vector<u_int8_t*> strings;
        std::random_device randomDevice;
        std::default_random_engine randomEngine;

    public:
        explicit Workload(
            int cpuCount,
            double memoryMb,
            ull iterFactor,
            ull iterBase
            ) :
            cpuCount(cpuCount),
            memoryMb(memoryMb),
            iterCount(iterFactor * iterBase),
            randomDevice(),
            randomEngine(randomDevice()) {}

        void execute() noexcept;

    private:
        void startThreads() noexcept;

        void occupyMemory() noexcept;

        void waitUntilAllThreadsDone() noexcept;

        void cleanup() noexcept;

        void initOneMbMemory(u_int8_t mem[]);

    };

}
