статья про GPU

##Why we started this project?
Our company Servers.com here for a purpose. The purpose of our hosting is to provide you the tools to make whatever you need happen. One of the great example - Prisma app https://itunes.apple.com/us/app/prisma-free-photo-editor-art/id1122649984?mt=8 . From the start of rapid and extensively growth of Prisma startup our platform support they needs in terms of fast growing and hardware delivery. Lately they optimized a code and we decided to reuse part of hardware for GPU-cloud.
They used to process their pictures on Dell servers with GPU Titan X and 1080, so, that was our starting point.



##What was the major problems?

Each videocard exposing a two devices in lspci

```
42:00.0 VGA compatible controller: NVIDIA Corporation Device 1b80 (rev a1)
42:00.1 Audio device: NVIDIA Corporation Device 10f0 (rev a1)
```
You can easely remove audio device trough /sys

```
echo -n "1" > /sys/bus/pci/devices/0000\:42\:00.1/remove
```

Officially the NVIDIA GeForce GTX 1080 is supported under Linux via the NV proprietary driver as of 367.18 Beta.

At that time driver was quite new and was still not packaged even for experimental
```
364.19-1 1
          1 http://mirror.yandex.ru/debian experimental/non-free amd64 Packages
     361.45.18-2 500
        500 http://mirror.yandex.ru/debian sid/non-free amd64 Packages
```

So, we used a new driver from NVIDIA site:

```
chmod +x NVIDIA-Linux-x86_64-367.35.run
./NVIDIA-Linux-x86_64-367.35.run -a  --dkms -Z  -s
update-initramfs -u 
modprobe nvidia-uvm
./cuda_8.0.27_linux.run --override --silent --toolkit --samples --verbose
```

and patch

```
./cuda_8.0.27.1_linux.run --silent --accept-eula
```

NVIDIA is trying to limited a virtualization inside kvm, so kvm=off is your friend. You are oblige to use qemu 2.1+. Later we faced another limitations with ffmpeg ( only two concurrent flow per one 1080 card for nvidia ffmpeg ) 

```
<kvm>
   <hidden state='on'/>
</kvm>
```

##How it looks like from host-side?

Your host should provide SR-IOV and DMAR (DMA remapping). It can be switched on in BIOS/EFI

```
dmesg|grep -e DMAR -e IOMMU
```

IOMMU (input/output memory management unit) should be turned on in kernel options
```
iommu_intel=on 
```

Drivers snd_hda_intel and nouveau should be blacklisted

```
modprobe.blacklist=snd_hda_intel,nouveau
```

VFIO driver should be loaded

```
modprobe vfio
```


##How it looks like from the Openstack side?


You should define pci-e device:

```
[DEFAULT]
pci_passthrough_whitelist = { "vendor_id": "10de", "product_id": "1b80" }
pci_alias = { "vendor_id":"10de", "product_id":"1b80", "name":"nvidia" }
```

and apply proper filters:
```
scheduler_default_filters=AggregateInstanceExtraSpecsFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,AggregateImagePropertiesStrictIsolation,AggregateCoreFilter,DiskFilter,PciPassthroughFilter
```

and set proper flavour settings

meta: pci_passthrough:alias = nvidia:1 ( nvidia coming from pci_alias directive in nova.conf)
nova flavor-key GPU.SSD.30 set "pci_passthrough:alias"="nvidia:1" (1 - number of cards)


##Migrate your instance in Openstack
Unfortunately, automated migration is still in the development, but you can migrate the instance manually

Symptoms:
```
libvirtError: Requested operation is not valid: PCI device 0000:84:00.0 is in use by driver QEMU
```

Simple migration process
```
nova migrate uuid
nova reset-state uuid --active
nova stop uuid
nova start uuid
Removing  source-node flag: rm -r /var/lib/instances/uuid_resize
```

TODO LICENSING
Работа с GPU с точки зрения Nvidia
Лицензии, CUDA, драйвера, патчики



Reference
(PCI-passtrough)[https://wiki.openstack.org/wiki/Pci_passthrough]
(Openstack)[http://docs.openstack.org/admin-guide/compute-pci-passthrough.html]
(Nvidia blob)[https://github.com/amarao/ansible-nvidia-blob-install]



