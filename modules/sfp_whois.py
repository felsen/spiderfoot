#-------------------------------------------------------------------------------
# Name:         sfp_whois
# Purpose:      SpiderFoot plug-in for scanning retreived content by other
#               modules (such as sfp_spider) and identifying e-mail addresses
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     06/04/2012
# Copyright:   (c) Steve Micallef 2012
# Licence:     GPL
#-------------------------------------------------------------------------------

import sys
import re
import pythonwhois
from sflib import SpiderFoot, SpiderFootPlugin, SpiderFootEvent

class sfp_whois(SpiderFootPlugin):
    """Whois:Perform a WHOIS look-up on domain names and owned netblocks."""

    # Default options
    opts = {
    }

    # Option descriptions
    optdescs = {
    }

    results = list()

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc

        self.results = list()

        for opt in userOpts.keys():
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return ["DOMAIN_NAME", "OWNED_NETBLOCK"]

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return [ "DOMAIN_WHOIS", "NETBLOCK_WHOIS", "DOMAIN_REGISTRAR" ]

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data
        parentEvent = event.sourceEvent

        if eventData in self.results:
            return None
        else:
            self.results.append(eventData)

        self.sf.debug("Received event, " + eventName + ", from " + srcModuleName)

        try:
            data = pythonwhois.net.get_whois_raw(eventData)
        except BaseException as e:
            self.sf.error("Unable to perform WHOIS on " + eventData + ": " + str(e), False)
            return None

        if eventName == "DOMAIN_NAME":
            typ = "DOMAIN_WHOIS"
        else:
            typ = "NETBLOCK_WHOIS"

        evt = SpiderFootEvent(typ, '\n'.join(data), self.__name__, event)
        self.notifyListeners(evt)

        info = pythonwhois.parse.parse_raw_whois(data, True)
        if eventName == "DOMAIN_NAME" and info['registrar'] != None:
            evt = SpiderFootEvent("DOMAIN_REGISTRAR", info['registrar'][0], 
                self.__name__, event)
            self.notifyListeners(evt)

# End of sfp_whois class
