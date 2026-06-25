cmake_minimum_required(VERSION 3.15)
project(test_slang CXX)

find_package(slang REQUIRED CONFIG)

add_executable(test_slang test_slang.cpp)
target_link_libraries(test_slang PRIVATE slang::slang)
target_compile_features(test_slang PRIVATE cxx_std_17)
