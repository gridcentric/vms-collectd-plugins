import vms
import collectd

# This is required to fix insanity (IOERROR no child processes on file close?)
# if this happens deep inside the VMS code. We currently have no idea why this
# happens, but when this import is done here the problem seems to disappear.
import platform
platform.machine()

PLUGIN_STATS = {
    'nominal' : ('pages', 'memory', 4096.0),
    'current' : ('memory.current', 'memory', 4096.0),
    'clean'   : ('memory.clean', 'memory', 4096.0),
    'dirty'   : ('dirty', 'memory', 4096.0),
    'limit'   : ('memory.limit', 'memory', 4096.0),
    'target'  : ('memory.target', 'memory', 4096.0),
    'shared'  : ('memory.shared', 'memory', 4096.0),
}

def vms_dispatch_one(name, value, type, host=None):
    val = collectd.Values(plugin='vms')
    val.type = type
    val.type_instance = name
    val.values = [value]
    if host != None:
        val.host = host
    val.dispatch()

def vms_collectd_read():
    vms.virt.init()
    hypervisor = vms.virt.AUTO.Hypervisor()

    # Get list of domains and iterate.
    domains = hypervisor.domain_list()
    vms_domains = []
    count = 0

    # Pre filter VMS domains.
    for d in domains:
        # Skip non-VMS domains.
        if not vms.control.exists(d):
            continue

        # Grab a control connection.
        dom = hypervisor.domain_lookup(d)
        if dom is None:
            continue
    	ctrl = dom._wait_for_control(wait=False)
        if ctrl is None:
            continue
 
        try:
            # Skip ghost domains.
            if ctrl.get('gd.isghost') == '1':
                continue
        except vms.control.ControlException:
            continue

        vms_domains.append((dom, ctrl))
        count += 1

    vms_dispatch_one('domains', count, type='absolute')

    # For each stat,
    for stat in PLUGIN_STATS:
        key = PLUGIN_STATS[stat][0]
        type = PLUGIN_STATS[stat][1]
        scale = PLUGIN_STATS[stat][2]
        total = 0

        # For each domain, 
        for dom, ctrl in vms_domains:
            try:
                # Get value and scale.
                value = float(ctrl.get(key)) * scale
            except vms.control.ControlException:
                continue

            # Dispatch.
            vms_dispatch_one(stat, value, type=type, host=dom.name())

            # Add to total.
            total = total + value

        # Dispatch total value.
        vms_dispatch_one(stat, total, type=type)

collectd.register_read(vms_collectd_read)
