#!/usr/bin/env python3
"""Generate Tahoe 26 EFI from Monterey hardware configuration and current upstream binaries.
Run on macOS CI; on any failure STOP rather than publish a broken EFI.
"""
import copy, json, plistlib, shutil, subprocess, tempfile, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ORIG=ROOT/"Monterey/EFI"
TAHOE=ROOT/"Tahoe"
repos={
"oc":"acidanthera/OpenCorePkg",
"Lilu":"acidanthera/Lilu","VirtualSMC":"acidanthera/VirtualSMC",
"WhateverGreen":"acidanthera/WhateverGreen","NVMeFix":"acidanthera/NVMeFix",
"VoodooPS2Controller":"acidanthera/VoodooPS2",
"USBToolBox":"USBToolBox/kext","RealtekRTL8111":"Mieze/RTL8111_driver_for_OS_X",
"IntelBluetoothFirmware":"OpenIntelWireless/IntelBluetoothFirmware",
"BlueToolFixup":"acidanthera/BrcmPatchRAM"}
ordered=["Lilu","VirtualSMC","SMCBatteryManager","SMCProcessor","SMCSuperIO",
"WhateverGreen","NVMeFix","USBToolBox","UTBMap","VoodooPS2Controller",
"RealtekRTL8111","IntelBluetoothFirmware","IntelBTPatcher","BlueToolFixup",
"AirportItlwm","AMFIPass"]
versions={}
def request(url):
    headers={"User-Agent":"Tahoe-EFI-builder"}
    if url.startswith("https://api.github.com/"):
        import os
        token=os.environ.get("GITHUB_TOKEN","")
        if token: headers["Authorization"]="Bearer "+token
    return urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=180)
def loadjson(url):
    with request(url) as f:return json.load(f)
def download(url,p):
    with request(url) as src,open(p,"wb") as dst:shutil.copyfileobj(src,dst)
def unzip(path,dest):
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path) as z:
        for item in z.infolist():
            v=Path(item.filename)
            if v.is_absolute() or ".." in v.parts:raise ValueError("unsafe zip")
        z.extractall(dest)
    return dest
def release(repo,tmp,selector,tag=None):
    r=loadjson("https://api.github.com/repos/"+repo+"/releases/"+("tags/"+tag if tag else "latest"))
    matches=[a for a in r["assets"] if selector(a["name"])]
    if len(matches)!=1:raise RuntimeError("Release asset mismatch "+repo+": "+str([a["name"] for a in matches]))
    a=matches[0];p=tmp/(repo.replace("/","_")+".zip")
    download(a["browser_download_url"],p)
    versions[repo]={"tag":r["tag_name"],"asset":a["name"]}
    return unzip(p,tmp/(repo.replace("/","_")+"_expanded"))
def find(root,name):
    matches=sorted([p for p in root.rglob(name) if p.name==name and (p.is_file() if name=="ocvalidate" else True)],key=lambda p:len(p.parts))
    if not matches:raise FileNotFoundError(str(root)+"/"+name)
    return matches[0]
def sync(old,sample):
    if isinstance(old,dict) and isinstance(sample,dict):
        return {k:sync(old[k],v) if k in old else copy.deepcopy(v) for k,v in sample.items()}
    if isinstance(old,list) and isinstance(sample,list):
        if len(sample)==1 and isinstance(sample[0],dict):
            return [sync(x,sample[0]) for x in old]
        return copy.deepcopy(old)
    return copy.deepcopy(old) if type(old)==type(sample) else copy.deepcopy(sample)
def kextentry(kdir,name):
    p=kdir/(name+".kext");info=plistlib.loads((p/"Contents/Info.plist").read_bytes())
    exe=info.get("CFBundleExecutable","")
    ep="Contents/MacOS/"+exe if exe else ""
    if ep and not (p/ep).is_file():raise FileNotFoundError(str(p/ep))
    return {"Arch":"Any","BundlePath":p.name,"Comment":name,"Enabled":True,
      "ExecutablePath":ep,"MaxKernel":"","MinKernel":"","PlistPath":"Contents/Info.plist"}
def validate_paths(cfg,oc):
    for x in cfg["Kernel"]["Add"]:
        if x["Enabled"] and not (oc/"Kexts"/x["BundlePath"]/x["PlistPath"]).is_file():
            raise RuntimeError("missing kext "+x["BundlePath"])
    for x in cfg["ACPI"]["Add"]:
        if x["Enabled"] and not (oc/"ACPI"/x["Path"]).is_file():
            raise RuntimeError("missing SSDT "+x["Path"])
    for x in cfg["UEFI"]["Drivers"]:
        if x["Enabled"] and not (oc/"Drivers"/x["Path"]).is_file():
            raise RuntimeError("missing EFI driver "+x["Path"])
def main():
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)
        ocpkg=release(repos["oc"],t,lambda n:n.endswith("-RELEASE.zip"))
        cache={}
        for key,r in repos.items():
            if key=="oc" or r in cache:continue
            cache[r]=release(r,t,lambda n:n.lower().endswith(".zip") and "debug" not in n.lower() and ("release" in n.lower() or r in ("Mieze/RTL8111_driver_for_OS_X","OpenIntelWireless/IntelBluetoothFirmware")))
        wifi=release("laobamac/itlwm",t,lambda n:n.startswith("AirportItlwm-Tahoe") and "RELEASE" in n and n.endswith(".zip"),tag="v2.4.0-alpha")
        p=t/"amfipass.zip"
        download("https://raw.githubusercontent.com/dortania/OpenCore-Legacy-Patcher/main/payloads/Kexts/Acidanthera/AMFIPass-v1.4.1-RELEASE.zip",p)
        amfi=unzip(p,t/"amfi")
        versions["AMFIPass"]={"tag":"1.4.1","source":"OCLP payload"}
        stage=t/"stage";stage.mkdir()
        for name in ordered:
            if name=="UTBMap":src=ORIG/"OC/Kexts/UTBMap.kext"
            elif name=="AMFIPass":src=find(amfi,name+".kext")
            elif name=="AirportItlwm":src=find(wifi,name+".kext")
            else:
                parent=repos.get(name)
                if name in ("SMCBatteryManager","SMCProcessor","SMCSuperIO"):parent=repos["VirtualSMC"]
                elif name=="IntelBTPatcher":parent=repos["IntelBluetoothFirmware"]
                src=find(cache[parent],name+".kext")
            if not (src/"Contents/Info.plist").is_file():raise RuntimeError("Missing Info.plist "+name)
            shutil.copytree(src,stage/(name+".kext"))
        sample=plistlib.loads((ocpkg/"Docs/Sample.plist").read_bytes())
        orig=plistlib.loads((ORIG/"OC/config.plist").read_bytes())
        for n,post in (("EFI-install",False),("EFI-nvidia",True)):
            dest=TAHOE/n
            if dest.exists():shutil.rmtree(dest)
            shutil.copytree(ORIG,dest)
            oc=dest/"OC"
            shutil.copy2(ocpkg/"X64/EFI/BOOT/BOOTx64.efi",dest/"BOOT/BOOTx64.efi")
            shutil.copy2(ocpkg/"X64/EFI/OC/OpenCore.efi",oc/"OpenCore.efi")
            dr=oc/"Drivers"
            for f in dr.glob("*.efi"):
                if f.name!="HfsPlus.efi":f.unlink()
            names=["HfsPlus.efi","OpenRuntime.efi","OpenCanopy.efi","OpenLinuxBoot.efi"]
            for v in names[1:]:shutil.copy2(ocpkg/"X64/EFI/OC/Drivers"/v,dr/v)
            shutil.rmtree(oc/"Kexts");(oc/"Kexts").mkdir()
            for src in stage.iterdir():
                if src.name=="AMFIPass.kext" and not post:continue
                shutil.copytree(src,oc/"Kexts"/src.name)
            cfg=sync(orig,sample)
            # Old public repository has an invalid SystemUUID; leave blank for user to regenerate privately.
            cfg["PlatformInfo"]["Generic"]["SystemUUID"]=""
            for a in cfg["ACPI"]["Add"]:
                if a["Path"]=="SSDT-DGPU.aml":a["Enabled"]=False
            cfg["DeviceProperties"]["Add"].get("PciRoot(0x0)/Pci(0x2,0x0)",{}).pop("disable-external-gpu",None)
            cfg["Kernel"]["Add"]=[kextentry(oc/"Kexts",k) for k in ordered if (oc/"Kexts"/(k+".kext")).exists()]
            cfg["Kernel"]["Block"]=[]
            if post:
                # New OC schema block entry derived from Sample.plist below.
                proto=(sample["Kernel"]["Block"] or [{}])[0]
                data={"Arch":"Any","Comment":"NullMoth framebuffer","Enabled":True,"Identifier":"com.apple.iokit.IONDRVSupport","MaxKernel":"","MinKernel":"25.0.0","Strategy":"Exclude"}
                cfg["Kernel"]["Block"]=[sync(data,proto)]
            cfg["Misc"]["Security"]["SecureBootModel"]="Disabled"
            cfg["Misc"]["Security"]["ScanPolicy"]=0
            cfg["Misc"]["Boot"]["ShowPicker"]=True
            cfg["UEFI"]["Quirks"]["ResizeGpuBars"]=-1
            cfg["Booter"]["Quirks"]["ResizeAppleGpuBars"]=0
            proto=(sample["UEFI"]["Drivers"] or [{}])[0]
            cfg["UEFI"]["Drivers"]=[sync({"Arguments":"","Comment":v,"Enabled":True,"LoadEarly":False,"Path":v},proto) for v in names]
            guid="7C436110-AB2A-4BBB-A880-FE41995C9F82"
            nv=cfg["NVRAM"]["Add"][guid]
            nv["csr-active-config"]=bytes.fromhex("430A0000" if post else "00000000")
            nv["boot-args"]=("-v keepsyms=1 gfxrst=4 nvfb=1 nvaccel=1 nvfbheads=4 -nvkmsnosmooth amfi_get_out_of_my_way=0x1 amfi=0x80 ipc_control_port_options=0 nvrmsettle=10000 -ibtcompatbeta -amfipassbeta" if post else "-v keepsyms=1 -igfxvesa -ibtcompatbeta")
            deletion=cfg["NVRAM"]["Delete"].setdefault(guid,[])
            for key in ("boot-args","csr-active-config"):
                if key not in deletion:deletion.append(key)
            with (oc/"config.plist").open("wb") as f:plistlib.dump(cfg,f,sort_keys=False)
            validate_paths(cfg,oc)
        tool=find(ocpkg,"ocvalidate")
        tool.chmod(tool.stat().st_mode|0o111)
        for name in ("EFI-install","EFI-nvidia"):
            cfg=TAHOE/name/"OC/config.plist"
            cp=subprocess.run([str(tool),str(cfg)],capture_output=True,text=True)
            print(name,cp.returncode,cp.stdout,cp.stderr)
            if cp.returncode:raise RuntimeError("OpenCore validation FAILED "+name)
        (TAHOE/"DRIVER-VERSIONS.json").write_text(json.dumps(versions,indent=2,ensure_ascii=False)+"\n")
        print("Both EFI folders schema-validated. Physical GPU and hardware operation NOT yet tested.")
if __name__=="__main__":main()
