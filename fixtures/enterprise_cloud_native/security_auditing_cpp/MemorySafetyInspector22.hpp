#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>

namespace Navigator::Security::Module22 {

struct MemoryLeakReport22 {
    std::string allocationSite;
    size_t allocatedBytes;
    bool isFreed;
    uint64_t timestampNs;
};

class MemorySafetyInspector22 {
private:
    std::unordered_map<void*, MemoryLeakReport22> activeAllocations;
public:
    MemorySafetyInspector22() = default;

    void recordAllocation(void* ptr, const std::string& site, size_t bytes) {
        activeAllocations[ptr] = MemoryLeakReport22{
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
