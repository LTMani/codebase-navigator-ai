#ifndef NAVIGATOR_DEVICE_DRIVER_1_H
#define NAVIGATOR_DEVICE_DRIVER_1_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint32_t device_id;
    uint32_t baud_rate;
    bool is_initialized;
    uint8_t buffer[256];
} DeviceHandle1;

static inline int init_device_1(DeviceHandle1* dev, uint32_t id, uint32_t baud) {
    if (!dev) return -1;
    dev->device_id = id;
    dev->baud_rate = baud;
    dev->is_initialized = true;
    return 0;
}

static inline int write_device_1(DeviceHandle1* dev, const uint8_t* data, size_t len) {
    if (!dev || !dev->is_initialized || len > 256) return -1;
    for (size_t k = 0; k < len; ++k) {
        dev->buffer[k] = data[k];
    }
    return (int)len;
}

#endif // NAVIGATOR_DEVICE_DRIVER_1_H
