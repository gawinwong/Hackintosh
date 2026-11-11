# macOS Tahoe 26 / 神舟 Z7-CT7PRO / GTX 1660 Ti

> **已更新 OpenCore 1.0.8 和已列出的 Kext 二进制，且两套 EFI 均通过官方 ocvalidate 1.0.8 校验。** 这是可用于**恢复 U 盘首轮启动测试**的实验包，不是“所有硬件已经驱动”的保证。真正安装前先验证 BIOS、镜像及恢复手段；不要覆盖原 Monterey EFI。
>
> **重要兼容限制**：macOS Tahoe 26 移除了 AppleHDA，原 ALC1220 模拟音频没有随 EFI 获得直接支持；需要额外研究 VoodooHDA 或受控 AppleHDA 恢复。Intel 9462 Wi-Fi 使用 Tahoe 专用的第三方 alpha 驱动，蓝牙/睡眠/触摸板也必须实机测。UHD 630 内屏在 Tahoe 下不保证图形加速；GTX 1660 Ti 外屏必须装 NullMoth 后再测 Metal。

## 2026-11-11 已构建 EFI：如何在神舟上使用

**已完成并由 GitHub Actions 验证**：OpenCore 1.0.8 + 配套 BOOTx64/OpenRuntime/OpenCanopy/OpenLinuxBoot；Lilu 1.7.2、VirtualSMC 1.3.8、WhateverGreen 1.7.1、NVMeFix 1.1.3、VoodooPS2 2.3.7、USBToolBox 1.2.0、RealtekRTL8111 3.0.0、IntelBluetooth 2.4.0、BlueToolFixup 2.7.2、Tahoe AirportItlwm 2.4.0-alpha，以及 NVIDIA 配置使用的 AMFIPass 1.4.1。保留原机 UTBMap、ACPI 与 HfsPlus.efi，取消禁用 dGPU 的 SSDT/设备属性。实际版本和下载资产见 [DRIVER-VERSIONS.json](DRIVER-VERSIONS.json)。

**拿到 USB 可用的完整目录**：
- 直接下载 [Tahoe/EFI-install](EFI-install) 或 GitHub Actions 的 `Tahoe-Z7-CT7PRO-experimental` Artifact（包含 EFI-install.zip 与 EFI-nvidia.zip）。将 `EFI-install` **目录里面的 BOOT 与 OC 文件夹** 放入 USB 的 `EFI` 文件夹：最终应为 `EFI/BOOT/BOOTx64.efi` 和 `EFI/OC/config.plist`。**不可形成 EFI/EFI-install/OC**。
- 准备一份**独立、未修改的 Monterey 恢复 EFI U 盘**。新系统最好装在另一块 SSD 或备份确认的独立分区；不要抹掉旧 Windows/Monterey 数据。
- 先从 `EFI-install` 启动，在**内屏**尝试进入 Tahoe 安装器。此版使用 `-igfxvesa` 临时固件显示，UHD 630 不能假定已有 QE/CI，首次界面可能低性能。**此时不应安装 NVIDIA 系统驱动，也不能期待外接视频口在系统桌面工作。**
- 如果 Tahoe 成功进入桌面：优先通过已知可用的网络方式准备 [1401 Mac 官方应用](https://github.com/nullmoth/nvidia-macos-driver/releases)；安装前备份当前正在使用的 EFI。由 1401 安装 NullMoth NVIDIA 最新正式驱动，并查看其对 OpenCore 的实际配置修改，允许系统扩展后重启。
- 使用 NVIDIA 的启动设置后，连接一台已在 Windows 中验证的外接屏，从 1080p/60Hz 开始，读取 `kmutil showloaded --list-only | grep -i nullmoth` 和 `system_profiler SPDisplaysDataType`。排查黑屏时优先看官方 1401 Crash Report 和 GPU 日志。**不要盲目将 EFI-nvidia 直接复制到内置 SSD**；它是手动调试的对照版，以 1401 对实际启动分区的改动为准。
- 首次引导后记录：内屏、外屏 HDMI/DP、核显、GTX 1660 Ti Metal、USB、I2C 触摸板、PS/2 键盘、Wi‑Fi、蓝牙、RJ45、麦克风、内置扬声器、耳机、睡眠/唤醒。任何未测条目均为“未知”，不能标注“已驱动”。
- **重要**：原仓库的 `SystemUUID` 格式不能通过新 OC 验证，因此此 EFI 中已清空。首次正式使用前，必须在本机重新生成私有 SMBIOS 四项并检查；不要把 Serial/MLB/ROM/UUID 发到公开仓库。静态校验通过不代表开机必定成功。

构建 CI：[GitHub Actions — Build Tahoe EFI](https://github.com/gawinwong/Hackintosh/actions/workflows/tahoe-efi.yml)。如果未来自动更新驱动失败，以最后一次成功构建的提交及 Artifact 为准。

## 实际硬件
神舟战神 Z7-CT7PRO（PB50_70RFRDRC），Intel Core i7-9750H，Intel UHD 630 + NVIDIA GTX 1660 Ti（Turing），4K OLED 内屏，Intel 9462 Wi-Fi，Realtek ALC1220 / RTL8111，64GB RAM。来源：仓库根 README。原版 EFI：`Monterey/EFI`。

## 已知显示线路及待确认事项

- **已确认（用户提供）：** 笔记本内置 4K OLED 屏幕可以使用 Intel UHD 630，也支持切换到 GTX 1660 Ti 进行图形渲染；机身**全部外接视频接口接 GTX 1660 Ti**。
- **尚不能由“支持独显渲染”推断内屏同时物理直连双显卡。** 常见的 NVIDIA Optimus 模式是 GTX 1660 Ti 渲染后经 Intel UHD 630 扫描输出到内屏；另一种是主板存在硬件 MUX（或 Advanced Optimus），可将内屏输出链路切换至 NVIDIA。当前未核实神舟 Z7-CT7PRO 具体实现。
- **macOS Tahoe 的意义：** NullMoth 驱动没有承诺实现 Optimus 跨 GPU 显示路径。因此若内屏只是 Optimus 渲染模式，即使 GTX 1660 Ti 可以做计算/渲染，也不能假定 macOS 内屏获得 NVIDIA Metal 加速。若确实具备独显直连 MUX，切换成功后才可能走 NVIDIA 内屏输出，但仍需实机验证驱动和面板兼容性。
- **优先验收顺序：** 先保留核显/固件帧缓冲并让 Tahoe 安装器启动；再通过**物理直连 GTX 1660 Ti 的外接视频接口**测试 NullMoth 的视频输出和 Metal；最后核实 BIOS 或 Windows 控制面板是否有“混合/独显直连”开关、读取内屏显示拓扑并做真机切换测试。不能因想启用 NVIDIA 而直接禁用 Intel 核显。
- **不预设 BIOS MUX 存在**，不将 Windows 下的“高性能 NVIDIA 处理器”应用级设置误写为硬件独显直连。

## 首要目标：修复外接显示器黑屏（GTX 1660 Ti 物理直连）

**用户首要目标是 macOS Tahoe 26 的外接显示输出和 NVIDIA 图形加速，不是让内屏由 NVIDIA 驱动。** 已确认所有外接 HDMI/DP 等视频口物理接到 GTX 1660 Ti，而内屏由 Intel UHD 630 输出，Windows 的 NVIDIA 应用偏好仅代表 Optimus 渲染，并不证明存在 MUX。

原 Monterey EFI 的 `SSDT-DGPU.aml` 和 `disable-external-gpu` 会屏蔽独显，旧系统连接外屏黑屏与此高度吻合。但**移除屏蔽并不自动解决 macOS 驱动问题**；Tahoe 需要安装、加载并实测 NullMoth 的 NVRM / NVRMFB / NVAccel / NVRMAGDC 系统扩展。它们安装在 `/Library/Extensions`，不是 OC/Kexts。

为防止先前黑屏问题，必须落实以下顺序：

1. **独立安装 U 盘**：`EFI-install` 用固件帧缓冲完成安装；保持 `IONDRVSupport` 未被排除；Booter→Quirks→`ResizeAppleGpuBars=0`、UEFI→Quirks→`ResizeGpuBars=-1` 是 NullMoth 建议的安装用设置。当前旧仓库 Booter 的 `ResizeAppleGpuBars=-1`，**必须在验证的新 OpenCore schema 下调整后才能试安装**。
2. **更新引导二进制**：OpenCore / Lilu / VirtualSMC / WhateverGreen 等最新版及全部声明文件须完整同步，生成后用对应版本 `ocvalidate`。不能拿只改了 config 的旧 EFI 当成 Tahoe 成品。
3. **先验证基础桌面，后安装 NVIDIA**：首轮测试内置屏与系统是否能操作，并提供远程管理或 Recovery 后路；内屏在 Tahoe 下没有加速也可能出现功能受限。
4. **通过 1401 安装 NullMoth 最新正式版**，由其备份正在启动的 OpenCore、处理对应设置与四个系统 kext；特别核对 `AMFIPass.kext`，当前旧 EFI 中没有，不能漏掉；按提示允许扩展、重启。手工 NVIDIA 候选应只用于对照和故障分析。
5. **先接外屏检查信号**：用原来在 Windows 下可正常工作的线材与视频口，优先 1080p/60 Hz 或低刷新率；记录 `system_profiler SPDisplaysDataType`、`kmutil showloaded --list-only | grep nullmoth`、OpenCore/WindowServer/GPU 日志、显示器是否被识别。若仅黑屏/闪烁，确认驱动版本以及 BAR、显示模式；可对照官方 `-nvrmnoflip` 故障参数，不要先在物理接线未知时乱改 Intel `AAPL,ig-platform-id`。
6. **接受驱动的已知边界**：官方表示 Turing GTX 16 在支持范围，但 Turing 的物理验证仍标为 Pending；无真机结果不能保证 1660 Ti 的所有视频口和分辨率工作。2026-11 的驱动仍有 HDMI/DP 音频未正常工作的已知问题，视频出画面和显示器扬声器有声需分开验收。
7. **保留回退**：始终保留原 Monterey EFI 与另一份恢复介质；1401 新版本自带从 OpenCore picker 临时关闭或移除 NVIDIA 驱动的入口，黑屏时优先使用官方回退办法。

参考：[NullMoth README](https://github.com/nullmoth/nvidia-macos-driver/blob/main/README.md)、[安装/显示管线说明](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/HOW-IT-WORKS.md)、[黑屏排障](https://github.com/nullmoth/nvidia-macos-driver/blob/main/docs/TROUBLESHOOTING.md)。

## 两套配置（以完全复制的原版 EFI 为基底）
- `EFI-install/`：macOS 26 安装 / Recovery / 故障回退配置。取消原来用于屏蔽独显的 `SSDT-DGPU.aml`（置为 Disabled），移除 `disable-external-gpu` 属性；保留完整 SIP 与固件显示，使用 `-igfxvesa` 临时避免旧核显加速问题。不启用 NullMoth NVIDIA 驱动，不强行排除 `IONDRVSupport`。
- `EFI-nvidia/`：**只在 Tahoe 已正常引导、用 1401 处理驱动且有已核验显示输出时试用**。加入 NullMoth 指定 NVIDIA 引导参数、弱化 SIP `csr-active-config=430A0000`、`SecureBootModel=Disabled`、添加 `IONDRVSupport` 的 kernel Block、`gfxrst=4`（与 WhateverGreen 同用）、`nvrmsettle=10000`（Turing 启动延迟）。该配置可能导致笔记本内屏黑屏，必须先从 U 盘验证，不能直接覆盖内部磁盘 EFI。

两套沿用原版 `MacBookPro16,4` SMBIOS（Tahoe 支持的 2019 款 16 英寸 MBP）。**原仓库公开了机器标识信息**，实际联网使用时建议重新生成并保护 Serial/MLB/UUID/ROM，不要将新机三码提交到公开仓库。

## 后续系统级兼容性与复验事项（OpenCore / Kext 已更新）
1. 先备份能启动 Monterey 的 EFI 和 macOS 磁盘，保留一个独立的恢复 U 盘。
2. 已从官方 [OpenCorePkg 1.0.8](https://github.com/acidanthera/OpenCorePkg/releases) 获取 OpenCore、BOOTx64 与 EFI 驱动，并按 1.0.8 Sample.plist 同步配置，通过 ocvalidate。未来升级必须保持套件版本匹配，不混用旧 EFI 驱动。
3. 已下载并纳入主流 Kext 的 Release 版本，旧 AppleALC 定制版**没有**注入 Tahoe EFI，因为 AppleHDA 已从 Tahoe 移除；模拟声卡需额外安装 VoodooHDA 或恢复 AppleHDA。旧 itlwm 已换成 Tahoe 专用 alpha AirportItlwm；如 Wi-Fi 不稳定则先使用有线网络，切勿当作已验证适配。
4. 保持原机 ACPI/USB/键盘/声卡路径，唯独禁用原本专门关独显的 SSDT-DGPU。检查设备属性中是否还有禁止独显的 SSDS/ACPI/PCI 设置，并在 Windows/Linux 真实读取 GTX 1660 Ti PCI ID、显示拓扑及是否有硬件 MUX。用户已确认所有外接视频口接 NVIDIA，以及内屏支持独显渲染；**内屏是否能直接切到独显输出仍待核实**。不要虚构 BIOS MUX 开关。
5. 已执行 OpenCore 1.0.8 `ocvalidate` 检查两个 config.plist，并以 Python plistlib 核验声明的 ACPI/Kext/UEFI 文件路径存在；实际安装仍需在 Darwin 25.x Tahoe 真机复验。
6. BIOS 保持 UEFI/CSM 关闭、Secure Boot 关闭；NullMoth 推荐 Above 4G Decoding ON（笔记本 BIOS 不一定有此选项，**无该选项不要凭空修改固件**）。先保留默认 `ResizeGpuBars=-1`，别照抄其他主板 BAR 配置。
7. 新版 Sonoma/Tahoe 对旧 Intel 集显驱动支持减弱，**内屏能显示不代表加速可用**。即使 GTX 1660 Ti ID 在驱动支持表里，项目明确声明**不实现 NVIDIA Optimus 显示 MUX**，不能保证这台笔记本内屏被 dGPU 加速。外接视频接口已确认直连 GTX 1660 Ti，但仍必须在 Tahoe 下验证信号输出与 Metal 加速。

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

**状态：OpenCore、Kext 二进制已构建并经 ocvalidate 静态校验通过；未真机启动、未在 Tahoe 安装器/显示器/显卡上验收。仅推荐先用 USB 测试，不能保证全部硬件驱动。**
