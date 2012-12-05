import vms
import collectd

PLUGIN_STATS = {
    'memory_nominal' : ('pages', 'bytes', 4096.0),
    'memory_current' : ('memory.current', 'bytes', 4096.0)
}

hypervisor = None

def vms_collectd_init():
    global hypervisor
    vms.virt.init()
    hypervisor = vms.virt.AUTO.Hypervisor()

def vms_dispatch_one(name, type, value):
    val = collectd.Values(plugin='vms')
    val.type = type
    val.type_instance = name
    val.values = [value]
    val.dispatch()

def vms_collectd_read():
    # Get list of domains and iterate
    domains = hypervisor.domain_list()
    vms_domains = []
    count = 0

    # Pre filter VMS domains
    for d in domains:
        # Skip non-VMS domains
        if not vms.control.exists(d):
            continue

        # Skip ghost domains
        if vms.commands.get(d, 'gd.isghost')[0] == '1':
            continue

        vms_domains.append(d)
        count += 1

    vms_dispatch_one('totals.vm_count', 'absolute', count)

    # For each stat,
    for stat in PLUGIN_STATS:
        key = PLUGIN_STATS[stat][0]
        type = PLUGIN_STATS[stat][1]
        scale = PLUGIN_STATS[stat][2]
        total = 0

        # For each domain, 
        for d in vms_domains:
            # Get value and scale
            value = float(vms.commands.get(d, key)[0]) * scale

            # Dispatch
            vms_dispatch_one('domains.' + str(d) + '.' + stat,
                             type, value)

            # Add to total
            total = total + value

        # Dispatch total value
        vms_dispatch_one('totals.' + stat, type, total)

collectd.register_init(vms_collectd_init)
collectd.register_read(vms_collectd_read)
