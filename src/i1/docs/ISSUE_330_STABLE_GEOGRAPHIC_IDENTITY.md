# #330: stable geographic option identity

This change removes the time suffix only for geographically identical one-hop Frontier/Transit proposals. The canonical target reference already includes physical origin and destination (and the witnessed frontier objective for transit). Current capture and source time validation still occur in Planning and Exploration; Stage11 evaluates the newly proposed plan every cycle.

No new knowledge, primitive, TD bonus or motor priority. Does not transfer evidence between route hops (#326). Exact-source parity pins and generated-I1 tests cover this bounded change. No new behavioral/population campaign.
