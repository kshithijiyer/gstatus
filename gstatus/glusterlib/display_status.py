from shutil import get_terminal_size
import pydoc

def display_status(data):
    """Print the status of GlusterFS cluster"""

    columns, rows = get_terminal_size((80, 20))
    status_str = _build_status(data)
    if status_str.count('\n') > rows:
        pydoc.pager(status_str)
    else:
        print(status_str)

def _build_status(data):
    version = data.glusterfs_version
    vols = ''

    # Cluster information
    cluster = "\nCluster:\n"
    cluster += "\t Status: %s \t\t GlusterFS: %s\n"%(data.cluster_status,
                                                     version)
    cluster += "\t Nodes: %d/%d \t\t\t Volumes: %d/%d\n\n"%\
               (data.nodes_reachable,
                data.nodes,
                data.volumes_started,
                data.volume_count)

    # Volume information
    if data.volume_count:
        vols = "Volumes: \n"

        for v in data.volume_data:
            health = health_display = ''
            try:
                vol_status = v['status']
                if vol_status.lower() == 'started':
                    health = "%s"%v['health']
                    health_display = "(%s)"%health.upper()

                vols += " {:>15}   {:>25} {:>16} {}".format(v['name'],
                                                            v['type'].\
                                                            capitalize(),
                                                            vol_status,
                                                            health_display)
                if vol_status.lower() == 'started' and health.lower() != 'down':
                    vols += " - %d/%d Bricks Up"%(v['online'], v['num_bricks'])
                    vols += " %s\n"%(v['voltype'])
                    vols += "{:>53} Capacity: ({:>}% used) {}/{} (used/total)\n".\
                            format(
                                ' ',
                                v['v_used_percent'],
                                v['v_size_used'],
                                v['v_size'])
                    if v['snapshot_count'] > 0:
                        vols += "{:>53} Snapshots: {:>}\n".format(' ', v['snapshot_count'])

                    # Snapshot information
                    if v['snapshot_count'] > 0 and (data.displaysnap or data.detail):
                        for snap in v['snapshots']:
                            vols += "{:>56} Name:   {}\n".format(' ', snap['name'])
                            vols += "{:>56} Status: {} {:>4} Created On: {}\n".\
                                    format(' ', snap['status'], ' ',
                                           snap['create_time'])

                    # Brick information
                    if data.brickinfo or data.detail:
                        vols += "{:>53} Bricks:\n".format(' ')
                        for subvol in v['subvols']:
                            dist_group = int(subvol['name'][-1]) + 1
                            vols += "{:>56} {}:\n".format(' ', "Distribute Group "+str(dist_group))
                            for brick in subvol['bricks']:
                                status = 'Online' if brick['online'] else 'Offline'
                                vols += "{:>59} {}   ({})\n".format(' ',
                                                                brick['name'],
                                                                status)

                    # Quota infomration
                    if v['quota'] and (data.detail or data.displayquota) and v['quota_list']:
                        vols += "{:>53} Quota List:\n".format(' ')
                        for quota in v['quota_list']:
                            vols += "{:>56} Path: {}\n".format(' ', quota['path'])
                            vols += "{:>60} Hard-limit: {:<15} {:>4}  \
Soft-limit(%): {}\n".\
                                    format(' ', quota['hard_limit'], ' ',
                                           quota['soft_limit_percent'])
                            vols += "{:>60} Used: {:<13}  {:>12} Avail: {}\n".\
                                    format(' ', quota['used_space'], ' ',
                                           quota['avail_space'])
                            vols += "{:>60} Soft-limit Exceeded?: {} {:>7}  "\
                                    "Hard-limit Exceeded?: {}\n".\
                                    format(' ', quota['sl_exceeded'], ' ',
                                           quota['hl_exceeded'])
                    elif v['quota']:
                        vols += "{:>53} Quota: {:>}\n".format(' ', v['quota'])
                else:
                    vols += "\n"

                if vol_status.lower() == 'started' and health.lower() != 'up':
                    vols += "{:>53} {}".format(' ', 'Note: glusterd/glusterfsd '
                                               'is down in one or more nodes.'
                                               '\n')
                if vol_status.lower() == 'started' and \
                   (health.lower() == 'partial' or \
                    health.lower() == 'degraded'):
                    vols += "{:>59} {}".format(' ', 'Sizes might not be '
                                               'accurate.\n')

                vols += "\n"
            except:
                raise
    return(cluster+vols)



