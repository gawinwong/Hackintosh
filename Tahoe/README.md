# macOS Tahoe 26 / 神舟 Z7-CT7PRO / GTX 1660 Ti

> **实验性 EFI 候选，未经真实硬件启动验证；不要覆盖现有 Monterey EFI。** 本目录保留仓库的 Monterey 基础文件用于升级，**其旧 OpenCore 和 Kext 二进制尚未更新，不能直接当作已验收的 Tahoe 启动盘**。安装前必须更新 OpenCore + kext 并执行 ocvalidate。

## 实际硬件
神舟战神 Z7-CT7PRO（PB50_70RFRDRC），Intel Core i7-9750H，Intel UHD 630 + NVIDIA GTX 1660 Ti（Turing），4K OLED 内屏，Intel 9462 Wi-Fi，Realtek ALC1220 / RTL8111，64GB RAM。来源：仓库根 README。原版 EFI：`Monterey/EFI`。

## 两套配置（以完全复制的原版 EFI 为基底）
- `EFI-install/`：macOS 26 安装 / Recovery / 故障回退配置。取消原来用于屏蔽独显的 `SSDT-DGPU.aml`（置为 Disabled），移除 `disable-external-gpu` 属性；保留完整 SIP 与固件显示，使用 `-igfxvesa` 临时避免旧核显加速问题。不启用 NullMoth NVIDIA 驱动，不强行排除 `IONDRVSupport`。
- `EFI-nvidia/`：**只在 Tahoe 已正常引导、用 1401 处理驱动且有已核验显示输出时试用**。加入 NullMoth 指定 NVIDIA 引导参数、弱化 SIP `csr-active-config=430A0000`、`SecureBootModel=Disabled`、添加 `IONDRVSupport` 的 kernel Block、`gfxrst=4`（与 WhateverGreen 同用）、`nvrmsettle=10000`（Turing 启动延迟）。该配置可能导致笔记本内屏黑屏，必须先从 U 盘验证，不能直接覆盖内部磁盘 EFI。

两套沿用原版 `MacBookPro16,4` SMBIOS（Tahoe 支持的 2019 款 16 英寸 MBP）。**原仓库公开了机器标识信息**，实际联网使用时建议重新生成并保护 Serial/MLB/UUID/ROM，不要将新机三码提交到公开仓库。

## 必须补齐的 OpenCore / kext 更新
1. 先备份能启动 Monterey 的 EFI 和 macOS 磁盘，保留一个独立的恢复 U 盘。
2. 从官方 [OpenCorePkg releases](https://github.com/acidanthera/OpenCorePkg/releases) 更新 **OpenCore.efi、BOOTx64.efi、OpenRuntime.efi、OpenCanopy.efi 等配套 EFI 驱动**（核验下载发布包 checksum）。本文件编写时官方最新版本为 **1.0.8**，Tahoe 至少需要支持 macOS 26 的版本；不可混用老版本驱动。按新 Sample.plist 补齐新增配置项。
3. 更新 Lilu、VirtualSMC 及其插件、WhateverGreen、AppleALC（本机原为定制版，先保留定制配置并评估迁移）、USBToolBox、UTBMap、VoodooPS2、RTL8111、NVMeFix、IntelBluetoothFirmware/BlueToolFixup/IntelBTPatcher 等。**原 itlwm.kext 必须替换成专门适配 Tahoe 的发行版**；找不到兼容版时先使用有线网络。不要假定旧二进制兼容 Tahoe。
4. 保持原机 ACPI/USB/键盘/声卡路径，唯独禁用原本专门关独显的 SSDT-DGPU。检查设备属性中是否还有禁止独显的 SSDS/ACPI/PCI 设置，并在 Windows/Linux 真实读取 GTX 1660 Ti PCI ID、内屏 eDP 和 HDMI/DP 到底接核显还是独显。不要虚构 dGPU 直连线路或 BIOS MUX 开关。
5. 用 **对应 OpenCore 版本** 的 `ocvalidate` 检查两个 config.plist，用 `plutil -lint` 或 Python `plistlib` 解析校验；确认文件/驱动声明的路径和 Enabled、MinKernel 与实际一致，适用内核是 Darwin 25.x。
6. BIOS 保持 UEFI/CSM 关闭、Secure Boot 关闭；NullMoth 推荐 Above 4G Decoding ON（笔记本 BIOS 不一定有此选项，**无该选项不要凭空修改固件**）。先保留默认 `ResizeGpuBars=-1`，别照抄其他主板 BAR 配置。
7. 新版 Sonoma/Tahoe 对旧 Intel 集显驱动支持减弱，**内屏能显示不代表加速可用**。即使 GTX 1660 Ti ID 在驱动支持表里，项目明确声明**不实现 NVIDIA Optimus 显示 MUX**，不能保证这台笔记本内屏被 dGPU 加速。外接屏也必须按物理接线实际测试。

## NVIDIA 驱动安装：不是把 kext 丢进 OC/Kexts
项目：[nullmoth/nvidia-macos-driver](https://github.com/nullmoth/nvidia-macos-driver)；编写时最新 **v2.9（2026-11-10）**，支持 Tahoe 26 / Turing 系列，但官网 [CARD-SUPPORT](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/CARD-SUPPORT.md) 中 Turing 的物理验证仍为 Pending。

**推荐流程：** 先用 `EFI-install` 在 U 盘引导已准备的 Tahoe 镜像并完成安装；进入 Tahoe 后从官方 release 获取对应版本 **1401 Mac app** 安装驱动。1401 会识别正在使用的 OpenCore 分区、备份配置、提示所需改动、安装带签名的驱动和移除入口；比直接拷贝本目录的 NVIDIA 配置安全。按 1401 提示在 macOS 隐私和安全性中允许扩展并重启。驱动的 NVRM/NVAccel/NVRMFB/NVRMAGDC 安装在系统 `/Library/Extensions`，**不得重复注入 `EFI/OC/Kexts`**。

如果使用手动档 `EFI-nvidia`，先核验实际显示输出线路、确认 1401/安装包版本和已有恢复 U 盘；单独装驱动并验证；此目录的 NVIDIA config 是研发对照/实验候选，不是已完成适配的成品。

## 真机验收与回退
- 安装器可显示且 NVMe/键盘/USB 工作；重启后能进入 Tahoe 桌面；确认内屏亮度、触摸板、声卡、Wi-Fi/蓝牙、有线、睡眠与外接屏，分别记“通过/失败/未知”。旧 README 中睡眠、外屏一直不正常，不能默认为修好。
- NVIDIA：`kmutil showloaded --list-only | grep -i nullmoth`、`system_profiler SPDisplaysDataType`、`ioreg`、Metal 系统信息；登录后观察 WindowServer 与显示输出稳定性。不要把“驱动安装成功”视为显卡完全可用。
- 黑屏：拔掉实验 EFI U 盘，继续使用**原有完整 Monterey EFI/独立恢复 U 盘**。NullMoth 1401 还提供一次性禁用/卸载驱动的 OpenCore picker 入口，见官方 [TROUBLESHOOTING](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/TROUBLESHOOTING.md)。系统已装 Tahoe 但不能回 Monterey 时，需要准备单独的 Tahoe 恢复介质，不是简单替换 EFI 就能降系统。
- 所有执行必须在神舟真机（或具备挂载镜像的受控环境）进行；**家中极空间的 Tahoe 镜像尚未通过当前 GitHub 接口读取、核验或写入安装 U 盘**。当前没有验证其版本、完整性及格式。

## 资料及风险
- [官方 macOS Tahoe 兼容 Mac 型号](https://support.apple.com/en-us/122867)
- [OpenCorePkg](https://github.com/acidanthera/OpenCorePkg/releases)
- [NullMoth README](https://github.com/nullmoth/nvidia-macos-driver/blob/main/README.md)
- [NullMoth 卡支持](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/CARD-SUPPORT.md)
- [NullMoth 排障及撤销](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/TROUBLESHOOTING.md)

**状态：针对原机型已作配置级变更并推送候选；未升级仓库里的 OpenCore/kext 二进制，未实机/安装器/显卡验收。请不要把本分支当作“开箱即用的 Tahoe EFI”。**
