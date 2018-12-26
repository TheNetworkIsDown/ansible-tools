# vcenter_inv_basic

This Ansible inventory script is based on [vcenter_inv](https://github.com/tierpod/ansible-vcenter).

There's another quite powerful inventory *plugin* [in the contrib section of the Ansible repo](https://github.com/ansible/ansible/blob/devel/contrib/inventory/vmware_inventory.py).

I'm using this one it with Ansible 2.7.5, Python 2.7, connecting to vCenter Server Appliance 6.5.

## Why this module and what is inventory anyway

Before doing anything, Ansible needs to know where to go and run its tasks. These objects are called hosts. Hosts can be defined statically (in a text file) and also dynamically, like we do here. So no matter if you'd like to use Ansible to run modifying commands, or only gather facts from your hosts (reporting), Ansible needs to know where to connect to. That is where inventory comes in.

A [vSphere inventory plugin is included with Ansible](https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory/vmware_vm_inventory.py) since 2.6, but it is very broken. I found vcenter_inv.py, understood its workings rapidly, and decided to build something usable based on that.

As opposed to an inventory plugin, the API between an inventory script and Ansible is quite simple. The script returns a JSON object containing host and group information, and optionally some variables.

## Initial changes from vcenter_inv

2018-12
* ENHANCEMENT: added support for multiple vCenters (configuration file format has not changed, you can just add more of them)
* CHANGE: virtual group "vcenter" has been removed, not sure what it was there for
* IMPROVEMENT: "all" group has been added, according to https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#tuning-the-external-inventory-script
* IMPROVEMENT: "_meta" group has been added, speeds things up according to docs
* ENHANCEMENT: Added debug logging using the Python logging facility, configurable logging level
* IMPROVEMENT: Explicitely skip templates and powered off VMs, previously this was implicit through "if vm.guest.guestId:"
* ENHANCEMENT: (optional) skip powered off VMs not containing a certain configurable string with a warning (helps keep your inventory clean)
* ENHANCEMENT: configurable options defined by new 'conf' dictionary in config file
* IMPROVEMENT: Checks for permissions of config file containing credentials, maybe using Ansible vault is for later
* IMPROVEMENT: ignore hosts having a loopback address for some reason
* ENHANCEMENT: create additional groups according to OS Family (Linux, Windows, ...)
* ENHANCEMENT: Let the user know when IPv6 adresses appear (configurable)

## Configuration file

The configuration file is called `vcenter_inv_basic.cfg` and contains a dictionary containing dictionairies defined in YAML. You put it alongside the script (same directory), most probably `/etc/ansible/` or some directory below it.

It contains the credentials to your vCenter server(s). Make sure the file belongs to the same user or group Ansible is run as, since the script won't run if a config file which is world-readable is detected.

Example vCenter credentials configured inside configuration file

```
"vcenter1":
  host: "vc1.my.company"
  username: "ansible@vsphere.local"
  password: "password"
  port: 443
"vcenter2":
  host: "vc2.my.company"
  username: "ansible@vsphere.local"
  password: "password"
  port: 443
```
The keys (here: "vcenter1", "vcenter2") are not actually used, they can be called whatever you like. 

The reserved keyword `conf` contains configuration options:
* `poweredOffStr`: The inventory script checks the power state of the VMs. It does not add powered off or suspended VMs to inventory. It however issues a warning if `poweredOffStr` is defined and a powered-off VM's name does not contain the value of `poweredOffStr`.
** type: string
** default value: none
* `loglevel`: determines level starting at which log messages are shown during execution
** type: string, possible values: one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
** default value: INFO (shows all messages of level INFO, WARNING, ERROR and CRITICAL, but not DEBUG)
** Notes: The default log destination is stderr since stdout is reserved for data transfer between the script and Ansible.
* `skip_ipv6`: Do not put hosts having an IPv6 address into inventory
** type: boolean
** default value: False

Example of configuration options specified in configuration file (optional)
```
"conf":
  poweredOffStr: "=OFF="
  loglevel: "DEBUG"
  skip_ipv6: True
```

## Usage

Create a user in vCenter and define it in the config file as shown above. I recommend creating a dedicated username inside vCenter for Ansible, assigning it to the vCenter server (top-most) object, and giving it the Read-Only role.

Then use this script like you would any other dynamic inventory script:

1. Call it explitely using `ansible -i`, or
2. Make it executable and put it into an inventory directory which is called explicitely using `ansible -i`, or
3. Configure your actual inventory directory in `ansible.conf` and put this script inside. Make it executable. This will implicitly run it in order to create inventory.

You can run the script manually using ``python ./vcenter_inv_basic.py --list`` for test.

Example output:
```
{
    "ubuntu64Guest": {
        "hosts": [
            "vm1",
            "vm2",
            "vm3",
            "vm5"
        ]
    },
    "all": {
        "hosts": [
            "vm1",
            "vm2",
            "vm3",
            "vm4",
            "vm5",
...
```

The following groups are created automatically:
* all: all VMs retrieved from vCenter server(s)
* *guestId*: the operating system as configured in vCenter (e.g. sles12_64Guest, ubuntu64Guest, ...) (**Careful**: need not be the actual OS)
* *guestFamily*: the operating system type as configured in vCenter (e.g. Windows, Linux, ...) (**Careful**: need not be the actual OS family)
* **_TODO_** *vcenter*: the vCenter hostname the guest was retrieved from

Now go ahead and create credentials potentially following [Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#variables-and-vaults)

Now you can run commands and playbooks against hosts from (dynamic) inventory.

