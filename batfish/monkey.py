from pybatfish.client.commands import *
from pybatfish.question.question import load_questions
from pybatfish.datamodel.flow import (HeaderConstraints,
                                         PathConstraints)
from pybatfish.question import bfq
from helpers import set_pd_display
import logging
import random
import sys

set_pd_display()
logging.disable(sys.maxsize)

NETWORK_NAME = "ebgp-spine-leaf-network1"
BASE_SNAPSHOT_NAME = "ebgp-spine-leaf-snapshot1"
SNAPSHOT_PATH = "nxos9k-ebgp-spine-leaf/snapshot-2"
BATFISH_SERVICE_IP = "172.29.236.139"

bf_session.host = BATFISH_SERVICE_IP
load_questions()

bf_set_network(NETWORK_NAME)
bf_init_snapshot(SNAPSHOT_PATH, name=BASE_SNAPSHOT_NAME, overwrite=True)

links = bfq.edges(nodes="/leaf|spine/").answer(BASE_SNAPSHOT_NAME).frame()

for i in range(20):
    failed_link1_index = random.randint(0, len(links) - 1)
    failed_link2_index = random.randint(0, len(links) - 1)
    print("Deactivating Links:{} + {}".format(links.loc[failed_link1_index].Interface,
                                                  links.loc[failed_link2_index].Interface))

    FAIL_SNAPSHOT_NAME = "fail_snapshot"
    bf_fork_snapshot(
        BASE_SNAPSHOT_NAME,
        FAIL_SNAPSHOT_NAME,
        deactivate_interfaces=[links.loc[failed_link1_index].Interface,
                               links.loc[failed_link2_index].Interface],
        overwrite=True
    )

    answer = bfq.differentialReachability(
        headers=HeaderConstraints(dstIps='server2')
    ).answer(
        snapshot=FAIL_SNAPSHOT_NAME,
        reference_snapshot=BASE_SNAPSHOT_NAME
    )

    if len(answer.frame()) > 0:
        sys.exit(0) 
        print(links.iloc[[failed_link1_index, failed_link2_index]])
        break

