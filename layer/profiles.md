<!-- markdownlint-disable MD041 -->
<p align="left"><img src="https://vulkan.lunarg.com/img/NewLunarGLogoBlack.png" alt="LunarG" width=263 height=113 /></p>
<p align="left">Copyright © 2015-2021 LunarG, Inc.</p>

[![Creative Commons][3]][4]

[3]: https://i.creativecommons.org/l/by-nd/4.0/88x31.png "Creative Commons License"
[4]: https://creativecommons.org/licenses/by-nd/4.0/

# VK\_LAYER\_LUNARG\_device\_simulation

## Overview

### Extend your Vulkan test coverage with the Khronos Profiles Layer
The Khronos Profiles Layer helps test across a wide range of hardware capabilities without requiring a physical copy of every device. It can be applied without modifying any application binaries, and in a fully automated fashion. The Profiles layer is a Vulkan layer that can override the values returned by your application’s queries of the GPU. Profiles layer uses a JSON text configuration file to make your application see a different driver/GPU than is actually in your system. This capability is useful to verify that your application both a) properly queries the limits from Vulkan, and b) obeys those limits.

The Profiles layer library is available pre-built in the Vulkan SDK, and continues to evolve. Profiles layer works for all Vulkan platforms (Linux, Windows, macOS, and Android), and is open-source software hosted on GitHub. The Profiles layer can be enabled and configured using the [Vulkan Configurator](https://vulkan.lunarg.com/doc/sdk/latest/windows/vkconfig.html) included with the Vulkan SDK.

The role of the Profiles layer is to "simulate" a less-capable Vulkan implementation by constraining the features and resources of a more-capable implementation. Note that the actual device in your machine should be more capable than that which you are simulating. Profiles layer does not add capabilities to your existing Vulkan implementation by "emulating" additional capabilities with software; e.g. Profiles layer cannot add geometry shader capability to an actual device that doesn’t already provide it. Also, Profiles layer does not "enforce" the features being simulated. For enforcement, you would continue to use the Validation Layers as usual, in conjunction with Profiles layer.

### Using Profiles layer
Profiles layer supports a flexible configuration file format using JSON syntax. The configuration file format is defined by a formal JSON schema available on the Khronos website, so any configuration file may be verified to be correct using freely available JSON validators. Browsing through the schema file, you can see the extent of parameters that are available for your configuration. As a convenience, Profiles layer supports loading multiple JSON files, so your configuration data can be split among separate files for modularity as desired.

### Android
To enable, use a setting with the path of configuration file to load:
```
adb shell settings put global debug.vulkan.profiles.filepath <path/to/profiles/JSON/configuration/file>
```
Example of a Profiles layer JSON configuration file: [tiny1.json](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/tiny1.json)

Optional: use settings to enable debugging output
```
adb shell settings put global debug.vulkan.profiles.debugenable 1
```

### How Profiles layer Works
Profiles layer builds its internal data tables by querying the capabilities of the underlying actual device, then applying each of the configuration files “on top of” those tables. Therefore you only need to specify the features you wish to modify from the actual device; tweaking a single feature is easy. Here’s an example of  a valid configuration file for changing only the maximum permitted viewport size:

```json
{
    "$schema": "https://schema.khronos.org/vulkan/profiles-1.3.201.json#",
    "capabilities": {
        "baseline": {
            "extensions": {},
            "features": {},
            "properties": {
                "VkPhysicalDeviceProperties": {
                    "limits": {
                        "maxViewportDimensions": [ 169, 170 ],
					}
				}
			},
            "formats": {},
            "queueFamiliesProperties": []
        }
    },
    "profiles": {
        "VP_LUNARG_test_structure_complex": {
            "version": 1,
            "api-version": "1.2.198",
            "label": "LunarG Profiles Structure Complex unit test",
            "description": "For schema unit test on C.I.",
            "contributors": {
                "Christophe Riccio": {
                    "company": "LunarG",
                    "email": "christophe@lunarg.com",
                    "github": "christophe-lunarg",
                    "contact": true
                }
            },
            "history": [
                {
                    "revision": 1,
                    "date": "2021-12-08",
                    "author": "Christophe Riccio",
                    "comment": "Initial revision"
                }
            ],
            "capabilities": [
                "baseline"
            ]
        }
    }
}
```

### Simulating Entire Real-World Devices
If you instead wish to simulate entire real-world devices, LunarG has collaborated with the [Vulkan Hardware Database](https://vulkan.gpuinfo.org/) to make their data compatible with the Profiles schema. You can download device configurations from the website in JSON format, and use those configuration files directly with Profiles layer.

# Technical Details

The Profiles Layer is a Vulkan layer that can modify the results of Vulkan PhysicalDevice queries based on a JSON configuration file, thus simulating some of the capabilities of device by overriding the capabilities of the actual device under test.

Please note that this device simulation layer "simulates", rather than "emulates", another device.
By that we mean that the layer cannot add emulated capabilities that do not already exist in the system's underlying actual device;
Profiles layer will not enable a less-capable device to emulate a more-capable device.
This layer enables a more-capable device to simulate a less-capable device by removing some of the capabilities reported by queries;
you can change or reduce what is already present in the underlying actual implementation.

Application code can be tested to verify it responds correctly to the capabilities reported by the simulated device.
That could include:
* Properly querying the capabilities of the device.
* Properly complying with the limits reported from the device.
* Verifying all necessary capabilities are reported present, rather than assuming they are available.
* Exercising fall-back code paths, if optional capabilities are not available.

The Profiles layer does not enforce the capabilities returned by queries.
The application is still responsible for querying and complying with the capabilities reported.
If an application erroneously attempts to overcommit a resource, or use a disabled feature, the Profiles layer will not generate errors.
To detect such errors, use the Vulkan Validation layers, as with any non-simulated device.

The Profiles layer will work with other Vulkan layers, such as Validation.
When configuring the order of the layers list, the Profiles layer should be "last";
i.e.: closest to the driver, farthest from the application.
That allows the Validation layer to see the results of the Profiles layer, and permit Validation to enforce the simulated capabilities.

Please report issues to [LunarG's VulkanTools GitHub repository](https://github.com/LunarG/VulkanTools/issues) and include "Profiles" in the title text.

### Layer name
`VK_LAYER_KHRONOS_profiles`

### Profiles Layer operation and configuration
At application startup, during vkCreateInstance(), the Profiles layer initializes its internal tables from the actual physical device in the system, then loads its configuration file, which specifies override values to apply to those internal tables.

How the JSON configuration values are applied depends on whether the top-level section begins with "ArrayOf" or not.
* If the section is not an array, values are applied if they appear in the JSON; if a value is not present in the JSON, the previous value is not modified.
Therefore not every parameter needs to be specified, only a sparse set of values that need to be changed.
* If the section defines an array (i.e.: begins with "ArrayOf"), then all previous contents of that array are cleared, and the JSON must specify all values of each desired array element.

JSON file formats consumed by the Profiles layer are specified by one of the JSON schemas in the table below.

| Schema Use | Canonical URI |
|:----------:|:-------------:|
| Vulkan v1.0 | https://schema.khronos.org/vulkan/devsim_1_0_0.json# |
| Vulkan v1.1 | https://schema.khronos.org/vulkan/devsim_1_1_0.json# |
| Vulkan v1.2 | https://schema.khronos.org/vulkan/devsim_1_2_0.json# |
| VK_KHR_portability_subset | https://schema.khronos.org/vulkan/devsim_VK_KHR_portability_subset-provisional-1.json# |
| VK_KHR_8bit_storage | https://schema.khronos.org/vulkan/devsim_VK_KHR_8bit_storage_1.json# |
| VK_KHR_16bit_storage | https://schema.khronos.org/vulkan/devsim_VK_KHR_16bit_storage_1.json# |
| VK_KHR_buffer_device_address | https://schema.khronos.org/vulkan/devsim_VK_KHR_buffer_device_address_1.json# |
| VK_KHR_depth_stencil_resolve | https://schema.khronos.org/vulkan/devsim_VK_KHR_depth_stencil_resolve_1.json# |
| VK_EXT_descriptor_indexing | https://schema.khronos.org/vulkan/devsim_VK_EXT_descriptor_indexing_1.json# |
| VK_EXT_host_query_reset | https://schema.khronos.org/vulkan/devsim_VK_EXT_host_query_reset_1.json# |
| VK_KHR_imageless_framebuffer | https://schema.khronos.org/vulkan/devsim_VK_KHR_imageless_framebuffer_1.json# |
| VK_KHR_maintenance2 | https://schema.khronos.org/vulkan/devsim_VK_KHR_maintenance2_1.json# |
| VK_KHR_maintenance3 | https://schema.khronos.org/vulkan/devsim_VK_KHR_maintenance3_1.json# |
| VK_KHR_multiview | https://schema.khronos.org/vulkan/devsim_VK_KHR_multiview_1.json# |
| VK_EXT_sampler_filter_minmax | https://schema.khronos.org/vulkan/devsim_VK_EXT_sampler_filter_minmax_1.json# |
| VK_KHR_sampler_ycbcr_conversion | https://schema.khronos.org/vulkan/devsim_VK_KHR_sampler_ycbcr_conversion_1.json# |
| VK_EXT_scalar_block_layout | https://schema.khronos.org/vulkan/devsim_VK_EXT_scalar_block_layout_1.json# |
| VK_KHR_separate_depth_stencil_layouts | https://schema.khronos.org/vulkan/devsim_VK_KHR_separate_depth_stencil_layouts_1.json# |
| VK_KHR_shader_atomic_int64 | https://schema.khronos.org/vulkan/devsim_VK_KHR_shader_atomic_int64_1.json# |
| VK_KHR_shader_float_controls | https://schema.khronos.org/vulkan/devsim_VK_KHR_shader_float_controls_1.json# |
| VK_KHR_shader_float16_int8 | https://schema.khronos.org/vulkan/devsim_VK_KHR_shader_float16_int8_1.json# |
| VK_KHR_shader_subgroup_extended_types | https://schema.khronos.org/vulkan/devsim_VK_KHR_shader_subgroup_extended_types_1.json# |
| VK_KHR_timeline_semaphore | https://schema.khronos.org/vulkan/devsim_VK_KHR_timeline_semaphore_1.json# |
| VK_KHR_uniform_buffer_standard_layout | https://schema.khronos.org/vulkan/devsim_VK_KHR_uniform_buffer_standard_layout_1.json# |
| VK_KHR_variable_pointers | https://schema.khronos.org/vulkan/devsim_VK_KHR_variable_pointers_1.json# |
| VK_KHR_vulkan_memory_model | https://schema.khronos.org/vulkan/devsim_VK_KHR_vulkan_memory_model_1.json# |

Usually you will be using configuration files validated with the Vulkan v1.2 schema.

The top-level sections of such configuration files are processed as follows:
* `$schema` - Mandatory.  Must be the URI string referencing the JSON schema.
* `comments` - Optional.  May contain arbitrary comments, description, copyright, etc.
* `VkPhysicalDeviceProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceDepthStencilResolveProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceDescriptorIndexingProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceFloatControlsProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceMaintenance3Properties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceMultiviewProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDevicePointClippingProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceProtectedMemoryProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceSamplerFilterMinmaxProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceTimelineSemaphoreProperties` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDevice16BitStorageFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDevice8BitStorageFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceDescriptorIndexingFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceHostQueryResetFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceImagelessFramebufferFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceMultiviewFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceProtectedMemoryFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceSamplerYcbcrConversionFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceScalarBlockLayoutFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceSeparateDepthStencilLayoutsFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceShaderAtomicInt64Features` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceShaderDrawParametersFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceShaderFloat16Int8Features` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceShaderSubgroupExtendedTypesFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceTimelineSemaphoreFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceUniformBufferStandardLayoutFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceVariablePointersFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceVulkanMemoryModelFeatures` - Optional.  Only values specified in the JSON will be modified.
* `VkPhysicalDeviceMemoryProperties` - Optional.  Only values specified in the JSON will be modified.
* `ArrayOfVkQueueFamilyProperties` - Optional.  If present, all values of all elements must be specified.
* `ArrayOfVkFormatProperties` - Optional.  If present, all values of all elements must be specified.
* `ArrayOfVkExtensionProperties` - Optional.  If present, all values of all elements must be specified. Modifies the list returned by `vkEnumerateDeviceExtensionProperties`.
* `Vulkan12Features` - Optional.  Only values specified in the JSON will be modified.
* `Vulkan12Properties` - Optional.  Only values specified in the JSON will be modified.
* The remaining top-level sections of the schema are not yet supported by Profiles layer.

The schema permits additional top-level sections to be optionally included in configuration files;
any additional top-level sections will be ignored by Profiles layer.

The schemas define basic range checking for common Vulkan data types, but they cannot detect whether a particular configuration makes no sense.
If a configuration defines capabilities beyond what the actual device is natively capable of providing, the results are undefined.
Profiles layer has some simple checking of configuration values and writes debug messages (if enabled) for values that are incompatible with the capabilities of the actual device.

This version of Profiles layer currently supports Vulkan v1.3 and below.
If the application requests an unsupported version of the Vulkan API, Profiles layer will emit an error message.

### Example of a Profiles JSON configuration file
```json
{
    "$schema": "https://schema.khronos.org/vulkan/profiles-1.3.201.json#",
    "capabilities": {
        "baseline": {
            "extensions": {},
            "features": {},
            "properties": {
                "VkPhysicalDeviceProperties": {
                    "limits": {
						"maxViewports": 1,
						"maxViewportDimensions": [1024, 1024]
					}
				}
			},
            "formats": {},
            "queueFamiliesProperties": []
        }
    },
    "profiles": {
        "VP_LUNARG_test_structure_complex": {
            "version": 1,
            "api-version": "1.2.198",
            "label": "LunarG Profiles Structure Complex unit test",
            "description": "For schema unit test on C.I.",
            "contributors": {
                "Christophe Riccio": {
                    "company": "LunarG",
                    "email": "christophe@lunarg.com",
                    "github": "christophe-lunarg",
                    "contact": true
                }
            },
            "history": [
                {
                    "revision": 1,
                    "date": "2021-12-08",
                    "author": "Christophe Riccio",
                    "comment": "Initial revision"
                }
            ],
            "capabilities": [
                "baseline"
            ]
        }
    }
}
```

#### Additional sample JSON configuration files

| Sample Name | Description | Link |
|:-----------:|:-----------:|:----:|
| iOS_gpu_family_3_portability.json | JSON configuration file describing iOS GPU family 3 portability features and properties. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/iOS_gpu_family_3_portability.json) |
| iOS_gpu_family_5_portability.json | JSON configuration file describing iOS GPU family 5 portability features and properties. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/iOS_gpu_family_5_portability.json) |
| macOS_gpu_family_1_portability.json | JSON configuration file describing macOS GPU family 1 portability features and properties. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/macOS_gpu_family_1_portability.json) |
| portability_minimum_vulkan_1_0.json | JSON configuration file for Vulkan 1.0 minimum requirements as defined by the Vulkan Specification. Values are modified to cover the Vulkan Portability Subset | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/portability_minimum_vulkan_1_0.json) |
| portability_minimum_vulkan_1_1.json | JSON configuration file for Vulkan 1.1 minimum requirements as defined by the Vulkan Specification. Values are modified to cover the Vulkan Portability Subset | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/portability_minimum_vulkan_1_1.json) |
| portability_minimum_vulkan_1_2.json | JSON configuration file for Vulkan 1.2 minimum requirements as defined by the Vulkan Specification. Values are modified to cover the Vulkan Portability Subset | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/portability_minimum_vulkan_1_2.json) |
| spec_minimum_vulkan_1_0.json | JSON configuration file for Vulkan 1.0 minimum requirements as defined by the Vulkan Specification. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/spec_minimum_vulkan_1_0.json) |
| spec_minimum_vulkan_1_1.json | JSON configuration file for Vulkan 1.1 minimum requirements as defined by the Vulkan Specification. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/spec_minimum_vulkan_1_1.json) |
| spec_minimum_vulkan_1_2.json | JSON configuration file for Vulkan 1.2 minimum requirements as defined by the Vulkan Specification. | [Link](https://github.com/LunarG/VulkanTools/blob/master/layersvt/device_simulation_examples/sdk_sample_configs/spec_minimum_vulkan_1_2.json) |

These and other sample files can be found in the [${VulkanTools}/layersvt/device_simulation_examples/sdk_sample_configs](https://github.com/LunarG/VulkanTools/tree/master/layersvt/device_simulation_examples/sdk_sample_configs) directory.

### `VK_KHR_portability_subset` Emulation

The DevSim layer provides the ability to emulate the `VK_KHR_portability_subset` extension on devices that do not implement this extension.
This feature allows users to test their application with limitations found on non-conformant Vulkan implementations.
To turn on this feature, set the `VK_KHRONOS_PROFILES_EMULATE_PORTABILITY_SUBSET_EXTENSION` environment variable (or the corresponding vk_layer_settings.txt option `khronos_profiles.emulate_portability`) to a positive integer.
DevSim config files that use this feature should validate to the portability specific schema https://schema.khronos.org/vulkan/devsim_VK_KHR_portability_subset-provisional-1.json#.

### DevSim Layer Options

#### Devsim JSON configuration file
- Environment Variable: `VK_KHRONOS_PROFILES_FILENAME`
- `vk_layer_settings.txt` Option: `khronos_profiles.filename`
- Android Option: `debug.vulkan.khronos_profiles.filename`
- Default Value: Not set

Name of one or more configuration file(s) to load. _Added in v1.2.1:_ This variable can have a delimited list of files to be loaded.
On Windows, the delimiter is `;` else it is `:`. Files are loaded in order.  Later files can override settings from earlier files.

#### Debug Enable
- Environment Variable: `VK_KHRONOS_PROFILES_DEBUG_ENABLE`
- `vk_layer_settings.txt` Option: `khronos_profiles.debug_enable`
- Android Option: `debug.vulkan.khronos_profiles.debug_enable`
- Default Value: false

Enables debug message output.

#### Emulate `VK_KHR_portability_subset`
- Environment Variable: `VK_KHRONOS_PROFILES_EMULATE_PORTABILITY`
- `vk_layer_settings.txt` Option: `khronos_profiles.emulate_portability`
- Android Option: `debug.vulkan.khronos_profiles.emulate_portability`
- Default Value: false

Enables emulation of the `VK_KHR_portability_subset` extension.

#### Modify Device Extension list
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_EXTENSION_LIST`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_extension_list`
- Android Option: `debug.vulkan.khronos_profiles.modify_extension_list`
- Default Value: none

 Enables modification of the device extensions list from the JSON config file. Valid options are "check_support", "from_profile", and "from_device".

#### Modify Device Memory Flags
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_MEMORY_FLAGS`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_memory_flags`
- Android Option: `debug.vulkan.khronos_profiles.modify_memory_flags`
- Default Value: false

Enables modification of the device memory heap flags and memory type flags from the JSON config file.

#### Modify Device Format list
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_FORMAT_LIST`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_format_list`
- Android Option: `debug.vulkan.khronos_profiles.modify_format_list`
- Default Value: none

Enables modification of the device format list from the JSON config file. Valid options are "check_support", "from_profile", and "from_device".

#### Modify Device Format Properties
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_FORMAT_PROPERTIES`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_format_properties`
- Android Option: `debug.vulkan.khronos_profiles.modify_format_properties`
- Default Value: none

Enables modification of the device format properties from the JSON config file. Valid options are "check_support", "from_profile", and "from_device".

#### Modify Device Surface Formats
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_SURFACE_FORMATS`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_surface_formats`
- Android Option: `debug.vulkan.khronos_profiles.modify_surface_formats`
- Default Value: none

Enables modification of the surface format list from the JSON config file. Valid options are "check_support", "from_profile", and "from_device".

#### Modify Device Present Modes
- Environment Variable: `VK_KHRONOS_PROFILES_MODIFY_PRESENT_MODES`
- `vk_layer_settings.txt` Option: `khronos_profiles.modify_present_modes`
- Android Option: `debug.vulkan.khronos_profiles.modify_present_modes`
- Default Value: none

Enables modification of the surface present mode list from the JSON config file. Valid options are "check_support", "from_profile", and "from_device".

**Note:** Environment variables take precedence over `vk_layer_settings.txt` options.

#### Array Combination Mode Options Descriptions

* check_support: Checks if the device supports the specified profile.
* from_profile: Fully replaces the device's properties list with the properties list provided by the profiles configuration file.
* from_device: Turns off modification of the device's properties list. Uses the device's real properties list.

### Example using the DevSim layer using Linux environment variables
```bash
# Configure bash to find the Vulkan SDK.
source $VKSDK/setup-env.sh

# Set loader parameters to find and load the Profiles layer from your local VulkanTools build.
export VK_LAYER_PATH="${VulkanTools}/build/layersvt"
export VK_INSTANCE_LAYERS="VK_LAYER_KHRONOS_profiles`"

# Specify the simulated device's configuration file.
export VK_KHRONOS_PROFILES_FILENAME="${VulkanTools}/layersvt/device_simulation_examples/tiny1.json"
# A list of files could look like:
# export VK_KHRONOS_PROFILES_FILENAME="/home/foo/first.json:/home/foo/second.json"

# Enable verbose messages from the Profiles layer.
export VK_KHRONOS_PROFILES_DEBUG_ENABLE="1"

# Run a Vulkan application through the Profiles layer.
vulkaninfo
# Compare the results with that app running without the Profiles layer.
```
See also
* [${VulkanTools}/tests/devsim_layer_test.sh](https://github.com/LunarG/VulkanTools/blob/master/tests/devsim_layer_test.sh) - a test runner script.
* [${VulkanTools}/tests/devsim_test1.json](https://github.com/LunarG/VulkanTools/blob/master/tests/devsim_test1_in.json) - an example configuration file, containing bogus test data.

### Device configuration data from vulkan.gpuinfo.org
A large and growing database of device capabilities is available at https://vulkan.gpuinfo.org/

That device data can be downloaded in JSON format, compatible with the Profiles JSON schema.

A JSON index of the available device records can be queried with https://vulkan.gpuinfo.org/api/v2/devsim/getreportlist.php

That index includes URLs to download the specific device records in DevSim-compatible format, for example https://vulkan.gpuinfo.org/api/v2/devsim/getreport.php?id=1456

As mentioned above, attempting to use a configuration file that does not fit within the capabilities of the underlying device may produce undefined results.
Downloaded device records should be reviewed to determine that their capabilities can be simulated by the underlying device.

### Device configuration data from the local system
Vulkan Info can write its output in a format compatible the Profiles JSON schema,
so the configuration of the local system can be captured.
Use `vulkaninfo -j` to generate output in JSON format and redirect to a file, which can be consumed directly by Profiles layer.
See the Vulkan Info documentation for further details.

### Device configuration data from an iOS device
Vulkan Info can be built and run for iOS using the source and XCode project available from the [Vulkan-Tools repository](https://github.com/KhronosGroup/Vulkan-Tools/tree/master/vulkaninfo). For details on running and extracting the json files see the [Vulkan Info documentation](https://vulkan.lunarg.com/doc/sdk/latest/mac/vulkaninfo.html). An [Apple Developer Program](https://developer.apple.com/programs/) membership is required to deploy Vulkan Info to an iOS hardware device.

### JSON validation
The Profiles layer itself does very little sanity-checking of the configuration file, so those files should be validated to the schema using a separate tool, such as the following web-based validators.
1. http://www.jsonschemavalidator.net/
2. https://json-schema-validator.herokuapp.com/
3. https://jsonschemalint.com/#/version/draft-04/markup/json/

### Other Resources
1. http://json.org/
2. http://json-schema.org/