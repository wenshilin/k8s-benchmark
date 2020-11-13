#include <iostream>

#include "argparse.hpp"
#include "workload.hpp"

argparse::ArgumentParser createParser(int argc, char* argv[]) {
    argparse::ArgumentParser parser("Workload");

    const auto stringToDouble = [](const std::string& value) { return std::stod(value); };
    const auto stringToUnsignedLongLong = [](const std::string& value) { return std::stoull(value); };
    const auto stringToInt = [](const std::string& value) { return std::stoi(value); };

    parser.add_description("程序最终迭代次数 = 工作量因子 * 底数，程序工作量底数的期望值使得1工作量因子的执行时间接近1ms");

    parser.add_argument("--cpu-count")
            .help("指定启动线程数")
            .action(stringToInt);
    parser.add_argument("--memory-mb")
            .help("内存占用（MB）")
            .action(stringToDouble);
    parser.add_argument("--iter-factor")
            .help("每个线程的程序工作量因子（迭代次数）")
            .action(stringToUnsignedLongLong);
    parser.add_argument("--iter-base")
            .help("每个线程的程序工作量底数，默认值125000")
            .action(stringToUnsignedLongLong)
            .default_value(static_cast<unsigned long long>(125000));

    try {
        parser.parse_args(argc, argv);
    } catch (const std::runtime_error& err) {
        std::cout << err.what() << std::endl;
        std::cout << parser;
        exit(0);
    }

    return parser;
}

int main(int argc, char* argv[]) {
    const auto parser = createParser(argc, argv);

    const auto cpuCount = parser.get<int>("--cpu-count");
    const auto memoryMb = parser.get<double>("--memory-mb");
    const auto iterFactor = parser.get<unsigned long long>("--iter-factor");
    const auto iterBase = parser.get<unsigned long long>("--iter-base");

    std::printf("启动线程数：%d\n", cpuCount);
    std::printf("预计内存占用：%.2lfMB\n", memoryMb);
    std::printf("计算迭代次数：%lld * %lld = %lld\n", iterFactor, iterBase, iterFactor * iterBase);
    std::printf("预计执行时间：%.2llus\n", iterFactor / 1000);

    linc::Workload workload{cpuCount, memoryMb, iterFactor, iterBase};
    workload.execute();

    return 0;
}
