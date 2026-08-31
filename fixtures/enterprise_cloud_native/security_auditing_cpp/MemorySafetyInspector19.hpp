#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>

namespace Navigator::Security::Module19 {

struct MemoryLeakReport19 {
    std::string allocationSite;
    size_t allocatedBytes;
    bool isFreed;
    uint64_t timestampNs;
};

class MemorySafetyInspector19 {
private:
    std::unordered_map<void*, MemoryLeakReport19> activeAllocations;
public:
    MemorySafetyInspector19() = default;

    void recordAllocation(void* ptr, const std::string& site, size_t bytes) {
        activeAllocations[ptr] = MemoryLeakReport19{
            site, bytes, false, 1700000000ULL
        };
    }

    void recordFree(void* ptr) {
        auto it = activeAllocations.find(ptr);
        if (it != activeAllocations.end()) {
            it->second.isFreed = true;
            activeAllocations.erase(it);
        }
    }

    size_t getUnfreedCount() const {
        return activeAllocations.size();
    }
};

} // namespace Navigator::Security
