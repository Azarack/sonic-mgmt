import pytest
import logging

from tests.common.reboot import reboot
from tests.common.utilities import wait_until
from tests.common.platform.interface_utils import \
    check_interface_status_of_up_ports
from tests.common.platform.processes_utils import wait_critical_processes
from tests.macsec.macsec_helper import check_appl_db


logger = logging.getLogger(__name__)
post_reboot_time = 240

pytestmark = [
    pytest.mark.macsec_required,
    pytest.mark.topology("any")
]


def compare_bgp_routes(v4_rt_cnt_1, v6_rt_cnt_1, v4_rt_cnt_2, v6_rt_cnt_2):
    logger.info("IPv4 routes: pre-reboot {} post-reboot {}".format(
        v4_rt_cnt_1, v4_rt_cnt_2))
    logger.info("IPv6 routes: pre-reboot {} post-reboot {}".format(
        v6_rt_cnt_1, v6_rt_cnt_2))
    return v4_rt_cnt_1 == v4_rt_cnt_2 and v6_rt_cnt_1 == v6_rt_cnt_2


def get_bgp_routes(duthost):
    sumv4, sumv6 = duthost.get_ip_route_summary(skip_kernel_tunnel=True)
    totalsv4 = sumv4.get('Totals', {})
    totalsv6 = sumv6.get('Totals', {})
    routesv4 = totalsv4.get('routes', 0)
    routesv6 = totalsv6.get('routes', 0)
    return routesv4, routesv6


@pytest.fixture(scope='module')
def setup(request, tbinfo, duthosts, rand_one_dut_hostname):
    duthost = duthosts[rand_one_dut_hostname]

    setup_info = {
        'duthost': duthost
    }

    logger.info('Setup_info: {}'.format(setup_info))

    yield setup_info


@pytest.mark.disable_loganalyzer
def test_switch_reboot(setup, localhost, ctrl_links, policy, cipher_suite, send_sci):
    """
     This test case reboot dut, wait for critical porcesses then ensure all
     interfaces are up, Check appl_db and that route summary count are equal
     pre and post reboot.
    """
    duthost = setup['duthost']

    pre_reboot_sumv4, pre_reboot_sumv6 = get_bgp_routes(duthost)

    reboot(duthost, localhost, wait=post_reboot_time)

    wait_critical_processes(duthost)

    assert wait_until(300, 60, 0, check_interface_status_of_up_ports,
                      duthost), "Could not confirm interface status up \
                        on all any/all ports"

    assert wait_until(300, 6, 12, check_appl_db, duthost, ctrl_links, policy,
                      cipher_suite, send_sci)

    post_reboot_sumv4, post_reboot_sumv6 = get_bgp_routes(duthost)

    compare_bgp_routes(pre_reboot_sumv4, pre_reboot_sumv6,
                       post_reboot_sumv4, post_reboot_sumv6)