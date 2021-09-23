/*
 * Copyright (c) 2021-2022 LunarG, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Authors:
 * - Christophe Riccio <christophe@lunarg.com>
 */

#include <vulkan/vulkan_core.h>

#define VP_MAX_PROFILE_NAME_SIZE 256U

#define VP_KHR_minimum_requirements 1
#define VP_KHR_MINIMUM_REQUIREMENTS_SPEC_VERSION 1
#define VP_KHR_MINIMUM_REQUIREMENTS_NAME "VP_KHR_minimum_requirements"

#define VP_KHR_1_2_roadmap_2022 1
#define VP_KHR_1_2_ROADMAP_2022_SPEC_VERSION 1
#define VP_KHR_1_2_ROADMAP_2022_NAME "VP_KHR_1_2_roadmap_2022"

static const VkExtensionProperties VP_KHR_1_2_ROADMAP_2022_EXTENSIONS[] = {
    VkExtensionProperties{"VK_EXT_extended_dynamic_state2", 1},
    VkExtensionProperties{"VK_EXT_texel_buffer_alignment", 1},
    VkExtensionProperties{"VK_EXT_subgroup_size_control", 2},
    VkExtensionProperties{"VK_EXT_shader_demote_to_helper_invocation", 1},
    VkExtensionProperties{"VK_EXT_private_data", 1},
    VkExtensionProperties{"VK_EXT_pipeline_creation_cache_control", 1},
    VkExtensionProperties{"VK_EXT_inline_uniform_block", 1},
    VkExtensionProperties{"VK_EXT_image_robustness", 1},
    VkExtensionProperties{"VK_KHR_zero_initialize_workgroup_memory", 1},
    VkExtensionProperties{"VK_KHR_synchronization2", 1},
    VkExtensionProperties{"VK_KHR_shader_terminate_invocation", 1},
    VkExtensionProperties{"VK_KHR_imageless_framebuffer", 1}};

#define VP_LUNARG_1_1_desktop_portability_2022 1
#define VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_SPEC_VERSION 1
#define VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_NAME "VP_LUNARG_1_1_desktop_portability_2022"

static const VkExtensionProperties VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS[] = {
    VkExtensionProperties{"VK_KHR_bind_memory2", 1},
    VkExtensionProperties{"VK_KHR_create_renderpass2", 1},
    VkExtensionProperties{"VK_KHR_dedicated_allocation", 1},
    VkExtensionProperties{"VK_KHR_depth_stencil_resolve", 1},
    VkExtensionProperties{"VK_KHR_descriptor_update_template", 1},
    VkExtensionProperties{"VK_KHR_device_group", 4},
    VkExtensionProperties{"VK_KHR_driver_properties", 1},
    VkExtensionProperties{"VK_KHR_external_fence", 1},
    VkExtensionProperties{"VK_KHR_external_memory", 1},
    VkExtensionProperties{"VK_KHR_external_semaphore", 1},
    VkExtensionProperties{"VK_KHR_get_memory_requirements2", 1},
    VkExtensionProperties{"VK_KHR_image_format_list", 1},
    VkExtensionProperties{"VK_KHR_imageless_framebuffer", 1},
    VkExtensionProperties{"VK_KHR_maintenance1", 1},
    VkExtensionProperties{"VK_KHR_maintenance2", 1},
    VkExtensionProperties{"VK_KHR_maintenance3", 1},
    VkExtensionProperties{"VK_KHR_multiview", 1},
    VkExtensionProperties{"VK_KHR_portability_subset", 1},
    VkExtensionProperties{"VK_KHR_relaxed_block_layout", 1},
    VkExtensionProperties{"VK_KHR_separate_depth_stencil_layouts", 1},
    VkExtensionProperties{"VK_KHR_shader_float_controls", 4},
    VkExtensionProperties{"VK_KHR_shader_subgroup_extended_types", 1},
    VkExtensionProperties{"VK_KHR_spirv_1_4", 1},
    VkExtensionProperties{"VK_KHR_storage_buffer_storage_class", 1},
    VkExtensionProperties{"VK_KHR_swapchain", 70},
    VkExtensionProperties{"VK_KHR_timeline_semaphore", 2},
    VkExtensionProperties{"VK_KHR_uniform_buffer_standard_layout", 1},
    VkExtensionProperties{"VK_EXT_host_query_reset", 1},
    VkExtensionProperties{"VK_EXT_sampler_filter_minmax", 1},
    VkExtensionProperties{"VK_EXT_separate_stencil_usage", 1},
    VkExtensionProperties{"VK_EXT_shader_viewport_index_layer", 1}};

#define countof(arr) sizeof(arr) / sizeof(arr[0])

typedef struct VpProfileProperties {
    char profileName[VP_MAX_PROFILE_NAME_SIZE];
    uint32_t specVersion;
} VpProfileProperties;

VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpProfileProperties *pProfile, const VkDeviceCreateInfo *pCreateInfo,
                        const VkAllocationCallbacks *pAllocator, VkDevice *pDevice);

VkResult vpEnumerateDeviceProfiles(VkPhysicalDevice physicalDevice, const char *pLayerName, uint32_t *pPropertyCount,
                                   VpProfileProperties *pProperties);

// Implementation details:
#include <cstring>
#include <vector>

inline bool vpCheckExtension(const VkExtensionProperties *supportedProperties, std::size_t supportedSize,
                             const char *requestedExtension) {
    for (size_t i = 0, n = supportedSize; i < n; ++i) {
        if (strcmp(supportedProperties[i].extensionName, requestedExtension) == 0) return true;
    }

    return false;
}

inline void *vpGetStructure(void* pNext, VkStructureType type) {
    if (pNext == nullptr) {
        return nullptr;
    }

    struct VkStruct {
        VkStructureType sType;
        void *pNext;
    };

    VkStruct *p = static_cast<VkStruct *>(pNext);

    if (p->sType == type) {
        return pNext;
    } else {
        return vpGetStructure(p->pNext, type);
    }
}

inline VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpProfileProperties *pProfile,
                               const VkDeviceCreateInfo *pCreateInfo, const VkAllocationCallbacks *pAllocator, VkDevice *pDevice) {

    if (pProfile == nullptr) {
        return vkCreateDevice(physicalDevice, pCreateInfo, pAllocator, pDevice);
    } else if (strcmp(pProfile->profileName, VP_KHR_MINIMUM_REQUIREMENTS_NAME) == 0) {
        return vkCreateDevice(physicalDevice, pCreateInfo, pAllocator, pDevice);
    } else if (strcmp(pProfile->profileName, VP_KHR_1_2_ROADMAP_2022_NAME) == 0) {
        std::vector<const char *> extensions;
        for (int i = 0, n = countof(VP_KHR_1_2_ROADMAP_2022_EXTENSIONS); i < n; ++i) {
            extensions.push_back(VP_KHR_1_2_ROADMAP_2022_EXTENSIONS[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->enabledExtensionCount; ++i) {
            if (vpCheckExtension(VP_KHR_1_2_ROADMAP_2022_EXTENSIONS, countof(VP_KHR_1_2_ROADMAP_2022_EXTENSIONS),
                                 pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->ppEnabledExtensionNames[i]);
        }

        VkPhysicalDeviceFeatures enabledFeatures = {};

        if (pCreateInfo->pEnabledFeatures != nullptr) {
            enabledFeatures = *pCreateInfo->pEnabledFeatures;
        }

        enabledFeatures.robustBufferAccess = VK_TRUE;
        enabledFeatures.imageCubeArray = VK_TRUE;
        enabledFeatures.independentBlend = VK_TRUE;
        enabledFeatures.sampleRateShading = VK_TRUE;
        enabledFeatures.drawIndirectFirstInstance = VK_TRUE;
        enabledFeatures.depthBiasClamp = VK_TRUE;
        enabledFeatures.samplerAnisotropy = VK_TRUE;
        enabledFeatures.occlusionQueryPrecise = VK_TRUE;
        enabledFeatures.fragmentStoresAndAtomics = VK_TRUE;
        enabledFeatures.shaderStorageImageExtendedFormats = VK_TRUE;
        enabledFeatures.shaderStorageImageReadWithoutFormat = VK_TRUE;
        enabledFeatures.shaderUniformBufferArrayDynamicIndexing = VK_TRUE;
        enabledFeatures.shaderSampledImageArrayDynamicIndexing = VK_TRUE;
        enabledFeatures.shaderStorageBufferArrayDynamicIndexing = VK_TRUE;
        enabledFeatures.shaderStorageImageArrayDynamicIndexing = VK_TRUE;

        void *pRoot = const_cast<void *>(pCreateInfo->pNext);
        void *pNext = pRoot;

        VkPhysicalDeviceVulkan11Features Next_1 = {};
        Next_1.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES;
        Next_1.pNext = pNext;
        Next_1.multiview = VK_TRUE;
        Next_1.samplerYcbcrConversion = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES) == nullptr) {
            pNext = &Next_1;
        }

        VkPhysicalDeviceVulkan12Features Next_2 = {};
        Next_2.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES;
        Next_2.pNext = pNext;
        Next_2.samplerMirrorClampToEdge = VK_TRUE;
        Next_2.shaderUniformTexelBufferArrayDynamicIndexing = VK_TRUE;
        Next_2.uniformBufferStandardLayout = VK_TRUE;
        Next_2.shaderSubgroupExtendedTypes = VK_TRUE;
        Next_2.separateDepthStencilLayouts = VK_TRUE;
        Next_2.hostQueryReset = VK_TRUE;
        Next_2.bufferDeviceAddress = VK_TRUE;
        Next_2.vulkanMemoryModel = VK_TRUE;
        Next_2.vulkanMemoryModelDeviceScope = VK_TRUE;
        Next_2.vulkanMemoryModelAvailabilityVisibilityChains = VK_TRUE;
        Next_2.subgroupBroadcastDynamicId = VK_TRUE;
        Next_2.imagelessFramebuffer = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES) == nullptr) {
            pNext = &Next_2;
        }

        VkPhysicalDeviceShaderTerminateInvocationFeaturesKHR Next_3 = {};
        Next_3.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_TERMINATE_INVOCATION_FEATURES_KHR;
        Next_3.pNext = pNext;
        Next_3.shaderTerminateInvocation = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_TERMINATE_INVOCATION_FEATURES_KHR) == nullptr) {
            pNext = &Next_3;
        }

        VkPhysicalDeviceSynchronization2FeaturesKHR Next_4 = {};
        Next_4.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES_KHR;
        Next_4.pNext = pNext;
        Next_4.synchronization2 = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES_KHR) == nullptr) {
            pNext = &Next_4;
        }

        VkPhysicalDeviceZeroInitializeWorkgroupMemoryFeaturesKHR Next_5 = {};
        Next_5.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ZERO_INITIALIZE_WORKGROUP_MEMORY_FEATURES_KHR;
        Next_5.pNext = pNext;
        Next_5.shaderZeroInitializeWorkgroupMemory = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ZERO_INITIALIZE_WORKGROUP_MEMORY_FEATURES_KHR) == nullptr) {
            pNext = &Next_5;
        }

        VkPhysicalDeviceImageRobustnessFeaturesEXT Next_6 = {};
        Next_6.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_IMAGE_ROBUSTNESS_FEATURES_EXT;
        Next_6.pNext = pNext;
        Next_6.robustImageAccess = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_IMAGE_ROBUSTNESS_FEATURES_EXT) == nullptr) {
            pNext = &Next_6;
        }

        VkPhysicalDeviceInlineUniformBlockFeaturesEXT Next_7 = {};
        Next_7.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
        Next_7.pNext = pNext;
        Next_7.inlineUniformBlock = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT) == nullptr) {
            pNext = &Next_7;
        }

        VkPhysicalDevicePipelineCreationCacheControlFeaturesEXT Next_8 = {};
        Next_8.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PIPELINE_CREATION_CACHE_CONTROL_FEATURES_EXT;
        Next_8.pNext = pNext;
        Next_8.pipelineCreationCacheControl = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PIPELINE_CREATION_CACHE_CONTROL_FEATURES_EXT) == nullptr) {
            pNext = &Next_8;
        }

        VkPhysicalDevicePrivateDataFeaturesEXT Next_9 = {};
        Next_9.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PRIVATE_DATA_FEATURES_EXT;
        Next_9.pNext = pNext;
        Next_9.privateData = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PRIVATE_DATA_FEATURES_EXT) == nullptr) {
            pNext = &Next_8;
        }

        VkPhysicalDeviceShaderDemoteToHelperInvocationFeaturesEXT Next_10 = {};
        Next_10.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_DEMOTE_TO_HELPER_INVOCATION_FEATURES_EXT;
        Next_10.pNext = pNext;
        Next_10.shaderDemoteToHelperInvocation = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_DEMOTE_TO_HELPER_INVOCATION_FEATURES_EXT) == nullptr) {
            pNext = &Next_10;
        }

        VkPhysicalDeviceSubgroupSizeControlFeaturesEXT Next_11 = {};
        Next_11.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_SIZE_CONTROL_FEATURES_EXT;
        Next_11.pNext = pNext;
        Next_11.subgroupSizeControl = VK_TRUE;
        Next_11.computeFullSubgroups = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_SIZE_CONTROL_FEATURES_EXT) == nullptr) {
            pNext = &Next_11;
        }

        VkPhysicalDeviceTexelBufferAlignmentFeaturesEXT Next_12 = {};
        Next_12.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TEXEL_BUFFER_ALIGNMENT_FEATURES_EXT;
        Next_12.pNext = pNext;
        Next_12.texelBufferAlignment = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_TEXEL_BUFFER_ALIGNMENT_FEATURES_EXT) == nullptr) {
            pNext = &Next_12;
        }

        VkPhysicalDeviceExtendedDynamicState2FeaturesEXT Next_13 = {};
        Next_13.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_EXTENDED_DYNAMIC_STATE_2_FEATURES_EXT;
        Next_13.pNext = pNext;
        Next_13.extendedDynamicState2 = VK_TRUE;
        if (vpGetStructure(pRoot, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_EXTENDED_DYNAMIC_STATE_2_FEATURES_EXT) == nullptr) {
            pNext = &Next_12;
        }

        VkDeviceCreateInfo deviceCreateInfo = {};
        deviceCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
        deviceCreateInfo.pNext = pNext;
        deviceCreateInfo.queueCreateInfoCount = pCreateInfo->queueCreateInfoCount;
        deviceCreateInfo.pQueueCreateInfos = pCreateInfo->pQueueCreateInfos;
        deviceCreateInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
        deviceCreateInfo.ppEnabledExtensionNames = static_cast<const char *const *>(extensions.data());
        deviceCreateInfo.pEnabledFeatures = &enabledFeatures;
        return vkCreateDevice(physicalDevice, &deviceCreateInfo, pAllocator, pDevice);
    } else if (strcmp(pProfile->profileName, VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_NAME) == 0) {
        std::vector<const char *> extensions;
        for (int i = 0, n = countof(VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS); i < n; ++i) {
            extensions.push_back(VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->enabledExtensionCount; ++i) {
            if (vpCheckExtension(VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS,
                                 countof(VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS),
                                 pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->ppEnabledExtensionNames[i]);
        }

        VkPhysicalDeviceFeatures enabledFeatures = {};
        if (pCreateInfo->pEnabledFeatures != nullptr) {
            enabledFeatures = *pCreateInfo->pEnabledFeatures;
        }

        enabledFeatures.robustBufferAccess = VK_TRUE;
        enabledFeatures.fullDrawIndexUint32 = VK_TRUE;
        enabledFeatures.imageCubeArray = VK_TRUE;
        enabledFeatures.independentBlend = VK_TRUE;
        enabledFeatures.tessellationShader = VK_TRUE;
        enabledFeatures.sampleRateShading = VK_TRUE;
        enabledFeatures.dualSrcBlend = VK_TRUE;
        enabledFeatures.multiDrawIndirect = VK_TRUE;
        enabledFeatures.drawIndirectFirstInstance = VK_TRUE;
        enabledFeatures.depthClamp = VK_TRUE;
        enabledFeatures.depthBiasClamp = VK_TRUE;
        enabledFeatures.fillModeNonSolid = VK_TRUE;
        enabledFeatures.largePoints = VK_TRUE;
        enabledFeatures.multiViewport = VK_TRUE;
        enabledFeatures.textureCompressionBC = VK_TRUE;
        enabledFeatures.occlusionQueryPrecise = VK_TRUE;
        enabledFeatures.vertexPipelineStoresAndAtomics = VK_TRUE;
        enabledFeatures.fragmentStoresAndAtomics = VK_TRUE;
        enabledFeatures.shaderTessellationAndGeometryPointSize = VK_TRUE;
        enabledFeatures.shaderImageGatherExtended = VK_TRUE;
        enabledFeatures.shaderStorageImageWriteWithoutFormat = VK_TRUE;
        enabledFeatures.shaderClipDistance = VK_TRUE;

        VkPhysicalDeviceImagelessFramebufferFeaturesKHR pNext_0 = {};
        pNext_0.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_IMAGELESS_FRAMEBUFFER_FEATURES;
        pNext_0.pNext = const_cast<void *>(pCreateInfo->pNext);
        pNext_0.imagelessFramebuffer = VK_TRUE;

        VkPhysicalDevice16BitStorageFeatures pNext_1 = {};
        pNext_1.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_16BIT_STORAGE_FEATURES;
        pNext_1.pNext = &pNext_0;
        pNext_1.storageBuffer16BitAccess = VK_TRUE;
        pNext_1.uniformAndStorageBuffer16BitAccess = VK_TRUE;

        VkPhysicalDeviceMultiviewFeatures pNext_2 = {};
        pNext_2.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_MULTIVIEW_FEATURES;
        pNext_2.pNext = &pNext_1;
        pNext_2.multiview = VK_TRUE;

        VkPhysicalDevice8BitStorageFeatures pNext_3 = {};
        pNext_3.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_8BIT_STORAGE_FEATURES;
        pNext_3.pNext = &pNext_2;
        pNext_3.storageBuffer8BitAccess = VK_TRUE;
        pNext_3.uniformAndStorageBuffer8BitAccess = VK_TRUE;

        VkPhysicalDeviceDescriptorIndexingFeatures pNext_4 = {};
        pNext_4.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_INDEXING_FEATURES;
        pNext_4.pNext = &pNext_3;
        pNext_4.shaderUniformTexelBufferArrayDynamicIndexing = VK_TRUE;
        pNext_4.shaderStorageTexelBufferArrayDynamicIndexing = VK_TRUE;
        pNext_4.shaderSampledImageArrayNonUniformIndexing = VK_TRUE;
        pNext_4.shaderStorageBufferArrayNonUniformIndexing = VK_TRUE;
        pNext_4.shaderUniformTexelBufferArrayNonUniformIndexing = VK_TRUE;
        pNext_4.descriptorBindingSampledImageUpdateAfterBind = VK_TRUE;
        pNext_4.descriptorBindingStorageImageUpdateAfterBind = VK_TRUE;
        pNext_4.descriptorBindingStorageBufferUpdateAfterBind = VK_TRUE;
        pNext_4.descriptorBindingUniformTexelBufferUpdateAfterBind = VK_TRUE;
        pNext_4.descriptorBindingStorageTexelBufferUpdateAfterBind = VK_TRUE;
        pNext_4.descriptorBindingUpdateUnusedWhilePending = VK_TRUE;
        pNext_4.descriptorBindingPartiallyBound = VK_TRUE;
        pNext_4.descriptorBindingVariableDescriptorCount = VK_TRUE;
        pNext_4.runtimeDescriptorArray = VK_TRUE;

        VkPhysicalDeviceHostQueryResetFeatures pNext_5 = {};
        pNext_5.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_HOST_QUERY_RESET_FEATURES;
        pNext_5.pNext = &pNext_4;
        pNext_5.hostQueryReset = VK_TRUE;

        VkPhysicalDeviceShaderSubgroupExtendedTypesFeatures pNext_6 = {};
        pNext_6.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_SUBGROUP_EXTENDED_TYPES_FEATURES;
        pNext_6.pNext = &pNext_5;
        pNext_6.shaderSubgroupExtendedTypes = VK_TRUE;

        VkPhysicalDeviceUniformBufferStandardLayoutFeatures pNext_7 = {};
        pNext_7.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_UNIFORM_BUFFER_STANDARD_LAYOUT_FEATURES;
        pNext_7.pNext = &pNext_6;
        pNext_7.uniformBufferStandardLayout = VK_TRUE;

        VkDeviceCreateInfo deviceCreateInfo = {};
        deviceCreateInfo.sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO;
        deviceCreateInfo.pNext = &pNext_7;
        deviceCreateInfo.queueCreateInfoCount = pCreateInfo->queueCreateInfoCount;
        deviceCreateInfo.pQueueCreateInfos = pCreateInfo->pQueueCreateInfos;
        deviceCreateInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
        deviceCreateInfo.ppEnabledExtensionNames = static_cast<const char *const *>(extensions.data());
        deviceCreateInfo.pEnabledFeatures = &enabledFeatures;
        return vkCreateDevice(physicalDevice, &deviceCreateInfo, pAllocator, pDevice);
    } else {
        return VK_ERROR_UNKNOWN;
    }
}

inline VkResult vpEnumerateDeviceProfiles(VkPhysicalDevice physicalDevice, const char *pLayerName, uint32_t *pPropertyCount,
                                          VpProfileProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    uint32_t instanceExtensionCount;
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &instanceExtensionCount, nullptr);
    std::vector<VkExtensionProperties> instanceExtensions(instanceExtensionCount);
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &instanceExtensionCount, instanceExtensions.data());

    uint32_t deviceExtensionCount;
    result = vkEnumerateDeviceExtensionProperties(physicalDevice, pLayerName, &deviceExtensionCount, nullptr);
    std::vector<VkExtensionProperties> deviceExtensions(deviceExtensionCount);
    result = vkEnumerateDeviceExtensionProperties(physicalDevice, pLayerName, &deviceExtensionCount, deviceExtensions.data());

    uint32_t supportedProfileCount = 0;

    const VpProfileProperties supportedProfiles[] = {
        VpProfileProperties{VP_KHR_MINIMUM_REQUIREMENTS_NAME, VP_KHR_MINIMUM_REQUIREMENTS_SPEC_VERSION},
        VpProfileProperties{VP_KHR_1_2_ROADMAP_2022_NAME, VP_KHR_1_2_ROADMAP_2022_SPEC_VERSION},
        VpProfileProperties{VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_NAME, VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_SPEC_VERSION}};

    for (int i = 0, n = countof(supportedProfiles); i < n; ++i) {
        VkBool32 supported = VK_TRUE;

        if (strcmp(supportedProfiles[i].profileName, VP_KHR_MINIMUM_REQUIREMENTS_NAME) == 0) {
        } else if (strcmp(supportedProfiles[i].profileName, VP_KHR_1_2_ROADMAP_2022_NAME) == 0) {
            for (std::size_t i = 0, n = countof(VP_KHR_1_2_ROADMAP_2022_EXTENSIONS); i < n && supported; ++i) {
                const bool supportedInstanceExt = vpCheckExtension(instanceExtensions.data(), instanceExtensions.size(),
                                                                   VP_KHR_1_2_ROADMAP_2022_EXTENSIONS[i].extensionName);
                const bool supportedDeviceExt = vpCheckExtension(deviceExtensions.data(), deviceExtensions.size(),
                                                                 VP_KHR_1_2_ROADMAP_2022_EXTENSIONS[i].extensionName);

                if (!supportedInstanceExt && !supportedDeviceExt) {
                    supported = VK_FALSE;
                }
            }

            VkPhysicalDeviceExtendedDynamicState2FeaturesEXT deviceExtendedDynamicState = {};
            deviceExtendedDynamicState.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            deviceExtendedDynamicState.pNext = nullptr;

            VkPhysicalDeviceTexelBufferAlignmentFeaturesEXT deviceTexelBufferAlign = {};
            deviceTexelBufferAlign.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            deviceTexelBufferAlign.pNext = &deviceExtendedDynamicState;

            VkPhysicalDeviceSubgroupSizeControlFeaturesEXT deviceSubgroupSize = {};
            deviceSubgroupSize.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            deviceSubgroupSize.pNext = &deviceTexelBufferAlign;

            VkPhysicalDeviceShaderDemoteToHelperInvocationFeaturesEXT deviceShaderDemote = {};
            deviceShaderDemote.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            deviceShaderDemote.pNext = &deviceSubgroupSize;

            VkPhysicalDevicePrivateDataFeaturesEXT devicePrivateData = {};
            devicePrivateData.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            devicePrivateData.pNext = &deviceShaderDemote;

            VkPhysicalDevicePipelineCreationCacheControlFeaturesEXT devicePipelineCreation = {};
            devicePipelineCreation.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            devicePipelineCreation.pNext = &devicePrivateData;

            VkPhysicalDeviceInlineUniformBlockFeaturesEXT deviceInlineUniformBlock = {};
            deviceInlineUniformBlock.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_INLINE_UNIFORM_BLOCK_FEATURES_EXT;
            deviceInlineUniformBlock.pNext = &devicePipelineCreation;

            VkPhysicalDeviceImageRobustnessFeaturesEXT deviceImageRobustness = {};
            deviceImageRobustness.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_IMAGE_ROBUSTNESS_FEATURES_EXT;
            deviceImageRobustness.pNext = &deviceInlineUniformBlock;

            VkPhysicalDeviceZeroInitializeWorkgroupMemoryFeaturesKHR deviceZeroInitialize = {};
            deviceZeroInitialize.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ZERO_INITIALIZE_WORKGROUP_MEMORY_FEATURES_KHR;
            deviceZeroInitialize.pNext = &deviceImageRobustness;

            VkPhysicalDeviceSynchronization2FeaturesKHR deviceSynchronization2 = {};
            deviceSynchronization2.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SYNCHRONIZATION_2_FEATURES_KHR;
            deviceSynchronization2.pNext = &deviceZeroInitialize;

            VkPhysicalDeviceShaderTerminateInvocationFeaturesKHR deviceShaderTerminateInvocation = {};
            deviceShaderTerminateInvocation.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_TERMINATE_INVOCATION_FEATURES_KHR;
            deviceShaderTerminateInvocation.pNext = &deviceSynchronization2;

            VkPhysicalDeviceVulkan12Features deviceFeatures12 = {};
            deviceFeatures12.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES;
            deviceFeatures12.pNext = &deviceShaderTerminateInvocation;

            VkPhysicalDeviceVulkan11Features deviceFeatures11 = {};
            deviceFeatures11.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_FEATURES;
            deviceFeatures11.pNext = &deviceFeatures12;

            VkPhysicalDeviceFeatures2 deviceFeatures = {};
            deviceFeatures.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2;
            deviceFeatures.pNext = &deviceFeatures11;

            vkGetPhysicalDeviceFeatures2(physicalDevice, &deviceFeatures);

            if (deviceFeatures.features.robustBufferAccess != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.imageCubeArray != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.independentBlend != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.sampleRateShading != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.drawIndirectFirstInstance != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.depthBiasClamp != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.samplerAnisotropy != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.occlusionQueryPrecise != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.fragmentStoresAndAtomics != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderStorageImageExtendedFormats != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderStorageImageReadWithoutFormat != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderUniformBufferArrayDynamicIndexing != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderSampledImageArrayDynamicIndexing != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderStorageBufferArrayDynamicIndexing != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures.features.shaderStorageImageArrayDynamicIndexing != VK_TRUE) {
                supported = VK_FALSE;
            }

            if (deviceFeatures11.multiview != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures11.samplerYcbcrConversion != VK_TRUE) {
                supported = VK_FALSE;
            }

            if (deviceFeatures12.samplerMirrorClampToEdge != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.shaderUniformTexelBufferArrayDynamicIndexing != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.uniformBufferStandardLayout != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.shaderSubgroupExtendedTypes != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.separateDepthStencilLayouts != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.hostQueryReset != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.bufferDeviceAddress != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.vulkanMemoryModel != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.vulkanMemoryModelDeviceScope != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.vulkanMemoryModelAvailabilityVisibilityChains != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.subgroupBroadcastDynamicId != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceFeatures12.imagelessFramebuffer != VK_TRUE) {
                supported = VK_FALSE;
            }

            if (deviceShaderTerminateInvocation.shaderTerminateInvocation != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceSynchronization2.synchronization2 != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceZeroInitialize.shaderZeroInitializeWorkgroupMemory != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceImageRobustness.robustImageAccess != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceInlineUniformBlock.inlineUniformBlock != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (devicePipelineCreation.pipelineCreationCacheControl != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (devicePrivateData.privateData != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceShaderDemote.shaderDemoteToHelperInvocation != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceSubgroupSize.subgroupSizeControl != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceSubgroupSize.computeFullSubgroups != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceTexelBufferAlign.texelBufferAlignment != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (deviceExtendedDynamicState.extendedDynamicState2 != VK_TRUE) {
                supported = VK_FALSE;
            }

            VkPhysicalDeviceVulkan12Properties devicePropertiesVulkan12 = {};
            devicePropertiesVulkan12.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_PROPERTIES;
            devicePropertiesVulkan12.pNext = nullptr;

            VkPhysicalDeviceVulkan11Properties devicePropertiesVulkan11 = {};
            devicePropertiesVulkan11.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_1_PROPERTIES;
            devicePropertiesVulkan11.pNext = &devicePropertiesVulkan12;

            VkPhysicalDeviceProperties2 deviceProperties{};
            deviceProperties.sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2_KHR;
            deviceProperties.pNext = &devicePropertiesVulkan11;

            vkGetPhysicalDeviceProperties2(physicalDevice, &deviceProperties);

            if (deviceProperties.properties.limits.maxImageDimension1D < 8192) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxImageDimension2D < 8192) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxImageDimensionCube < 8192) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxImageArrayLayers < 2048) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxUniformBufferRange < 65536) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.bufferImageGranularity > 4096) {
                supported = VK_FALSE;
            }

            if (deviceProperties.properties.limits.maxPerStageDescriptorSamplers < 64) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxPerStageDescriptorUniformBuffers < 15) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxPerStageDescriptorStorageBuffers < 30) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxPerStageDescriptorSampledImages < 200) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxPerStageDescriptorStorageImages < 16) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxPerStageResources < 200) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxDescriptorSetSamplers < 576) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxDescriptorSetUniformBuffers < 90) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxDescriptorSetStorageBuffers < 96) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxDescriptorSetSampledImages < 1800) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxDescriptorSetStorageImages < 144) {
                supported = VK_FALSE;
            }

            if (deviceProperties.properties.limits.maxFragmentCombinedOutputResources < 16) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxComputeWorkGroupInvocations < 256) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxComputeWorkGroupSize[0] < 256 ||
                deviceProperties.properties.limits.maxComputeWorkGroupSize[1] < 256 ||
                deviceProperties.properties.limits.maxComputeWorkGroupSize[2] < 64) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.subTexelPrecisionBits < 8) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.mipmapPrecisionBits < 6) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.maxSamplerLodBias < 14) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.pointSizeGranularity > 0.125) {
                supported = VK_FALSE;
            }
            if (deviceProperties.properties.limits.lineWidthGranularity > 0.5) {
                supported = VK_FALSE;
            }

            if (devicePropertiesVulkan11.subgroupSize < 4) {
                supported = VK_FALSE;
            }

            if (devicePropertiesVulkan12.shaderSignedZeroInfNanPreserveFloat16 != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (devicePropertiesVulkan12.shaderSignedZeroInfNanPreserveFloat32 != VK_TRUE) {
                supported = VK_FALSE;
            }
            if (devicePropertiesVulkan12.maxPerStageDescriptorUpdateAfterBindInputAttachments < 7) {
                supported = VK_FALSE;
            }

        } else if (strcmp(supportedProfiles[i].profileName, VP_LUNARG_1_1_DESKTOP_PORTABILITY_2022_NAME) == 0) {
            for (std::size_t i = 0, n = countof(VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS); i < n && supported; ++i) {
                const bool supportedInstanceExt = vpCheckExtension(instanceExtensions.data(), instanceExtensions.size(),
                                                                   VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS[i].extensionName);
                const bool supportedDeviceExt = vpCheckExtension(deviceExtensions.data(), deviceExtensions.size(),
                                                                 VP_KHR_1_1_DESKTOP_PORTABILITY_2022_EXTENSIONS[i].extensionName);

                if (!supportedInstanceExt && !supportedDeviceExt) {
                    supported = VK_FALSE;
                }
            }
        }

        if (supported) {
            if (pProperties != nullptr && supportedProfileCount < *pPropertyCount) {
                pProperties[supportedProfileCount] = supportedProfiles[i];
            }
            supportedProfileCount++;
        }
    }

    if (pProperties == nullptr) {
        *pPropertyCount = supportedProfileCount;
    }

    return result;
}
