"""A1-C M11 published TD update -> inspectable bias-feature eligibility.

Pure read-only arithmetic. For full M11 custody, run the independent original
48-ZIP verifier against source SHA 26f7929b... and run 40944104333.
This reconstructs only the constant bias feature, NOT full Q, and does not
certify benefits or permit new I1 births.
"""
from collections import defaultdict
from math import isfinite


def _finite(value):
    if type(value) is dict and set(value) == {"$f64"}:
        result = float.fromhex(value["$f64"])
        if result.hex().lower() != value["$f64"]:
            raise ValueError("noncanonical M11 float")
    elif type(value) in (int, float) and type(value) is not bool:
        result = float(value)
    else:
        raise ValueError("not a numeric TD field")
    if not isfinite(result):
        raise ValueError("nonfinite TD field")
    return result


def reconstruct_bias_updates(events, *, beta, lambda_e, eta):
    """Reconstruct e_bias and delta_w_bias for each native TD publication.

    Canonical update_segment decays all traces by (beta*lambda_e)**length
    and increments the previous signature by phi_bias=1. Only the bias
    feature is state-independent; the full feature vector is not inferred.
    """
    if not (type(beta) in (int, float) and 0 < beta < 1
            and type(lambda_e) in (int, float) and 0 <= lambda_e <= 1
            and type(eta) in (int, float) and isfinite(eta) and eta > 0):
        raise ValueError("invalid effective born TD coefficients")
    trace = defaultdict(float)
    results = []
    for event in events:
        if event.get("kind") != "td_update_published":
            continue
        data = event["data"]
        length = data["segment_length"]
        if type(length) is not int or length < 1:
            raise ValueError("invalid TD segment")
        factor = (beta * lambda_e) ** length
        for sig in tuple(trace):
            trace[sig] *= factor
        prev = data["previous_signature"]
        if not isinstance(prev, str) or not prev:
            raise ValueError("missing TD previous signature")
        trace[prev] += 1.0
        declared = data["updated_signatures"]
        if (type(declared) is not list
                or len(declared) != len(set(declared))
                or set(declared) != {s for s, value in trace.items()
                                    if value != 0.0}):
            raise ValueError("M11 published signatures contradict eligibility")
        delta = _finite(data["delta"])
        results.append({
            "step": event["t_monde"],
            "previous_signature": prev,
            "trace_bias": dict(trace),
            "bias_weight_increment": {
                sig: eta * delta * value for sig, value in trace.items()},
        })
    return results
