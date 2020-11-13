cmake_minimum_required(VERSION 3.16)
project(DockerWorkload)

set(CMAKE_CXX_STANDARD 17)

find_package(Threads)

add_executable(
        DockerWorkload
        argparse.hpp
        main.cpp
        workload.hpp
        workload.cpp)

target_link_libraries (${PROJECT_NAME} ${CMAKE_THREAD_LIBS_INIT})
