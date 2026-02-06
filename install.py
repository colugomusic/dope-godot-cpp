from dope import *
from git import Repo
import argparse
import sys
import shutil
import os


def make_platform():
	if sys.platform == "win32":
		return "windows"
	elif sys.platform == "linux":
		return "linux"
	elif sys.platform == "darwin":
		return "osx"
	else:
		raise ValueError(f"Unsupported platform: {sys.platform}")

def run_scons(src_dir, platform, options, verbose):
	cmd  = f'scons'
	cmd += f' -C {src_dir}'
	cmd += f' platform={platform}'
	if sys.platform == "darwin":
		llvm_prefix = "/opt/homebrew/opt/llvm"
		libcxx_prefix = os.path.expanduser("~/llvm-libcxx")
		cmd += f' macos_deployment_target=10.15'
		cmd += f' CC="{llvm_prefix}/bin/clang"'
		cmd += f' CXX="{llvm_prefix}/bin/clang++"'
		# Use custom-built shared libc++ for deployment
		cmd += f' LINKFLAGS="-fuse-ld=lld -nostdlib++ -L{libcxx_prefix}/lib -lc++ -lc++abi -Wl,-rpath,@executable_path -Wl,-rpath,@loader_path"'
	cmd += f' {options}'
	cmd += f' -j 4'
	run(cmd, verbose)

def get_library_suffix():
	if sys.platform == "win32":
		return "lib"
	elif sys.platform == "linux":
		return "a"
	elif sys.platform == "darwin":
		return "a"

def cmake_configure(src_dir, build_dir, install_dir, target, arch, verbose):
	cmake_cmd = 'cmake'
	cmake_cmd += f' -B "{build_dir}"'
	cmake_cmd += f' -S "{src_dir}"'
	cmake_cmd += f' -DGODOTCPP_TARGET="{target}"'
	if arch:
		cmake_cmd += f' -DGODOTCPP_ARCH="{arch}"'
	cmake_cmd += f' -DCMAKE_PREFIX_PATH="{install_dir}"'
	cmake_cmd += f' -DCMAKE_INSTALL_PREFIX="{install_dir}"'
	run(cmake_cmd, verbose)

def cmake_install(build_dir, verbose):
	run(f'cmake --install {build_dir}', verbose)

def to_scons_target(config:str):
	if config == "Debug":
		return "debug"
	if config == "Release":
		return "release"
	if config == "RelWithDebInfo":
		return "release"

def load_settings(root_dir):
	settings_path = os.path.join(root_dir, "settings.yml")
	with open(settings_path, 'r') as f:
		return YAML().load(f)

def get_config_spec(settings, config_name):
	"""Look up config in platform-specific configs first, then fall back to generic configs."""
	if sys.platform == "darwin":
		platform_settings = settings.get("macos", {})
		platform_configs = platform_settings.get("configs", {})
		if config_name in platform_configs:
			return platform_configs[config_name]
	# Fall back to generic configs
	return settings.get("configs", {}).get(config_name, {})

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--root", type=str, required=True)
	parser.add_argument("--assets", type=str, required=True)
	parser.add_argument("--clean", action="store_true")
	parser.add_argument("--verbose", action="store_true")
	parser.add_argument('--config', action='append', help='Configuration to install')
	args = parser.parse_args()
	settings = load_settings(args.root)
	dep = Dependency(name="godot-cpp")
	src_dir = make_dep_src_dir(dep, args.root, cmake=False)
	repo = Repo(src_dir)
	repo.git.submodule('update', '--init', '--recursive')
	platform = make_platform()
	done_one_config = False
	for config in args.config:
		config_spec = get_config_spec(settings, config)
		config_type = config_spec.get("config", config)
		arch = config_spec.get("arch")
		install_dir = make_install_dir(args.root, config)
		lib_suffix = get_library_suffix()
		target = to_scons_target(config_type)
		build_lib = os.path.join(src_dir, "bin", f'libgodot-cpp.{platform}.{target}.64.{lib_suffix}')
		if not os.path.exists(build_lib):
			scons_args = f'target={target}'
			if sys.platform == "darwin" and arch:
				scons_args += f' macos_arch={arch}'
			if not done_one_config:
				scons_args = scons_args + ' generate_bindings=yes'
				done_one_config = True
			run_scons(src_dir, platform, scons_args, args.verbose)
		build_dir = make_dep_build_dir(dep, config, args.root)
		cmake_configure(src_dir, build_dir, install_dir, target, arch, args.verbose)
		cmake_install(build_dir, args.verbose)
