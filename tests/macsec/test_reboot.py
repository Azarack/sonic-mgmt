'''This script is to test the device reboot behavior for SONiC.

Test 1: Line Card
Step 1: Configure Macsec between neighbor and DUT
Step 2: Save config on DUT and reboot the line card
Step 3: Verify macsec connection is re-established after reboot

Test 2: Chassis
Step 1: Configure Macsec between neighbor and DUT
Step 2: Save config on DUT and reboot the chassis
Step 3: Verify macsec connection is re-established after reboot

'''

import logging
import pytest
import re
import time
from tests.common import reboot
from tests.common.helpers.assertions import pytest_assert
from tests.common.utilities import wait_until

logger = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.topology('t2')
]


def get_macsec_sessions(dut, space_var):
    out = dut.shell("show macsec{}".format(space_var))['stdout']
    sess_list = []
    regex = re.compile(r"\s*MACsec port\((.+)\)")
    count = 0
    for line in out.splitlines():
        if "MACsec port" in line:
            temp_sess = regex.match(line).group(1)
            count = 0
        elif count == 3:
            if "true" in line:
                sess_list.append(temp_sess)
        count = count + 1
    logger.info("macsec sessions: " + str(sess_list))
    return sess_list.sort()


@pytest.mark.reboot
def test_lc_reboot(duthosts, localhost, enum_frontend_dut_hostname):
    duthost = duthosts[enum_frontend_dut_hostname]
    if not duthost.is_macsec_capable_node():
        pytest.skip("DUT must be a MACSec enabled device.")
    dut_lldp_table = duthost.shell("show lldp table")['stdout'].split("\n")
    dut_to_neigh_int = dut_lldp_table[3].split()[0]
    if duthost.is_multi_asic:
        asic_index = duthost.get_port_asic_instance(dut_to_neigh_int).asic_index
        space_var = " -n {}".format(asic_index)
    else:
        asic_index = None
        space_var = ""
    duthost.command("config save -y")
    pre_list = get_macsec_sessions(duthost, space_var)
    reboot(duthost, localhost, wait=240)

    # wait extra for macsec to establish
    wait_until(120, 10, 0, lambda: duthost.iface_macsec_ok(dut_to_neigh_int))
    logger.debug(f"iface macsec: {duthost.iface_macsec_ok(dut_to_neigh_int)}")
    time.sleep(30)

    out = duthost.shell("show macsec{}".format(space_var))['stdout']
    logger.debug(f"full macsec status: {out}")

    macsec_status = duthost.shell("show macsec{} {}".format(space_var, dut_to_neigh_int))['stdout'].splitlines()
    logger.debug(f"macsec status {macsec_status}")
    assert macsec_status
    assert dut_to_neigh_int in macsec_status[0]
    assert "true" in macsec_status[3]

    # Ensure all sessions came back after reboot
    post_list = get_macsec_sessions(duthost, space_var)
    assert pre_list == post_list


@pytest.mark.reboot
def test_chassis_reboot(duthosts, localhost, enum_supervisor_dut_hostname, duthost):
    rphost = duthosts[enum_supervisor_dut_hostname]
    if not duthost.is_macsec_capable_node():
        pytest.skip("DUT must be a MACSec enabled device.")
    dut_lldp_table = duthost.shell("show lldp table")['stdout'].split("\n")[3].split()
    dut_to_neigh_int = dut_lldp_table[0]
    if duthost.is_multi_asic:
        asic_index = duthost.get_port_asic_instance(dut_to_neigh_int).asic_index
        space_var = " -n {}".format(asic_index)
    else:
        asic_index = None
        space_var = ""
    rphost.shell("config save -y")
    pre_list = get_macsec_sessions(duthost, space_var)
    reboot(rphost, localhost, wait=240)

    # wait extra for macsec to establish
    wait_until(120, 10, 0, lambda: duthost.iface_macsec_ok(dut_to_neigh_int))
    logger.debug(f"iface macsec: {duthost.iface_macsec_ok(dut_to_neigh_int)}")
    time.sleep(30)
    macsec_status = duthost.shell("show macsec{} {}".format(space_var, dut_to_neigh_int))['stdout'].splitlines()
    logger.debug(f"macsec status {macsec_status}")
    pytest_assert(dut_to_neigh_int in macsec_status[0])
    logger.debug(f"enabled line {macsec_status[3]}")
    pytest_assert("true" in macsec_status[3])

    # Ensure all sessions came back after reboot
    post_list = get_macsec_sessions(duthost, space_var)
    assert pre_list == post_list
