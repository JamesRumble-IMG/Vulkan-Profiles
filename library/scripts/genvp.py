#!/usr/bin/python3
#
# Copyright (c) 2021-2022 LunarG, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Daniel Rakos, RasterGrid

import os
import re
import argparse
import xml.etree.ElementTree as etree
import json

COPYRIGHT_HEADER = '''/**
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
 * DO NOT EDIT: This file is generated.
 */
'''

H_HEADER = '''
#ifndef VULKAN_PROFILES_H_
#define VULKAN_PROFILES_H_ 1

#define VPAPI_ATTR

#ifdef __cplusplus
    extern "C" {
#endif

#include <vulkan/vulkan_core.h>
#ifdef VK_ENABLE_BETA_EXTENSIONS
#include <vulkan/vulkan_beta.h>
#endif
'''

H_FOOTER = '''
#ifdef __cplusplus
}
#endif

#endif // VULKAN_PROFILES_H_
'''

CPP_HEADER = '''
#include <vulkan/vulkan_profiles.h>
#include <stddef.h>
#include <string.h>
#include <stdint.h>
#include <vector>
#include <algorithm>
'''

HPP_HEADER = '''
#ifndef VULKAN_PROFILES_HPP_
#define VULKAN_PROFILES_HPP_ 1

#define VPAPI_ATTR inline

#include <vulkan/vulkan_core.h>
#ifdef VK_ENABLE_BETA_EXTENSIONS
#include <vulkan/vulkan_beta.h>
#endif
#include <stddef.h>
#include <string.h>
#include <stdint.h>
#include <vector>
#include <algorithm>
'''

HPP_FOOTER = '''
#endif // VULKAN_PROFILES_HPP_
'''

API_DEFS = '''
#define VP_MAX_PROFILE_NAME_SIZE 256U

typedef struct VpProfileProperties {
    char        profileName[VP_MAX_PROFILE_NAME_SIZE];
    uint32_t    specVersion;
} VpProfileProperties;

typedef enum VpInstanceCreateFlagBits {
    VP_INSTANCE_CREATE_MERGE_EXTENSIONS_BIT = 0x00000001,
    VP_INSTANCE_CREATE_OVERRIDE_EXTENSIONS_BIT = 0x00000002,

    VP_INSTANCE_CREATE_FLAG_BITS_MAX_ENUM = 0x7FFFFFFF
} VpInstanceCreateFlagBits;
typedef VkFlags VpInstanceCreateFlags;

typedef struct VpInstanceCreateInfo {
    const VkInstanceCreateInfo* pCreateInfo;
    const VpProfileProperties*  pProfile;
    VpInstanceCreateFlags       flags;
} VpInstanceCreateInfo;

typedef enum VpDeviceCreateFlagBits {
    VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT = 0x00000001,
    VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT = 0x00000002,
    VP_DEVICE_CREATE_MERGE_EXTENSIONS_BIT = 0x00000004,
    VP_DEVICE_CREATE_OVERRIDE_EXTENSIONS_BIT = 0x00000008,

    VP_DEVICE_CREATE_DISABLE_ROBUST_ACCESS_BIT =
        VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT | VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT,
    VP_DEVICE_CREATE_FLAG_BITS_MAX_ENUM = 0x7FFFFFFF
} VpDeviceCreateFlagBits;
typedef VkFlags VpDeviceCreateFlags;

typedef struct VpDeviceCreateInfo {
    const VkDeviceCreateInfo*   pCreateInfo;
    const VpProfileProperties*  pProfile;
    VpDeviceCreateFlags         flags;
} VpDeviceCreateInfo;

// Query the list of available profiles in the library
VPAPI_ATTR VkResult vpGetProfiles(uint32_t *pPropertyCount, VpProfileProperties *pProperties);

// List the recommended fallback profiles of a profile
VPAPI_ATTR VkResult vpGetProfileFallbacks(const VpProfileProperties *pProfile, uint32_t *pPropertyCount, VpProfileProperties *pProperties);

// Check whether a profile is supported at the instance level
VPAPI_ATTR VkResult vpGetInstanceProfileSupport(const char *pLayerName, const VpProfileProperties *pProfile, VkBool32 *pSupported);

// Create a VkInstance with the profile instance extensions enabled
VPAPI_ATTR VkResult vpCreateInstance(const VpInstanceCreateInfo *pCreateInfo,
                                     const VkAllocationCallbacks *pAllocator, VkInstance *pInstance);

// Check whether a profile is supported by the physical device
VPAPI_ATTR VkResult vpGetPhysicalDeviceProfileSupport(VkInstance instance, VkPhysicalDevice physicalDevice,
                                                      const VpProfileProperties *pProfile, VkBool32 *pSupported);

// Create a VkDevice with the profile features and device extensions enabled
VPAPI_ATTR VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpDeviceCreateInfo *pCreateInfo,
                                   const VkAllocationCallbacks *pAllocator, VkDevice *pDevice);

// Query the list of instance extensions of a profile
VPAPI_ATTR VkResult vpGetProfileInstanceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                            VkExtensionProperties *pProperties);

// Query the list of device extensions of a profile
VPAPI_ATTR VkResult vpGetProfileDeviceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkExtensionProperties *pProperties);

// Fill the feature structures with the requirements of a profile
VPAPI_ATTR void vpGetProfileFeatures(const VpProfileProperties *pProfile, void *pNext);

// Query the list of feature structure types specified by the profile
VPAPI_ATTR VkResult vpGetProfileFeatureStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                      VkStructureType *pProperties);

// Fill the property structures with the requirements of a profile
VPAPI_ATTR void vpGetProfileProperties(const VpProfileProperties *pProfile, void *pNext);

// Query the list of property structure types specified by the profile
VPAPI_ATTR VkResult vpGetProfilePropertyStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                       VkStructureType *pProperties);

// Query the requirements of queue families by a profile
VPAPI_ATTR VkResult vpGetProfileQueueFamilyProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                      VkQueueFamilyProperties2KHR *pProperties);

// Query the list of query family structure types specified by the profile
VPAPI_ATTR VkResult vpGetProfileQueueFamilyStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkStructureType *pProperties);

// Query the list of formats with specified requirements by a profile
VPAPI_ATTR VkResult vpGetProfileFormats(const VpProfileProperties *pProfile, uint32_t *pFormatCount, VkFormat *pFormats);

// Query the requirements of a format for a profile
VPAPI_ATTR void vpGetProfileFormatProperties(const VpProfileProperties *pProfile, VkFormat format, void *pNext);

// Query the list of format structure types specified by the profile
VPAPI_ATTR VkResult vpGetProfileFormatStructureTypes(const VpProfileProperties *pProfile, VkFormat format, uint32_t *pPropertyCount,
                                                     VkStructureType *pProperties);
'''

PRIVATE_DEFS = '''
using PFN_vpStructFiller = void(*)(VkBaseOutStructure* p);
using PFN_vpStructComparator = bool(*)(VkBaseOutStructure* p);
using PFN_vpStructChainerCb =  void(*)(VkBaseOutStructure* p, void* pUser);
using PFN_vpStructChainer = void(*)(VkBaseOutStructure* p, void* pUser, PFN_vpStructChainerCb pfnCb);

struct VpFeatureDesc {
    PFN_vpStructFiller              pfnFiller;
    PFN_vpStructComparator          pfnComparator;
    PFN_vpStructChainer             pfnChainer;
};

struct VpPropertyDesc {
    PFN_vpStructFiller              pfnFiller;
    PFN_vpStructComparator          pfnComparator;
    PFN_vpStructChainer             pfnChainer;
};

struct VpQueueFamilyDesc {
    PFN_vpStructFiller              pfnFiller;
    PFN_vpStructComparator          pfnComparator;
};

struct VpFormatDesc {
    VkFormat                        format;
    PFN_vpStructFiller              pfnFiller;
    PFN_vpStructComparator          pfnComparator;
};

struct VpStructChainerDesc {
    PFN_vpStructChainer             pfnFeature;
    PFN_vpStructChainer             pfnProperty;
    PFN_vpStructChainer             pfnQueueFamily;
    PFN_vpStructChainer             pfnFormat;
};

struct VpProfileDesc {
    VpProfileProperties             props;
    uint32_t                        minApiVersion;

    const VkExtensionProperties*    pInstanceExtensions;
    uint32_t                        instanceExtensionCount;

    const VkExtensionProperties*    pDeviceExtensions;
    uint32_t                        deviceExtensionCount;

    const VpProfileProperties*      pFallbacks;
    uint32_t                        fallbackCount;

    const VkStructureType*          pFeatureStructTypes;
    uint32_t                        featureStructTypeCount;
    VpFeatureDesc                   feature;

    const VkStructureType*          pPropertyStructTypes;
    uint32_t                        propertyStructTypeCount;
    VpPropertyDesc                  property;

    const VkStructureType*          pQueueFamilyStructTypes;
    uint32_t                        queueFamilyStructTypeCount;
    const VpQueueFamilyDesc*        pQueueFamilies;
    uint32_t                        queueFamilyCount;

    const VkStructureType*          pFormatStructTypes;
    uint32_t                        formatStructTypeCount;
    const VpFormatDesc*             pFormats;
    uint32_t                        formatCount;

    VpStructChainerDesc             chainers;
};
'''

PRIVATE_IMPL_BODY = '''
VPAPI_ATTR const VpProfileDesc* vpGetProfileDesc(const char profileName[VP_MAX_PROFILE_NAME_SIZE]) {
    for (uint32_t i = 0; i < vpProfileCount; ++i) {
        if (strncmp(vpProfiles[i].props.profileName, profileName, VP_MAX_PROFILE_NAME_SIZE) == 0) return &vpProfiles[i];
    }
    return nullptr;
}

VPAPI_ATTR bool vpCheckExtension(const VkExtensionProperties *supportedProperties, size_t supportedSize,
                                 const char *requestedExtension, uint32_t expectedVersion = 0) {
    for (size_t i = 0, n = supportedSize; i < n; ++i) {
        if (strcmp(supportedProperties[i].extensionName, requestedExtension) == 0) {
            return true;
            // Drivers don't actually update their spec version, so we cannot rely on this
            // return supportedProperties[i].specVersion >= expectedVersion;
        }
    }
    return false;
}

VPAPI_ATTR void vpGetInstanceExtensions(const VpInstanceCreateInfo *pCreateInfo, uint32_t propertyCount,
                                        const VkExtensionProperties *pProperties, std::vector<const char *> &extensions) {
    if (pCreateInfo->flags & VP_INSTANCE_CREATE_MERGE_EXTENSIONS_BIT) {
        for (uint32_t i = 0, n = propertyCount; i < n; ++i) {
            extensions.push_back(pProperties[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->pCreateInfo->enabledExtensionCount; ++i) {
            if (vpCheckExtension(pProperties, propertyCount, pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    } else {  // or VP_INSTANCE_CREATE_OVERRIDE_EXTENSIONS_BIT
        for (uint32_t i = 0, n = pCreateInfo->pCreateInfo->enabledExtensionCount; i < n; ++i) {
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    }
}

VPAPI_ATTR void vpGetDeviceExtensions(const VpDeviceCreateInfo *pCreateInfo, uint32_t propertyCount,
                                      const VkExtensionProperties *pProperties, std::vector<const char *> &extensions) {
    if (pCreateInfo->flags & VP_DEVICE_CREATE_MERGE_EXTENSIONS_BIT) {
        for (int i = 0, n = propertyCount; i < n; ++i) {
            extensions.push_back(pProperties[i].extensionName);
        }

        for (uint32_t i = 0; i < pCreateInfo->pCreateInfo->enabledExtensionCount; ++i) {
            if (vpCheckExtension(pProperties, propertyCount, pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i])) {
                continue;
            }
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    } else {  // or VP_DEVICE_CREATE_OVERRIDE_EXTENSIONS_BIT
        for (int i = 0, n = pCreateInfo->pCreateInfo->enabledExtensionCount; i < n; ++i) {
            extensions.push_back(pCreateInfo->pCreateInfo->ppEnabledExtensionNames[i]);
        }
    }
}

VPAPI_ATTR const void* vpGetStructure(const void* pNext, VkStructureType type) {
    const VkBaseOutStructure *p = static_cast<const VkBaseOutStructure*>(pNext);
    while (p != nullptr) {
        if (p->sType == type) return p;
        p = p->pNext;
    }
    return nullptr;
}

VPAPI_ATTR void* vpGetStructure(void* pNext, VkStructureType type) {
    VkBaseOutStructure *p = static_cast<VkBaseOutStructure*>(pNext);
    while (p != nullptr) {
        if (p->sType == type) return p;
        p = p->pNext;
    }
    return nullptr;
}
'''

PUBLIC_IMPL_BODY = '''
VPAPI_ATTR VkResult vpGetProfiles(uint32_t *pPropertyCount, VpProfileProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    if (pProperties == nullptr) {
        *pPropertyCount = detail::vpProfileCount;
    } else {
        if (*pPropertyCount < detail::vpProfileCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = detail::vpProfileCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = detail::vpProfiles[i].props;
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileFallbacks(const VpProfileProperties *pProfile, uint32_t *pPropertyCount, VpProfileProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->fallbackCount;
    } else {
        if (*pPropertyCount < pDesc->fallbackCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->fallbackCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pFallbacks[i];
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetInstanceProfileSupport(const char *pLayerName, const VpProfileProperties *pProfile, VkBool32 *pSupported) {
    VkResult result = VK_SUCCESS;

    uint32_t apiVersion = VK_MAKE_VERSION(1, 0, 0);
    static PFN_vkEnumerateInstanceVersion pfnEnumerateInstanceVersion =
        (PFN_vkEnumerateInstanceVersion)vkGetInstanceProcAddr(VK_NULL_HANDLE, "vkEnumerateInstanceVersion");
    if (pfnEnumerateInstanceVersion != nullptr) {
        pfnEnumerateInstanceVersion(&apiVersion);
    }

    uint32_t extCount = 0;
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &extCount, nullptr);
    if (result != VK_SUCCESS) {
        return result;
    }
    std::vector<VkExtensionProperties> ext(extCount);
    result = vkEnumerateInstanceExtensionProperties(pLayerName, &extCount, ext.data());
    if (result != VK_SUCCESS) {
        return result;
    }

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    *pSupported = VK_FALSE;

    if (pDesc->props.specVersion < pProfile->specVersion) {
        return result;
    }

    if (VK_VERSION_PATCH(apiVersion) < VK_VERSION_PATCH(pDesc->minApiVersion)) {
        return result;
    }

    for (uint32_t i = 0; i < pDesc->instanceExtensionCount; ++i) {
        if (!detail::vpCheckExtension(ext.data(), ext.size(),
            pDesc->pInstanceExtensions[i].extensionName,
            pDesc->pInstanceExtensions[i].specVersion)) {
            return result;
        }
    }

    // We require VK_KHR_get_physical_device_properties2 if we are on Vulkan 1.0
    if (apiVersion < VK_API_VERSION_1_1) {
        bool foundGPDP2 = false;
        for (size_t i = 0; i < ext.size(); ++i) {
            if (strcmp(ext[i].extensionName, VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME) == 0) {
                foundGPDP2 = true;
                break;
            }
        }
        if (!foundGPDP2) {
            return result;
        }
    }

    *pSupported = VK_TRUE;
    return result;
}

VPAPI_ATTR VkResult vpCreateInstance(const VpInstanceCreateInfo *pCreateInfo,
                                     const VkAllocationCallbacks *pAllocator, VkInstance *pInstance) {
    VkInstanceCreateInfo createInfo{ VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO };
    VkApplicationInfo appInfo{ VK_STRUCTURE_TYPE_APPLICATION_INFO };
    std::vector<const char*> extensions;
    VkInstanceCreateInfo* pInstanceCreateInfo = nullptr;
    VkExtensionProperties* pProfileExtensions = nullptr;
    uint32_t profileExtensionCount = 0;

    if (pCreateInfo != nullptr && pCreateInfo->pCreateInfo != nullptr) {
        createInfo = *pCreateInfo->pCreateInfo;
        pInstanceCreateInfo = &createInfo;

        const detail::VpProfileDesc* pDesc = nullptr;
        if (pCreateInfo->pProfile != nullptr) {
            pDesc = detail::vpGetProfileDesc(pCreateInfo->pProfile->profileName);
            if (pDesc == nullptr) return VK_ERROR_UNKNOWN;
        }

        if (createInfo.pApplicationInfo == nullptr) {
            appInfo.apiVersion = pDesc->minApiVersion;
            createInfo.pApplicationInfo = &appInfo;
        }

        if (pDesc != nullptr && pDesc->pInstanceExtensions != nullptr) {
            detail::vpGetInstanceExtensions(pCreateInfo, pDesc->instanceExtensionCount, pDesc->pInstanceExtensions, extensions);

            // Need to include VK_KHR_get_physical_device_properties2 if we are on Vulkan 1.0
            if (createInfo.pApplicationInfo->apiVersion < VK_API_VERSION_1_1) {
                bool foundGPDP2 = false;
                for (size_t i = 0; i < extensions.size(); ++i) {
                    if (strcmp(extensions[i], VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME) == 0) {
                        foundGPDP2 = true;
                        break;
                    }
                }
                if (!foundGPDP2) {
                    extensions.push_back(VK_KHR_GET_PHYSICAL_DEVICE_PROPERTIES_2_EXTENSION_NAME);
                }
            }

            createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
            createInfo.ppEnabledExtensionNames = extensions.data();
        }
    }

    return vkCreateInstance(pInstanceCreateInfo, pAllocator, pInstance);
}

VPAPI_ATTR VkResult vpGetPhysicalDeviceProfileSupport(VkInstance instance, VkPhysicalDevice physicalDevice,
                                                      const VpProfileProperties *pProfile, VkBool32 *pSupported) {
    VkResult result = VK_SUCCESS;

    uint32_t extCount = 0;
    result = vkEnumerateDeviceExtensionProperties(physicalDevice, nullptr, &extCount, nullptr);
    if (result != VK_SUCCESS) {
        return result;
    }
    std::vector<VkExtensionProperties> ext(extCount);
    result = vkEnumerateDeviceExtensionProperties(physicalDevice, nullptr, &extCount, ext.data());
    if (result != VK_SUCCESS) {
        return result;
    }

    // Workaround old loader bug where count could be smaller on the second call to vkEnumerateDeviceExtensionProperties
    ext.resize(extCount);

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    *pSupported = VK_FALSE;

    if (pDesc->props.specVersion < pProfile->specVersion) {
        return result;
    }

    {
        VkPhysicalDeviceProperties props{};
        vkGetPhysicalDeviceProperties(physicalDevice, &props);
        if (VK_VERSION_PATCH(props.apiVersion) < VK_VERSION_PATCH(pDesc->minApiVersion)) {
            return result;
        }
    }

    for (uint32_t i = 0; i < pDesc->deviceExtensionCount; ++i) {
        if (!detail::vpCheckExtension(ext.data(), ext.size(),
            pDesc->pDeviceExtensions[i].extensionName,
            pDesc->pDeviceExtensions[i].specVersion)) {
            return result;
        }
    }

    struct GPDP2EntryPoints {
        PFN_vkGetPhysicalDeviceFeatures2KHR                 pfnGetPhysicalDeviceFeatures2;
        PFN_vkGetPhysicalDeviceProperties2KHR               pfnGetPhysicalDeviceProperties2;
        PFN_vkGetPhysicalDeviceFormatProperties2KHR         pfnGetPhysicalDeviceFormatProperties2;
        PFN_vkGetPhysicalDeviceQueueFamilyProperties2KHR    pfnGetPhysicalDeviceQueueFamilyProperties2;
    };

    struct UserData {
        VkPhysicalDevice                    physicalDevice;
        const detail::VpProfileDesc*        pDesc;
        GPDP2EntryPoints                    gpdp2;
        uint32_t                            index;
        uint32_t                            count;
        detail::PFN_vpStructChainerCb       pfnCb;
        bool                                supported;
    } userData{ physicalDevice, pDesc };

    // Attempt to load core versions of the GPDP2 entry points
    userData.gpdp2.pfnGetPhysicalDeviceFeatures2 =
        (PFN_vkGetPhysicalDeviceFeatures2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceFeatures2");
    userData.gpdp2.pfnGetPhysicalDeviceProperties2 =
        (PFN_vkGetPhysicalDeviceProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties2");
    userData.gpdp2.pfnGetPhysicalDeviceFormatProperties2 =
        (PFN_vkGetPhysicalDeviceFormatProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceFormatProperties2");
    userData.gpdp2.pfnGetPhysicalDeviceQueueFamilyProperties2 =
        (PFN_vkGetPhysicalDeviceQueueFamilyProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceQueueFamilyProperties2");

    // If not successful, try to load KHR variant
    if (userData.gpdp2.pfnGetPhysicalDeviceFeatures2 == nullptr) {
        userData.gpdp2.pfnGetPhysicalDeviceFeatures2 =
            (PFN_vkGetPhysicalDeviceFeatures2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceFeatures2KHR");
        userData.gpdp2.pfnGetPhysicalDeviceProperties2 =
            (PFN_vkGetPhysicalDeviceProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceProperties2KHR");
        userData.gpdp2.pfnGetPhysicalDeviceFormatProperties2 =
            (PFN_vkGetPhysicalDeviceFormatProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceFormatProperties2KHR");
        userData.gpdp2.pfnGetPhysicalDeviceQueueFamilyProperties2 =
            (PFN_vkGetPhysicalDeviceQueueFamilyProperties2KHR)vkGetInstanceProcAddr(instance, "vkGetPhysicalDeviceQueueFamilyProperties2KHR");
    }

    if (userData.gpdp2.pfnGetPhysicalDeviceFeatures2 == nullptr ||
        userData.gpdp2.pfnGetPhysicalDeviceProperties2 == nullptr ||
        userData.gpdp2.pfnGetPhysicalDeviceFormatProperties2 == nullptr ||
        userData.gpdp2.pfnGetPhysicalDeviceQueueFamilyProperties2 == nullptr) {
        return VK_ERROR_EXTENSION_NOT_PRESENT;
    }

    {
        VkPhysicalDeviceFeatures2KHR features{ VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2_KHR };
        pDesc->chainers.pfnFeature(static_cast<VkBaseOutStructure*>(static_cast<void*>(&features)), &userData,
            [](VkBaseOutStructure* p, void* pUser) {
                UserData* pUserData = static_cast<UserData*>(pUser);
                pUserData->gpdp2.pfnGetPhysicalDeviceFeatures2(pUserData->physicalDevice,
                                                               static_cast<VkPhysicalDeviceFeatures2KHR*>(static_cast<void*>(p)));
                pUserData->supported = pUserData->pDesc->feature.pfnComparator(p);
            }
        );
        if (!userData.supported) {
            return result;
        }
    }

    {
        VkPhysicalDeviceProperties2KHR props{ VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2_KHR };
        pDesc->chainers.pfnProperty(static_cast<VkBaseOutStructure*>(static_cast<void*>(&props)), &userData,
            [](VkBaseOutStructure* p, void* pUser) {
                UserData* pUserData = static_cast<UserData*>(pUser);
                pUserData->gpdp2.pfnGetPhysicalDeviceProperties2(pUserData->physicalDevice,
                                                                 static_cast<VkPhysicalDeviceProperties2KHR*>(static_cast<void*>(p)));
                pUserData->supported = pUserData->pDesc->property.pfnComparator(p);
            }
        );
        if (!userData.supported) {
            return result;
        }
    }

    for (uint32_t i = 0; i < pDesc->formatCount; ++i) {
        userData.index = i;
        VkFormatProperties2KHR props{ VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_2_KHR };
        pDesc->chainers.pfnFormat(static_cast<VkBaseOutStructure*>(static_cast<void*>(&props)), &userData,
            [](VkBaseOutStructure* p, void* pUser) {
                UserData* pUserData = static_cast<UserData*>(pUser);
                pUserData->gpdp2.pfnGetPhysicalDeviceFormatProperties2(pUserData->physicalDevice,
                                                                       pUserData->pDesc->pFormats[pUserData->index].format,
                                                                       static_cast<VkFormatProperties2KHR*>(static_cast<void*>(p)));
                pUserData->supported = pUserData->pDesc->pFormats[pUserData->index].pfnComparator(p);
            }
        );
        if (!userData.supported) {
            return result;
        }
    }

    {
        userData.gpdp2.pfnGetPhysicalDeviceQueueFamilyProperties2(physicalDevice, &userData.count, nullptr);
        std::vector<VkQueueFamilyProperties2KHR> props(userData.count, { VK_STRUCTURE_TYPE_QUEUE_FAMILY_PROPERTIES_2_KHR });
        userData.index = 0;

        detail::PFN_vpStructChainerCb callback = [](VkBaseOutStructure* p, void* pUser) {
            UserData* pUserData = static_cast<UserData*>(pUser);
            if (++pUserData->index < pUserData->count) {
                pUserData->pDesc->chainers.pfnQueueFamily(++p, pUser, pUserData->pfnCb);
            } else {
                p -= pUserData->count - 1;
                pUserData->gpdp2.pfnGetPhysicalDeviceQueueFamilyProperties2(pUserData->physicalDevice,
                                                                            &pUserData->count,
                                                                            static_cast<VkQueueFamilyProperties2KHR*>(static_cast<void*>(p)));
                for (uint32_t i = 0; i < pUserData->pDesc->queueFamilyCount; ++i) {
                    pUserData->supported = false;
                    for (uint32_t j = 0; j < pUserData->count; ++j) {
                        if (pUserData->pDesc->pQueueFamilies[i].pfnComparator(&p[j])) {
                            pUserData->supported = true;
                            break;
                        }
                    }
                    if (!pUserData->supported) {
                        return;
                    }
                }
            }
        };
        userData.pfnCb = callback;

        pDesc->chainers.pfnQueueFamily(static_cast<VkBaseOutStructure*>(static_cast<void*>(props.data())), &userData, callback);
        if (!userData.supported) {
            return result;
        }
    }

    *pSupported = VK_TRUE;
    return result;
}

VPAPI_ATTR VkResult vpCreateDevice(VkPhysicalDevice physicalDevice, const VpDeviceCreateInfo *pCreateInfo,
                                   const VkAllocationCallbacks *pAllocator, VkDevice *pDevice) {
    if (physicalDevice == VK_NULL_HANDLE || pCreateInfo == nullptr || pDevice == nullptr) {
        return vkCreateDevice(physicalDevice, pCreateInfo == nullptr ? nullptr : pCreateInfo->pCreateInfo, pAllocator, pDevice);
    }

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pCreateInfo->pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    struct UserData {
        VkPhysicalDevice                physicalDevice;
        const detail::VpProfileDesc*    pDesc;
        const VpDeviceCreateInfo*       pCreateInfo;
        const VkAllocationCallbacks*    pAllocator;
        VkDevice*                       pDevice;
        VkResult                        result;
    } userData{ physicalDevice, pDesc, pCreateInfo, pAllocator, pDevice };

    VkPhysicalDeviceFeatures2KHR features{ VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2_KHR };
    pDesc->chainers.pfnFeature(static_cast<VkBaseOutStructure*>(static_cast<void*>(&features)), &userData,
        [](VkBaseOutStructure* p, void* pUser) {
            UserData* pUserData = static_cast<UserData*>(pUser);
            const detail::VpProfileDesc* pDesc = pUserData->pDesc;
            const VpDeviceCreateInfo* pCreateInfo = pUserData->pCreateInfo;

            std::vector<const char*> extensions;
            detail::vpGetDeviceExtensions(pCreateInfo, pDesc->deviceExtensionCount, pDesc->pDeviceExtensions, extensions);

            VkBaseOutStructure profileStructList;
            profileStructList.pNext = p;
            VkPhysicalDeviceFeatures2KHR* pFeatures = static_cast<VkPhysicalDeviceFeatures2KHR*>(static_cast<void*>(p));
            if (pDesc->feature.pfnFiller != nullptr) {
                while (p != nullptr) {
                    pDesc->feature.pfnFiller(p);
                    p = p->pNext;
                }
            }

            if (pCreateInfo->pCreateInfo->pEnabledFeatures != nullptr) {
                pFeatures->features = *pCreateInfo->pCreateInfo->pEnabledFeatures;
            }

            if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT) {
                pFeatures->features.robustBufferAccess = VK_FALSE;
            }

#ifdef VK_EXT_robustness2
            VkPhysicalDeviceRobustness2FeaturesEXT* pRobustness2FeaturesEXT = static_cast<VkPhysicalDeviceRobustness2FeaturesEXT*>(
                detail::vpGetStructure(pFeatures, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_ROBUSTNESS_2_FEATURES_EXT));
            if (pRobustness2FeaturesEXT != nullptr) {
                if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_BUFFER_ACCESS_BIT) {
                    pRobustness2FeaturesEXT->robustBufferAccess2 = VK_FALSE;
                }
                if (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT) {
                    pRobustness2FeaturesEXT->robustImageAccess2 = VK_FALSE;
                }
            }
#endif

#ifdef VK_EXT_image_robustness
            VkPhysicalDeviceImageRobustnessFeaturesEXT* pImageRobustnessFeaturesEXT = static_cast<VkPhysicalDeviceImageRobustnessFeaturesEXT*>(
                detail::vpGetStructure(pFeatures, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_IMAGE_ROBUSTNESS_FEATURES_EXT));
            if (pImageRobustnessFeaturesEXT != nullptr && (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT)) {
                pImageRobustnessFeaturesEXT->robustImageAccess = VK_FALSE;
            }
#endif

#ifdef VK_VERSION_1_3
            VkPhysicalDeviceVulkan13Features* pVulkan13Features = static_cast<VkPhysicalDeviceVulkan13Features*>(
                detail::vpGetStructure(pFeatures, VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES));
            if (pVulkan13Features != nullptr && (pCreateInfo->flags & VP_DEVICE_CREATE_DISABLE_ROBUST_IMAGE_ACCESS_BIT)) {
                pVulkan13Features->robustImageAccess = VK_FALSE;
            }
#endif

            VkBaseOutStructure* pNext = static_cast<VkBaseOutStructure*>(const_cast<void*>(pCreateInfo->pCreateInfo->pNext));
            for (uint32_t i = 0; i < pDesc->featureStructTypeCount; ++i) {
                const void* pRequested = detail::vpGetStructure(pNext, pDesc->pFeatureStructTypes[i]);
                if (pRequested == nullptr) {
                    VkBaseOutStructure* pPrevStruct = &profileStructList;
                    VkBaseOutStructure* pCurrStruct = pPrevStruct->pNext;
                    while (pCurrStruct->sType != pDesc->pFeatureStructTypes[i]) {
                        pPrevStruct = pCurrStruct;
                        pCurrStruct = pCurrStruct->pNext;
                    }
                    pPrevStruct->pNext = pCurrStruct->pNext;
                    pCurrStruct->pNext = pNext;
                    pNext = pCurrStruct;
                }
            }

            VkDeviceCreateInfo createInfo{ VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO };
            createInfo.pNext = pNext;
            createInfo.queueCreateInfoCount = pCreateInfo->pCreateInfo->queueCreateInfoCount;
            createInfo.pQueueCreateInfos = pCreateInfo->pCreateInfo->pQueueCreateInfos;
            createInfo.enabledExtensionCount = static_cast<uint32_t>(extensions.size());
            createInfo.ppEnabledExtensionNames = extensions.data();
            pUserData->result = vkCreateDevice(pUserData->physicalDevice, &createInfo, pUserData->pAllocator, pUserData->pDevice);
        }
    );

    return userData.result;
}

VPAPI_ATTR VkResult vpGetProfileInstanceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                            VkExtensionProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->instanceExtensionCount;
    } else {
        if (*pPropertyCount < pDesc->instanceExtensionCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->instanceExtensionCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pInstanceExtensions[i];
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileDeviceExtensionProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkExtensionProperties *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->deviceExtensionCount;
    } else {
        if (*pPropertyCount < pDesc->deviceExtensionCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->deviceExtensionCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pDeviceExtensions[i];
        }
    }
    return result;
}

VPAPI_ATTR void vpGetProfileFeatures(const VpProfileProperties *pProfile, void *pNext) {
    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc != nullptr && pDesc->feature.pfnFiller != nullptr) {
        VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(pNext);
        while (p != nullptr) {
            pDesc->feature.pfnFiller(p);
            p = p->pNext;
        }
    }
}

VPAPI_ATTR VkResult vpGetProfileFeatureStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                      VkStructureType *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->featureStructTypeCount;
    } else {
        if (*pPropertyCount < pDesc->featureStructTypeCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->featureStructTypeCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pFeatureStructTypes[i];
        }
    }
    return result;
}

VPAPI_ATTR void vpGetProfileProperties(const VpProfileProperties *pProfile, void *pNext) {
    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc != nullptr && pDesc->property.pfnFiller != nullptr) {
        VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(pNext);
        while (p != nullptr) {
            pDesc->property.pfnFiller(p);
            p = p->pNext;
        }
    }
}

VPAPI_ATTR VkResult vpGetProfilePropertyStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                       VkStructureType *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->propertyStructTypeCount;
    } else {
        if (*pPropertyCount < pDesc->propertyStructTypeCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->propertyStructTypeCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pPropertyStructTypes[i];
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileQueueFamilyProperties(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                      VkQueueFamilyProperties2KHR *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->queueFamilyCount;
    } else {
        if (*pPropertyCount < pDesc->queueFamilyCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->queueFamilyCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(static_cast<void*>(&pProperties[i]));
            while (p != nullptr) {
                pDesc->pQueueFamilies[i].pfnFiller(p);
                p = p->pNext;
            }
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileQueueFamilyStructureTypes(const VpProfileProperties *pProfile, uint32_t *pPropertyCount,
                                                          VkStructureType *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->queueFamilyStructTypeCount;
    } else {
        if (*pPropertyCount < pDesc->queueFamilyStructTypeCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->queueFamilyStructTypeCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pQueueFamilyStructTypes[i];
        }
    }
    return result;
}

VPAPI_ATTR VkResult vpGetProfileFormats(const VpProfileProperties *pProfile, uint32_t *pFormatCount, VkFormat *pFormats) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pFormats == nullptr) {
        *pFormatCount = pDesc->formatCount;
    } else {
        if (*pFormatCount < pDesc->formatCount) {
            result = VK_INCOMPLETE;
        } else {
            *pFormatCount = pDesc->formatCount;
        }
        for (uint32_t i = 0; i < *pFormatCount; ++i) {
            pFormats[i] = pDesc->pFormats[i].format;
        }
    }
    return result;
}

VPAPI_ATTR void vpGetProfileFormatProperties(const VpProfileProperties *pProfile, VkFormat format, void *pNext) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return;

    for (uint32_t i = 0; i < pDesc->formatCount; ++i) {
        if (pDesc->pFormats[i].format == format) {
            VkBaseOutStructure* p = static_cast<VkBaseOutStructure*>(static_cast<void*>(pNext));
            while (p != nullptr) {
                pDesc->pFormats[i].pfnFiller(p);
                p = p->pNext;
            }
#if defined(VK_VERSION_1_3) || defined(VK_KHR_format_feature_flags2)
            VkFormatProperties2KHR* fp2 = static_cast<VkFormatProperties2KHR*>(
                detail::vpGetStructure(pNext, VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_2_KHR));
            VkFormatProperties3KHR* fp3 = static_cast<VkFormatProperties3KHR*>(
                detail::vpGetStructure(pNext, VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_3_KHR));
            if (fp3 != nullptr) {
                VkFormatProperties2KHR fp{ VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_2_KHR };
                pDesc->pFormats[i].pfnFiller(static_cast<VkBaseOutStructure*>(static_cast<void*>(&fp)));
                fp3->linearTilingFeatures = static_cast<VkFormatFeatureFlags2KHR>(fp3->linearTilingFeatures | fp.formatProperties.linearTilingFeatures);
                fp3->optimalTilingFeatures = static_cast<VkFormatFeatureFlags2KHR>(fp3->optimalTilingFeatures | fp.formatProperties.optimalTilingFeatures);
                fp3->bufferFeatures = static_cast<VkFormatFeatureFlags2KHR>(fp3->bufferFeatures | fp.formatProperties.bufferFeatures);
            }
            if (fp2 != nullptr) {
                VkFormatProperties3KHR fp{ VK_STRUCTURE_TYPE_FORMAT_PROPERTIES_3_KHR };
                pDesc->pFormats[i].pfnFiller(static_cast<VkBaseOutStructure*>(static_cast<void*>(&fp)));
                fp2->formatProperties.linearTilingFeatures = static_cast<VkFormatFeatureFlags>(fp2->formatProperties.linearTilingFeatures | fp.linearTilingFeatures);
                fp2->formatProperties.optimalTilingFeatures = static_cast<VkFormatFeatureFlags>(fp2->formatProperties.optimalTilingFeatures | fp.optimalTilingFeatures);
                fp2->formatProperties.bufferFeatures = static_cast<VkFormatFeatureFlags>(fp2->formatProperties.bufferFeatures | fp.bufferFeatures);
            }
#endif
        }
    }
}

VPAPI_ATTR VkResult vpGetProfileFormatStructureTypes(const VpProfileProperties *pProfile, VkFormat format, uint32_t *pPropertyCount,
                                                     VkStructureType *pProperties) {
    VkResult result = VK_SUCCESS;

    const detail::VpProfileDesc* pDesc = detail::vpGetProfileDesc(pProfile->profileName);
    if (pDesc == nullptr) return VK_ERROR_UNKNOWN;

    if (pProperties == nullptr) {
        *pPropertyCount = pDesc->formatStructTypeCount;
    } else {
        if (*pPropertyCount < pDesc->formatStructTypeCount) {
            result = VK_INCOMPLETE;
        } else {
            *pPropertyCount = pDesc->formatStructTypeCount;
        }
        for (uint32_t i = 0; i < *pPropertyCount; ++i) {
            pProperties[i] = pDesc->pFormatStructTypes[i];
        }
    }
    return result;
}
'''


class Log():
    def f(msg):
        print('FATAL: ' + msg)
        raise Exception(msg)

    def e(msg):
        print('ERROR: ' + msg)

    def w(msg):
        print('WARNING: ' + msg)

    def i(msg):
        print(msg)


class VulkanPlatform():
    def __init__(self, data):
        self.name = data.get('name')
        self.protect = data.get('protect')


class VulkanStructMember():
    def __init__(self, name, type, limittype, isArray = False):
        self.name = name
        self.type = type
        self.limittype = limittype
        self.isArray = isArray


class VulkanStruct():
    def __init__(self, name):
        self.name = name
        self.sType = None
        self.extends = []
        self.members = dict()
        self.aliases = [ name ]
        self.definedByVersion = None
        self.definedByExtensions = []


class VulkanDefinitionScope():
    def parseAliases(self, xml):
        self.sTypeAliases = dict()
        for sTypeAlias in xml.findall("./require/enum[@alias]"):
            if re.search(r'^VK_STRUCTURE_TYPE_.*', sTypeAlias.get('name')):
                self.sTypeAliases[sTypeAlias.get('alias')] = sTypeAlias.get('name')


class VulkanVersion(VulkanDefinitionScope):
    def __init__(self, xml):
        self.name = xml.get('name')
        self.number = xml.get('number')
        self.parseAliases(xml)


class VulkanExtension(VulkanDefinitionScope):
    def __init__(self, xml, upperCaseName):
        self.name = xml.get('name')
        self.upperCaseName = upperCaseName
        self.type = xml.get('type')
        self.platform = xml.get('platform')
        self.parseAliases(xml)


class VulkanRegistry():
    def __init__(self, registryFile):
        Log.i("Loading registry file: '{0}'".format(registryFile))
        xml = etree.parse(registryFile)
        self.parsePlatformInfo(xml)
        self.parseVersionInfo(xml)
        self.parseExtensionInfo(xml)
        self.parseStructInfo(xml)
        self.parsePrerequisites(xml)
        self.parseAliases(xml)
        self.applyWorkarounds()

    def parsePlatformInfo(self, xml):
        self.platforms = dict()
        for plat in xml.findall("./platforms/platform"):
            self.platforms[plat.get('name')] = VulkanPlatform(plat)


    def parseVersionInfo(self, xml):
        self.versions = dict()
        for feature in xml.findall('./feature'):
            if re.search(r"^[1-9][0-9]*\.[0-9]+$", feature.get('number')):
                self.versions[feature.get('number')] = VulkanVersion(feature)
            else:
                Log.f("Unsupported feature with number '{0}'", feature.get('number'))


    def parseExtensionInfo(self, xml):
        self.extensions = dict()
        for ext in xml.findall("./extensions/extension"):
            # Only care about enabled extensions
            if ext.get('supported') == "vulkan":
                name = ext.get('name')

                # Find name enum (due to inconsistencies in lower case and upper case names this is non-trivial)
                foundNameEnum = False
                matches = ext.findall("./require/enum[@value='\"" + name + "\"']")
                for match in matches:
                    if match.get('name').endswith("_EXTENSION_NAME"):
                        # Add extension definition
                        self.extensions[name] = VulkanExtension(ext, match.get('name')[:-len("_EXTENSION_NAME")])
                        foundNameEnum = True
                        break
                if not foundNameEnum:
                    Log.f("Cannot find name enum for extension '{0}'".format(name))


    def parseStructInfo(self, xml):
        self.structs = dict()
        for struct in xml.findall("./types/type[@category='struct']"):
            # Define base struct information
            structDef = VulkanStruct(struct.get('name'))

            # Find out whether it's an extension structure
            extends = struct.get('structextends')
            if extends != None:
                structDef.extends = extends.split(',')

            # Find sType value
            sType = struct.find("./member[name='sType']")
            if sType != None:
                structDef.sType = sType.get('values')

            # Parse struct members
            for member in struct.findall('./member'):
                name = member.find('./name').text
                tail = member.find('./name').tail
                type = member.find('./type').text

                # Only add real members (skip sType and pNext)
                if name != 'sType' and name != 'pNext':
                    # Define base member information
                    structDef.members[name] = VulkanStructMember(
                        name,
                        type,
                        member.get('limittype')
                    )

                    # Detect if it's an array
                    if tail != None and tail[0] == '[':
                        structDef.members[name].isArray = True

            # Store struct definition
            self.structs[struct.get('name')] = structDef


    def parsePrerequisites(self, xml):
        # Check features (i.e. API versions)
        for feature in xml.findall('./feature'):
            for requireType in feature.findall('./require/type'):
                # Add feature as the source of the definition of a struct
                if requireType.get('name') in self.structs:
                    self.structs[requireType.get('name')].definedByVersion = feature.get('number')

        # Check extensions
        for extension in xml.findall('./extensions/extension'):
            for requireType in extension.findall('./require/type'):
                # Add extension as the source of the definition of a struct
                if requireType.get('name') in self.structs:
                    self.structs[requireType.get('name')].definedByExtensions.append(extension.get('name'))


    def parseAliases(self, xml):
        # Find any struct aliases
        for struct in xml.findall("./types/type[@category='struct']"):
            alias = struct.get('alias')
            if alias != None:
                if alias in self.structs:
                    baseStructDef = self.structs[alias]
                    aliasStructDef = self.structs[struct.get('name')]

                    # Fill missing struct information for the alias
                    aliasStructDef.extends = baseStructDef.extends
                    aliasStructDef.members = baseStructDef.members
                    aliasStructDef.aliases = baseStructDef.aliases
                    aliasStructDef.aliases.append(struct.get('name'))

                    if baseStructDef.sType != None:
                        sTypeAlias = None

                        # First try to find sType alias in core versions
                        if aliasStructDef.definedByVersion != None:
                            for version in self.versions:
                                if version <= aliasStructDef.definedByVersion:
                                    sTypeAlias = self.versions[version].sTypeAliases.get(baseStructDef.sType)
                                    if sTypeAlias != None:
                                        break

                        # Otherwise need to find sType alias in extension
                        if sTypeAlias == None:
                            for extName in aliasStructDef.definedByExtensions:
                                sTypeAlias = self.extensions[extName].sTypeAliases.get(baseStructDef.sType)
                                if sTypeAlias != None:
                                    break

                        if sTypeAlias != None:
                            aliasStructDef.sType = sTypeAlias
                        else:
                            Log.f("Could not find sType enum of alias '{0}' of struct '{1}'".format(alias, struct.get('name')))
                else:
                    Log.f("Failed to find alias '{0}' of struct '{1}'".format(alias, struct.get('name')))


    def applyWorkarounds(self):
        # TODO: We currently have to apply workarounds due to "noauto" limittypes and other bugs related to limittypes in the vk.xml
        # These can only be solved permanently if we make modifications to the registry xml itself
        self.structs['VkPhysicalDeviceLimits'].members['bufferImageGranularity'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['subPixelPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['subTexelPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['mipmapPrecisionBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['viewportSubPixelBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['minMemoryMapAlignment'].limittype = 'max' # should be minalign
        self.structs['VkPhysicalDeviceLimits'].members['minTexelBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['minUniformBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['minStorageBufferOffsetAlignment'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['subPixelInterpolationOffsetBits'].limittype = 'max'
        self.structs['VkPhysicalDeviceLimits'].members['timestampPeriod'].limittype = 'IGNORE' # good question what this should be...
        self.structs['VkPhysicalDeviceLimits'].members['nonCoherentAtomSize'].limittype = 'min' # should be maxalign
        self.structs['VkPhysicalDeviceLimits'].members['maxColorAttachments'].limittype = 'max' # vk.xml declares this with 'bitmask' limittype for some reason
        self.structs['VkPhysicalDeviceLimits'].members['pointSizeGranularity'].limittype = 'min' # should be maxmul
        self.structs['VkPhysicalDeviceLimits'].members['lineWidthGranularity'].limittype = 'min' # should be maxmul
        self.structs['VkPhysicalDeviceVulkan11Properties'].members['subgroupSize'].limittype = 'IGNORE' # good question what this should be...
        self.structs['VkPhysicalDevicePortabilitySubsetPropertiesKHR'].members['minVertexInputBindingStrideAlignment'].limittype = 'min' # should be maxalign

        # TODO: There are also some bugs in the vk.xml, like parameters having "bitmask" limittype but actually VkBool32 type
        # This is non-sense, so we patch them
        for structName in self.structs:
            for memberName in self.structs[structName].members:
                memberDef = self.structs[structName].members[memberName]
                if memberDef.limittype == 'bitmask' and memberDef.type == 'VkBool32':
                    self.structs[structName].members[memberName].limittype = 'noauto'

        # TODO: The registry xml is also missing limittype definitions for format and queue family properties
        # For now we just add the important ones, this needs a larger overhaul in the vk.xml
        self.structs['VkFormatProperties'].members['linearTilingFeatures'].limittype = 'bitmask'
        self.structs['VkFormatProperties'].members['optimalTilingFeatures'].limittype = 'bitmask'
        self.structs['VkFormatProperties'].members['bufferFeatures'].limittype = 'bitmask'
        self.structs['VkFormatProperties3'].members['linearTilingFeatures'].limittype = 'bitmask'
        self.structs['VkFormatProperties3'].members['optimalTilingFeatures'].limittype = 'bitmask'
        self.structs['VkFormatProperties3'].members['bufferFeatures'].limittype = 'bitmask'
        self.structs['VkQueueFamilyProperties'].members['queueCount'].limittype = 'max'
        self.structs['VkQueueFamilyProperties'].members['timestampValidBits'].limittype = 'max'
        self.structs['VkQueueFamilyProperties'].members['minImageTransferGranularity'].limittype = 'min' # should be maxmul


    def getChainableStructDef(self, name, extends):
        structDef = self.structs.get(name)
        if structDef == None:
            Log.f("Structure '{0}' does not exist".format(name))
        if structDef.sType == None:
            Log.f("Structure '{0}' is not chainable".format(name))
        if not extends in structDef.extends + [ name ]:
            Log.f("Structure '{0}' does not extend '{1}'".format(name, extends))
        return structDef


class VulkanProfileCapabilities():
    def __init__(self, registry, data, caps):
        self.extensions = dict()
        self.instanceExtensions = dict()
        self.deviceExtensions = dict()
        self.features = dict()
        self.properties = dict()
        self.formats = dict()
        self.queueFamiliesProperties = []
        self.memoryProperties = dict()
        for capName in data['capabilities']:
            if capName in caps:
                self.mergeCaps(registry, caps[capName])
            else:
                Log.f("Capability '{0}' needed by profile '{1}' is missing".format(capName, data['name']))


    def mergeCaps(self, registry, caps):
        self.mergeProfileExtensions(registry, caps)
        self.mergeProfileFeatures(caps)
        self.mergeProfileProperties(caps)
        self.mergeProfileFormats(caps)
        self.mergeProfileQueueFamiliesProperties(caps)
        self.mergeProfileMemoryProperties(caps)


    def mergeProfileCapData(self, dst, src):
        if type(src) != type(dst):
            Log.f("Data type confict during profile capability data merge (src is '{0}', dst is '{1}')".format(type(src), type(dst)))
        elif type(src) == dict:
            for key, val in src.items():
                if type(val) == dict:
                    if not key in dst:
                        dst[key] = dict()
                    self.mergeProfileCapData(dst[key], val)

                elif type(val) == list:
                    if not key in dst:
                        dst[key] = []
                    dst[key].extend(val)

                else:
                    if key in dst and type(dst[key]) != type(val):
                        Log.f("Data type confict during profile capability data merge (src is '{0}', dst is '{1}')".format(type(val), type(dst[key])))
                    dst[key] = val
        else:
            Log.f("Unexpected data type during profile capability data merge (src is '{0}', dst is '{1}')".format(type(src), type(dst)))


    def mergeProfileExtensions(self, registry, data):
        if data.get('extensions') != None:
            for extName, specVer in data['extensions'].items():
                extInfo = registry.extensions.get(extName)
                if extInfo != None:
                    self.extensions[extName] = specVer
                    if extInfo.type == 'instance':
                        self.instanceExtensions[extName] = specVer
                    elif extInfo.type == 'device':
                        self.deviceExtensions[extName] = specVer
                    else:
                        Log.f("Extension '{0}' has invalid type '{1}'".format(extName, extInfo.type))
                else:
                    Log.f("Extension '{0}' does not exist".format(extName))


    def mergeProfileFeatures(self, data):
        if data.get('features') != None:
            self.mergeProfileCapData(self.features, data['features'])


    def mergeProfileProperties(self, data):
        if data.get('properties') != None:
            self.mergeProfileCapData(self.properties, data['properties'])


    def mergeProfileFormats(self, data):
        if data.get('formats') != None:
            self.mergeProfileCapData(self.formats, data['formats'])


    def mergeProfileQueueFamiliesProperties(self, data):
        if data.get('queueFamiliesProperties') != None:
            self.queueFamiliesProperties.extend(data['queueFamiliesProperties'])


    def mergeProfileMemoryProperties(self, data):
        if data.get('memoryProperties') != None:
            self.mergeProfileCapData(self.memoryProperties, data['memoryProperties'])


class VulkanProfileStructs():
    def __init__(self, registry, caps):
        # Feature struct types
        self.feature = []
        for name in caps.features:
            if name in 'VkPhysicalDeviceFeatures':
                # Special case, as it's wrapped in VkPhysicalDeviceFeatures2KHR
                self.feature.append(registry.structs['VkPhysicalDeviceFeatures2KHR'])
            else:
                self.feature.append(registry.getChainableStructDef(name, 'VkPhysicalDeviceFeatures2'))
        self.eliminateAliases(self.feature)

        # Property struct types
        self.property = []
        for name in caps.properties:
            if name == 'VkPhysicalDeviceProperties':
                # Special case, as it's wrapped in VkPhysicalDeviceProperties2KHR
                self.property.append(registry.structs['VkPhysicalDeviceProperties2KHR'])
            else:
                self.property.append(registry.getChainableStructDef(name, 'VkPhysicalDeviceProperties2'))
        self.eliminateAliases(self.property)

        # Queue family struct types
        self.queueFamily = []
        queueFamilyStructs = dict()
        for queueFamilyProps in caps.queueFamiliesProperties:
            queueFamilyStructs.update(queueFamilyProps)
        for name in queueFamilyStructs:
            if name == 'VkQueueFamilyProperties':
                # Special case, as it's wrapped in VkQueueFamilyProperties2KHR
                self.queueFamily.append(registry.structs['VkQueueFamilyProperties2KHR'])
            else:
                self.queueFamily.append(registry.getChainableStructDef(name, 'VkQueueFamilyProperties2'))
        self.eliminateAliases(self.queueFamily)

        # Format struct types
        self.format = []
        formatStructs = dict()
        for formatProps in caps.formats.values():
            formatStructs.update(formatProps)
        for name in formatStructs:
            if name == 'VkFormatProperties':
                # Special case, as it's wrapped in VkFormatProperties2KHR or VkFormatProperties3KHR
                self.format.append(registry.structs['VkFormatProperties2KHR'])
                self.format.append(registry.structs['VkFormatProperties3KHR'])
            else:
                self.format.append(registry.getChainableStructDef(name, 'VkFormatProperties2'))
        self.eliminateAliases(self.format)


    def eliminateAliases(self, structs):
        structNames = []
        duplicates = []
        # Collect duplicates
        for structDef in structs:
            if structDef.name in structNames:
                duplicates.append(structDef)
            structNames.append(structDef.aliases)
        # Remove duplicates
        for duplicate in duplicates:
            structs.remove(duplicate)


class VulkanProfile():
    def __init__(self, registry, name, data, caps):
        self.registry = registry
        self.name = name
        self.version = data['version']
        self.apiVersion = data['api-version']
        self.fallback = data.get('fallback')
        self.versionRequirements = []
        self.extensionRequirements = []
        self.capabilities = VulkanProfileCapabilities(registry, data, caps)
        self.structs = VulkanProfileStructs(registry, self.capabilities)
        self.collectCompileTimeRequirements()
        self.validate()


    def collectCompileTimeRequirements(self):
        # Add API version to the list of requirements
        match = re.search(r"^([1-9][0-9]*\.[0-9]+)[^0-9].*$", self.apiVersion)
        if match != None:
            versionNumber = match.group(1)
            if versionNumber in self.registry.versions:
                self.versionRequirements.append(self.registry.versions[versionNumber].name)
            else:
                Log.f("No version '{0}' found in registry required by profile '{1}'".format(versionNumber, self.name))
        else:
            Log.f("Invalid version number '{0}' in profile '{1}'".format(self.apiVersion, self.name))

        # Add any required extension to the list of requirements
        for extName in self.capabilities.extensions:
            if extName in self.registry.extensions:
                self.extensionRequirements.append(extName)
            else:
                Log.f("Extension '{0}' required by profile '{1}' does not exist".format(extName, self.name))


    def validate(self):
        self.validateStructDependencies()


    def validateStructDependencies(self):
        for feature in self.capabilities.features:
            self.validateStructDependency(feature)

        for prop in self.capabilities.properties:
            self.validateStructDependency(prop)

        for queueFamilyData in self.capabilities.queueFamiliesProperties:
            for queueFamilyProp in queueFamilyData:
                self.validateStructDependency(queueFamilyProp)

        for memoryProp in self.capabilities.memoryProperties:
            self.validateStructDependency(memoryProp)


    def validateStructDependency(self, structName):
        if structName in self.registry.structs:
            structDef = self.registry.structs[structName]
            depFound = False

            # Check if the required API version defines this struct
            if structDef.definedByVersion != None and structDef.definedByVersion <= self.apiVersion:
                depFound = True

            # Check if any required extension defines this struct
            for definedByExtension in structDef.definedByExtensions:
                if definedByExtension in self.capabilities.extensions:
                    depFound = True
                    break

            if not depFound:
                Log.f("Unexpected required struct '{0}' in profile '{1}'".format(structName, self.name))
        else:
            Log.f("Struct '{0}' in profile '{1}' does not exist in the registry".format(structName, self.name))


    def generatePrivateImpl(self):
        uname = self.name.upper()
        gen = '\n'
        gen += ('#ifdef {0}\n'
                'namespace {1} {{\n').format(self.name, uname)
        gen += self.gen_extensionData('instance')
        gen += self.gen_extensionData('device')
        gen += self.gen_fallbackData()
        gen += self.gen_structTypeData()
        gen += self.gen_structDesc()
        gen += ('\n'
                '}} // namespace {0}\n'
                '#endif\n').format(uname)
        return gen

    def gen_extensionData(self, type):
        foundExt = False
        gen = '\n'
        gen += 'static const VkExtensionProperties {0}Extensions[] = {{\n'.format(type)
        for extName, specVer in sorted(self.capabilities.extensions.items()):
            extInfo = self.registry.extensions[extName]
            if extInfo.type == type:
                gen += '    VkExtensionProperties{{ {0}_EXTENSION_NAME, {1} }},\n'.format(extInfo.upperCaseName, specVer)
                foundExt = True
        gen += '};\n'
        return gen if foundExt else ''


    def gen_fallbackData(self):
        gen = ''
        if self.fallback:
            gen += ('\n'
                    'static const VpProfileProperties fallbacks[] = {\n')
            for fallback in self.fallback:
                gen += '    {{ {0}_NAME, {0}_SPEC_VERSION }},\n'.format(fallback.upper())
            gen += '};\n'
        return gen


    def gen_structTypeData(self, structDefs = None, name = None):
        gen = ''
        if structDefs == None:
            gen += self.gen_structTypeData(self.structs.feature, 'feature')
            gen += self.gen_structTypeData(self.structs.property, 'property')
            gen += self.gen_structTypeData(self.structs.queueFamily, 'queueFamily')
            gen += self.gen_structTypeData(self.structs.format, 'format')
        else:
            if structDefs:
                gen += ('\n'
                        'static const VkStructureType {0}StructTypes[] = {{\n').format(name)
                for structDef in structDefs:
                    gen += '    {{ {0} }},\n'.format(structDef.sType)
                gen += '};\n'
        return gen


    def gen_listValue(self, values, isEnum = True):
        gen = ''
        if isEnum:
            gen += '('
        else:
            gen += '{ '

        separator = ''
        if values != None and len(values) > 0:
            for value in values:
                gen += separator + str(value)
                if isEnum:
                    separator = ' | '
                else:
                    separator = ', '
        elif isEnum:
            gen += '0'

        if isEnum:
            gen += ')'
        else:
            gen += ' }'
        return gen


    def gen_structFill(self, fmt, structDef, var, values):
        gen = ''
        for member, value in sorted(values.items()):
            if member in structDef.members:
                if type(value) == dict:
                    # Nested structure
                    memberDef = self.registry.structs.get(structDef.members[member].type)
                    if memberDef != None:
                        gen += self.gen_structFill(fmt, memberDef, var + member + '.', value)
                    else:
                        Log.f("Member '{0}' in structure '{1}' is not a struct".format(member, structDef.name))

                elif type(value) == list:
                    # Some sort of list (enums or integer/float list for structure initialization)
                    if len(value) == 0:
                        # If list is empty then ignore
                        continue
                    if structDef.members[member].isArray:
                        # If it's an array we have to generate per-element assignment code
                        for i, v in enumerate(value):
                            gen += fmt.format('{0}{1}[{2}] = {3}'.format(var, member, i, v))
                    else:
                        # For enums and struct initialization, most of the code can be shared
                        isEnum = isinstance(value[0], str)
                        if isEnum:
                            # For enums we only add bits
                            genAssign = '{0}{1} |= '.format(var, member)
                        else:
                            genAssign = '{0}{1} = '.format(var, member)
                        genAssign += '{0}'.format(self.gen_listValue(value, isEnum))
                        gen += fmt.format(genAssign)

                elif type(value) == bool:
                    # Boolean
                    gen += fmt.format('{0}{1} = {2}'.format(var, member, 'VK_TRUE' if value else 'VK_FALSE'))

                else:
                    # Everything else
                    gen += fmt.format('{0}{1} = {2}'.format(var, member, value))
            else:
                Log.f("No member '{0}' in structure '{1}'".format(member, structDef.name))
        return gen


    def gen_structCompare(self, fmt, structDef, var, values, parentLimittype = None):
        gen = ''
        for member, value in sorted(values.items()):
            if member in structDef.members:
                limittype = structDef.members[member].limittype
                if limittype == None:
                    # Use parent's limit type
                    limittype = parentLimittype
                if limittype == 'IGNORE':
                    # Skip this member as we don't know how to validate it
                    continue
                if limittype == 'bitmask':
                    # Compare bitmask by checking if device value contains every bit of profile value
                    comparePredFmt = '(({0} & {1}) == {1})'
                elif limittype == 'max':
                    # Compare max limit by checking if device value is greater than or equal to profile value
                    comparePredFmt = '({0} >= {1})'
                elif limittype == 'min':
                    # Compare min limit by checking if device value is less than or equal to profile value
                    comparePredFmt = '({0} <= {1})'
                elif limittype == 'range':
                    # Compare range limit by checking if device range is larger than or equal to profile range
                    comparePredFmt = [ '({0} <= {1})', '({0} >= {1})' ]
                elif limittype is None or limittype == 'noauto' or limittype == 'struct':
                    # Compare everything else with equality
                    comparePredFmt = '({0} == {1})'
                else:
                    Log.f("Unsupported limittype '{0}' in member '{1}' of structure '{2}'".format(limittype, member, structDef.name))

                if type(value) == dict:
                    # Nested structure
                    memberDef = self.registry.structs.get(structDef.members[member].type)
                    if memberDef != None:
                        gen += self.gen_structCompare(fmt, memberDef, var + member + '.', value, limittype)
                    else:
                        Log.f("Member '{0}' in structure '{1}' is not a struct".format(member, structDef.name))

                elif type(value) == list:
                    # Some sort of list (enums or integer/float list for structure initialization)
                    if len(value) == 0:
                        # If list is empty then ignore
                        continue
                    if structDef.members[member].isArray:
                        # If it's an array we have to generate per-element comparison code
                        for i in range(len(value)):
                            if limittype == 'range':
                                gen += fmt.format(comparePredFmt[i].format('{0}{1}[{2}]'.format(var, member, i), value[i]))
                            else:
                                gen += fmt.format(comparePredFmt.format('{0}{1}[{2}]'.format(var, member, i), value[i]))
                    else:
                        # Enum flags and basic structs can be compared directly
                        isEnum = isinstance(value[0], str)
                        gen += fmt.format(comparePredFmt.format('{0}{1}'.format(var, member), self.gen_listValue(value, isEnum)))

                elif type(value) == bool:
                    # Boolean
                    gen += fmt.format(comparePredFmt.format('{0}{1}'.format(var, member), 'VK_TRUE' if value else 'VK_FALSE'))

                else:
                    # Everything else
                    gen += fmt.format(comparePredFmt.format('{0}{1}'.format(var, member), value))
            else:
                Log.f("No member '{0}' in structure '{1}'".format(member, structDef.name))
        return gen


    def gen_structFunc(self, structDefs, caps, func, fmt):
        gen = ''

        hasData = False

        gen += ('            switch (p->sType) {\n')

        for structDef in structDefs:
            paramList = []

            # Fill VkPhysicalDeviceFeatures into VkPhysicalDeviceFeatures2[KHR]
            if structDef.name in ['VkPhysicalDeviceFeatures2', 'VkPhysicalDeviceFeatures2KHR']:
                innerCap = caps.get('VkPhysicalDeviceFeatures')
                if innerCap:
                    paramList.append((self.registry.structs['VkPhysicalDeviceFeatures'], 's->features.', innerCap))

            # Fill VkPhysicalDeviceProperties into VkPhysicalDeviceProperties2[KHR]
            if structDef.name in ['VkPhysicalDeviceProperties2', 'VkPhysicalDeviceProperties2KHR']:
                innerCap = caps.get('VkPhysicalDeviceProperties')
                if innerCap:
                    paramList.append((self.registry.structs['VkPhysicalDeviceProperties'], 's->properties.', innerCap))

            # Fill VkQueueFamilyProperties into VkQueueFamilyProperties2[KHR]
            if structDef.name in ['VkQueueFamilyProperties2', 'VkQueueFamilyProperties2KHR']:
                innerCap = caps.get('VkQueueFamilyProperties')
                if innerCap:
                    paramList.append((self.registry.structs['VkQueueFamilyProperties'], 's->queueFamilyProperties.', innerCap))

            # Fill VkFormatProperties into VkFormatProperties2[KHR]
            if structDef.name in ['VkFormatProperties2', 'VkFormatProperties2KHR']:
                innerCap = caps.get('VkFormatProperties')
                if innerCap:
                    paramList.append((self.registry.structs['VkFormatProperties'], 's->formatProperties.', innerCap))

            # Fill all other structures directly
            if structDef.name in caps:
                paramList.append((structDef, 's->', caps[structDef.name]))

            if paramList:
                gen += '                case {0}: {{\n'.format(structDef.sType)
                gen += '                    {0}* s = static_cast<{0}*>(static_cast<void*>(p));\n'.format(structDef.name)
                for params in paramList:
                    genAssign = func('                    ' + fmt, params[0], params[1], params[2])
                    if genAssign != '':
                        hasData = True
                        gen += genAssign
                gen += '                } break;\n'

        gen += ('                default: break;\n'
                '            }\n')
        return gen if hasData else ''


    def gen_structChainerFunc(self, structDefs, baseStruct):
        gen = '    [](VkBaseOutStructure* p, void* pUser, PFN_vpStructChainerCb pfnCb) {\n'
        if structDefs:
            pNext = 'nullptr'
            for structDef in structDefs:
                if structDef.name != baseStruct:
                    varName = structDef.name[2].lower() + structDef.name[3:]
                    gen += '        {0} {1}{{ {2}, {3} }};\n'.format(structDef.name, varName, structDef.sType, pNext)
                    pNext = '&' + varName
            gen += '        p->pNext = static_cast<VkBaseOutStructure*>(static_cast<void*>({0}));\n'.format(pNext)

        gen += ('        pfnCb(p, pUser);\n'
                '    },\n')
        return gen



    def gen_structDesc(self):
        gen = ''

        fillFmt = '{0};\n'
        cmpFmt = 'ret = ret && {0};\n'

        # Feature descriptor
        gen += ('\n'
                'static const VpFeatureDesc featureDesc = {\n'
                '    [](VkBaseOutStructure* p) {\n')
        gen += self.gen_structFunc(self.structs.feature, self.capabilities.features, self.gen_structFill, fillFmt)
        gen += ('    },\n'
                '    [](VkBaseOutStructure* p) -> bool {\n'
                '        bool ret = true;\n')
        gen += self.gen_structFunc(self.structs.feature, self.capabilities.features, self.gen_structCompare, cmpFmt)
        gen += ('        return ret;\n'
                '    }\n'
                '};\n')

        # Property descriptor
        gen += ('\n'
                'static const VpPropertyDesc propertyDesc = {\n'
                '    [](VkBaseOutStructure* p) {\n')
        gen += self.gen_structFunc(self.structs.property, self.capabilities.properties, self.gen_structFill, fillFmt)
        gen += ('    },\n'
                '    [](VkBaseOutStructure* p) -> bool {\n'
                '        bool ret = true;\n')
        gen += self.gen_structFunc(self.structs.property, self.capabilities.properties, self.gen_structCompare, cmpFmt)
        gen += ('        return ret;\n'
                '    }\n'
                '};\n')

        # Queue family descriptor
        if self.structs.queueFamily:
            gen += ('\n'
                    'static const VpQueueFamilyDesc queueFamilyDesc[] = {\n')
            for queueFamilyCaps in self.capabilities.queueFamiliesProperties:
                gen += ('    {\n'
                        '        [](VkBaseOutStructure* p) {\n')
                gen += self.gen_structFunc(self.structs.queueFamily, queueFamilyCaps, self.gen_structFill, fillFmt)
                gen += ('        },\n'
                        '        [](VkBaseOutStructure* p) -> bool {\n'
                        '            bool ret = true;\n')
                gen += self.gen_structFunc(self.structs.queueFamily, queueFamilyCaps, self.gen_structCompare, cmpFmt)
                gen += ('            return ret;\n'
                        '        }\n'
                        '    },\n')
            gen += ('};\n')

        # Format descriptor
        if self.structs.format:
            gen += ('\n'
                    'static const VpFormatDesc formatDesc[] = {\n')
            for formatName, formatCaps in sorted(self.capabilities.formats.items()):
                gen += ('    {{\n'
                        '        {0},\n'
                        '        [](VkBaseOutStructure* p) {{\n').format(formatName)
                gen += self.gen_structFunc(self.structs.format, formatCaps, self.gen_structFill, fillFmt)
                gen += ('        },\n'
                        '        [](VkBaseOutStructure* p) -> bool {\n'
                        '            bool ret = true;\n')
                gen += self.gen_structFunc(self.structs.format, formatCaps, self.gen_structCompare, cmpFmt)
                gen += ('            return ret;\n'
                        '        }\n'
                        '    },\n')
            gen += '};\n'

        # Structure chaining descriptors
        gen += ('\n'
                'static const VpStructChainerDesc chainerDesc = {\n')
        gen += self.gen_structChainerFunc(self.structs.feature, 'VkPhysicalDeviceFeatures2KHR')
        gen += self.gen_structChainerFunc(self.structs.property, 'VkPhysicalDeviceProperties2KHR')
        gen += self.gen_structChainerFunc(self.structs.queueFamily, 'VkQueueFamilyProperties2KHR')
        gen += self.gen_structChainerFunc(self.structs.format, 'VkFormatProperties2KHR')
        gen += '};\n'

        return gen


class VulkanProfiles():
    def loadFromDir(registry, profilesDir):
        profiles = dict()
        dirAbsPath = os.path.abspath(profilesDir)
        filenames = os.listdir(dirAbsPath)
        for filename in filenames:
            fileAbsPath = os.path.join(dirAbsPath, filename)
            if os.path.isfile(fileAbsPath) and os.path.splitext(filename)[-1] == '.json':
                Log.i("Loading profile file: '{0}'".format(filename))
                with open(fileAbsPath, 'r') as f:
                    jsonData = json.load(f)
                    VulkanProfiles.parseProfiles(registry, profiles, jsonData['profiles'], jsonData['capabilities'])
        return profiles


    def parseProfiles(registry, profiles, json, caps):
        for name, data in json.items():
            Log.i("Registering profile '{0}'".format(name))
            profiles[name] = VulkanProfile(registry, name, data, caps)


class VulkanProfilesBuilder():
    def __init__(self, registry, profiles):
        self.registry = registry
        self.profiles = profiles


    def generate(self, outIncDir, outSrcDir):
        self.generate_h(outIncDir)
        self.generate_cpp(outSrcDir)
        self.generate_hpp(outIncDir)


    def generate_h(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.h')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(H_HEADER)
            f.write(self.gen_profileDefs())
            f.write(API_DEFS)
            f.write(H_FOOTER)


    def generate_cpp(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.cpp')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(CPP_HEADER)
            f.write(self.gen_privateImpl())
            f.write(self.gen_publicImpl())


    def generate_hpp(self, outDir):
        fileAbsPath = os.path.join(os.path.abspath(outDir), 'vulkan_profiles.hpp')
        Log.i("Generating '{0}'...".format(fileAbsPath))
        with open(fileAbsPath, 'w') as f:
            f.write(COPYRIGHT_HEADER)
            f.write(HPP_HEADER)
            f.write(self.gen_profileDefs())
            f.write(API_DEFS)
            f.write(self.gen_privateImpl())
            f.write(self.gen_publicImpl())
            f.write(HPP_FOOTER)


    def gen_profileDefs(self):
        gen = ''
        for name, profile in sorted(self.profiles.items()):
            uname = name.upper()
            gen += '\n'

            # Add prerequisites
            allRequirements = sorted(profile.versionRequirements) + sorted(profile.extensionRequirements)
            if allRequirements:
                for i, requirement in enumerate(allRequirements):
                    if i == 0:
                        gen += '#if '
                    else:
                        gen += '    '

                    gen += 'defined({0})'.format(requirement)

                    if i < len(allRequirements) - 1:
                        gen += ' && \\\n'
                    else:
                        gen += '\n'

            gen += '#define {0} 1\n'.format(name)
            gen += '#define {0}_NAME "{1}"\n'.format(uname, name)
            gen += '#define {0}_SPEC_VERSION {1}\n'.format(uname, profile.version)
            gen += '#define {0}_MIN_API_VERSION VK_MAKE_VERSION({1})\n'.format(uname, profile.apiVersion.replace(".", ", "))

            if allRequirements:
                gen += '#endif\n'

        return gen


    def gen_privateImpl(self):
        gen = '\n'
        gen += 'namespace detail {\n\n'
        gen += PRIVATE_DEFS
        gen += self.gen_profilePrivateImpl()
        gen += self.gen_profileDescTable()
        gen += PRIVATE_IMPL_BODY
        gen += '\n} // namespace detail\n'
        return gen


    def gen_profilePrivateImpl(self):
        gen = ''
        for _, profile in sorted(self.profiles.items()):
            gen += profile.generatePrivateImpl()
        return gen


    def gen_dataArrayInfo(self, condition, name):
        if condition:
            return '        &{0}[0], static_cast<uint32_t>(sizeof({0}) / sizeof({0}[0])),\n'.format(name)
        else:
            return '        nullptr, 0,\n'


    def gen_profileDescTable(self):
        gen = '\n'
        gen += 'static const VpProfileDesc vpProfiles[] = {\n'

        for name, profile in sorted(self.profiles.items()):
            uname = name.upper()
            gen += ('#ifdef {0}\n'
                    '    VpProfileDesc{{\n'
                    '        VpProfileProperties{{ {1}_NAME, {1}_SPEC_VERSION }},\n'
                    '        {1}_MIN_API_VERSION,\n').format(name, uname)

            gen += self.gen_dataArrayInfo(profile.capabilities.instanceExtensions, '{0}::instanceExtensions'.format(uname))
            gen += self.gen_dataArrayInfo(profile.capabilities.deviceExtensions, '{0}::deviceExtensions'.format(uname))
            gen += self.gen_dataArrayInfo(profile.fallback, '{0}::fallbacks'.format(uname))
            gen += self.gen_dataArrayInfo(profile.structs.feature, '{0}::featureStructTypes'.format(uname))
            gen += '        {0}::featureDesc,\n'.format(uname)
            gen += self.gen_dataArrayInfo(profile.structs.property, '{0}::propertyStructTypes'.format(uname))
            gen += '        {0}::propertyDesc,\n'.format(uname)
            gen += self.gen_dataArrayInfo(profile.structs.queueFamily, '{0}::queueFamilyStructTypes'.format(uname))
            gen += self.gen_dataArrayInfo(profile.structs.queueFamily, '{0}::queueFamilyDesc'.format(uname))
            gen += self.gen_dataArrayInfo(profile.structs.format, '{0}::formatStructTypes'.format(uname))
            gen += self.gen_dataArrayInfo(profile.structs.format, '{0}::formatDesc'.format(uname))
            gen += '        {0}::chainerDesc,\n'.format(uname)

            gen += ('    },\n'
                    '#endif\n')

        gen += ('};\n'
                'static const uint32_t vpProfileCount = static_cast<uint32_t>(sizeof(vpProfiles) / sizeof(vpProfiles[0]));\n')
        return gen


    def gen_publicImpl(self):
        gen = PUBLIC_IMPL_BODY
        return gen


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-registry', action='store', required=True,
                        help='Use specified registry file instead of vk.xml')
    parser.add_argument('-profiles', action='store', required=True,
                        help='Generate based on profiles in the specified directory')
    parser.add_argument('-outIncDir', action='store', required=True,
                        help='Output include directory')
    parser.add_argument('-outSrcDir', action='store', required=True,
                        help='Output source directory')

    args = parser.parse_args()

    registry = VulkanRegistry(args.registry)
    profiles = VulkanProfiles.loadFromDir(registry, args.profiles)
    builder = VulkanProfilesBuilder(registry, profiles)
    builder.generate(args.outIncDir, args.outSrcDir)