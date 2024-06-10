import ipaddress
import os
import subprocess
import time
import logging
import json

from sonic_py_common import device_info
from tests.common.utilities import wait_until

TC_NAME = "ACL Basics"
LC0 = "Sonic-C8808-T2-1-LC0"
LC2 = "Sonic-C8808-T2-1-LC2"
CHASSIS_DUTS = [LC0, LC2]
DUTS = [CHASSIS_DUTS]
SONIC_CONFIG_RELOAD = False

LC0_INGRESS_SRC = {
    'name':"LC0_INGRESS_SRC_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212.0.0.0-212.0.1.0/24",
    'deny_rules':"212.0.2.0-212.0.3.0/24",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_SRC_V6 = {
    'name':"LC0_INGRESS_SRC_IPV6",
    'policy_desc':"ingress_LC0_V6",
    'type':"L3V6",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212::-212:0:0:1::/64",
    'deny_rules':"212:0:0:2::-212:0:0:3::/64",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_EGRESS_SRC = {
    'name':"LC0_EGRESS_SRC_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215.0.4.0-215.0.5.0/24",
    'deny_rules':"215.0.6.0-215.0.7.0/24",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_SRC_V6 = {
    'name':"LC0_EGRESS_SRC_IPV6",
    'policy_desc':"egress_LC0_V6",
    'type':"L3V6",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215:0:0:4::-215:0:0:5::/64",
    'deny_rules':"215:0:0:6::-215:0:0:7::/64",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_INGRESS_SRC = {
    'name':"LC2_INGRESS_SRC_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215.0.2.0-215.0.3.0/24",
    'deny_rules':"215.0.0.0-215.0.1.0/24",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_INGRESS_SRC_V6 = {
    'name':"LC2_INGRESS_SRC_IPV6",
    'policy_desc':"ingress_LC2_V6",
    'type':"L3V6",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215:0:0:2::-215:0:0:3::/64",
    'deny_rules':"215::-215:0:0:1::/64",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_SRC = {
    'name':"LC2_EGRESS_SRC_IP",
    'policy_desc':"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212.0.6.0-212.0.7.0/24",
    'deny_rules':"212.0.4.0-212.0.5.0/24",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_EGRESS_SRC_V6 = {
    'name':"LC2_EGRESS_SRC_IPV6",
    'policy_desc':"egress_LC2_V6",
    'type':"L3V6",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212:0:0:6::-212:0:0:7::/64",
    'deny_rules':"212:0:0:4::-212:0:0:5::/64",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_DST = {
    'name':"LC0_INGRESS_DST_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215.0.0.0-215.0.1.0/24",
    'deny_rules':"215.0.2.0-215.0.3.0/24",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_DST_V6 = {
    'name':"LC0_INGRESS_DST_IPV6",
    'policy_desc':"ingress_LC0_V6",
    'type':"L3V6",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215::-215:0:0:1::/64",
    'deny_rules':"215:0:0:2::-215:0:0:3::/64",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_INGRESS_DST = {
    'name':"LC2_INGRESS_DST_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212.0.2.0-212.0.3.0/24",
    'deny_rules':"212.0.0.0-212.0.1.0/24",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_INGRESS_DST_V6 = {
    'name':"LC2_INGRESS_DST_IPV6",
    'policy_desc':"ingress_LC2_V6",
    'type':"L3V6",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212:0:0:2::-212:0:0:3::/64",
    'deny_rules':"212::-212:0:0:1::/64",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_DST = {
    'name':"LC0_EGRESS_DST_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212.0.4.0-212.0.5.0/24",
    'deny_rules':"212.0.6.0-212.0.7.0/24",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_DST_V6 = {
    'name':"LC0_EGRESS_DST_IPV6",
    'policy_desc':"egress_LC0_V6",
    'type':"L3V6",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"212:0:0:4::-212:0:0:5::/64",
    'deny_rules':"212:0:0:6::-212:0:0:7::/64",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_DST = {
    'name':"LC2_EGRESS_DST_IP",
    'policy_desc':"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215.0.6.0-215.0.7.0/24",
    'deny_rules':"215.0.4.0-215.0.5.0/24",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_EGRESS_DST_V6 = {
    'name':"LC2_EGRESS_DST_IPV6",
    'policy_desc':"egress_LC2_V6",
    'type':"L3V6",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':False,
    'ip_protocol':False,
    'permit_rules':"215:0:0:6::-215:0:0:7::/64",
    'deny_rules':"215:0:0:4::-215:0:0:5::/64",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_TP_SRC = {
    'name':"LC0_INGRESS_TP_SRC_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1024",
    'deny_rules':"1109",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_INGRESS_TP_SRC = {
    'name':"LC2_INGRESS_TP_SRC_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1109",
    'deny_rules':"1024",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_TP_SRC = {
    'name':"LC0_EGRESS_TP_SRC_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1109",
    'deny_rules':"1024",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_TP_SRC = {
    'name':"LC2_EGRESS_TP_SRC_IP",
    'policy_desc':"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1024",
    'deny_rules':"1109",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_TP_DST = {
    'name':"LC0_INGRESS_TP_DST_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1024",
    'deny_rules':"1109",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_INGRESS_TP_DST = {
    'name':"LC2_INGRESS_TP_DST_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1109",
    'deny_rules':"1024",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_TP_DST = {
    'name':"LC0_EGRESS_TP_DST_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1109",
    'deny_rules':"1024",
    'match_by':"destination",
    'default_permit':True,
    "capture_port":"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_TP_DST = {
    'name':"LC2_EGRESS_TP_DST_IP",
    'policy_desc':"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1024",
    'deny_rules':"1109",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_TP_RNG_SRC = {
    'name':"LC0_INGRESS_TP_RNG_SRC_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1020..1028",
    'deny_rules':"1105..1113",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_INGRESS_TP_RNG_SRC = {
    'name':"LC2_INGRESS_TP_RNG_SRC_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1105..1113",
    'deny_rules':"1020..1028",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_TP_RNG_SRC = {
    'name':"LC0_EGRESS_TP_RNG_SRC_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1105..1113",
    'deny_rules':"1020..1028",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_TP_RNG_SRC = {
    'name' :"LC2_EGRESS_TP_RNG_SRC_IP",
    'policy_desc' :"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1020..1028",
    'deny_rules':"1105..1113",
    'match_by':"source",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_INGRESS_TP_RNG_DST = {
    'name':"LC0_INGRESS_TP_RNG_DST_IP",
    'policy_desc':"ingress_LC0",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1020..1028",
    'deny_rules':"1105..1113",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC2_INGRESS_TP_RNG_DST = {
    'name':"LC2_INGRESS_TP_RNG_DST_IP",
    'policy_desc':"ingress_LC2",
    'type':"L3",
    'stage':"ingress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1105..1113",
    'deny_rules':"1020..1028",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC0_EGRESS_TP_RNG_DST = {
    'name':"LC0_EGRESS_TP_RNG_DST_IP",
    'policy_desc':"egress_LC0",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet264",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1105..1113",
    'deny_rules':"1020..1028",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC0_Ethernet264"
}

LC2_EGRESS_TP_RNG_DST= {
    'name':"LC2_EGRESS_TP_RNG_DST_IP",
    'policy_desc':"egress_LC2",
    'type':"L3",
    'stage':"egress",
    'ports':"Ethernet132",
    'transport':True,
    'ip_protocol':False,
    'permit_rules':"1020..1028",
    'deny_rules':"1105..1113",
    'match_by':"destination",
    'default_permit':True,
    'capture_port':"T2-1-C8808-LC2_Ethernet132"
}

LC0_TEST1_ACL_TABLES = [LC0_INGRESS_SRC, LC0_INGRESS_SRC_V6, LC0_EGRESS_SRC, LC0_EGRESS_SRC_V6]
LC2_TEST1_ACL_TABLES = [LC2_INGRESS_SRC, LC2_INGRESS_SRC_V6, LC2_EGRESS_SRC, LC2_EGRESS_SRC_V6]

LC0_TEST2_ACL_TABLES = [LC0_INGRESS_DST, LC0_INGRESS_DST_V6, LC0_EGRESS_DST, LC0_EGRESS_DST_V6]
LC2_TEST2_ACL_TABLES = [LC2_INGRESS_DST, LC2_INGRESS_DST_V6, LC2_EGRESS_DST, LC2_EGRESS_DST_V6]

LC0_TEST3_ACL_TABLES = [LC0_INGRESS_TP_SRC, LC0_EGRESS_TP_SRC]
LC2_TEST3_ACL_TABLES = [LC2_INGRESS_TP_SRC, LC2_EGRESS_TP_SRC]

LC0_TEST4_ACL_TABLES = [LC0_INGRESS_TP_DST, LC0_EGRESS_TP_DST]
LC2_TEST4_ACL_TABLES = [LC2_INGRESS_TP_DST, LC2_EGRESS_TP_DST]

LC0_TEST5_ACL_TABLES = [LC0_INGRESS_TP_RNG_SRC, LC0_EGRESS_TP_RNG_SRC]
LC2_TEST5_ACL_TABLES = [LC2_INGRESS_TP_RNG_SRC, LC2_EGRESS_TP_RNG_SRC]

LC0_TEST6_ACL_TABLES = [LC0_INGRESS_TP_RNG_DST, LC0_EGRESS_TP_RNG_DST]
LC2_TEST6_ACL_TABLES = [LC2_INGRESS_TP_RNG_DST, LC2_EGRESS_TP_RNG_DST]

ACL_PATH = "/home/sonic-mgmt/tests/acl/"
APPLY_SLEEP = 30
IGNORE_NETS = ['12.3.0.0/16', '12:3::/32', 'fe80::/64']
logger = logging.getLogger(__name__)

# Functions

def SONiC_Get_Config_DB(duthost, npu, file):
    #Documentation:     Returns the full running config_db of the NPU specified
    #Arguments:         ${npu}=${NONE}  ${file}=${NONE}

    if file == None:
        if npu == None:
            output =  duthost.shell(cmd = "sonic-cfggen -d --print-data")
        else:
            output =  duthost.shell(cmd = "sonic-cfggen -n asic" + npu + " -d --print-data")
    else:
        if npu == None:
            system_call3 = "echo ####################~~~~ sonic-cfggen -d --print-data ~~~~#################### >> "
            duthost.shell(cmd = system_call3 + file)
            system_call4 = "sudo sonic-cfggen -d --print-data >> "
            output =  duthost.shell(cmd = system_call4 + file)
        else:
            system_call5 = "echo '####################~~~~ sonic-cfggen -n asic"
            system_call6 = " -d --print-data ~~~~####################' >> "
            duthost.shell(cmd = system_call5 + npu + system_call6 + file)
            system_call7 = "sudo sonic-cfggen -n asic"
            system_call8 = " -d --print-data >> "
            output =  duthost.shell(cmd = system_call7 + npu + system_call8 + file)

    return output

def SONiC_Get_Config_DB_Section(duthost, npu, section):
    #Documentation:     Returns specified section of the running config_db of the specified NPU
    #Arguments:         ${npu}=${NONE}  ${section}=${NONE}  ${file}=${NONE}

    if "." in section:
        arg = "-v"
    else:
        arg = "--var-json"
    
    if npu == None:
        cmd = "sonic-cfggen -d " + arg + " " + section
        output =  duthost.shell(cmd)
    else:
        cmd = "sonic-cfggen -n asic" + npu + " -d " + arg + " " + section
        output =  duthost.shell(cmd)
    
    return output
 
def SONiC_Get_Running_Configuration(duthost, npu, section, file):
    #Documentation:     Returns the specified section from running configuration config_db#
    #Arguments:         ${npu}=${NONE}  ${section}=${NONE}  ${file}=${NONE}

    if section == None:
        output =  SONiC_Get_Config_DB(duthost, npu, file)
    else:
        output =  SONiC_Get_Config_DB_Section(duthost, npu, section)

    matches = ["error", "unknown", "invalid", "exception", "traceback"]
    if any(x in output.lower() for x in matches):
        return False

    return output

def Show_ACL_Configuration(duthost):
    
    file =  None

    duthost.shell(cmd="show runningconfiguration acl")
    duthost.shell(cmd="sudo show acl table")
    duthost.shell(cmd="sudo show acl rule")
    SONiC_Get_Running_Configuration(duthost = duthost, section = "ACL_TABLE",  file = file)
    SONiC_Get_Running_Configuration(duthost = duthost, section = "ACL_RULE",  file = file)
    #num_npu =  SONiC_Get_NPU_Count(duthost)
    num_npu =  duthost.shell(cmd = "${TB_OBJ.devices.get("+duthost+").custom.num_npu}")
    if num_npu != 1:
        for npu in num_npu:
            SONiC_Get_Running_Configuration(duthost, npu, section = "ACL_TABLE", file = file)
            SONiC_Get_Running_Configuration(duthost, npu, section = "ACL_RULE", file = file)

def Remove_Configured_ACL_Tables(duthost):
    
    cmd = "sudo config acl update full " + ACL_PATH + "/empty_acl_rules.json"
    duthost.shell(cmd)
    #num_npu =  SONiC_Get_NPU_Count(duthost)
    num_npu =  duthost.shell(cmd = "${TB_OBJ.devices.get(" + duthost + ").custom.num_npu}")
    for npu in num_npu:
        cmd2 = "sudo sonic-cfggen -n asic" + npu + " -j /home/admin/acl/empty_acl_tables.json --write-to-db"
        duthost.shell(cmd2)
    duthost.shell(cmd = "sudo sonic-cfggen -j /home/admin/acl/empty_acl_tables.json --write-to-db")
    Show_ACL_Configuration(duthost)

def SONiC_Get_Interfaces_For_Multi_NPU(duthost):
    #[Documentation]  Get Interfaces respective of their ASIC
    #...              and return them as a dictionary.
    #[Arguments]      ${dut}

    ASIC_INTS = {}
    num_npu = duthost.shell(cmd = "${TB_OBJ.devices.get("+duthost+").custom.num_npu}")
    for x in range(num_npu):
        ints = SONiC_Get_ASIC_Interfaces(duthost,x)
        ASIC_INTS.update({"asic" + x: ints})

    #set suite variable  ${ASIC_INTS}

    return ASIC_INTS

def SONiC_Get_ASIC_Interfaces(duthost, asic):
    #[Documentation]  Get Interfaces respective of their ASIC
    #...              and return them in a dictionary.
    #[Arguments]      ${asic}

    output = duthost.shell(cmd = "show int status -n asic" + asic + " -d all")
    output = output.splitlines()
    output = output[2:]
    logging.info("ASIC Interface {}".format(output))
    ints = []
    for line in output:
        int =  line.split()
        int = int[0]
        ints.append(int)

    return ints

def SONiC_Get_ASIC_for_Interface(duthost, interface):
    #[Documentation]  Takes the interface as an argument (Ethernet or Portchannel),
    #...              and grabs and returns the corresponding ASIC.
    #[Arguments]      ${interface}

    ASIC = SONiC_Get_Interfaces_For_Multi_NPU(duthost)
    ASIC_INTS = {}
    ASIC_INTS.udpate({ASIC})

    #num_npu = SONiC_Get_NPU_Count(duthost)
    num_npu =  duthost.shell(cmd = "${TB_OBJ.devices.get(" + duthost + ").custom.num_npu}")
    for x in range(num_npu):
        asic_interfaces = ASIC_INTS.get("asic" + x)
        #continue for loop if  "'${interface}'" not in """${asic_interfaces}"""
        if interface in asic_interfaces <= 0:
            continue

        asic = asic + x

    message = "Interface not found on any asic"
    if asic == "":
        return False
    elif asic == message:
        return False
    else:
        return asic

def Create_ACL_Table_Dictionaries(duthost, ACL_Tables):

    tables_config_db =  {}
    ports = []
    # Generate config_db dictionary
    table_dbs =  {}
    for table in ACL_Tables:
        table_ports =  []
        port_string = table.get(ports)
        if "," in port_string:
            string = port_string.split(',')
            ports.append(string)
            table_ports.append(ports)
        else:
            table_ports.append(port_string)

        table_db =  {}
        table_db.update({"policy_desc":table["policy_desc"], "ports":table_ports, "type":table["type"], "stage":table["stage"]})
        table_dbs.update({"table[name]":table_db})

    tables_config_db.update({"config_db":table_dbs})
    num_npu = duthost.shell(cmd = "${TB_OBJ.devices.get("+duthost+").custom.num_npu}")
    if num_npu != 1:
        # Generate config_db# dictionaries
        for npu in range(num_npu):
            table_dbs = {}
            for table in ACL_Tables:
                table_ports = []
                port_string = table.get("ports")
                if "," in port_string:
                    string = port_string.split(',')
                    ports.append(string)
                    table_ports.append(ports)
                else:
                    table_ports.append(port_string)

                asic_ports = {}
                for port in table_ports:
                    asic = SONiC_Get_ASIC_for_Interface(duthost, port)
                    asic_num =  asic.rpartition("asic")[2]
                    if npu == asic_num:
                        asic_ports.append(port)

                table_db = {}
                table_db.udpate({"policy_desc":table["policy_desc"], "ports":asic_ports, "type":table["type"], "stage":table["stage"]})
                table_dbs.update({table["name"]:table_db})

            tables_config_db.update({"config_db" + npu:table_dbs})

    logger.info("ACL Table Dictionary {}".format(tables_config_db))

    return tables_config_db

def Generate_JSON_File_and_Save_to_DUT(duthost, dict, filename):
    path = ACL_PATH

    #prev_log_level =  Logger.setLevel(logging.ERROR)
    json_dict =  json.dumps(dict)
    logger.info('JSON Dictionary {}'.format(json_dict))
    
    file = open("/home/sonic-mgmt/tests/acl/" + filename, "w")
    file.close

    #set timeout "300"
    wait_until(timeout = 300)
    json_output = duthost.shell(cmd = "sonic-cfggen -j " + path + "/" + filename + " --print-data")
    
    #set timeout "120"
    wait_until(timeout = 120)
    logger.setLevel(logging.ERROR)

    return json_output

def Generate_ACL_TABLE_JSON_Files(duthost, dictionary):

    temp_dict = {}
    dict = dictionary.get('config_db')
    temp_dict.update({"ACL_TABLE":dict})
    filename = "config_db_acl_tables.json"
    json_file = Generate_JSON_File_and_Save_to_DUT(duthost, temp_dict, filename)
    #num_npu = SONiC_Get_NPU_Count(duthost)
    num_npu = duthost.shell(cmd = "${TB_OBJ.devices.get("+ duthost +").custom.num_npu}")
    if num_npu != 1:
        for npu in range(num_npu):
            temp_dict = {}
            config_db = "config_db" + npu
            dict = dictionary.get(config_db)
            temp_dict.update({"ACL_TABLE":dict})
            file = "config_db" + npu + "_acl_tables.json"
            json_file = Generate_JSON_File_and_Save_to_DUT(duthost, temp_dict, file)

def Configure_ACL_Tables(duthost, LC_TEST_ACL_TABLES):

    tables_config_db =  Create_ACL_Table_Dictionaries(duthost, LC_TEST_ACL_TABLES)
    Generate_ACL_TABLE_JSON_Files(duthost, tables_config_db)
    cmd = "sudo sonic-cfggen -j " + ACL_PATH + "/config_db_acl_tables.json --write-to-db"
    duthost.shell(cmd)
    #num_npu = SONiC_Get_NPU_Count(duthost)
    num_npu = duthost.shell(cmd = "${TB_OBJ.devices.get("+duthost+").custom.num_npu}")
    if num_npu != 1:
        for npu in num_npu:
            cmd2 = "sudo sonic-cfggen -n asic"+npu+" -j "+ACL_PATH+"/config_db" + npu + "_acl_tables.json --write-to-db"
            duthost.shell(cmd2)
    Show_ACL_Configuration(duthost)

def Get_IP_Range(start_ip, end_ip, prefix):
    
    #prev_log_level =  set log level  ERROR
    host_nets = []
    network = eval(ipaddress.ip_network(start_ip/prefix).with_hostmask)
    hostmask =  network.rpartition("/")[2]
    start_int = eval(int(ipaddress.ip_address(start_ip)))
    step_int = eval(int(ipaddress.ip_address(hostmask)) + 1)
    end_int = eval(int(ipaddress.ip_address(end_ip)) + step_int)
    for x in range(start_int, end_int, step_int):
        net = eval(ipaddress.ip_address(x))
        host_nets.append(net/prefix)

    logger.setLevel(logging.ERROR)

    return host_nets

def Get_Host_IPs(ip_string):
    
    host_ips = []
    ip_list = []
    ips = []
    if "," in ip_string:
        string = ip_string.split(',')
        ip_list.append(string)
        for ip in ip_list:
            if "-" in ip:
                ip_range, prefix = ip.split('/', 1)
                start_ip, end_ip = ip_range.split('-', 1)
                ips = Get_IP_Range(start_ip, end_ip, prefix)
                host_ips.append(ips)
            else:
                host_ips.append(ip)

    elif "-" in ip_string:
        ip_range, prefix = ip_string.split('/', 1)
        start_ip, end_ip = ip_range.split('-', 1)
        ips = Get_IP_Range(start_ip, end_ip, prefix)
        host_ips.append(ips)
    else:
        host_ips.append(ip_string)

    return host_ips

def Create_ACL_Rule_Dictionaries(duthost, ACL_Table):
    
    table_rules = {}
    for table in ACL_Table:
        rules = {}
        # Create Default Permit Rule if necessary
        if table["default_permit"]:
            sequence_id =  {"sequence-id":"9998"}
            forwarding_action =  {"forwarding-action":"ACCEPT"}
            action_config =  {"config":forwarding_action}
            rule_config =  {"config":sequence_id, "actions":action_config}
            rules.update({1:rule_config})
        
        if table["transport"]:
            permit_rules = permit_rules.append(table[permit_rules])
            deny_rules = deny_rules.append(table[deny_rules])
            all_rules = permit_rules + deny_rules
            all_rules = list(filter(None, all_rules))
            all_rules = sorted(all_rules, key= str)
            # Create Rules
            for index, rule in enumerate(all_rules):
                seq_id = 1 + index
                if table["default_permit"]:
                    seq_id = 1 + seq_id

                seq_id_string = str(seq_id)
                # Create Dictionaries
                sequence_id = {"sequence-id":seq_id}
                if rule in permit_rules:
                    forwarding_action = {"forwarding-action":"ACCEPT"}
                    action_config = {"config":forwarding_action}
                elif rule in deny_rules:
                    forwarding_action = {"forwarding-action":"DROP"}
                    action_config = {"config":forwarding_action}
                else:
                    logger.debug(duthost.shell('Rule' + rule + 'could not be found in either permit nor deny list.'))
                    continue
                
                match_by = {table[match_by]-port:rule}
                transport_config = {"config":match_by}
                rule_config = {"config":sequence_id, "actions":action_config, "transport":transport_config}
                rules.update({"seq_id_string":rule_config})

            acl_entry = {"acl-entry":rules}
            acl_entries = {"acl-entries":acl_entry}
            table_rules.update({table["name"]:acl_entries})
        else:
            permit_rules = Get_Host_IPs(table[permit_rules])
            deny_rules = Get_Host_IPs(table[deny_rules])
            all_rules = permit_rules + deny_rules
            all_rules = list(filter(None, all_rules))
            all_rules = sorted(all_rules, key= str)
            # Create Rules
            if all_rules:
                for index, rule in enumerate(all_rules):
                    seq_id = 1 + index
                    if table["default_permit"]:
                        seq_id = 1 + seq_id

                    seq_id_string = str(seq_id)
                    # Create Dictionaries
                    sequence_id = {"sequence-id":seq_id}
                    if rule in permit_rules:
                        forwarding_action = {"forwarding-action":"ACCEPT"}
                        action_config = {"config":forwarding_action}
                        if table["ip_protocol"]:
                            protocol = table["permit_ip_protocol"]

                    elif rule in deny_rules:
                        forwarding_action = {"forwarding-action":"DROP"}
                        action_config = {"config":forwarding_action}
                        if table["ip_protocol"]:
                            protocol = table["deny_ip_protocol"]

                    else:
                        logger.debug(duthost.shell('Rule' + rule + 'could not be found in either permit nor deny list.'))
                        continue

                    if table["ip_protocol"]:
                        match_by = {table[match_by]-ip-address:rule, "protocol":protocol}
                    else:
                        match_by = {table[match_by]-ip-address:rule}

                    ip_config = {"config":"match_by"}
                    rule_config = {"config":sequence_id, "actions":action_config, "ip":ip_config}
                    rules.update({"seq_id_string":"rule_config"})

            else:
                permit_rules = permit_rules.append(table["permit_ip_protocol"])
                deny_rules = deny_rules.append(table["deny_ip_protocol"])
                all_rules = permit_rules + deny_rules
                for index, rule in enumerate(all_rules):
                    seq_id = 1 + index
                    if table["default_permit"]:
                        seq_id = 1 + seq_id

                    seq_id_string = str(seq_id)
                    # Create Dictionaries
                    sequence_id = {"sequence-id":seq_id}
                    if rule in permit_rules:
                        forwarding_action = {"forwarding-action":"ACCEPT"}
                        action_config = {"config":forwarding_action}
                        protocol = table["permit_ip_protocol"]
                    elif rule in deny_rules:
                        forwarding_action = {"forwarding-action":"DROP"}
                        action_config = {"config":forwarding_action}
                        protocol = table["deny_ip_protocol"]
                    else:
                        logger.debug(duthost.shell('Rule' + rule + 'could not be found in either permit nor deny list.'))
                        continue

                    match_by = {"protocol":protocol}
                    ip_config = {"config":match_by}
                    rule_config = {"config":sequence_id, "actions":action_config, "ip":ip_config}
                    rules.update({"seq_id_string":rule_config})

            acl_entry = {"acl-entry":rules}
            acl_entries = {"acl-entries":acl_entry}
            table_rules.update({table["name"]:acl_entries})

    acl_set = {"acl-set":table_rules}
    acl_sets = {"acl-sets":acl_set}
    acl = {"acl":acl_sets}

    return acl

def Configure_ACL_Rules(duthost, ACL_Table):

    rules_config = Create_ACL_Rule_Dictionaries(duthost, ACL_Table)
    json_file = Generate_JSON_File_and_Save_to_DUT(duthost, rules_config,  "acl_rules.json")
    #set timeout "600"
    wait_until(timeout = 600)
    cmd = "sudo config acl update full " + ACL_PATH + "/acl_rules.json"
    duthost.shell(cmd)
    #set timeout "120"
    wait_until(timeout = 120)
    time.sleep(APPLY_SLEEP)
    Show_ACL_Configuration(duthost)

"""
def Get_Permit_Deny_Matches(port, ACL_TABLES):
    
    #prev_log_level =  set log level  ERROR
    port_permit = []
    port_deny = []
    for table in ACL_TABLES:
        if table["capture_port"] == port:
            permit_rules = Get_Host_IPs(table["permit_rules"])
            for rule in permit_rules: 
                port_permit.append(rule)

            deny_rules = Get_Host_IPs(table["deny_rules"])
            for rule in deny_rules: 
                port_deny.append(rule)

    logger.setLevel(logging.ERROR)

    return  port_permit, port_deny

    """

"""
def Verify_ACL_Rules(LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES):

    # Get Port Captures
    source_capture_ports = []
    dest_capture_ports = []
    #for table in ACL_TABLES:
    for table in (LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES):
        if "source" in table["match_by"]:
            add = eval(table["capture_port"] in source_capture_ports)
            if add == False:
                source_capture_ports.append(table["capture_port"])
        elif "destination" in table["match_by"]:
            add = eval(table["capture_port"] in dest_capture_ports)
            if add == False:
                dest_capture_ports.append(table["capture_port"])
        else:
            logging.info("Please set 'match_by' to either 'source' or 'destination'.")

    capture_ports =  source_capture_ports + dest_capture_ports
    # Verify Port Captures
    for port in capture_ports:
        ip_matches = []
        source_ips = []
        destination_ips = []
        source_ips, destination_ips =  Spirent Port Packet Capture  ${port}  start_capture=${start_capture}
        if port in source_capture_ports:
            ip_matches.append(source_ips)
        elif port in dest_capture_ports:
            ip_matches.append(destination_ips)
        else:
            logging.info("Could not determine port 'match by'.")

        #prev_log_level =  set log level  ERROR
        for ip in ip_matches:
            if "Cisco" in ip:
                ip_matches.remove(ip)
            else:
                for net in IGNORE_NETS:
                    stat = eval(ipaddress.ip_address(ip) in ipaddress.ip_network(net))
                    if stat:
                        ip_matches.remove(ip)

        logger.setLevel(logging.ERROR)
        if ip_matches == "":
            return False
        #permit_nets, deny_nets = Get_Permit_Deny_Matches(port, ACL_TABLES)
        permit_nets, deny_nets = Get_Permit_Deny_Matches(port, [LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES])
        permit_nets = list(filter(None, permit_nets))
        deny_nets = list(filter(None, deny_nets))
        for ip in ip_matches:
            if permit_nets == "":
                empty_list = False
            else:
                empty_list = True

            if not empty_list:
                logger.info("No Permit Rules to Verify")
                break

            for net in permit_nets:
                stat = eval(ipaddress.ip_address(ip) in ipaddress.ip_network(net))
                if stat:
                    break

            if not stat:
                return False
  
        for ip in ip_matches:
            if deny_nets == "":
                empty_list = False
            else:
                empty_list = True

            if not empty_list:
                logging.info("No Deny Rules to Verify")

            for net in deny_nets:
                stat = eval(ipaddress.ip_address(ip) in ipaddress.ip_network(net))
                if stat:
                    break

            if stat:
                return False
"""

"""
def Get_Port_Range(port_range):

    low =  port_range.partition("..")[0]
    high = port_range.rpartition("..")[2]
    ports = []
    for port in range(low, high):
        ports.append(port)

    return ports

def Get_Transport_Permit_Deny_Matches(port, ACL_TABLES):

    #${prev_log_level}=  set log level  ERROR
    port_permit = []
    port_deny = []
    for table in ACL_TABLES:
        if table["capture_port"] == port:
            if ".." in table[permit_rules]:
                permit_rules = Get_Port_Range(table["permit_rules"])
                port_permit.append(permit_rules)
            else:
                port_permit.append(table["permit_rules"])

            if ".." in table["deny_rules"]:
                deny_rules = Get_Port_Range(table["deny_rules"])
                port_deny.append(deny_rules)
            else:
                port_deny.append(table["deny_rules"])

    port_permit =  list(set(port_permit))
    port_deny =  list(set(port_deny))
    logging.setLevel(logging.ERROR)

    return port_permit, port_deny

def Verify_Transport_ACL_Rules(LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES):

    # Get Port Captures
    source_capture_ports = []
    dest_capture_ports = []
    for table in (LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES):
        if "source" in table["match_by"]:
            add = eval(table["capture_port"] in source_capture_ports)
            if add == False:
                source_capture_ports.append(table["capture_port"])
        elif "destination" in table["match_by"]:
            add = eval(table["capture_port"] in dest_capture_ports)
            if add == False:
                dest_capture_ports.append(table["capture_port"])
        else:
            logger.info("Please set 'match_by' to either 'source' or 'destination'.")
            break

    capture_ports = [source_capture_ports, dest_capture_ports]
    # Verify Port Captures
    for port in capture_ports:
        port_matches = []
        source_ports = []
        dest_ports = []
        source_ips, destination_ips, protocols, source_ports, dest_ports=  Spirent Transport Packet Capture  ${port}  start_capture=${start_capture}
        if port in source_capture_ports:
            port_matches.append(source_ports)
        elif port in dest_capture_ports:
            port_matches.append(dest_ports)
        else:
            logger.info("Could not determine port 'match by'.")
            break

        if port_matches == "":
            return False
        permit_ports, deny_ports = Get_Transport_Permit_Deny_Matches(port, [LC_TEST_ACL_TABLES, LC1_TEST_ACL_TABLES])
        permit_nets = list(filter(None, permit_nets))
        deny_nets = list(filter(None, deny_nets))
        for port_match in port_matches:
            if permit_ports == "":
                empty_list = False
            else:
                empty_list = True

            if not empty_list:
                logger.info("No Permit Rules to Verify")
                break

            for port in permit_ports:
                stat = eval(port_match == port)
                if stat:
                    break

            if not stat:
                return False

        for port in port_matches:
            if deny_ports == "":
                empty_list = False
            else:
                empty_list = True

            if not empty_list:
                logger.info("No Deny Rules to Verify")
                break

            for port in deny_ports:
                stat = eval(port_match == port)
                if stat:
                    break
  
            if stat:
                return False
"""
#================#
##  Test Cases ###
#================#

def test_pre_test_action():
    # PRE-TEST ACTIONS
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)
    #SPRT Start Streams

def test_match_sourceip():
# TEST 1: Verify INGRESS/EGRESS ACL matching SOURCE IP
    Configure_ACL_Tables(LC0, LC0_TEST1_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST1_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST1_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST1_ACL_TABLES)
    #Verify_ACL_Rules(LC0_TEST1_ACL_TABLES, LC2_TEST1_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_match_destip():
# TEST 2: Verify INGRESS/EGRESS ACL matching DESTINATION IP
    Configure_ACL_Tables(LC0, LC0_TEST2_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST2_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST2_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST2_ACL_TABLES)
    #Verify_ACL_Rules(LC0_TEST2_ACL_TABLES, LC2_TEST2_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_match_sourcel4_port():
# TEST 3: Verify INGRESS/EGRESS ACL matching SOURCE L4 PORT
    Configure_ACL_Tables(LC0, LC0_TEST3_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST3_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST3_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST3_ACL_TABLES)
    #Verify_Transport_ACL_Rules(LC0_TEST3_ACL_TABLES, LC2_TEST3_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_match_destl4_port():
# TEST 4: Verify INGRESS/EGRESS ACL matching DESTINATION L4 PORT
    Configure_ACL_Tables(LC0, LC0_TEST4_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST4_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST4_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST4_ACL_TABLES)
   # Verify_Transport_ACL_Rules(LC0_TEST4_ACL_TABLES, LC2_TEST4_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_match_sourcel4_portrange():
# TEST 5: Verify INGRESS/EGRESS ACL matching SOURCE L4 PORT RANGE
    Configure_ACL_Tables(LC0, LC0_TEST5_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST5_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST5_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST5_ACL_TABLES)
    #Verify_Transport_ACL_Rules(LC0_TEST5_ACL_TABLES, LC2_TEST5_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_match_destl4_portrange():
# TEST 6: Verify INGRESS/EGRESS ACL matching DESTINATION L4 PORT RANGE
    Configure_ACL_Tables(LC0, LC0_TEST6_ACL_TABLES)
    Configure_ACL_Rules(LC0, LC0_TEST6_ACL_TABLES)
    Configure_ACL_Tables(LC2, LC2_TEST6_ACL_TABLES)
    Configure_ACL_Rules(LC2, LC2_TEST6_ACL_TABLES)
    #Verify_Transport_ACL_Rules(LC0_TEST6_ACL_TABLES, LC2_TEST6_ACL_TABLES)
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

def test_post_test_action():
# POST-TEST ACTIONS
    Remove_Configured_ACL_Tables(LC0)
    Remove_Configured_ACL_Tables(LC2)

#==============#
### Keywords ###
#==============#

