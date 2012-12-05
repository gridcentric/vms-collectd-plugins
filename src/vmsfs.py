import os
import collectd

PLUGIN_STATS = {
    'memory_resident'  : ('cur_resident', 'bytes', 4096.0),
    'memory_allocated' : ('cur_allocated', 'bytes', 4096.0)
}

def vmsfs_stats_read(filename):
    stats = {}

    # Open vmsfs sys info
    stats_fd = None
    try:
        stats_fd = open(filename)

        for line in stats_fd:
            tokens = line.split()
            stats[tokens[0][0:-1]] = float(tokens[1])

    except:
        if stats_fd:
            close(stats_fd)

    return stats

def vmsfs_dispatch_one(name, type, value):
    val = collectd.Values(plugin='vmsfs')
    val.type = type
    val.type_instance = name
    val.values = [value]
    val.dispatch()

def vmsfs_stats_dispatch(prefix, filename):
    stats = vmsfs_stats_read(filename)

    for collectd_name in PLUGIN_STATS:
        name = PLUGIN_STATS[collectd_name][0]
        type = PLUGIN_STATS[collectd_name][1]
        scale = PLUGIN_STATS[collectd_name][2]
        if name in stats:
            vmsfs_dispatch_one(prefix + '.' + collectd_name, type, 
                               stats[name] * scale)

def vmsfs_collectd_read():
    # Dispatch total stats
    vmsfs_stats_dispatch('totals', '/sys/fs/vmsfs/stats')

    # Dispatch per-generation stats
    TO_IGNORE = ('stats', 'version', '00000000-0000-0000-0000-000000000000')
    files = os.listdir('/sys/fs/vmsfs')
    for f in files:
        if f not in TO_IGNORE:
            vmsfs_stats_dispatch('generation.' + f, '/sys/fs/vmsfs/' + f)

collectd.register_read(vmsfs_collectd_read)
