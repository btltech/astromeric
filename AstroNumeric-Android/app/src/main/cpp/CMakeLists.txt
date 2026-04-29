cmake_minimum_required(VERSION 3.22.1)

project(swissephbridge)

set(CMAKE_C_STANDARD 99)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SWISSEPH_DIR ${CMAKE_CURRENT_SOURCE_DIR}/swisseph)

add_library(
    swissephbridge
    SHARED
    swiss_ephemeris_jni.cpp
    ${SWISSEPH_DIR}/swecl.c
    ${SWISSEPH_DIR}/swedate.c
    ${SWISSEPH_DIR}/sweephe4.c
    ${SWISSEPH_DIR}/swehel.c
    ${SWISSEPH_DIR}/swehouse.c
    ${SWISSEPH_DIR}/swejpl.c
    ${SWISSEPH_DIR}/swemmoon.c
    ${SWISSEPH_DIR}/swemplan.c
    ${SWISSEPH_DIR}/sweph.c
    ${SWISSEPH_DIR}/swephlib.c
)

target_include_directories(
    swissephbridge
    PRIVATE
    ${SWISSEPH_DIR}
)

find_library(log-lib log)

target_link_libraries(
    swissephbridge
    ${log-lib}
)