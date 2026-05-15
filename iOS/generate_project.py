#!/usr/bin/env python3
"""Generate a valid Xcode project.pbxproj for SingerBuddy iOS app."""

import uuid
import os

IOS_ROOT = "/Volumes/work/Stanford/SingerBuddy/iOS"
REPO_ROOT = os.path.dirname(IOS_ROOT)
# These become PBXFolderReference (blue folder) — preserves directory structure in bundle
WEB_RESOURCE_DIRS = ["scores", "scripts", "soundfonts"]
# These become individual PBXFileReference at bundle root
WEB_RESOURCE_FILES = ["index.html", "favicon.ico"]

def uid():
    return uuid.uuid4().hex.upper()

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

def detect_file_type(filename):
    if filename.endswith('.swift'):
        return "sourcecode.swift"
    if filename.endswith('.js'):
        return "sourcecode.javascript"
    if filename.endswith('.css'):
        return "text.css"
    if filename.endswith('.html'):
        return "text.html"
    if filename.endswith('.mei'):
        return "text.xml"
    if filename.endswith('.ico'):
        return "image.ico"
    if filename.endswith('.pat'):
        return "text"
    return "text"


def stable_key(path):
    return path.replace("/", "_").replace(".", "_").replace("-", "_")


# Only top-level individual files (not directory contents)
web_files = []
for filename in WEB_RESOURCE_FILES:
    full_path = os.path.join(REPO_ROOT, filename)
    if not os.path.exists(full_path):
        continue
    web_files.append((filename, detect_file_type(filename), filename))

# All UUIDs
ids = {}
for name in [
    "project", "main_group", "sb_group", "wr_group", "products_group",
    "app_swift", "content_swift", "webview_swift", "vm_swift",
    "info_plist", "assets",
    "app_target", "bundle_target",
    "app_product", "bundle_product", "bundle_product_path",
    "app_sources", "app_frameworks", "app_resources", "app_headers",
    "bundle_sources", "bundle_frameworks", "bundle_resources", "bundle_headers",
    "app_config_list", "bundle_config_list", "project_config_list",
    "project_debug", "project_release",
    "app_debug", "app_release", "bundle_debug", "bundle_release",
    "native_deps", "target_proxy",
    "swiftui_fw", "webkit_fw", "foundation_fw",
    "wr_swift",
]:
    ids[name] = uid()

# Per-file UUIDs for top-level root files only (index.html, favicon.ico)
web_refs = {}
web_bfs = {}
for name, ft, rel_path in web_files:
    key = stable_key(rel_path)
    web_refs[key] = uid()
    web_bfs[key] = uid()

# Per-directory UUIDs — PBXFolderReference (blue folder) preserves dir structure in bundle
dir_refs = {}
dir_bfs = {}
for dirname in WEB_RESOURCE_DIRS:
    dir_refs[dirname] = uid()
    dir_bfs[dirname] = uid()

# App source build files
app_bf = {}
for name, ref in [
    ("SingerBuddyApp.swift", ids["app_swift"]),
    ("ContentView.swift", ids["content_swift"]),
    ("WebView.swift", ids["webview_swift"]),
    ("WebViewViewModel.swift", ids["vm_swift"]),
]:
    app_bf[name] = uid()

# Framework build files
ids["swiftui_bf"] = uid()
ids["webkit_bf"] = uid()
ids["foundation_bf"] = uid()
ids["info_plist_bf"] = uid()
ids["assets_bf"] = uid()
ids["bundle_product_bf"] = uid()
ids["wr_swift_bf"] = uid()

lines = []
def w(s):
    lines.append(s)

# Header
w("// !$*UTF8*$!")
w("{")
w("\tarchiveVersion = 1;")
w("\tclasses = {};")
w("\tobjectVersion = 77;")
w("\tobjects = {")

# ===== PBXBuildFile =====
w(f"\t\t{app_bf['SingerBuddyApp.swift']} /* SingerBuddyApp.swift */ = {{isa = PBXBuildFile; fileRef = {ids['app_swift']};}};")
w(f"\t\t{app_bf['ContentView.swift']} /* ContentView.swift */ = {{isa = PBXBuildFile; fileRef = {ids['content_swift']};}};")
w(f"\t\t{app_bf['WebView.swift']} /* WebView.swift */ = {{isa = PBXBuildFile; fileRef = {ids['webview_swift']};}};")
w(f"\t\t{app_bf['WebViewViewModel.swift']} /* WebViewViewModel.swift */ = {{isa = PBXBuildFile; fileRef = {ids['vm_swift']};}};")
w(f"\t\t{ids['swiftui_bf']} /* SwiftUI.framework */ = {{isa = PBXBuildFile; fileRef = {ids['swiftui_fw']};}};")
w(f"\t\t{ids['webkit_bf']} /* WebKit.framework */ = {{isa = PBXBuildFile; fileRef = {ids['webkit_fw']};}};")
w(f"\t\t{ids['foundation_bf']} /* Foundation.framework */ = {{isa = PBXBuildFile; fileRef = {ids['foundation_fw']};}};")
w(f"\t\t{ids['info_plist_bf']} /* Info.plist */ = {{isa = PBXBuildFile; fileRef = {ids['info_plist']};}};")
w(f"\t\t{ids['assets_bf']} /* Assets.xcassets */ = {{isa = PBXBuildFile; fileRef = {ids['assets']};}};")
w(f"\t\t{ids['bundle_product_bf']} /* WebResources.bundle */ = {{isa = PBXBuildFile; fileRef = {ids['bundle_product']};}};")
w(f"\t\t{ids['wr_swift_bf']} /* WebResources.swift */ = {{isa = PBXBuildFile; fileRef = {ids['wr_swift']};}};")

for name, ft, rel_path in web_files:
    key = stable_key(rel_path)
    w(f"\t\t{web_bfs[key]} /* {name} */ = {{isa = PBXBuildFile; fileRef = {web_refs[key]};}};")

# Folder reference build files (one per directory — copies as tree into bundle)
for dirname in WEB_RESOURCE_DIRS:
    w(f"\t\t{dir_bfs[dirname]} /* {dirname} in Resources */ = {{isa = PBXBuildFile; fileRef = {dir_refs[dirname]};}};")

# ===== PBXFileReference =====
w(f"\t\t{ids['app_swift']} /* SingerBuddyApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = \"sourcecode.swift\"; name = \"SingerBuddyApp.swift\"; path = \"SingerBuddy/SingerBuddyApp.swift\"; sourceTree = \"SOURCE_ROOT\";}};")
w(f"\t\t{ids['content_swift']} /* ContentView.swift */ = {{isa = PBXFileReference; lastKnownFileType = \"sourcecode.swift\"; name = \"ContentView.swift\"; path = \"SingerBuddy/ContentView.swift\"; sourceTree = \"SOURCE_ROOT\";}};")
w(f"\t\t{ids['webview_swift']} /* WebView.swift */ = {{isa = PBXFileReference; lastKnownFileType = \"sourcecode.swift\"; name = \"WebView.swift\"; path = \"SingerBuddy/WebView.swift\"; sourceTree = \"SOURCE_ROOT\";}};")
w(f"\t\t{ids['vm_swift']} /* WebViewViewModel.swift */ = {{isa = PBXFileReference; lastKnownFileType = \"sourcecode.swift\"; name = \"WebViewViewModel.swift\"; path = \"SingerBuddy/WebViewViewModel.swift\"; sourceTree = \"SOURCE_ROOT\";}};")
w(f"\t\t{ids['assets']} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = \"folder.assetcatalog\"; name = \"Assets.xcassets\"; path = \"SingerBuddy/Assets.xcassets\"; sourceTree = \"SOURCE_ROOT\";}};")
w(f"\t\t{ids['info_plist']} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = \"text.plist.xml\"; name = \"Info.plist\"; path = \"SingerBuddy/Info.plist\"; sourceTree = \"SOURCE_ROOT\";}};")

w(f"\t\t{ids['swiftui_fw']} /* SwiftUI.framework */ = {{isa = PBXFileReference; lastKnownFileType = \"wrapper.framework\"; name = \"SwiftUI.framework\"; path = \"System/Library/Frameworks/SwiftUI.framework\"; sourceTree = \"SDKROOT\";}};")
w(f"\t\t{ids['webkit_fw']} /* WebKit.framework */ = {{isa = PBXFileReference; lastKnownFileType = \"wrapper.framework\"; name = \"WebKit.framework\"; path = \"System/Library/Frameworks/WebKit.framework\"; sourceTree = \"SDKROOT\";}};")
w(f"\t\t{ids['foundation_fw']} /* Foundation.framework */ = {{isa = PBXFileReference; lastKnownFileType = \"wrapper.framework\"; name = \"Foundation.framework\"; path = \"System/Library/Frameworks/Foundation.framework\"; sourceTree = \"SDKROOT\";}};")

w(f"\t\t{ids['app_product']} /* SingerBuddy */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; lastKnownFileType = \"wrapper.application\"; name = \"SingerBuddy\"; path = \"SingerBuddy.app\"; sourceTree = \"BUILT_PRODUCTS_DIR\";}};")
w(f"\t\t{ids['bundle_product']} /* WebResources.bundle */ = {{isa = PBXFileReference; explicitFileType = \"wrapper.plug-in\"; includeInIndex = 0; lastKnownFileType = \"wrapper.plug-in\"; name = \"WebResources.bundle\"; path = \"WebResources.bundle\"; sourceTree = \"BUILT_PRODUCTS_DIR\";}};")
w(f"\t\t{ids['bundle_product_path']} /* WebResources.bundle */ = {{isa = PBXFileReference; lastKnownFileType = \"wrapper.plug-in\"; name = \"WebResources.bundle\"; path = \"Products/WebResources.bundle\"; sourceTree = \"SOURCE_ROOT\";}};")

for name, ft, rel_path in web_files:
    key = stable_key(rel_path)
    # All web_files are root-level (no "/" in rel_path)
    w(
        f"\t\t{web_refs[key]} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = \"{ft}\"; name = \"{name}\"; path = \"../{rel_path}\"; sourceTree = \"SOURCE_ROOT\";}};"
    )

w(f"\t\t{ids['wr_swift']} /* WebResources.swift */ = {{isa = PBXFileReference; lastKnownFileType = \"sourcecode.swift\"; name = \"WebResources.swift\"; path = \"WebResources/WebResources.swift\"; sourceTree = \"SOURCE_ROOT\";}};")

# ===== PBXFileReference (blue folder refs — copy as directory trees into bundle) =====
for dirname in WEB_RESOURCE_DIRS:
    w(f"\t\t{dir_refs[dirname]} /* {dirname} */ = {{isa = PBXFileReference; lastKnownFileType = folder; name = \"{dirname}\"; path = \"../{dirname}\"; sourceTree = \"SOURCE_ROOT\";}};")

# ===== PBXFrameworksBuildPhase =====
w(f"\t\t{ids['app_frameworks']} /* Frameworks */ = {{")
w(f"\t\t\tisa = PBXFrameworksBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t\t{ids['swiftui_bf']},")
w(f"\t\t\t\t{ids['webkit_bf']},")
w(f"\t\t\t\t{ids['foundation_bf']},")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_frameworks']} /* Frameworks */ = {{")
w(f"\t\t\tisa = PBXFrameworksBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

# ===== PBXGroup =====
# WebResources group — contains top-level files + folder references + WebResources.swift
w(f"\t\t{ids['wr_group']} /* WebResources */ = {{")
w(f"\t\t\tisa = PBXGroup;")
w(f"\t\t\tchildren = (")
for name, ft, rel_path in web_files:
    key = stable_key(rel_path)
    w(f"\t\t\t\t{web_refs[key]},")
for dirname in WEB_RESOURCE_DIRS:
    w(f"\t\t\t\t{dir_refs[dirname]},")
w(f"\t\t\t\t{ids['wr_swift']},")
w(f"\t\t\t);")
w(f"\t\t\tname = \"WebResources\";")
w(f"\t\t\tsourceTree = \"SOURCE_ROOT\";")
w(f"\t\t}};")

# SingerBuddy group
w(f"\t\t{ids['sb_group']} /* SingerBuddy */ = {{")
w(f"\t\t\tisa = PBXGroup;")
w(f"\t\t\tchildren = (")
w(f"\t\t\t\t{ids['app_swift']},")
w(f"\t\t\t\t{ids['content_swift']},")
w(f"\t\t\t\t{ids['webview_swift']},")
w(f"\t\t\t\t{ids['vm_swift']},")
w(f"\t\t\t\t{ids['info_plist']},")
w(f"\t\t\t\t{ids['assets']},")
w(f"\t\t\t);")
w(f"\t\t\tpath = \"SingerBuddy\";")
w(f"\t\t\tsourceTree = \"SOURCE_ROOT\";")
w(f"\t\t}};")

# Products group
w(f"\t\t{ids['products_group']} /* Products */ = {{")
w(f"\t\t\tisa = PBXGroup;")
w(f"\t\t\tchildren = (")
w(f"\t\t\t\t{ids['app_product']},")
w(f"\t\t\t\t{ids['bundle_product_path']},")
w(f"\t\t\t);")
w(f"\t\t\tsourceTree = \"SOURCE_ROOT\";")
w(f"\t\t}};")

# Main group
w(f"\t\t{ids['main_group']} = {{")
w(f"\t\t\tisa = PBXGroup;")
w(f"\t\t\tchildren = (")
w(f"\t\t\t\t{ids['sb_group']},")
w(f"\t\t\t\t{ids['wr_group']},")
w(f"\t\t\t\t{ids['products_group']},")
w(f"\t\t\t);")
w(f"\t\t\tsourceTree = \"SOURCE_ROOT\";")
w(f"\t\t}};")

# ===== PBXHeadersBuildPhase =====
w(f"\t\t{ids['app_headers']} /* Headers */ = {{")
w(f"\t\t\tisa = PBXHeadersBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_headers']} /* Headers */ = {{")
w(f"\t\t\tisa = PBXHeadersBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

# ===== PBXNativeTarget =====
w(f"\t\t{ids['app_target']} /* SingerBuddy */ = {{")
w(f"\t\t\tisa = PBXNativeTarget;")
w(f"\t\t\tbuildConfigurationList = {ids['app_config_list']};")
w(f"\t\t\tbuildPhases = (")
w(f"\t\t\t\t{ids['app_sources']},")
w(f"\t\t\t\t{ids['app_frameworks']},")
w(f"\t\t\t\t{ids['app_resources']},")
w(f"\t\t\t);")
w(f"\t\t\tbuildRules = (")
w(f"\t\t\t);")
w(f"\t\t\tdependencies = (")
w(f"\t\t\t\t{ids['native_deps']},")
w(f"\t\t\t);")
w(f"\t\t\tname = \"SingerBuddy\";")
w(f"\t\t\tproductName = \"SingerBuddy\";")
w(f"\t\t\tproductReference = {ids['app_product']};")
w(f"\t\t\tproductType = \"com.apple.product-type.application\";")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_target']} /* WebResources */ = {{")
w(f"\t\t\tisa = PBXNativeTarget;")
w(f"\t\t\tbuildConfigurationList = {ids['bundle_config_list']};")
w(f"\t\t\tbuildPhases = (")
w(f"\t\t\t\t{ids['bundle_sources']},")
w(f"\t\t\t\t{ids['bundle_frameworks']},")
w(f"\t\t\t\t{ids['bundle_resources']},")
w(f"\t\t\t);")
w(f"\t\t\tbuildRules = (")
w(f"\t\t\t);")
w(f"\t\t\tdependencies = (")
w(f"\t\t\t);")
w(f"\t\t\tname = \"WebResources\";")
w(f"\t\t\tproductName = \"WebResources\";")
w(f"\t\t\tproductReference = {ids['bundle_product']};")
w(f"\t\t\tproductType = \"com.apple.product-type.bundle\";")
w(f"\t\t}};")

# ===== PBXContainerItemProxy =====
w(f"\t\t{ids['target_proxy']} /* PBXContainerItemProxy */ = {{")
w(f"\t\t\tisa = PBXContainerItemProxy;")
w(f"\t\t\tcontainerPortal = {ids['project']} /* Project object */;")
w(f"\t\t\tproxyType = 1;")
w(f"\t\t\tremoteGlobalIDString = {ids['bundle_target']};")
w(f"\t\t\tremoteInfo = WebResources;")
w(f"\t\t}};")

# ===== PBXTargetDependency =====
w(f"\t\t{ids['native_deps']} /* PBXTargetDependency */ = {{")
w(f"\t\t\tisa = PBXTargetDependency;")
w(f"\t\t\ttarget = {ids['bundle_target']};")
w(f"\t\t\ttargetProxy = {ids['target_proxy']} /* PBXContainerItemProxy */;")
w(f"\t\t}};")

# ===== PBXResourcesBuildPhase =====
w(f"\t\t{ids['app_resources']} /* Resources */ = {{")
w(f"\t\t\tisa = PBXResourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t\t{ids['assets_bf']},")
w(f"\t\t\t\t{ids['bundle_product_bf']},")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_resources']} /* Resources */ = {{")
w(f"\t\t\tisa = PBXResourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
# Top-level files (index.html, favicon.ico) copied flat to bundle root
for name, ft, rel_path in web_files:
    key = stable_key(rel_path)
    w(f"\t\t\t\t{web_bfs[key]},")
# Directories copied as trees (preserves scripts/, scores/, soundfonts/ structure)
for dirname in WEB_RESOURCE_DIRS:
    w(f"\t\t\t\t{dir_bfs[dirname]},")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

# ===== PBXSourcesBuildPhase =====
w(f"\t\t{ids['app_sources']} /* Sources */ = {{")
w(f"\t\t\tisa = PBXSourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t\t{app_bf['SingerBuddyApp.swift']},")
w(f"\t\t\t\t{app_bf['ContentView.swift']},")
w(f"\t\t\t\t{app_bf['WebView.swift']},")
w(f"\t\t\t\t{app_bf['WebViewViewModel.swift']},")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_sources']} /* Sources */ = {{")
w(f"\t\t\tisa = PBXSourcesBuildPhase;")
w(f"\t\t\tbuildActionMask = 2147483647;")
w(f"\t\t\tfiles = (")
w(f"\t\t\t\t{ids['wr_swift_bf']},")
w(f"\t\t\t);")
w(f"\t\t\trunOnlyForDeploymentPostprocessing = 0;")
w(f"\t\t}};")

# ===== XCBuildConfiguration =====
# Project Debug
w(f"\t\t{ids['project_debug']} /* Debug */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;")
w(f"\t\t\t\tCLANG_ENABLE_MODULES = YES;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tSDKROOT = \"iphoneos\";")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Debug\";")
w(f"\t\t}};")

# Project Release
w(f"\t\t{ids['project_release']} /* Release */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;")
w(f"\t\t\t\tCLANG_ENABLE_MODULES = YES;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tSWIFT_COMPILATION_MODE = \"wholemodule\";")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Release\";")
w(f"\t\t}};")

# App Debug
w(f"\t\t{ids['app_debug']} /* Debug */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = \"AppIcon\";")
w(f"\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = \"AccentColor\";")
w(f"\t\t\t\tCODE_SIGN_STYLE = \"Automatic\";")
w(f"\t\t\t\tCURRENT_PROJECT_VERSION = 1;")
w(f"\t\t\t\tDEVELOPMENT_TEAM = \"\";")
w(f"\t\t\t\tENABLE_PREVIEWS = YES;")
w(f"\t\t\t\tGENERATE_INFOPLIST_FILE = NO;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tINFOPLIST_FILE = \"SingerBuddy/Info.plist\";")
w(f"\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;")
w(f"\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;")
w(f"\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = \"(UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight)\";")
w(f"\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = \"(UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight)\";")
w(f"\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\"$(inherited) @executable_path/Frameworks\");")
w(f"\t\t\t\tMARKETING_VERSION = \"1.0\";")
w(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.singerbuddy.app\";")
w(f"\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";")
w(f"\t\t\t\tSDKROOT = \"iphoneos\";")
w(f"\t\t\t\tSUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";")
w(f"\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Debug\";")
w(f"\t\t}};")

# App Release
w(f"\t\t{ids['app_release']} /* Release */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = \"AppIcon\";")
w(f"\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = \"AccentColor\";")
w(f"\t\t\t\tCODE_SIGN_STYLE = \"Automatic\";")
w(f"\t\t\t\tCURRENT_PROJECT_VERSION = 1;")
w(f"\t\t\t\tDEVELOPMENT_TEAM = \"\";")
w(f"\t\t\t\tENABLE_PREVIEWS = YES;")
w(f"\t\t\t\tGENERATE_INFOPLIST_FILE = NO;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tINFOPLIST_FILE = \"SingerBuddy/Info.plist\";")
w(f"\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;")
w(f"\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;")
w(f"\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = \"(UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight)\";")
w(f"\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = \"(UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight)\";")
w(f"\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\"$(inherited) @executable_path/Frameworks\");")
w(f"\t\t\t\tMARKETING_VERSION = \"1.0\";")
w(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.singerbuddy.app\";")
w(f"\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";")
w(f"\t\t\t\tSDKROOT = \"iphoneos\";")
w(f"\t\t\t\tSUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";")
w(f"\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Release\";")
w(f"\t\t}};")

# Bundle Debug
w(f"\t\t{ids['bundle_debug']} /* Debug */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tCODE_SIGN_STYLE = \"Automatic\";")
w(f"\t\t\t\tCURRENT_PROJECT_VERSION = 1;")
w(f"\t\t\t\tGENERATE_INFOPLIST_FILE = YES;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\"$(inherited) @executable_path/Frameworks\");")
w(f"\t\t\t\tMARKETING_VERSION = \"1.0\";")
w(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.singerbuddy.app.WebResources\";")
w(f"\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";")
w(f"\t\t\t\tSDKROOT = \"iphoneos\";")
w(f"\t\t\t\tSUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";")
w(f"\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Debug\";")
w(f"\t\t}};")

# Bundle Release
w(f"\t\t{ids['bundle_release']} /* Release */ = {{")
w(f"\t\t\tisa = XCBuildConfiguration;")
w(f"\t\t\tbuildSettings = {{")
w(f"\t\t\t\tCODE_SIGN_STYLE = \"Automatic\";")
w(f"\t\t\t\tCURRENT_PROJECT_VERSION = 1;")
w(f"\t\t\t\tGENERATE_INFOPLIST_FILE = YES;")
w(f"\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = \"17.0\";")
w(f"\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\"$(inherited) @executable_path/Frameworks\");")
w(f"\t\t\t\tMARKETING_VERSION = \"1.0\";")
w(f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \"com.singerbuddy.app.WebResources\";")
w(f"\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";")
w(f"\t\t\t\tSDKROOT = \"iphoneos\";")
w(f"\t\t\t\tSUPPORTED_PLATFORMS = \"iphoneos iphonesimulator\";")
w(f"\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;")
w(f"\t\t\t\tSWIFT_VERSION = 5.0;")
w(f"\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";")
w(f"\t\t\t}};")
w(f"\t\t\tname = \"Release\";")
w(f"\t\t}};")

# ===== XCConfigurationList =====
w(f"\t\t{ids['project_config_list']} /* Build configuration list for PBXProject */ = {{")
w(f"\t\t\tisa = XCConfigurationList;")
w(f"\t\t\tbuildConfigurations = (")
w(f"\t\t\t\t{ids['project_debug']},")
w(f"\t\t\t\t{ids['project_release']},")
w(f"\t\t\t);")
w(f"\t\t\tdefaultConfigurationIsVisible = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['app_config_list']} /* Build configuration list for PBXNativeTarget \"SingerBuddy\" */ = {{")
w(f"\t\t\tisa = XCConfigurationList;")
w(f"\t\t\tbuildConfigurations = (")
w(f"\t\t\t\t{ids['app_debug']},")
w(f"\t\t\t\t{ids['app_release']},")
w(f"\t\t\t);")
w(f"\t\t\tdefaultConfigurationIsVisible = 0;")
w(f"\t\t}};")

w(f"\t\t{ids['bundle_config_list']} /* Build configuration list for PBXNativeTarget \"WebResources\" */ = {{")
w(f"\t\t\tisa = XCConfigurationList;")
w(f"\t\t\tbuildConfigurations = (")
w(f"\t\t\t\t{ids['bundle_debug']},")
w(f"\t\t\t\t{ids['bundle_release']},")
w(f"\t\t\t);")
w(f"\t\t\tdefaultConfigurationIsVisible = 0;")
w(f"\t\t}};")

# Project object (MUST be inside the objects block)
w(f"\t\t{ids['project']} /* Project object */ = {{")
w(f"\t\t\tisa = PBXProject;")
w(f"\t\t\tattributes = {{")
w(f"\t\t\t\tBuildIndependentTargetsInParallel = 1;")
w(f"\t\t\t\tLastSwiftUpdateCheck = 2640;")
w(f"\t\t\t\tLastUpgradeCheck = 2640;")
w(f"\t\t\t\tTargetAttributes = {{")
w(f"\t\t\t\t\t{ids['app_target']} = {{")
w(f"\t\t\t\t\t\tLastSwiftMigration = 1700;")
w(f"\t\t\t\t\t}};")
w(f"\t\t\t\t\t{ids['bundle_target']} = {{")
w(f"\t\t\t\t\t\tLastSwiftMigration = 1700;")
w(f"\t\t\t\t\t}};")
w(f"\t\t\t\t}};")
w(f"\t\t\t}};")
w(f"\t\t\tbuildConfigurationList = {ids['project_config_list']};")
w(f"\t\t\tdevelopmentRegion = \"en\";")
w(f"\t\t\thasScannedForEncodings = 0;")
w(f"\t\t\tknownRegions = (")
w(f"\t\t\t\t\"en\",")
w(f"\t\t\t\t\"Base\",")
w(f"\t\t\t);")
w(f"\t\t\tmainGroup = {ids['main_group']};")
w(f"\t\t\tpackageProducts = (")
w(f"\t\t\t);")
w(f"\t\t\tprojectDirPath = \"\";")
w(f"\t\t\tprojectRoot = \"\";")
w(f"\t\t\tpreferredProjectObjectVersion = 77;")
w(f"\t\t\ttargets = (")
w(f"\t\t\t\t{ids['app_target']},")
w(f"\t\t\t\t{ids['bundle_target']},")
w(f"\t\t\t);")
w(f"\t\t}};")

# Close objects
w("\t};")
w(f"\trootObject = {ids['project']} /* Project object */;")

# Close root
w("}")

content = "\n".join(lines) + "\n"

# Validate brace balance
cleaned = content.replace('{{', '').replace('}}', '')
open_b = cleaned.count('{')
close_b = cleaned.count('}')
print(f"Open braces: {open_b}, Close braces: {close_b}, Diff: {open_b - close_b}")

if open_b != close_b:
    print("ERROR: Braces not balanced!")
else:
    print("Braces balanced!")
    write_file("/Volumes/work/Stanford/SingerBuddy/iOS/SingerBuddy.xcodeproj/project.pbxproj", content)
    print("project.pbxproj written successfully")
