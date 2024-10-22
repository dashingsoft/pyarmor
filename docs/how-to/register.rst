=======================
 Using Pyarmor License
=======================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: top

.. highlight:: console

.. program:: pyarmor reg

Prerequisite
============

First of all

1. One :term:`activation file` of :term:`Pyarmor License`, refer to :doc:`../licenses` to purchase right one
2. One device has installed Pyarmor 9.0+
3. Internet connection
4. Product name which bind to this license

.. _initial registration:

Initial registration
====================

Any license need this step to request :term:`registration file` from Pyarmor License Server by :term:`activation file` like :file:`pyarmor-regcode-xxxx.txt`::

    $ pyarmor reg -p "XXX" pyarmor-regcode-xxxx.txt

Using :option:`-p` to specify product name for this license, please replace "XXX" with real product name. For non-commercial use, replace it to ``non-profits``.

If initial registration is successful, one :term:`registration file` like :file:`pyarmor-regfile-xxxx.zip` is generated in the current path at the same time. This file is used for subsequent registration in other machines.

Once initial registration completed, activation file :file:`pyarmor-regcode-xxxx.txt` is invalid, do not use it again.

Once initial registration completed, product name can't be changed.

Please backup registration file :file:`pyarmor-regfile-xxxx.zip` carefully. If lost, Pyarmor is not responsible for keeping this license and no lost-found service.

Product name is not decided
---------------------------

When a product is in development, and the product name is not decided. Set product name to ``TBD`` on initial registration. For example::

    $ pyarmor reg -p "TBD" pyarmor-regcode-xxxx.txt

In 6 months real product name must be set by this command::

    $ pyarmor reg -p "XXX" pyarmor-regcode-xxxx.txt

If it's not changed after 6 months, the product name will be set to ``non-profits`` automatically and can't be changed again.

Using Pyarmor Basic or Pro
==========================

1. Refer to :ref:`initial registration`, got :term:`registration file` like `pyarmor-regfile-xxxx.zip`
2. Using :term:`registration file` to register Pyarmor in other devices

Copy :term:`registration file` to other machines, then run this command::

    $ pyarmor reg pyarmor-regfile-xxxx.zip

Check the registration information::

    $ pyarmor -v

After successful registration, all obfuscations will automatically apply this license, and each obfuscation requires online license verification.

This license can register Pyarmor on at most 100 devices

On each device it's enough to register Pyarmor once, do not register Pyarmor before each obfuscation

Do not register Pyarmor in the CI/CD pipeline or docker container by this :term:`registration file`, each run will taken as one new device.

.. seealso:: :doc:`ci`

.. _using ci license:

Using CI License
================

.. versionadded:: 9.0

Refer to :ref:`initial registration`, got :term:`registration file` like `pyarmor-regfile-xxxx.zip`

Do not use ``pyarmor-regfile-xxxx.zip`` in CI/CD pipeline directly, it's only used to request CI regfile:

- In local device run the following command to request one CI regfile ``pyarmor-ci-xxxx.zip``::

      $ pyarmor reg -C pyarmor-regfile-xxxx.zip

  Check CI license info in local machine::

      $ pyarmor --home temp reg pyarmor-ci-xxxx.zip

- In CI/CD pipeline, add 2 steps to register Pyarmor by CI regfile::

      # Please replace "9.X.Y" with current Pyarmor version
      pip install pyarmor=9.X.Y
      pyarmor reg pyarmor-ci-xxxx.zip

  Check registration information in CI/CD pipeline::

      pyarmor -v

Notes

* Do not request CI regfile in CI/CD pipeline
* CI regfile ``pyarmor-ci-xxxx.zip`` will be expired about in 360 days
* CI regfile may not work in future Pyarmor version
* Once CI regfile doesn't work, require new one
* One license can request <= 100 CI regfiles

.. important::

   :term:`Pyarmor CI` License doesn't work in local device

.. seealso:: :doc:`ci`

.. _check device for group license:

Check Device For Group License
==============================

Check one device works for group license by this way:

* First install Pyarmor 8.4.0+ trial version in this device
* Got machine id by the following command::

    $ pyarmor reg -g 1
    ...
    INFO     current machine id is "mc92c9f22c732b482fb485aad31d789f1"
    INFO     device file has been generated successfully

* Reboot this device, check machine id is same or not
* If machine id is same after each reboot, group license works in this device. Otherwise group license doesn't work in this device.

For docker container, please check docker host as above. Only if docker host could work with group license, unlimited docker containers could be run in this docker host, refer to :doc:`how-to/register` section ``run unlimited dockers in offline device``

**If machine id of docker host is changed after reboot, group license doesn't work in any docker container**

Most of physics machine, cloud server or VM like qemu, virtual box, vmware with same disk image work with Group license. Most of runners in CI/CD pipeline could not use Group License.

.. _using group license:

Using group license
===================

.. versionadded:: 8.2

Each :term:`Pyarmor Group` could have 100 offline devices, each device has its own number, from 1 to 100.

Only the machine id of device is not changed after reboot, it could be used as group device. Most of physics machine, cloud server or VM like Qemu, Virtual box, Vmware with same disk image work with Group license. Refer to :ref:`Check Device For Group License`

The allocated device No. is never free, if a device is reinstalled, it need allocate new one.

Basic steps:

1. Using activation file :file:`pyarmor-regcode-xxxx.txt` to initial registration, set product name bind to this license, and generate :term:`registration file`
2. Generating group device file separately on each offline device
3. Using :term:`registration file` and group device file to generate device registration file.
4. Using device registration file to register Pyarmor on offline device [#]_

.. [#] The device registration file is bind to specified device, each device has its own device regfile

Initial registration
--------------------

After purchasing :term:`Pyarmor Group`, an activation file :file:`pyarmor-regcode-xxxx.txt` is sent to registration email.

Initial registration need internet connection and Pyarmor 8.2+. Suppose product name is ``XXX``, then run this command::

    $ pyarmor reg -p XXX pyarmor-regcode-xxxx.txt

After initial registration completed, a :term:`registration file` ``pyarmor-regfile-xxxx.zip`` will be generated.

Group device file
-----------------

On each offline device, install Pyarmor 8.2+, and generate group device file. For example, on device no. 1, run this command::

    $ pyarmor reg -g 1

    INFO     Python 3.12.0
    INFO     Pyarmor 8.4.7 (trial), 000000, non-profits
    INFO     Platform darwin.x86_64
    INFO     generating device file ".pyarmor/group/pyarmor-group-device.1"
    INFO     current machine id is "mc92c9f22c732b482fb485aad31d789f1"
    INFO     device file has been generated successfully

It will generate group device file ``pyarmor-group-device.1``.

In order to make sure group license works for this device, reboot this device, and run this command again::

    $ pyarmor reg -g 1

    ...
    INFO     current machine id is "mc92c9f22c732b482fb485aad31d789f1"
    ...

Make sure this machine id is same after reboot.

Because group license is bind to device, so machine id should keep same after reboot. If it's changed after reboot, group license doesn't work in this device.

For VM machine, WSL(Windows Subsystem Linux) or any other system, please check the documentation to configure the network and harddisk, make sure network mac address and serial number of harddisk are fixed. If they're volatile, group license could not work in this system.

Generating offline device regfile
---------------------------------

Generating offline device regfile needs an internet connection, Pyarmor 8.2+, group device file  ``pyarmor-group-device.1`` and group license :term:`registration file` ``pyarmor-regfile-xxxx.zip``.

Copying group device file ``pyarmor-group-device.1`` to initial registration device or any computer which has internet connection and registration file, this file must be saved in the path ``.pyarmor/group/``, then run the following command to generate device regfile ``pyarmor-device-regfile-xxxx.1.zip``::

    $ mkdir -p .pyarmor/group
    $ cp pyarmor-group-device.1 .pyarmor/group/

    $ pyarmor reg -g 1 /path/to/pyarmor-regfile-xxxx.zip

The device regfile ``pyarmor-device-regfile-xxxx.1.zip`` is bind to machine id in the device file ``pyarmor-group-device.1``.

.. note::

   If there are new versions which fix any bug that machine id is changed after this device reboot, it need generate new device file ``pyarmor-group-device.2`` for this device by new Pyarmor version, and generate new device regfile ``pyarmor-device-regfile-xxxx.2.zip`` by new Pyarmor version too.

   Because device no. ``1`` has been used, so it need use next device no. ``2``, that is to say, one device may occupy more than one device no. Generally it should not be problem because there are 100 device no. available.

Registering Pyarmor in offline device
-------------------------------------

Once device regfile is generated, copy it to the corresponding device, run this command to register Pyarmor::

    $ pyarmor reg /path/to/pyarmor-device-regfile-xxxx.1.zip

    INFO     Python 3.12.0
    INFO     Pyarmor 8.4.7 (trial), 000000, non-profits
    INFO     Platform darwin.x86_64
    INFO     register "/path/to/pyarmor-device-regfile-xxxx.1.zip"
    INFO     machine id in group license: mc92c9f22c732b482fb485aad31d789f1
    INFO     got machine id: mc92c9f22c732b482fb485aad31d789f1
    INFO     this machine id matchs group license
    INFO     This license registration information:

    License Type    : pyarmor-group
    License No.     : pyarmor-vax-006000
    License To      : Tester
    License Product : btarmor

    BCC Mode        : Yes
    RFT Mode        : Yes

    Notes
    * Offline obfuscation

Note that this log says this device regfile is only for this machine id::

    INFO     machine id in group license: mc92c9f22c732b482fb485aad31d789f1

And this log show machine id of this device::

    INFO     got machine id: mc92c9f22c732b482fb485aad31d789f1

They must be matched, otherwise this device regfile doesn't work, it may need generate new device regfile for this device.

Check registration information::

    $ pyarmor -v

After successful registration, all obfuscations will automatically apply this group license, and each obfuscation need not online license verification.

Run unlimited dockers in offline device
---------------------------------------

.. versionadded:: 8.3

Group license supports unlimited dockers which uses default bridge network and not highly customized, the docker containers use same device regfile of host.

**how it works**

1. Each docker host is taken as an offlice device and must be registered as above.

2. Then start an auth-server in docker host to listen auth-request from docker container.

3. When run Pyarmor in docker container, it will send auth-request to auth-server in docker host, and verify the result returned from docker host.

**Linux Docker Host**

The practice for group license with unlimited docker containers:

- Docker host, Ubuntu x86_64, Python 3.8
- Docker container, Ubuntu x86_64, Python 3.11

The prerequisite in docker host:

- offline device regfile ``pyarmor-device-regfile-xxxx.1.zip`` as above
- Pyarmor 8.4.1+

First copy the following files to docker host:

- pyarmor-8.4.2.tar.gz
- pyarmor.cli.core-5.4.1-cp38-none-manylinux1_x86_64.whl
- pyarmor.cli.core-5.4.1-cp311-none-manylinux1_x86_64.whl
- pyarmor-device-regfile-6000.1.zip

Then run the following commands in the docker host::

    $ python3 --version
    Python 3.8.10

    $ pip install pyarmor.cli.core-5.4.1-cp38-none-manylinux1_x86_64.whl
    $ pip install pyarmor-8.4.1.tar.bgz

Next start ``pyarmor-auth`` to listen the request from docker containers::

    $ pyarmor-auth pyarmor-device-regfile-6000.1.zip

    2023-06-24 09:43:14,939: work path: /root/.pyarmor/docker
    2023-06-24 09:43:14,940: register "pyarmor-device-regfile-6000.1.zip"
    2023-06-24 09:43:15,016: listen container auth request on 0.0.0.0:29092

Do not close this console, open another console to run dockers.

For Linux container run it with extra ``--add-host=host.docker.internal:host-gateway``::

    $ docker run -it --add-host=host.docker.internal:host-gateway python bash

    root@86b180b28a50:/# python --version
    Python 3.11.4
    root@86b180b28a50:/#

In docker host open third console to copy files to container::

    $ docker cp pyarmor-8.4.1.tar.gz 86b180b28a50:/
    $ docker cp pyarmor.cli.core-5.4.1-cp311-none-manylinux1_x86_64.whl 86b180b28a50:/
    $ docker cp pyarmor-device-regfile-6000.1.zip 86b180b28a50:/

In docker container, register Pyarmor with same device regfile. For example::

    root@86b180b28a50:/# pip install pyarmor.cli.core-5.4.1-cp311-none-manylinux1_x86_64.whl
    root@86b180b28a50:/# pip install pyarmor-8.4.1.tar.gz
    root@86b180b28a50:/# pyarmor reg pyarmor-device-regfile-6000.1.zip
    root@86b180b28a50:/# pyarmor -v

If everything is fine, it should print group license information. And then test it with simple script::

    root@86b180b28a50:/# echo "print('hello world')" > foo.py
    root@86b180b28a50:/# pyarmor gen --enable-rft foo.py

When need to verify license, the docker container will send request to docker host. The `pyarmor-auth` console should print auth request from docker container, if there is no any request, please check docker network configuration, make sure IPv4 addresses of docker host and container are in the same network. For example, in docker container::

   root@86b180b28a50:/# ifconfig -a

   eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
         inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
   ...

In docker host::

   $ ifconig -a
   docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
            inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
   ...

**MacOS Docker Host**

There is a little difference when docker host is MacOS, because docker container is running in Linux VM, not in MacOS directly.

So one solution is running `pyarmor-auth` in Linux VM, in this case, it should take this Linux VM as offline device, and generate device regfile for this Linux VM, not for **MacOS**, and start docker container with extra options::

    $ docker run --add-host=host.docker.internal:172.17.0.1 ...

In this case, it may need some extra configuration for Linux VM to make sure the machine id could be fixed.

Refer to `issue 1542`__ for more information.

__ https://github.com/dashingsoft/pyarmor/issues/1542

**Windows Docker Host**

For Windows docker host, first check Windows network configuration::

  C:> ipconfig

  Ethernet adapter vEthernet (WSL):

       Connection-specific DNS Suffix  . :
       Link-local IPv6 Address . . . . . : fe80::8984:457:2335:588e%28
       IPv4 Address. . . . . . . . . . . : 172.22.32.1
       Subnet Mask . . . . . . . . . . . : 255.255.240.0
       Default Gateway . . . . . . . . . :

If there is IPv4 Address, for example ``172.22.32.1``, which is in the same network as docker container, it's simple. Just take this Windows as offline device, and run `pyarmor-auth` on it, then start docker container with extra options::

    $ docker run --add-host=host.docker.internal:172.22.32.1 ...

Anyway, `pyarmor-auth` must listen on any IPv4 address which is in the same network as docker container.

If there is no available IPv4 address in Windows, the other solution is running `pyarmor-auth` in WSL, in this case, WSL should be taken as offline device.

**When something is wrong**

1. Check docker container network:

.. code-block:: bash

   root@86b180b28a50:/# ifconfig -a

   eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
         inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
   ...

   root@86b180b28a50:/# ping host.docker.internal
   PING host.docker.internal (172.17.0.1) 56(84) bytes of data.
   64 bytes from host.docker.internal (172.17.0.1): icmp_seq=1 ttl=64 time=0.048 ms
   ...

If `ping` doesn't works, please check docker host network. If docker host is MacOS, it also checks Linux VM network. If docker host is Windows, also check WSL network.

And make sure IPv4 address of `host.docker.internal` is in same network as `eth0` which IPv4 address is `172.17.0.2`. In above example, it's `172.17.0.1`, so it's OK.

If not, also check docker host network. If docker host is MacOS, it may need run `pyarmor-auth` in Linux VM, not MacOS. If docker host is Windows, it may need run `pyarmor-auth` in WSL, not Windows.

Anyway, please configure the docker host/container network so that `pyarmor-auth` could listen in any IPv4 address which is in the same network as docker container.

2. Check docker host to make sure group license works::

   $ pyarmor -d reg pyarmor-device-regfile-6000.1.zip
   $ pyarmor -v

If run `pyarmor-auth` in Linux VM or WSL, please check group license could work in Linux VM or WSL. It may need generate new device regfile for Linux VM or WSL.

Using multiple Pyarmor Licenses in same device
==============================================

Generally the registration information is sotred in the Pyarmor :term:`Home Path`, the default value is :file:`~/.pyarmor`. It means

- All Python virtual environments share same registration information
- It may not work to register other Pyarmor license in same device

When need many Pyarmor Licenses in one machine, set each license to different path. For example::

    $ pyarmor --home ~/.pyarmor1 reg pyarmor-regfile-2051.zip
    $ pyarmor --home ~/.pyarmor1 gen project1/foo.py

    $ pyarmor --home ~/.pyarmor2 reg pyarmor-regfile-2052.zip
    $ pyarmor --home ~/.pyarmor2 gen project2/foo.py

What need to do after upgrading Pyarmor
=======================================

Generally it need do nothing after upgrading Pyarmor, the registration information still works.

But in the following versions something is changed

- **Pyarmor 8.0**

  Old license for Pyarmor 7 doesn't work

  - Some old licenses can be upgraded to Basic License freely, refer to :ref:`upgrade old license <upgrading old license>`
  - Old license can't be upgraded to Pro or Group License

- **Pyarmor 9.0**

  A big change about using Pyarmor in CI/CD pipeline

  - :term:`Pyarmor Basic`

    - :ref:`upgrade to pyarmor 9` freely
    - If using Pyarmor in CI/CD pipeline, refer to :doc:`ci`

  - :term:`Pyarmor Pro`

    - If not using Pyarmor in CI/CD pipeline, :ref:`upgrade to pyarmor 9` freely
    - If using Pyarmor in CI/CD pipeline, 2 choices

      - Still use Pyarmor 8.x as before
      - Upgrade to Pyarmor 9, it need upgrade :term:`Pyarmor Pro` to :term:`Pyarmor CI`

        - :term:`Pyarmor CI` is paid per year
        - Please contact pyarmor@163.com if need upgrade to :term:`Pyarmor CI`

  - :term:`Pyarmor Group`

    It need generate device regfile for each offline device again by Pyarmor 9.0+, refer to :ref:`upgrade to pyarmor 9`

.. _upgrading old license:

Upgrading old license
---------------------

Not all the old license (Pyarmor 7) could be upgraded to latest version.

The old license could be upgraded to Pyarmor Basic freely only if it matches these conditions:

* Following new `Pyarmor EULA`_
* The license no. starts with ``pyarmor-vax-``
* The original activation file ``pyarmor-regcode-xxxx.txt`` exists and isn't used more than 100 times
* The old license is purchased before June 1, 2023. In principle, the old license purchased after Pyarmor 8 is available could not be upgraded to new license.

If failed to upgrade the old license, please purchase new license to use Pyarmor latest version.

The old license can't be upgraded to Pyarmor Pro and Group.

**Upgrading old license to Pyarmor Basic**

First find the activation file ``pyarmor-regcode-xxxx.txt``, which is sent to registration email when purchasing the license.

Next install Pyarmor 8.2+, according to new `EULA of Pyarmor`_, each license is only for one product.

Assume this license will be used to obfuscate product ``XXX``, run this command::

    $ pyarmor reg -u -p "XXX" pyarmor-regcode-xxxx.txt

Check the upgraded license information::

    $ pyarmor -v

After upgrade successfully, do not use activation file ``pyarmor-regcode-xxxx.txt`` again, it's invalid now. A new :term:`registration file` like :file:`pyarmor-regfile-xxxx.zip` will be generated at the same time.

In other devices using this new :term:`registration file` to register Pyarmor by this command::

    $ pyarmor reg pyarmor-regfile-xxxx.zip

After successful registration, all obfuscations will automatically apply this license, and each obfuscation requires online license verification.

If old license is used by many products (mainly old personal license), only one product could be used after upgrading. For the others, it need purchase new license.

.. _upgrade to pyarmor 9:

Upgrade to Pyarmor 9
--------------------

1. :term:`Pyarmor Basic` and :term:`Pyarmor Pro`

   **If Pyarmor License has been registered in this device**

   - First upgrade to Pyarmor 9::

         $ pip install -U pyarmor

   - When first time to obfuscate scripts, it will show hints::

         $ pyarmor gen foo.py

         ...
         Pyarmor 9 has big change on CI/CD pipeline
         If not using Pyarmor License in CI/CD pipeline
         Press "c" to continue
         Otherwise press "h" to check Pyarmor 9.0 Upgrade Notes

         Continue (c), Help (h), Quit (q):

   - Just press :kbd:`c` to continue, there is no prompt later

   **If Pyarmor License isn't registered in this device**

   - First use :term:`activation file` to generate new :term:`registration file`::

         $ pip install -U pyarmor

         # Please replace XXX with real product name
         $ pyarmor reg -p XXX pyarmor-regcode-xxxx.txt

   - Save and backup new :term:`registration file` ``pyarmor-regfile-xxxx.zip``

   - Use this new regfile to register Pyarmor in other new device::

         $ pyarmor reg pyarmor-regfile-xxxx.zip
         $ pyarmor -v

   If :term:`activation file` is used too many times, please first install Pyarmor 8, then upgrade to Pyarmor 9

2. :term:`Pyarmor Group` License

   It need generate device regfile again with Pyarmor 9.0+

   - First upgrade to Pyarmor 9::

         $ pip install -U pyarmor

   - Then generate device regfile as before

     For example, generate device regfile ``pyarmor-device-regfile-6000.1.zip`` for device no. 1::

         $ pyarmor reg -g 1 /path/to/pyarmor-regfile-6000.zip

  - Finally, use new one to register Pyarmor in offline device::

         $ pyarmor reg pyarmor-device-regfile-6000.1.zip

.. include:: ../_common_definitions.txt
