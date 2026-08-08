cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(edge_io_ring_zephyr)

set(RING_FW_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/..)

target_include_directories(app PRIVATE
  ${RING_FW_ROOT}
  ${RING_FW_ROOT}/app
  ${RING_FW_ROOT}/drivers
  ${RING_FW_ROOT}/include
  ${RING_FW_ROOT}/boards/arm/edge_io_ring
)

target_sources(app PRIVATE
  src/main.c
  ${RING_FW_ROOT}/app/ring_app.c
  ${RING_FW_ROOT}/drivers/bus/ring_bus_fake.c
  ${RING_FW_ROOT}/drivers/bmi270/bmi270.c
  ${RING_FW_ROOT}/drivers/iqs7222a/iqs7222a.c
  ${RING_FW_ROOT}/drivers/se050/se050.c
  ${RING_FW_ROOT}/drivers/npm1300/npm1300.c
  ${RING_FW_ROOT}/drivers/dw3000/dw3000.c
  ${RING_FW_ROOT}/drivers/bmm350/bmm350.c
)

target_compile_definitions(app PRIVATE RING_DEVELOPMENT=1)
