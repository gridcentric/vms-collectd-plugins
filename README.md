Overview
========

This files implement basic plugins for `collectd`, the system statistics
collection daemon. Because `collectd` supports store or sending statistics in
many different ways, this allows users of VMS to gain insights into how the
technology is performing using a variety of graphing and analysis tools.

Installation
============

Copy the files `src/vmsdoms.py` and `src/vmsfs.py` to the collectd module
`/usr/lib/collectd` path on your system. Normally this path is
`/usr/lib/collectd` but it may be different on your system.

If you are using VMS with the KVM hypervisor, you may also copy `src/vmsfs.py`
to the collectd module path for some additional statistics.

Finally, edit the file `/etc/collectd/collectd.conf` to load the module. In a
minimal configuration, this would look like:

    <LoadPlugin python>
      Globals true
    </LoadPlugin>
    <Plugin python>
      ModulePath "/usr/lib/collectd/"
      Import "vmsdoms"
      Import "vmsfs"
    </Plugin>

To register statistics for individual VMs, you will probably also want:

    LoadPlugin libvirt

Usage with Graphite
===================

You may have other python modules loaded or different ways of sending data
using `collectd`.  If you are using `collectd` with graphite, the relevant
portion of your `/etc/collectd/collectd.conf` file would look like:

    <LoadPlugin python>
      Globals true
    </LoadPlugin>

    <Plugin python>
      ModulePath "/usr/lib/collectd/"
      Import "vmsdoms"
      Import "vmsfs"
      Import "carbon_writer"

      <Module "carbon_writer">
        LineReceiverHost "my-stats-server"
        LineReceiverPort 2003
        DifferentiateCountersOverTime true
        LowercaseMetricNames true
        TypesDB "/usr/share/collectd/types.db"
      </Module>
    </Plugin>
