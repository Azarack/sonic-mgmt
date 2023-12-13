'''

The test case will verify that forcing a macsec key refresh behaves as intended.

Step 1: 
Step 2: 
Step 3: 
Step 3: 
Step 4: 
Step 5: 


'''
import logging

import pytest
import time
# import textfsm
from tests.common.config_reload import config_reload

logger = logging.getLogger(__name__)
# dut_4byte_asn = 400003
# neighbor_4byte_asn = 400001
# bgp_sleep = 60
# bgp_id_textfsm = "./bgp/templates/bgp_id.template"

pytestmark = [
    pytest.mark.topology('t2')
]


@pytest.fixture(scope='module')
def setup(tbinfo, nbrhosts, duthosts, enum_frontend_dut_hostname, enum_rand_one_frontend_asic_index, request):
    # verify neighbors are type sonic
    if request.config.getoption("neighbor_type") != "sonic":
        pytest.skip("Neighbor type must be sonic")
    duthost = duthosts[enum_frontend_dut_hostname]
    asic_index = enum_rand_one_frontend_asic_index
    namespace = duthost.get_namespace_from_asic_id(asic_index)
    dut_asn = tbinfo['topo']['properties']['configuration_properties']['common']['dut_asn']
    tor1 = duthost.shell("show lldp table")['stdout'].split("\n")[3].split()[1]
    tor2 = duthost.shell("show lldp table")['stdout'].split("\n")[5].split()[1]

    tor_neighbors = dict()
    skip_hosts = duthost.get_asic_namespace_list()
    bgp_facts = duthost.bgp_facts(instance_id=asic_index)['ansible_facts']
    neigh_asn = dict()

    # verify sessions are established and gather neighbor information
    for k, v in bgp_facts['bgp_neighbors'].items():
        if v['description'].lower() not in skip_hosts:
            if v['description'] == tor1:
                if v['ip_version'] == 4:
                    neigh_ip_v4 = k
                    peer_group_v4 = v['peer group']
                elif v['ip_version'] == 6:
                    neigh_ip_v6 = k
                    peer_group_v6 = v['peer group']
            if v['description'] == tor2:
                if v['ip_version'] == 4:
                    neigh2_ip_v4 = k
                elif v['ip_version'] == 6:
                    neigh2_ip_v6 = k
            assert v['state'] == 'established'
            neigh_asn[v['description']] = v['remote AS']
            tor_neighbors[v['description']] = nbrhosts[v['description']]["host"]

    dut_ip_v4 = tbinfo['topo']['properties']['configuration'][tor1]['bgp']['peers'][dut_asn][0]
    dut_ip_v6 = tbinfo['topo']['properties']['configuration'][tor1]['bgp']['peers'][dut_asn][1]

    dut_ip_bgp_sum = duthost.shell('show ip bgp summary')['stdout']
    neigh_ip_bgp_sum = nbrhosts[tor1]["host"].shell('show ip bgp summary')['stdout']
    neigh2_ip_bgp_sum = nbrhosts[tor1]["host"].shell('show ip bgp summary')['stdout']
    with open(bgp_id_textfsm) as template:
        fsm = textfsm.TextFSM(template)
        dut_bgp_id = fsm.ParseText(dut_ip_bgp_sum)[0][0]
        neigh_bgp_id = fsm.ParseText(neigh_ip_bgp_sum)[1][0]
        neigh2_bgp_id = fsm.ParseText(neigh2_ip_bgp_sum)[1][0]

    dut_ipv4_network = duthost.shell("show run bgp | grep 'ip prefix-list'")['stdout'].split()[6]
    dut_ipv6_network = duthost.shell("show run bgp | grep 'ipv6 prefix-list'")['stdout'].split()[6]
    neigh_ipv4_network = nbrhosts[tor1]["host"].shell("show run bgp | grep 'ip prefix-list'")['stdout'].split()[6]
    neigh_ipv6_network = nbrhosts[tor1]["host"].shell("show run bgp | grep 'ipv6 prefix-list'")['stdout'].split()[6]

    setup_info = {
        'duthost': duthost,
        'neighhost': tor_neighbors[tor1],
        'neigh2host': tor_neighbors[tor2],
        'tor1': tor1,
        'tor2': tor2,
        'dut_asn': dut_asn,
        'neigh_asn': neigh_asn[tor1],
        'neigh2_asn': neigh_asn[tor2],
        'asn_dict':  neigh_asn,
        'neighbors': tor_neighbors,
        'namespace': namespace,
        'dut_ip_v4': dut_ip_v4,
        'dut_ip_v6': dut_ip_v6,
        'neigh_ip_v4': neigh_ip_v4,
        'neigh_ip_v6': neigh_ip_v6,
        'neigh2_ip_v4': neigh2_ip_v4,
        'neigh2_ip_v6': neigh2_ip_v6,
        'peer_group_v4': peer_group_v4,
        'peer_group_v6': peer_group_v6,
        'asic_index': asic_index,
        'dut_bgp_id': dut_bgp_id,
        'neigh_bgp_id': neigh_bgp_id,
        'neigh2_bgp_id': neigh2_bgp_id,
        'dut_ipv4_network': dut_ipv4_network,
        'dut_ipv6_network': dut_ipv6_network,
        'neigh_ipv4_network': neigh_ipv4_network,
        'neigh_ipv6_network': neigh_ipv6_network
    }

    logger.info("DUT BGP Config: {}".format(duthost.shell("show run bgp", module_ignore_errors=True)['stdout']))
    logger.info("Neighbor BGP Config: {}".format(nbrhosts[tor1]["host"].shell("show run bgp")['stdout']))
    logger.info('Setup_info: {}'.format(setup_info))

    yield setup_info

    # restore config to original state
    config_reload(duthost)
    config_reload(tor_neighbors[tor1], is_dut=False)

    # verify sessions are established
    bgp_facts = duthost.bgp_facts(instance_id=asic_index)['ansible_facts']
    for k, v in bgp_facts['bgp_neighbors'].items():
        if v['description'].lower() not in skip_hosts:
            logger.debug(v['description'])
            assert v['state'] == 'established'


def test_forced_key_refresh(setup):
    cmd = 'vtysh -n {}'