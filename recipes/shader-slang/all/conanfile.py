from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"

class SlangConan(ConanFile):
    name = "slang"
    description = (
        "Slang is a shading language that makes it easier to build and maintain large shader codebases in a modular and"
        "extensible fashion, while also maintaining the highest possible performance on modern GPUs and graphics APIs. Slang"
        "is based on years of collaboration between researchers at NVIDIA, Carnegie Mellon University, Stanford, MIT, UCSD"
        "and the University of Washington."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/shader-slang/slang"
    topics = ("shaders", "hlsl", "glsl", "spirv", "vulkan", "d3d12", "cuda", "gpu")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "enable_slangd": [True, False],
        "enable_slangc": [True, False],
        "enable_slang_glslang": [True, False],
        "enable_slangrt": [True, False],
        "embed_core_module": [True, False],
    }
    default_options = {
        "enable_slangd": False,
        "enable_slangc": True,
        "enable_slang_glslang": True,
        "enable_slangrt": True,
        "embed_core_module": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.os == "Windows" and self.settings.arch not in ("x86_64", "armv8"):
            raise ConanInvalidConfiguration(
                f"{self.ref} only supports x86_64 and armv8 (aarch64) on Windows"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SLANG_ENABLE_TESTS"] = False
        tc.variables["SLANG_ENABLE_EXAMPLES"] = False
        tc.variables["SLANG_ENABLE_GFX"] = False
        tc.variables["SLANG_ENABLE_REPLAYER"] = False
        tc.variables["SLANG_ENABLE_SLANGD"] = self.options.enable_slangd
        tc.variables["SLANG_ENABLE_SLANGC"] = self.options.enable_slangc
        tc.variables["SLANG_ENABLE_SLANG_GLSLANG"] = self.options.enable_slang_glslang
        tc.variables["SLANG_ENABLE_SLANGRT"] = self.options.enable_slangrt
        tc.variables["SLANG_EMBED_CORE_MODULE"] = self.options.embed_core_module
        tc.variables["SLANG_EMBED_CORE_MODULE_SOURCE"] = not self.options.embed_core_module
        tc.variables["SLANG_LIB_TYPE"] = "SHARED"
        tc.variables["SLANG_ENABLE_CUDA"] = False
        tc.variables["SLANG_ENABLE_NVAPI"] = False
        tc.variables["SLANG_ENABLE_OPTIX"] = False
        tc.variables["SLANG_ENABLE_AFTERMATH"] = False
        tc.variables["SLANG_USE_SYSTEM_MINIZ"] = False
        tc.variables["SLANG_USE_SYSTEM_LZ4"] = False
        tc.variables["SLANG_USE_SYSTEM_VULKAN_HEADERS"] = False
        tc.variables["SLANG_USE_SYSTEM_SPIRV_HEADERS"] = False
        tc.variables["SLANG_USE_SYSTEM_SPIRV_TOOLS"] = False
        tc.variables["SLANG_USE_SYSTEM_GLSLANG"] = False
        tc.variables["SLANG_SLANG_LLVM_FLAVOR"] = "DISABLE"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
      
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "slang")
        self.cpp_info.set_property("cmake_target_name", "slang::slang")

        self.cpp_info.libs = ["slang-compiler"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]

        # slangc binary location
        if self.options.enable_slangc:
            slangc = "slangc.exe" if self.settings.os == "Windows" else "slangc"
            self.conf_info.define(
                "user.slang:slangc",
                os.path.join(self.package_folder, "bin", slangc),
            )
            self.buildenv_info.define_path(
                "SLANGC",
                os.path.join(self.package_folder, "bin", slangc),
            )
