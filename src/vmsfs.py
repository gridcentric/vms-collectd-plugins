import os
import collectd

PLUGIN_STATS = {
    'resident'  : ('cur_resident', 'memory', 4096.0),
    'allocated' : ('cur_allocated', 'memory', 4096.0)
}

def vmsfs_stats_read(filename):
    stats = {}

    # Open vmsfs sys info.
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

def vmsfs_dispatch_one(name, value, type):
    val = collectd.Values(plugin='vmsfs')
    val.type = type
    val.type_instance = name
    val.values = [value]
    val.dispatch()

def vmsfs_stats_dispatch(filename, prefix=''):
    stats = vmsfs_stats_read(filename)

    for collectd_name in PLUGIN_STATS:
        name = PLUGIN_STATS[collectd_name][0]
        type = PLUGIN_STATS[collectd_name][1]
        scale = PLUGIN_STATS[collectd_name][2]
        if name in stats:
            vmsfs_dispatch_one(prefix + collectd_name, stats[name] * scale, type=type)

def vmsfs_collectd_read():
    # Dispatch total stats.
    vmsfs_stats_dispatch('/sys/fs/vmsfs/stats')

    # Dispatch per-generation stats.
    # NOTE: We do not currently report the per-generation statistics to collectd.
    # This is because we do not have a good strategy for aggregating generation
    # data and exposing it in a sensible way. There are two strategies:
    #  1) Collect everything at the host level.
    #     The problem here is that the number of metrics will explode for that
    #     that individual host (and keep growing).
    #  2) Collect at the top-level (one virtual host per generation).
    #     Then the problem is finding the generation through UI tools, etc.
    #  3) Figure out some way to put the stats in each instance associated
    #     with that generation.
    # I favor (2) currently, but there's not much value in implementing it until
    # it can be exposed to the user.
    if False:
        TO_IGNORE = ('stats', 'version', '00000000-0000-0000-0000-000000000000')
        files = os.listdir('/sys/fs/vmsfs')
        for f in files:
            if f not in TO_IGNORE:
                vmsfs_stats_dispatch('/sys/fs/vmsfs/' + f, prefix=("%s:" % f))

collectd.register_read(vmsfs_collectd_read)
